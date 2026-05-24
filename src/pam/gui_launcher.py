"""Desktop Launcher — interface Tkinter para o PAM (complementa a CLI)."""

from __future__ import annotations

import argparse
import queue
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


class PamGuiApp:
    """Launcher desktop que delega execução aos handlers da CLI."""

    COMMANDS = ("plan", "run", "review", "resume")
    KEY_PROVIDERS = ("cursor", "gemini", "openai", "anthropic")

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Project Agent Manager — Desktop Launcher")
        self.root.minsize(720, 600)

        self._settings = SettingsManager()
        self._log_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._running = False
        self._provider_status_labels: dict[str, ttk.Label] = {}

        self.project_var = tk.StringVar()
        self.folder_var = tk.StringVar()
        self.command_var = tk.StringVar(value="plan")
        self.agent_var = tk.StringVar(value="")
        self.task_var = tk.StringVar()
        self.prompt_var = tk.StringVar()
        self.force_onboard_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.refresh_projects()
        self.refresh_provider_status()
        self._poll_log_queue()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tab_ops = ttk.Frame(notebook, padding=4)
        self.tab_settings = ttk.Frame(notebook, padding=8)
        self.tab_profiles = ttk.Frame(notebook, padding=8)
        notebook.add(self.tab_ops, text="Operações")
        notebook.add(self.tab_settings, text="Configurações")
        notebook.add(self.tab_profiles, text="Runtime Profiles")

        self._build_ops_tab()
        self._build_settings_tab()
        self._build_profiles_tab()

    def _build_ops_tab(self) -> None:
        pad = {"padx": 8, "pady": 4}
        main = self.tab_ops

        proj_frame = ttk.LabelFrame(main, text="Projeto cadastrado (PAM)", padding=8)
        proj_frame.pack(fill=tk.X, **pad)

        row = ttk.Frame(proj_frame)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Projeto:").pack(side=tk.LEFT)
        self.project_combo = ttk.Combobox(
            row, textvariable=self.project_var, state="readonly", width=40
        )
        self.project_combo.pack(side=tk.LEFT, padx=(6, 6), fill=tk.X, expand=True)
        self.project_combo.bind("<<ComboboxSelected>>", self._on_project_selected)
        ttk.Button(row, text="Atualizar", command=self.refresh_projects).pack(
            side=tk.LEFT
        )

        self.repo_label = ttk.Label(proj_frame, text="Repositório: —", wraplength=680)
        self.repo_label.pack(anchor=tk.W, pady=(4, 0))

        folder_frame = ttk.LabelFrame(main, text="Pasta do repositório", padding=8)
        folder_frame.pack(fill=tk.X, **pad)

        frow = ttk.Frame(folder_frame)
        frow.pack(fill=tk.X)
        ttk.Entry(frow, textvariable=self.folder_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(frow, text="Selecionar pasta…", command=self._browse_folder).pack(
            side=tk.LEFT, padx=(6, 0)
        )

        onboard_row = ttk.Frame(folder_frame)
        onboard_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Checkbutton(
            onboard_row,
            text="--force (sobrescrever templates)",
            variable=self.force_onboard_var,
        ).pack(side=tk.LEFT)
        ttk.Button(onboard_row, text="Executar onboard", command=self._run_onboard).pack(
            side=tk.RIGHT
        )

        cmd_frame = ttk.LabelFrame(main, text="Comando agentico", padding=8)
        cmd_frame.pack(fill=tk.X, **pad)

        crow = ttk.Frame(cmd_frame)
        crow.pack(fill=tk.X)
        ttk.Label(crow, text="Comando:").grid(row=0, column=0, sticky=tk.W)
        cmd_box = ttk.Combobox(
            crow,
            textvariable=self.command_var,
            values=self.COMMANDS,
            state="readonly",
            width=12,
        )
        cmd_box.grid(row=0, column=1, sticky=tk.W, padx=(6, 16))
        cmd_box.bind("<<ComboboxSelected>>", self._on_command_changed)

        ttk.Label(crow, text="Agente:").grid(row=0, column=2, sticky=tk.W)
        self.agent_combo = ttk.Combobox(
            crow, textvariable=self.agent_var, width=18, state="readonly"
        )
        self.agent_combo.grid(row=0, column=3, sticky=tk.W, padx=(6, 0))

        trow = ttk.Frame(cmd_frame)
        trow.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(trow, text="Task:").pack(side=tk.LEFT)
        ttk.Entry(trow, textvariable=self.task_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6)
        )
        ttk.Button(trow, text="Arquivo…", command=self._browse_task).pack(side=tk.LEFT)

        ttk.Label(cmd_frame, text="Prompt extra (-p):").pack(anchor=tk.W, pady=(6, 0))
        ttk.Entry(cmd_frame, textvariable=self.prompt_var).pack(fill=tk.X)

        action_row = ttk.Frame(cmd_frame)
        action_row.pack(fill=tk.X, pady=(8, 0))
        self.run_btn = ttk.Button(
            action_row, text="Executar comando", command=self._run_command
        )
        self.run_btn.pack(side=tk.LEFT)
        ttk.Button(action_row, text="Limpar log", command=self._clear_log).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        log_frame = ttk.LabelFrame(main, text="Saída / log", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True, **pad)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=14, state=tk.DISABLED, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self._refresh_agents()
        self._on_command_changed()

    def _build_settings_tab(self) -> None:
        frame = ttk.LabelFrame(
            self.tab_settings,
            text="Chaves de API (.env local — nunca exibidas por completo)",
            padding=12,
        )
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text=(
                "Configure providers abaixo. Valores são salvos apenas em .env "
                "(gitignored). Cursor: edição profunda. Gemini: tarefas leves (ai-*)."
            ),
            wraplength=640,
        ).pack(anchor=tk.W, pady=(0, 12))

        for status in self._settings.list_providers_status():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=4)

            ttk.Label(row, text=f"{status.label}:", width=12).pack(side=tk.LEFT)
            status_label = ttk.Label(row, text="—", width=36)
            status_label.pack(side=tk.LEFT, padx=(4, 8))
            self._provider_status_labels[status.provider] = status_label

            ttk.Button(
                row,
                text=f"Inserir/Atualizar chave {status.label}",
                command=lambda p=status.provider: self._prompt_set_key(p),
            ).pack(side=tk.RIGHT)

        ttk.Button(
            frame,
            text="Atualizar status",
            command=self.refresh_provider_status,
        ).pack(anchor=tk.W, pady=(16, 0))

    def _build_profiles_tab(self) -> None:
        frame = ttk.LabelFrame(
            self.tab_profiles,
            text="Runtime Profiles (somente leitura)",
            padding=12,
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
        ).pack(anchor=tk.W, pady=(0, 8))

        columns = ("agent", "provider", "model")
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.profiles_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12,
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
        ).pack(anchor=tk.W, pady=(8, 0))

        self.refresh_runtime_profiles()

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
            padding=(12, 12, 12, 4),
        ).pack()

        key_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=key_var, show="*", width=48)
        entry.pack(padx=12, pady=4)
        entry.focus_set()

        btn_row = ttk.Frame(dialog, padding=12)
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

    def _refresh_agents(self) -> None:
        agents = [""] + AgentRegistry().list_agents()
        self.agent_combo["values"] = agents
        if self.agent_var.get() not in agents:
            self.agent_var.set("")

    def refresh_projects(self) -> None:
        projects = list_projects()
        self.project_combo["values"] = projects
        if projects:
            current = self.project_var.get()
            if current not in projects:
                self.project_var.set(projects[0])
            self._on_project_selected()
        else:
            self.project_var.set("")
            self.repo_label.configure(text="Repositório: (nenhum projeto cadastrado)")

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

    def _on_project_selected(self, _event: object | None = None) -> None:
        name = self.project_var.get()
        if not name:
            return
        try:
            cfg = load_project(name)
            self.repo_label.configure(text=f"Repositório: {cfg.repo_path}")
            self.folder_var.set(str(cfg.repo_path))
        except (FileNotFoundError, ValueError) as exc:
            self.repo_label.configure(text=f"Repositório: erro — {exc}")

    def _on_command_changed(self, _event: object | None = None) -> None:
        self.agent_combo.configure(state="readonly")

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

            class _Writer:
                def write(self, data: str) -> None:
                    if data:
                        self._log_queue.put(("log", data))

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
        prompt = self.prompt_var.get().strip() or None

        args = argparse.Namespace(
            project=project,
            task=task,
            prompt=prompt,
            agent=agent,
        )

        self._run_in_thread(command, lambda: handler(args))


def start_gui() -> None:
    """Abre a janela principal do Desktop Launcher."""
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
