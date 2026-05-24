"""Agentic Workbench — interface Tkinter para o PAM (complementa a CLI)."""

from __future__ import annotations

import argparse
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from dotenv import load_dotenv

from pam.agent_registry import AgentRegistry
from pam.config_loader import list_projects, load_project
from pam.runtime_profiles import list_resolved_profiles
from pam.settings_manager import SettingsManager, SettingsManagerError
from pam.task_manager import TaskManager

PAD = 8
FONT_MONO = ("Consolas", 10)
WINDOW_GEOMETRY = "1120x780"
WINDOW_MIN = (960, 640)

EDITOR_COMMANDS: dict[str, str] = {
    "cursor": "cursor",
    "vscode": "code",
}

EDITOR_LABELS: dict[str, str] = {
    "cursor": "Cursor",
    "vscode": "VS Code",
}


class EditorOpenError(RuntimeError):
    """Falha ao abrir projeto em editor externo."""


def open_project_in_editor(editor: str, path: str | Path) -> None:
    """
    Abre pasta do projeto no editor externo (cursor ou code).

    Raises:
        EditorOpenError: caminho inválido, comando ausente ou falha ao executar.
    """
    key = editor.strip().lower()
    command = EDITOR_COMMANDS.get(key)
    if not command:
        raise EditorOpenError(
            f"Editor desconhecido: '{editor}'. Use: cursor, vscode."
        )

    project_path = Path(path).expanduser().resolve()
    if not project_path.is_dir():
        raise EditorOpenError(
            f"Pasta do projeto não encontrada:\n{project_path}"
        )

    executable = shutil.which(command)
    if not executable:
        label = EDITOR_LABELS.get(key, command)
        raise EditorOpenError(
            f"Comando '{command}' não encontrado no PATH.\n\n"
            f"Instale o {label} e garanta que '{command}' está disponível "
            "no terminal (Shell Command: Install 'cursor'/'code' command)."
        )

    try:
        subprocess.Popen(
            [executable, str(project_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        label = EDITOR_LABELS.get(key, command)
        raise EditorOpenError(
            f"Não foi possível abrir o projeto no {label}:\n{exc}"
        ) from exc


class PamGuiApp:
    """Workbench desktop que delega execução aos handlers da CLI."""

    COMMANDS = ("plan", "run", "review", "resume")

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Project Agent Manager — Agentic Workbench")
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(*WINDOW_MIN)

        self._settings = SettingsManager()
        self._task_manager = TaskManager()
        self._log_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._running = False
        self._provider_status_labels: dict[str, ttk.Label] = {}

        self.project_var = tk.StringVar()
        self.folder_var = tk.StringVar()
        self.command_var = tk.StringVar(value="plan")
        self.agent_var = tk.StringVar(value="")
        self.task_var = tk.StringVar()
        self.force_onboard_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.refresh_projects()
        self.refresh_provider_status()
        self._poll_log_queue()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=PAD)
        outer.pack(fill=tk.BOTH, expand=True)

        main_paned = ttk.PanedWindow(outer, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(main_paned)
        log_frame = ttk.LabelFrame(main_paned, text="Saída / log", padding=PAD)
        main_paned.add(top, weight=3)
        main_paned.add(log_frame, weight=2)

        workbench = ttk.PanedWindow(top, orient=tk.HORIZONTAL)
        workbench.pack(fill=tk.BOTH, expand=True)

        sidebar = self._build_sidebar(top)
        content = self._build_content_notebook(top)
        workbench.add(sidebar, weight=1)
        workbench.add(content, weight=4)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=FONT_MONO,
            spacing1=2,
            spacing3=2,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _build_sidebar(self, parent: ttk.Frame) -> ttk.LabelFrame:
        container = ttk.LabelFrame(parent, text="Projetos", padding=PAD)
        inner = ttk.Frame(container)
        inner.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.Frame(inner)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.project_listbox = tk.Listbox(
            list_frame,
            height=14,
            exportselection=False,
            font=("Segoe UI", 10),
        )
        list_scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.project_listbox.yview
        )
        self.project_listbox.configure(yscrollcommand=list_scroll.set)
        self.project_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.project_listbox.bind("<<ListboxSelect>>", self._on_project_list_select)

        self.repo_label = ttk.Label(
            inner,
            text="Repositório: —",
            wraplength=220,
            justify=tk.LEFT,
        )
        self.repo_label.pack(anchor=tk.W, pady=(PAD, 0))

        btn_specs = (
            ("Atualizar", self.refresh_projects),
            ("Abrir pasta…", self._browse_folder),
            ("Executar onboard", self._run_onboard),
            ("Abrir no Cursor", lambda: self._open_project_in_editor("cursor")),
            ("Abrir no VS Code", lambda: self._open_project_in_editor("vscode")),
        )
        for text, command in btn_specs:
            ttk.Button(inner, text=text, command=command).pack(
                fill=tk.X, pady=(PAD // 2, 0)
            )

        ttk.Checkbutton(
            inner,
            text="--force (sobrescrever templates)",
            variable=self.force_onboard_var,
        ).pack(anchor=tk.W, pady=(PAD, 0))

        folder_frame = ttk.LabelFrame(inner, text="Pasta para onboard", padding=4)
        folder_frame.pack(fill=tk.X, pady=(PAD, 0))
        ttk.Entry(folder_frame, textvariable=self.folder_var).pack(fill=tk.X)

        return container

    def _build_content_notebook(self, parent: ttk.Frame) -> ttk.Notebook:
        notebook = ttk.Notebook(parent)

        self.tab_ops = ttk.Frame(notebook, padding=PAD)
        self.tab_tasks = ttk.Frame(notebook, padding=PAD)
        self.tab_profiles = ttk.Frame(notebook, padding=PAD)
        self.tab_settings = ttk.Frame(notebook, padding=PAD)
        self.tab_logs = ttk.Frame(notebook, padding=PAD)

        notebook.add(self.tab_ops, text="Operações")
        notebook.add(self.tab_tasks, text="Tasks")
        notebook.add(self.tab_profiles, text="Runtime Profiles")
        notebook.add(self.tab_settings, text="Configurações")
        notebook.add(self.tab_logs, text="Logs")

        self._build_ops_tab()
        self._build_tasks_tab()
        self._build_profiles_tab()
        self._build_settings_tab()
        self._build_logs_tab()

        notebook.pack(fill=tk.BOTH, expand=True)
        return notebook

    def _build_ops_tab(self) -> None:
        main = self.tab_ops

        ttk.Label(
            main,
            text="Execute comandos agenticos no projeto selecionado na barra lateral.",
            wraplength=640,
        ).pack(anchor=tk.W, pady=(0, PAD))

        cmd_frame = ttk.LabelFrame(main, text="Comando agentico", padding=PAD)
        cmd_frame.pack(fill=tk.X, pady=(0, PAD))

        row1 = ttk.Frame(cmd_frame)
        row1.pack(fill=tk.X)
        ttk.Label(row1, text="Comando:", width=14).pack(side=tk.LEFT)
        cmd_box = ttk.Combobox(
            row1,
            textvariable=self.command_var,
            values=self.COMMANDS,
            state="readonly",
            width=16,
        )
        cmd_box.pack(side=tk.LEFT, padx=(0, PAD * 2))
        cmd_box.bind("<<ComboboxSelected>>", self._on_command_changed)

        ttk.Label(row1, text="Agente:", width=10).pack(side=tk.LEFT)
        self.agent_combo = ttk.Combobox(
            row1, textvariable=self.agent_var, width=22, state="readonly"
        )
        self.agent_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        row2 = ttk.Frame(cmd_frame)
        row2.pack(fill=tk.X, pady=(PAD, 0))
        ttk.Label(row2, text="Task:", width=14).pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.task_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, PAD)
        )
        ttk.Button(row2, text="Arquivo…", command=self._browse_task).pack(side=tk.LEFT)

        ttk.Label(cmd_frame, text="Prompt extra (-p):").pack(
            anchor=tk.W, pady=(PAD, 4)
        )
        self.prompt_text = scrolledtext.ScrolledText(
            cmd_frame,
            height=6,
            wrap=tk.WORD,
            font=FONT_MONO,
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        action_row = ttk.Frame(cmd_frame)
        action_row.pack(fill=tk.X, pady=(PAD, 0))
        self.run_btn = ttk.Button(
            action_row, text="Executar", command=self._run_command
        )
        self.run_btn.pack(side=tk.LEFT)

        self._refresh_agents()
        self._on_command_changed()

    def _build_tasks_tab(self) -> None:
        frame = ttk.LabelFrame(
            self.tab_tasks,
            text="Tasks do projeto selecionado",
            padding=PAD,
        )
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text=(
                "Tarefas gerenciadas em ai/tasks/ (lifecycle PAM). "
                "Selecione um projeto na barra lateral e clique em Atualizar."
            ),
            wraplength=640,
        ).pack(anchor=tk.W, pady=(0, PAD))

        columns = ("task_id", "title", "status", "agent")
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tasks_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=14,
        )
        self.tasks_tree.heading("task_id", text="ID")
        self.tasks_tree.heading("title", text="Título")
        self.tasks_tree.heading("status", text="Status")
        self.tasks_tree.heading("agent", text="Agente")
        self.tasks_tree.column("task_id", width=90, stretch=False)
        self.tasks_tree.column("title", width=280)
        self.tasks_tree.column("status", width=90, stretch=False)
        self.tasks_tree.column("agent", width=120, stretch=False)

        scroll = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview
        )
        self.tasks_tree.configure(yscrollcommand=scroll.set)
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tasks_tree.bind("<<TreeviewSelect>>", self._on_task_selected)

        ttk.Button(
            frame,
            text="Atualizar tasks",
            command=self.refresh_tasks,
        ).pack(anchor=tk.W, pady=(PAD, 0))

    def _build_settings_tab(self) -> None:
        frame = ttk.LabelFrame(
            self.tab_settings,
            text="Chaves de API (.env local — nunca exibidas por completo)",
            padding=PAD + 4,
        )
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text=(
                "Configure providers abaixo. Valores são salvos apenas em .env "
                "(gitignored). Cursor: edição profunda. Gemini: tarefas leves (ai-*)."
            ),
            wraplength=640,
        ).pack(anchor=tk.W, pady=(0, PAD + 4))

        for status in self._settings.list_providers_status():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=4)

            ttk.Label(row, text=f"{status.label}:", width=12).pack(side=tk.LEFT)
            status_label = ttk.Label(row, text="—", width=36)
            status_label.pack(side=tk.LEFT, padx=(4, 8))
            self._provider_status_labels[status.provider] = status_label

            ttk.Button(
                row,
                text=f"Atualizar chave {status.label}",
                command=lambda p=status.provider: self._prompt_set_key(p),
            ).pack(side=tk.RIGHT)

        ttk.Button(
            frame,
            text="Atualizar status",
            command=self.refresh_provider_status,
        ).pack(anchor=tk.W, pady=(PAD + 8, 0))

    def _build_profiles_tab(self) -> None:
        frame = ttk.LabelFrame(
            self.tab_profiles,
            text="Runtime Profiles (somente leitura)",
            padding=PAD + 4,
        )
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text=(
                "Provider e modelo por agente conforme "
                "ai/runtime_profiles/default_profiles.yaml. "
                "Agentes sem entrada usam fallback Cursor."
            ),
            wraplength=640,
        ).pack(anchor=tk.W, pady=(0, PAD))

        columns = ("agent", "provider", "model")
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.profiles_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=14,
        )
        self.profiles_tree.heading("agent", text="Agente")
        self.profiles_tree.heading("provider", text="Provider")
        self.profiles_tree.heading("model", text="Modelo")
        self.profiles_tree.column("agent", width=140)
        self.profiles_tree.column("provider", width=100)
        self.profiles_tree.column("model", width=280)

        scroll = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.profiles_tree.yview
        )
        self.profiles_tree.configure(yscrollcommand=scroll.set)
        self.profiles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(
            frame,
            text="Atualizar profiles",
            command=self.refresh_runtime_profiles,
        ).pack(anchor=tk.W, pady=(PAD, 0))

        self.refresh_runtime_profiles()

    def _build_logs_tab(self) -> None:
        frame = ttk.LabelFrame(
            self.tab_logs,
            text="Controle de logs",
            padding=PAD + 4,
        )
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text=(
                "A saída dos comandos aparece em tempo real na área inferior "
                "da janela (painel Saída / log). Use os botões abaixo para "
                "gerenciar a visualização."
            ),
            wraplength=640,
        ).pack(anchor=tk.W, pady=(0, PAD))

        btn_row = ttk.Frame(frame)
        btn_row.pack(anchor=tk.W)
        ttk.Button(btn_row, text="Limpar log", command=self._clear_log).pack(
            side=tk.LEFT, padx=(0, PAD)
        )
        ttk.Button(btn_row, text="Rolar para o fim", command=self._scroll_log_to_end).pack(
            side=tk.LEFT
        )

    def _scroll_log_to_end(self) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def refresh_runtime_profiles(self) -> None:
        """Atualiza tabela de runtime profiles (somente leitura)."""
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)

        for profile in list_resolved_profiles():
            self.profiles_tree.insert(
                "",
                tk.END,
                values=(
                    profile.agent,
                    profile.provider,
                    profile.display_model(),
                ),
            )

    def refresh_tasks(self) -> None:
        """Atualiza lista de tasks do projeto selecionado."""
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)

        project = self.project_var.get().strip()
        if not project:
            return

        for meta in self._task_manager.list_tasks(project=project):
            self.tasks_tree.insert(
                "",
                tk.END,
                iid=meta.task_id,
                values=(meta.task_id, meta.title, meta.status, meta.agent),
            )

    def _on_task_selected(self, _event: object | None = None) -> None:
        selected = self.tasks_tree.selection()
        if not selected:
            return
        task_id = selected[0]
        files = self._task_manager.find_task_files(task_id)
        if files:
            self.task_var.set(str(files[0]))

    def refresh_provider_status(self) -> None:
        """Atualiza labels de status na aba Configurações."""
        load_dotenv(self._settings.env_path, override=True)
        for item in self._settings.list_providers_status():
            label = self._provider_status_labels.get(item.provider)
            if not label:
                continue
            if item.configured:
                text = f"configurado ({item.masked})"
            else:
                text = "não configurado"
            label.configure(text=text)

    def _prompt_set_key(self, provider: str) -> None:
        """Dialog para inserir chave com campo password."""
        try:
            self._settings.validate_provider(provider)
        except SettingsManagerError as exc:
            messagebox.showerror("PAM", str(exc))
            return

        label = provider.capitalize()
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Chave {label}")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        ttk.Label(
            dialog,
            text=f"Digite a chave {label} (não será exibida):",
            padding=(PAD + 4, PAD + 4, PAD + 4, 4),
        ).pack()

        key_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=key_var, show="*", width=48)
        entry.pack(padx=PAD + 4, pady=4)
        entry.focus_set()

        btn_row = ttk.Frame(dialog, padding=PAD + 4)
        btn_row.pack()

        def save() -> None:
            value = key_var.get().strip()
            if not value:
                messagebox.showwarning("PAM", "Chave vazia — operação cancelada.")
                return
            try:
                self._settings.set_key(provider, value)
            except SettingsManagerError as exc:
                messagebox.showerror("PAM", str(exc))
                return
            masked = SettingsManager.mask_key(value)
            self.refresh_provider_status()
            messagebox.showinfo("PAM", f"Chave {label} salva ({masked})")
            dialog.destroy()

        def cancel() -> None:
            dialog.destroy()

        ttk.Button(btn_row, text="Salvar", command=save).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Cancelar", command=cancel).pack(side=tk.LEFT, padx=4)
        dialog.bind("<Return>", lambda _e: save())
        dialog.bind("<Escape>", lambda _e: cancel())

    def _append_log(self, text: str, *, tag: str | None = None) -> None:
        self.log_text.configure(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, text, tag)
        else:
            self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _clear_log(self) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _log(self, message: str) -> None:
        self._append_log(message if message.endswith("\n") else message + "\n")

    def _get_prompt_extra(self) -> str | None:
        text = self.prompt_text.get("1.0", tk.END).strip()
        return text or None

    def _refresh_agents(self) -> None:
        agents = [""] + AgentRegistry().list_agents()
        self.agent_combo["values"] = agents
        if self.agent_var.get() not in agents:
            self.agent_var.set("")

    def refresh_projects(self) -> None:
        projects = list_projects()
        self.project_listbox.delete(0, tk.END)
        for name in projects:
            self.project_listbox.insert(tk.END, name)

        if projects:
            current = self.project_var.get()
            index = projects.index(current) if current in projects else 0
            self.project_listbox.selection_clear(0, tk.END)
            self.project_listbox.selection_set(index)
            self.project_listbox.see(index)
            self.project_var.set(projects[index])
            self._on_project_selected()
        else:
            self.project_var.set("")
            self.repo_label.configure(text="Repositório: (nenhum projeto cadastrado)")

        self.refresh_tasks()

        lines = ["Projetos cadastrados:"]
        if projects:
            for name in projects:
                try:
                    cfg = load_project(name)
                    lines.append(f"  - {name}: {cfg.repo_path}")
                except (FileNotFoundError, ValueError) as exc:
                    lines.append(f"  - {name}: (erro ao carregar — {exc})")
        else:
            lines.append("  (nenhum)")
        self._log("\n".join(lines) + "\n")

    def _on_project_list_select(self, _event: object | None = None) -> None:
        selection = self.project_listbox.curselection()
        if not selection:
            return
        name = self.project_listbox.get(selection[0])
        self.project_var.set(name)
        self._on_project_selected()
        self.refresh_tasks()

    def _on_project_selected(self, _event: object | None = None) -> None:
        name = self.project_var.get()
        if not name:
            return
        try:
            cfg = load_project(name)
            self.repo_label.configure(text=f"Repositório:\n{cfg.repo_path}")
            self.folder_var.set(str(cfg.repo_path))
        except (FileNotFoundError, ValueError) as exc:
            self.repo_label.configure(text=f"Repositório: erro — {exc}")

    def _on_command_changed(self, _event: object | None = None) -> None:
        self.agent_combo.configure(state="readonly")

    def _selected_project_path(self) -> Path | None:
        folder = self.folder_var.get().strip()
        if folder and Path(folder).is_dir():
            return Path(folder)
        name = self.project_var.get().strip()
        if not name:
            return None
        try:
            cfg = load_project(name)
            return Path(cfg.repo_path)
        except (FileNotFoundError, ValueError):
            return None

    def _open_project_in_editor(self, editor: str) -> None:
        path = self._selected_project_path()
        if path is None:
            messagebox.showerror(
                "PAM",
                "Selecione um projeto cadastrado ou informe uma pasta válida.",
            )
            return
        try:
            open_project_in_editor(editor, path)
        except EditorOpenError as exc:
            messagebox.showerror("PAM", str(exc))

    def _browse_folder(self) -> None:
        path = filedialog.askdirectory(title="Selecionar pasta do projeto")
        if path:
            self.folder_var.set(path)

    def _browse_task(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar arquivo de task",
            filetypes=[("Markdown", "*.md"), ("Todos", "*.*")],
        )
        if path:
            self.task_var.set(path)

    def _set_busy(self, busy: bool) -> None:
        self._running = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self.run_btn.configure(state=state)

    def _run_in_thread(self, label: str, func) -> None:
        if self._running:
            messagebox.showwarning("PAM", "Aguarde a operação em andamento.")
            return

        self._set_busy(True)
        self._log(f"\n--- {label} ---\n")

        def worker() -> None:
            stdout = sys.stdout
            stderr = sys.stderr
            log_queue = self._log_queue

            class _Writer:
                def write(self, data: str) -> None:
                    if data:
                        log_queue.put(("log", data))

                def flush(self) -> None:
                    pass

            try:
                sys.stdout = _Writer()
                sys.stderr = _Writer()
                exit_code = func()
            except Exception as exc:  # noqa: BLE001
                self._log_queue.put(("log", f"Erro inesperado: {exc}\n"))
                exit_code = 1
            finally:
                sys.stdout = stdout
                sys.stderr = stderr
                self._log_queue.put(("done", exit_code))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_log_queue(self) -> None:
        while True:
            try:
                kind, payload = self._log_queue.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self._append_log(str(payload))
            elif kind == "done":
                code = int(payload)
                self._set_busy(False)
                self._log(f"--- concluído (código {code}) ---\n")
                if code != 0:
                    self.root.bell()
            elif kind == "refresh":
                self.refresh_projects()
            elif kind == "refresh_tasks":
                self.refresh_tasks()
        self.root.after(100, self._poll_log_queue)

    def _run_onboard(self) -> None:
        from pam.main import cmd_onboard

        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showerror("PAM", "Selecione uma pasta para onboard.")
            return
        if not Path(folder).is_dir():
            messagebox.showerror("PAM", f"Pasta inválida: {folder}")
            return

        args = argparse.Namespace(
            path=folder,
            project_name=None,
            force=self.force_onboard_var.get(),
        )

        def run() -> int:
            code = cmd_onboard(args)
            if code == 0:
                self._log_queue.put(("refresh", None))
            return code

        self._run_in_thread("onboard", run)

    def _run_command(self) -> None:
        from pam.main import cmd_plan, cmd_resume, cmd_review, cmd_run

        project = self.project_var.get().strip()
        if not project:
            messagebox.showerror(
                "PAM",
                "Selecione um projeto cadastrado.\n"
                "Use onboard primeiro ou cadastre em ai/projects/.",
            )
            return

        command = self.command_var.get()
        handlers = {
            "plan": cmd_plan,
            "run": cmd_run,
            "review": cmd_review,
            "resume": cmd_resume,
        }
        handler = handlers[command]

        agent = self.agent_var.get().strip() or None
        task = self.task_var.get().strip() or None
        prompt = self._get_prompt_extra()

        args = argparse.Namespace(
            project=project,
            task=task,
            prompt=prompt,
            agent=agent,
        )

        def run() -> int:
            code = handler(args)
            if code == 0:
                self._log_queue.put(("refresh_tasks", None))
            return code

        self._run_in_thread(command, run)


def start_gui() -> None:
    """Abre a janela principal do Agentic Workbench."""
    load_dotenv()
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    PamGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    start_gui()
