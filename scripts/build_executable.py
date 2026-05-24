"""Script de build automatizado do PAM para executável portátil usando PyInstaller."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def build() -> int:
    print("Iniciando build do Project Agent Manager (PAM) Portátil...")

    # Caminhos fundamentais
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    entrypoint = src_dir / "pam" / "main.py"

    if not entrypoint.is_file():
        print(f"Erro: Entrypoint não encontrado em {entrypoint}")
        return 1

    # Separador de paths do PyInstaller (; no Windows, : em outros)
    sep = ";" if os.name == "nt" else ":"

    # Mapeamento de recursos (Dual-Path Assets)
    # Formato: (Origem, Destino)
    resources = [
        (repo_root / "ai" / "agents", "ai/agents"),
        (repo_root / "ai" / "prompts", "ai/prompts"),
        (repo_root / "ai" / "runtime_profiles", "ai/runtime_profiles"),
        (repo_root / "ai" / "pipelines", "ai/pipelines"),
        (repo_root / "protocol", "protocol"),
        (repo_root / ".env.example", "."),
        (src_dir / "pam" / "templates", "pam/templates"),
    ]

    # Prepara os argumentos do PyInstaller
    args = [
        str(entrypoint),
        "--name=pam",
        "--onefile",
        "--clean",
        # Adiciona o diretório src ao PYTHONPATH para o PyInstaller resolver as importações 'pam.xxx'
        f"--paths={src_dir}",
    ]

    for src, dest in resources:
        if not src.exists():
            print(f"Aviso: Recurso ausente no repositório: {src}")
            continue
        args.append(f"--add-data={src}{sep}{dest}")

    print(f"Executando PyInstaller com os argumentos: {args}\n")

    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(args)
        print("\n[SUCESSO] Build concluído com sucesso!")
        print(f"Executável gerado em: {repo_root / 'dist' / 'pam.exe' if os.name == 'nt' else 'pam'}")
        return 0
    except ImportError:
        print("\nErro: PyInstaller não está instalado no ambiente atual.")
        print("Instale executando: pip install pyinstaller")
        return 1
    except Exception as exc:
        print(f"\nErro durante a execução do PyInstaller: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(build())
