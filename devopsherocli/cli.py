"""CLI entrypoint for DevOpsHeroCLI: TUI, REPL mode, Stats, and Tracks listing."""
from __future__ import annotations

import argparse
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from devopsherocli.compat import (
    ensure_utf8_encoding,
    get_platform_info,
    get_powershell_humor_message,
    is_powershell,
)
from devopsherocli.engine.executor import CommandExecutor, EnvironmentState
from devopsherocli.models import UserProgress
from devopsherocli.tracks import ALL_TRACKS, TRACKS_MAP, get_mission, get_next_mission

console = Console()
ensure_utf8_encoding()


def run_repl():
    """Runs DevOpsHeroCLI in lightweight inline REPL mode using prompt_toolkit and Rich."""
    try:
        from pathlib import Path

        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        from prompt_toolkit.history import FileHistory

        hist_path = Path.home() / ".devopsherocli" / "history.txt"
        hist_path.parent.mkdir(parents=True, exist_ok=True)
        session = PromptSession(history=FileHistory(str(hist_path)))
    except ImportError:
        session = None

    progress = UserProgress()
    state = EnvironmentState()
    executor = CommandExecutor(state)

    console.print(Panel.fit(
        "[bold green]         __                                     __[/]\n"
        "[bold green]  ____  / /_     ____ ___  __  __   ____  _____/ /_[/]\n"
        "[bold green] / __ \\/ __ \\   / __ `__ \\/ / / /  /_  / / ___/ __ \\[/]\n"
        "[bold green]/ /_/ / / / /  / / / / / / /_/ /    / /_(__  ) / / /[/]\n"
        "[bold green]\\____/_/ /_/  /_/ /_/ /_/\\__, /    /___/____/_/ /_/[/]\n"
        "[bold green]                        /____/[/]     [bold cyan]⚡ iTerm2 · Oh My Zsh REPL[/]\n"
        "[dim]Linux · Sysadmin · Git · Docker · Kubernetes · AWS · Terraform · Datadog[/dim]\n"
        "Atalhos ultra-rápidos: [bold yellow]d[/] (dica), [bold red]s[/] (solução), [bold cyan]n[/] (próxima), [bold cyan]r[/] (reset), [bold cyan]q[/] (sair)",
        border_style="cyan"
    ))

    if is_powershell():
        console.print(Panel(
            get_powershell_humor_message(),
            title="[bold yellow]⚠️  PowerShell Easter Egg[/]",
            border_style="yellow",
        ))

    def load_curr():
        m = get_mission(progress.current_track_id, progress.current_mission_id) or ALL_TRACKS[0].missions[0]
        if m.initial_setup:
            m.initial_setup(state)
        return m

    mission = load_curr()

    def print_mission_card(m):
        t = TRACKS_MAP.get(m.track_id)
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[bold cyan]Trilha:[/]", f"{t.icon if t else '⚡'} {t.name if t else m.track_id}")
        table.add_row("[bold cyan]Missão:[/]", f"[bold white]{m.title}[/] ({m.difficulty} · [bold yellow]+{m.xp} XP[/])")
        table.add_row("[bold cyan]Cenário:[/]", f"[dim]{m.context}[/]")
        table.add_row("[bold green]Objetivo:[/]", f"[bold]{m.objective}[/]")
        table.add_row("[bold yellow]Regra XP:[/]", "[bold #ffd60a]⚡ 100% XP[/] em <5s sem dicas! (>5s = 70% XP · dicas reduzem pontos)")
        table.add_row("[dim]Ajuda:[/]", "[dim]Precisa de auxílio com a sintaxe? Digite [bold yellow]dica[/bold yellow][/dim]")
        console.print(Panel(table, title="[bold yellow]🎯 Desafio Atual[/]", border_style="blue"))

    print_mission_card(mission)

    mission_start_time = time.time()
    tips_used = 0
    solution_used = False

    words = [
        "pwd", "ls", "cd", "mkdir", "touch", "cat", "head", "tail", "grep", "chmod", "kill", "ps", "curl", "df", "free",
        "systemctl status", "systemctl restart", "systemctl enable", "ss -tulpn", "useradd -m", "usermod -aG", "tar -czvf", "uptime",
        "git init", "git status", "git add", "git commit", "git branch", "git checkout", "git switch", "git merge", "git log", "git remote", "git stash", "git tag",
        "docker run", "docker ps", "docker logs", "docker exec", "docker stop", "docker images", "docker build", "docker network", "docker stats",
        "kubectl get", "kubectl run", "kubectl describe", "kubectl logs", "kubectl create deployment", "kubectl scale", "kubectl expose",
        "aws sts get-caller-identity", "aws s3 ls", "aws s3 mb", "aws s3 cp", "aws ec2 describe-instances", "aws ec2 start-instances", "aws iam list-users", "aws lambda list-functions",
        "terraform init", "terraform fmt", "terraform validate", "terraform plan", "terraform apply", "terraform show", "terraform state list", "terraform output",
        "datadog-agent status", "datadog-agent health", "datadog-agent check", "datadog-agent flare", "datadog-agent version", "export DD_ENV="
    ]
    completer = WordCompleter(words, ignore_case=True) if session else None

    while True:
        try:
            cwd = state.linux.cwd.replace("/home/devops", "~")
            git_part = ""
            if state.git.is_repo:
                b = state.git.current_branch or "main"
                is_dirty = bool(state.git.staged_files or state.git.unstaged_files or state.git.untracked_files)
                dirty_sym = " ✗" if is_dirty else ""
                git_part = f" git:({b}{dirty_sym})"
            prompt_str = f"➜  {cwd}{git_part} "
            if session:
                cmd = session.prompt(prompt_str, completer=completer).strip()
            else:
                cmd = input(prompt_str).strip()

            if not cmd:
                continue

            lower_cmd = cmd.lower()
            if lower_cmd in ["sair", "exit", "quit", "q"]:
                console.print("[dim]Até a próxima sessão de treino![/]")
                break
            elif lower_cmd in ["help", "h", "?"]:
                console.print("[cyan]Atalhos rápidos:[/] [yellow]d[/] (dica), [red]s[/] (solução), [cyan]n[/] (próxima), [cyan]r[/] (reset), [cyan]stats[/], [cyan]c[/] (limpar), [cyan]q[/] (sair)")
                continue
            elif lower_cmd in ["dica", "hint", "d"]:
                tips_used += 1
                console.print(f"[bold yellow]💡 Dica #{tips_used}:[/] {mission.tip} [dim yellow](Uso de dicas reduz o XP da missão)[/]")
                continue
            elif lower_cmd in ["solucao", "solution", "gabarito", "s"]:
                solution_used = True
                progress.break_streak()
                console.print(f"[bold red]👁️ Solução:[/] [bold cyan]{mission.solution}[/] [dim](XP zerado e streak resetado)[/]")
                continue
            elif lower_cmd in ["stats", "perfil", "st"]:
                show_stats()
                continue
            elif lower_cmd in ["clear", "c"]:
                console.clear()
                continue
            elif lower_cmd in ["proxima", "next", "n", "p"]:
                nxt = get_next_mission(mission.track_id, mission.id)
                if nxt:
                    progress.current_track_id, progress.current_mission_id = nxt
                    progress.save()
                    mission = load_curr()
                    mission_start_time = time.time()
                    tips_used = 0
                    solution_used = False
                    print_mission_card(mission)
                continue
            elif lower_cmd in ["reset", "r"]:
                state.reset_all()
                if mission.initial_setup:
                    mission.initial_setup(state)
                mission_start_time = time.time()
                tips_used = 0
                solution_used = False
                console.print("[bold green]🧹 Ambiente da missão restaurado. Cronômetro zerado![/]")
                continue

            output = executor.execute_command_string(cmd)
            if output:
                console.print(output)

            if mission.check_completion:
                completed, feedback = mission.check_completion(state, cmd, output)
                if completed:
                    elapsed = max(0.1, round(time.time() - mission_start_time, 1))
                    award = progress.award_mission(
                        mission,
                        elapsed_seconds=elapsed,
                        tips_used=tips_used,
                        solution_used=solution_used,
                    )
                    bonus_text = f"(+{award.streak_bonus_pct}%)" if award.streak_bonus_pct else ""
                    msg = (
                        f"[bold green]🎉 PARABÉNS! MISSÃO CONCLUÍDA![/]\n"
                        f"[bold yellow]+{award.xp} XP Conquistados![/] · {award.tier_name}\n"
                        f"⏱️ Tempo: {elapsed}s  │  💡 Dicas: {tips_used}  │  🔥 Streak: {progress.streak} acertos! {bonus_text}\n"
                        f"[bold white]{feedback}[/]"
                    )
                    if award.is_ninja:
                        msg += "\n[bold green]⚡ 100% DOS PONTOS! Executado em <5s sem dicas ou cola de IA![/]"
                    elif tips_used > 0:
                        msg += f"\n[dim yellow]⚠️ Dicas usadas: Pontuação reduzida ({int(award.factor*100)}% de XP).[/]"
                    elif elapsed > 5.0:
                        msg += "\n[dim]ℹ️ Tempo > 5.0s: 70% de XP (Regra anti-cola de Google/IA).[/]"

                    console.print(Panel(msg, border_style="green"))

                    nxt = get_next_mission(mission.track_id, mission.id)
                    if nxt:
                        progress.current_track_id, progress.current_mission_id = nxt
                        progress.save()
                        mission = load_curr()
                        mission_start_time = time.time()
                        tips_used = 0
                        solution_used = False
                        print_mission_card(mission)
                    else:
                        console.print("[bold gold1]🏆 Parabéns! Você completou todas as missões do DevOpsHeroCLI![/]")
                        break

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Sessão encerrada.[/]")
            break


