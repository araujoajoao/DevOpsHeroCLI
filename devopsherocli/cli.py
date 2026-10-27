"""CLI entrypoint for DevOpsHeroCLI: TUI, REPL mode, Stats, and Tracks listing."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from devopsherocli.engine.executor import CommandExecutor, EnvironmentState
from devopsherocli.models import UserProgress
from devopsherocli.tracks import ALL_TRACKS, TRACKS_MAP, get_mission, get_next_mission

console = Console()


def run_repl():
    """Runs DevOpsHeroCLI in lightweight inline REPL mode using prompt_toolkit and Rich."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        from prompt_toolkit.history import FileHistory
        from pathlib import Path

        hist_path = Path.home() / ".devopsherocli" / "history.txt"
        hist_path.parent.mkdir(parents=True, exist_ok=True)
        session = PromptSession(history=FileHistory(str(hist_path)))
    except ImportError:
        session = None

    progress = UserProgress()
    state = EnvironmentState()
    executor = CommandExecutor(state)

    console.print(Panel.fit(
        "[bold cyan]⚡ DevOpsHeroCLI REPL Mode[/bold cyan]\n"
        "[dim]Linux · Docker · Kubernetes · Datadog — Treine comandos reais no terminal.[/dim]\n"
        "Comandos especiais: [bold yellow]dica[/], [bold yellow]solucao[/], [bold yellow]proxima[/], [bold yellow]stats[/], [bold yellow]sair[/]",
        border_style="cyan"
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
        table.add_row("[dim]Ajuda:[/]", "[dim]Precisa de auxílio com a sintaxe? Digite [bold yellow]dica[/bold yellow][/dim]")
        console.print(Panel(table, title="[bold yellow]🎯 Desafio Atual[/]", border_style="blue"))

    print_mission_card(mission)

    words = [
        "pwd", "ls", "cd", "mkdir", "touch", "cat", "head", "tail", "grep", "chmod", "kill", "ps", "curl", "df", "free",
        "docker run", "docker ps", "docker logs", "docker exec", "docker stop", "docker images", "docker build", "docker network", "docker stats",
        "kubectl get", "kubectl run", "kubectl describe", "kubectl logs", "kubectl create deployment", "kubectl scale", "kubectl expose",
        "datadog-agent status", "datadog-agent health", "datadog-agent check", "datadog-agent flare", "datadog-agent version", "export DD_ENV="
    ]
    completer = WordCompleter(words, ignore_case=True) if session else None

    while True:
        try:
            cwd = state.linux.cwd.replace("/home/devops", "~")
            prompt_str = f"devopshero:{cwd}$ "
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
            elif lower_cmd == "help":
                console.print("[cyan]Comandos:[/] dica, solucao, proxima, reset, stats, clear, sair")
                continue
            elif lower_cmd in ["dica", "hint"]:
                console.print(f"[bold yellow]💡 Dica:[/] {mission.tip}")
                continue
            elif lower_cmd in ["solucao", "solution", "gabarito"]:
                progress.break_streak()
                console.print(f"[bold red]👁️ Solução:[/] [bold cyan]{mission.solution}[/] [dim](Streak zerado)[/]")
                continue
            elif lower_cmd in ["stats", "perfil"]:
                show_stats()
                continue
            elif lower_cmd == "clear":
                console.clear()
                continue
            elif lower_cmd in ["proxima", "next"]:
                nxt = get_next_mission(mission.track_id, mission.id)
                if nxt:
                    progress.current_track_id, progress.current_mission_id = nxt
                    progress.save()
                    mission = load_curr()
                    print_mission_card(mission)
                continue
            elif lower_cmd == "reset":
                state.reset_all()
                if mission.initial_setup:
                    mission.initial_setup(state)
                console.print("[bold green]🧹 Ambiente da missão restaurado.[/]")
                continue

            output = executor.execute_command_string(cmd)
            if output:
                console.print(output)

            if mission.check_completion:
                completed, feedback = mission.check_completion(state, cmd, output)
                if completed:
                    earned = progress.award_mission(mission)
                    console.print(Panel(
                        f"[bold green]🎉 PARABÉNS! MISSÃO CONCLUÍDA![/]\n"
                        f"+{earned} XP Conquistados!  🔥 Streak: {progress.streak} acertos seguidos!\n"
                        f"[bold white]{feedback}[/]",
                        border_style="green"
                    ))
                    nxt = get_next_mission(mission.track_id, mission.id)
                    if nxt:
                        progress.current_track_id, progress.current_mission_id = nxt
                        progress.save()
                        mission = load_curr()
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


def main():
    parser = argparse.ArgumentParser(description="⚡ DevOpsHeroCLI: Aprenda Linux, Docker, Kubernetes e Datadog no terminal")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("tui", help="Inicia a interface visual completa (Padrão)")
    subparsers.add_parser("repl", help="Inicia modo linha de comando interativo rápido")
    subparsers.add_parser("stats", help="Exibe seu nível, XP e streak")
    subparsers.add_parser("list", help="Lista todas as trilhas e missões")
    subparsers.add_parser("reset", help="Reseta todo o progresso do usuário")

    args = parser.parse_args()

    if args.command == "repl":
        run_repl()
    elif args.command == "stats":
        show_stats()
    elif args.command == "list":
        list_tracks()
    elif args.command == "reset":
        progress = UserProgress()
        progress.reset_progress()
        console.print("[bold red]🧹 Progresso resetado com sucesso![/]")
    else:
        # Default: Launch rich Textual TUI
        from devopsherocli.app import launch_app
        launch_app()


if __name__ == "__main__":
    main()
