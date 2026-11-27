"""Self-update logic shared by `dh update` and the TUI update modal."""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

RELEASES_URL = "https://github.com/araujoajoao/DevOpsHeroCLI/releases/latest"
DEB_URL = f"{RELEASES_URL}/download/DevOpsHero.deb"
DMG_URL = f"{RELEASES_URL}/download/DevOpsHero.dmg"
WINDOWS_URL = f"{RELEASES_URL}/download/DevOpsHero-windows.zip"
REPO_URL = "https://github.com/araujoajoao/DevOpsHeroCLI"

REPO_DIR = Path(__file__).resolve().parent.parent


@dataclass
class UpdateResult:
    ok: bool
    message: str
    details: str = ""
    restart_required: bool = False


def installer_url() -> str:
    """Download URL of the native installer for the current OS."""
    if sys.platform == "darwin":
        return DMG_URL
    if sys.platform.startswith("win"):
        return WINDOWS_URL
    return DEB_URL


def is_git_checkout() -> bool:
    return (REPO_DIR / ".git").exists() and shutil.which("git") is not None


def perform_update(timeout: int = 120) -> UpdateResult:
    """Updates a git checkout in place (fast-forward only) and reinstalls the package.

    Packaged installs (.deb / .app / ZIP) cannot update themselves in place; for
    those, the result points the user to the right installer for their OS.
    """
    if not is_git_checkout():
        return UpdateResult(
            ok=False,
            message="Instalação sem Git: baixe o instalador mais recente.",
            details=f"{installer_url()}\nOu clone o repositório: git clone {REPO_URL}",
        )

    try:
        pull = subprocess.run(
            ["git", "-C", str(REPO_DIR), "pull", "--ff-only", "origin", "main"],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return UpdateResult(ok=False, message="Falha ao executar git pull.", details=str(exc))

    if pull.returncode != 0:
        return UpdateResult(
            ok=False,
            message="Não foi possível aplicar a atualização (alterações locais ou histórico divergente).",
            details=(pull.stderr or pull.stdout).strip(),
        )

    if "Already up to date" in pull.stdout or "Já está atualizado" in pull.stdout:
        return UpdateResult(ok=True, message="Você já está na versão mais recente.", details=pull.stdout.strip())

    try:
        pip = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-e", str(REPO_DIR)],
            capture_output=True, text=True, timeout=timeout,
        )
        pip_warning = "" if pip.returncode == 0 else pip.stderr.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        pip_warning = str(exc)

    details = pull.stdout.strip()
    if pip_warning:
        details += f"\nAviso ao sincronizar dependências: {pip_warning}"
    return UpdateResult(
        ok=True,
        message="Atualização aplicada. Reinicie o DevOpsHero para usar a nova versão.",
        details=details,
        restart_required=True,
    )