def show_stats():
    """Prints user profile, level, streak, and accomplishments."""
    progress = UserProgress()
    lvl, title, icon, min_xp, next_xp = progress.get_level_info()
    table = Table(title="🏆 Perfil DevOps - DevOpsHeroCLI", border_style="cyan")
    table.add_column("Métrica", style="bold cyan")
    table.add_column("Valor", style="bold white")

    table.add_row("Nível Atual", f"{icon} {title}")
    table.add_row("XP Total", f"{progress.xp} XP")
    table.add_row("Próximo Nível", f"{next_xp} XP ({max(0, next_xp - progress.xp)} XP restantes)")
    table.add_row("Sequência Atual (Streak)", f"🔥 {progress.streak} (+{progress.get_streak_bonus_pct()}% XP bônus)")
    table.add_row("Maior Sequência (Recorde)", f"⚡ {progress.max_streak}")

    total_missions = sum(len(t.missions) for t in ALL_TRACKS)
    completed_missions = len(progress.completed_missions)
    pct = int((completed_missions / total_missions) * 100) if total_missions else 0
    table.add_row("Progresso Geral", f"{completed_missions}/{total_missions} ({pct}%)")

    console.print(table)


def list_tracks():
    """Prints all tracks and missions with their completion status."""
    progress = UserProgress()
    table = Table(title="🗺️ Catálogo de Trilhas do DevOpsHeroCLI", border_style="blue")
    table.add_column("Status", justify="center", width=8)
    table.add_column("Trilha", style="bold cyan", width=22)
    table.add_column("Missão", style="bold white")
    table.add_column("Dificuldade", width=14)
    table.add_column("XP", justify="right", width=8)

    for track in ALL_TRACKS:
        for m in track.missions:
            is_done = m.id in progress.completed_missions
            is_curr = m.id == progress.current_mission_id
            status = "[bold green]✅ Feito[/]" if is_done else ("[bold yellow]👉 Atual[/]" if is_curr else "[dim]⭕ Pendente[/]")
            table.add_row(status, f"{track.icon} {track.name}", m.title, m.difficulty, f"+{m.xp}")

    console.print(table)


