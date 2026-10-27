"""CLI entrypoint for DevOpsHeroCLI: TUI, REPL mode, Stats, and Tracks listing."""
from __future__ import annotations

import argparse
import sys
import time
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
        "[dim]Linux · Sysadmin · Git · Docker · K8s · AWS · Terraform · Datadog[/dim]\n"
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
                tips_used += 1
                console.print(f"[bold yellow]💡 Dica #{tips_used}:[/] {mission.tip} [dim yellow](Uso de dicas reduz o XP da missão)[/]")
                continue
            elif lower_cmd in ["solucao", "solution", "gabarito"]:
                solution_used = True
                progress.break_streak()
                console.print(f"[bold red]👁️ Solução:[/] [bold cyan]{mission.solution}[/] [dim](XP zerado e streak resetado)[/]")
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
                    mission_start_time = time.time()
                    tips_used = 0
                    solution_used = False
                    print_mission_card(mission)
                continue
            elif lower_cmd == "reset":
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


def main():
    parser = argparse.ArgumentParser(description="⚡ DevOpsHeroCLI: Aprenda Linux, Sysadmin, Git, Docker, Kubernetes, AWS, Terraform e Datadog no terminal")
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
