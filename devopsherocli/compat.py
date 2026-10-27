"""Cross-platform compatibility and environment detection for DevOpsHeroCLI.

Supports Linux, macOS, WSL, Windows (CMD, PowerShell, Windows Terminal).
Includes humorous Easter-egg detection for PowerShell sessions.
"""
from __future__ import annotations

import os
import subprocess
import sys


def is_windows() -> bool:
    """Returns True if running on native Windows."""
    return sys.platform == "win32"


def is_macos() -> bool:
    """Returns True if running on macOS (Darwin)."""
    return sys.platform == "darwin"


def is_linux() -> bool:
    """Returns True if running on Linux (including WSL)."""
    return sys.platform.startswith("linux")


def is_wsl() -> bool:
    """Returns True if running inside Windows Subsystem for Linux (WSL)."""
    if not is_linux():
        return False
    if os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
        return True
    try:
        with open("/proc/version", "r", encoding="utf-8") as f:
            v = f.read().lower()
            return "microsoft" in v or "wsl" in v
    except Exception:
        return False


def _get_parent_process_name() -> str:
    """Attempts to discover the parent process name across OSes without third-party deps."""
    ppid = os.getppid() if hasattr(os, "getppid") else None
    if not ppid:
        return ""

    if is_windows():
        try:
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {ppid}", "/FO", "CSV", "/NH"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=1,
            )
            if out and '"' in out:
                parts = [p.strip().strip('"') for p in out.split(",") if p.strip()]
                if parts:
                    return parts[0].lower()
        except Exception:
            pass
        return ""

    # Linux /proc lookup (instant, zero process spawn)
    comm_path = f"/proc/{ppid}/comm"
    if os.path.exists(comm_path):
        try:
            with open(comm_path, "r", encoding="utf-8") as f:
                return f.read().strip().lower()
        except Exception:
            pass

    # POSIX ps command fallback (macOS, BSD, Solaris)
    try:
        out = subprocess.check_output(
            ["ps", "-o", "comm=", "-p", str(ppid)],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=1,
        ).strip().lower()
        return os.path.basename(out)
    except Exception:
        return ""


def is_powershell() -> bool:
    """Detects whether the current session was launched from or is running inside PowerShell.

    Checks:
    1. DEVOPSHERO_SHELL environment override (e.g. from devopshero.ps1).
    2. PowerShell Core environment variables (POWERSHELL_DISTRIBUTION_CHANNEL, PWSH).
    3. Windows PowerShell variables (PSExecutionPolicyPreference).
    4. Parent process inspection (powershell.exe, pwsh.exe, pwsh).
    5. PSModulePath presence when not under standard CMD prompt.
    """
    # 1. Explicit launcher flag or environment variable
    override = os.environ.get("DEVOPSHERO_SHELL", "").strip().lower()
    if "powershell" in override or "pwsh" in override:
        return True

    # 2. PowerShell Core / Modern pwsh variables (present on Windows, Linux, macOS)
    if os.environ.get("POWERSHELL_DISTRIBUTION_CHANNEL"):
        return True

    # 3. Windows PowerShell specific variables
    if os.environ.get("PSExecutionPolicyPreference"):
        return True

    # 4. Check parent process name
    parent_name = _get_parent_process_name()
    if any(p in parent_name for p in ("powershell", "pwsh")):
        return True

    # 5. Check SHELL environment variable on POSIX
    shell_val = os.environ.get("SHELL", "").lower()
    if shell_val.endswith("pwsh") or shell_val.endswith("powershell"):
        return True

    # 6. Windows fallback: PSModulePath set without typical pure CMD prompt
    if is_windows():
        if "PSModulePath" in os.environ and "PROMPT" not in os.environ:
            return True

    return False


def get_powershell_humor_message(plain: bool = False) -> str:
    """Returns the humorous warning displayed when running under PowerShell."""
    if plain:
        return (
            "====================================================================\n"
            " ⚠️  ALERTA DE SEGURANÇA MENTAL: PowerShell Detectado!\n"
            " Você realmente chama o PowerShell de terminal?! 😂\n"
            " Recomendamos um de verdade (bash/zsh) bem longe do Windows! 🐧🍎\n"
            " Mas relaxa: o DevOpsHero roda suave até aqui. Bons estudos, herói!\n"
            "===================================================================="
        )
    return (
        "[bold #ffd60a]⚠️  ALERTA DE SEGURANÇA MENTAL: PowerShell Detectado![/]\n"
        "[bold white]Você realmente chama o [italic #ff6961]PowerShell[/italic #ff6961] de terminal?! 😂[/]\n"
        "[dim]Recomendamos fortemente um terminal de verdade ([bold #30d158]bash/zsh[/]) bem longe do Windows! 🐧🍎[/]\n"
        "[bold #5ac8fa]Mas relaxa:[/] como somos generosos com sysadmins em recuperação, o [bold green]DevOpsHero[/] funciona 100% aqui também. Aproveite!"
    )


def get_platform_info() -> dict[str, str | bool]:
    """Inspects the runtime environment and returns diagnostics."""
    os_name = "Linux"
    if is_macos():
        os_name = "macOS"
    elif is_windows():
        os_name = "Windows"
    elif is_wsl():
        os_name = "WSL (Linux on Windows)"

    term_app = os.environ.get("TERM_PROGRAM") or os.environ.get("TERM") or "unknown"
    if os.environ.get("WT_SESSION"):
        term_app = "Windows Terminal"

    return {
        "os": os_name,
        "is_wsl": is_wsl(),
        "is_powershell": is_powershell(),
        "terminal": term_app,
        "python_version": sys.version.split()[0],
        "encoding": sys.stdout.encoding if sys.stdout else "unknown",
    }


def ensure_utf8_encoding() -> None:
    """Ensures standard streams use UTF-8 to prevent encoding crashes on Windows and legacy terminals."""
    if is_windows():
        # Enable Windows ANSI Virtual Terminal Processing
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            for handle_id in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
                handle = kernel32.GetStdHandle(handle_id)
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                    kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass

        # Switch code page to UTF-8 via Win32 API
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:
            pass

    for stream in (sys.stdout, sys.stderr, sys.stdin):
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