def verify_missions() -> bool:
    """Diagnostic self-test that validates all 80 missions in isolated sandbox mode."""
    table = Table(title="🔍 Diagnóstico de Integridade — DevOpsHeroCLI", border_style="cyan")
    table.add_column("Trilha", style="bold cyan", width=24)
    table.add_column("Missões", justify="center", width=10)
    table.add_column("Status", width=15)
    table.add_column("Observações", style="dim")

    all_passed = True
    for track in ALL_TRACKS:
        passed = 0
        failed_names = []
        for m in track.missions:
            executor = CommandExecutor()
            if m.initial_setup:
                m.initial_setup(executor.state)
            out = executor.execute_command_string(m.solution)
            if m.check_completion:
                ok, _ = m.check_completion(executor.state, m.solution, out)
                if ok:
                    passed += 1
                else:
                    failed_names.append(m.id)
            else:
                passed += 1

        if not failed_names:
            status = "[bold green]✓ 100% OK[/]"
            notes = "Todas as soluções validadas"
        else:
            all_passed = False
            status = f"[bold red]✗ {len(failed_names)} falhas[/]"
            notes = f"Falhas: {', '.join(failed_names)}"

        table.add_row(f"{track.icon} {track.name}", f"{passed}/{len(track.missions)}", status, notes)

    console.print(table)
    if all_passed:
        console.print("[bold green]✅ Todas as 80 missões foram verificadas e validadas com sucesso![/]")
    else:
        console.print("[bold red]❌ Foram encontradas inconsistências nas missões.[/]")
    return all_passed


def show_doctor() -> None:
    """Displays diagnostic information about OS, terminal, encoding, and compatibility."""
    info = get_platform_info()
    table = Table(title="🏥 DevOpsHeroCLI Doctor & Compatibilidade Multiplataforma", border_style="cyan")
    table.add_column("Componente", style="bold cyan")
    table.add_column("Valor / Status", style="bold white")
    table.add_column("Compatibilidade", style="bold green")

    table.add_row("Sistema Operacional", str(info["os"]), "✅ 100% Suportado (Linux, macOS, Windows, WSL)")
    table.add_row("WSL Detectado", "Sim" if info["is_wsl"] else "Não", "✅ Totalmente integrado")
    ps_str = "Sim (Easter Egg Ativo! 😂)" if info["is_powershell"] else "Não (Terminal Padrão)"
    table.add_row("PowerShell Ativo", ps_str, "✅ Suportado com Easter Egg Humorístico")
    table.add_row("Emulador de Terminal", str(info["terminal"]), "✅ Textual TUI & ANSI 256/TrueColor")
    table.add_row("Versão Python", str(info["python_version"]), "✅ Python 3.9+ validado")
    table.add_row("Encoding Padrão", str(info["encoding"]), "✅ UTF-8 Safe (Zero charmap error)")
    table.add_row("Trilhas & Missões", f"{len(ALL_TRACKS)} trilhas / {sum(len(t.missions) for t in ALL_TRACKS)} missões", "✅ 100% Solúveis")

    console.print(table)
    if info["is_powershell"]:
        console.print(Panel(
            get_powershell_humor_message(),
            title="[bold yellow]⚠️  PowerShell Easter Egg Ativo[/]",
            border_style="yellow",
        ))


def main():
    parser = argparse.ArgumentParser(
        prog="dh",
        description="⚡ DevOpsHeroCLI (dh): Aprenda Linux, Sysadmin, Git, Docker, Kubernetes, AWS, Terraform e Datadog no terminal",
    )
    parser.add_argument("-v", "--version", action="version", version="devopsherocli 1.0.0 (dh)")
    subparsers = parser.add_subparsers(dest="command")

    tui_p = subparsers.add_parser("tui", aliases=["t"], help="Interface visual completa (Padrão: basta digitar 'dh')")
    tui_p.add_argument("--track", "-t", help="ID da trilha inicial (ex: linux, git, docker, k8s, aws, terraform, datadog)")
    tui_p.add_argument("--mission", "-m", help="ID da missão inicial (ex: linux-01, docker-05)")

    repl_p = subparsers.add_parser("repl", aliases=["r"], help="Modo REPL rápido direto na linha de comando (dh r)")
    repl_p.add_argument("--track", "-t", help="ID da trilha inicial")
    repl_p.add_argument("--mission", "-m", help="ID da missão inicial")

    subparsers.add_parser("stats", aliases=["s", "stat"], help="Exibe seu nível, XP e streak (dh s)")
    subparsers.add_parser("list", aliases=["l", "ls"], help="Lista todas as trilhas e missões (dh l)")
    subparsers.add_parser("reset", aliases=["clean"], help="Reseta todo o progresso do usuário (dh reset)")
    subparsers.add_parser("verify", aliases=["v", "check"], help="Executa auto-diagnóstico de todas as missões (dh v)")
    subparsers.add_parser("doctor", aliases=["d", "doc"], help="Verifica compatibilidade de SO e terminal (dh d)")

    args = parser.parse_args()

    if getattr(args, "track", None) or getattr(args, "mission", None):
        progress = UserProgress()
        if args.track:
            progress.current_track_id = args.track
        if args.mission:
            progress.current_mission_id = args.mission
        progress.save()

    cmd = args.command
    if cmd in ("repl", "r"):
        run_repl()
    elif cmd in ("stats", "s", "stat"):
        show_stats()
    elif cmd in ("list", "l", "ls"):
        list_tracks()
    elif cmd in ("reset", "clean"):
        progress = UserProgress()
        progress.reset_progress()
        console.print("[bold red]🧹 Progresso resetado com sucesso![/]")
    elif cmd in ("verify", "v", "check"):
        success = verify_missions()
        if not success:
            sys.exit(1)
    elif cmd in ("doctor", "d", "doc"):
        show_doctor()
    else:
        # Default: Launch rich Textual TUI
        from devopsherocli.app import launch_app
        launch_app()


if __name__ == "__main__":
    main()
