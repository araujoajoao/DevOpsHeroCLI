"""Main Textual TUI Application for DevOpsHeroCLI."""
from __future__ import annotations

import os
import time
from typing import Optional

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    RichLog,
    Static,
)

from devopsherocli.engine.executor import CommandExecutor, EnvironmentState
from devopsherocli.models import Mission, Track, UserProgress
from devopsherocli.tracks import ALL_TRACKS, TRACKS_MAP, get_mission, get_next_mission


class TracksModal(ModalScreen):
    """Modal dialog displaying all tracks and mission selector."""

    def __init__(self, progress: UserProgress):
        super().__init__()
        self.progress = progress

    def compose(self) -> ComposeResult:
        with Vertical(id="tracks-dialog"):
            yield Label("🗺️ Trilhas de Aprendizado — Escolha uma Missão", classes="track-modal-header")
            with VerticalScroll(id="tracks-list"):
                for track in ALL_TRACKS:
                    completed_count = sum(1 for m in track.missions if m.id in self.progress.completed_missions)
                    total_count = len(track.missions)
                    yield Label(f"\n{track.icon} {track.name} ({completed_count}/{total_count} Concluídas) — {track.description}", classes="track-group-title")
                    for m in track.missions:
                        is_done = m.id in self.progress.completed_missions
                        is_curr = m.id == self.progress.current_mission_id
                        status_ico = "✅" if is_done else ("👉" if is_curr else "⭕")
                        btn_label = f"{status_ico} [{m.id}] {m.title} ({m.difficulty} · {m.xp} XP)"
                        btn_classes = "mission-item-btn " + ("mission-item-done" if is_done else ("mission-item-curr" if is_curr else ""))
                        btn = Button(btn_label, id=f"sel_m_{m.track_id}_{m.id}", classes=btn_classes)
                        yield btn
            yield Button("Fechar (Esc)", id="btn-close-modal")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "btn-close-modal":
            self.dismiss(None)
        elif btn_id.startswith("sel_m_"):
            parts = btn_id.replace("sel_m_", "").split("_")
            track_id = parts[0]
            mission_id = "_".join(parts[1:])
            self.dismiss((track_id, mission_id))


class DevOpsHeroApp(App):
    """Full-featured Terminal User Interface for DevOpsHeroCLI."""

    CSS_PATH = "styles/devopshero.tcss"

    BINDINGS = [
        Binding("f1", "help", "Ajuda", show=True),
        Binding("f2", "tracks", "Trilhas (F2)", show=True),
        Binding("f3", "toggle_tip", "Dica (F3)", show=True),
        Binding("f4", "solution", "Gabarito (F4)", show=True),
        Binding("f5", "reset_lab", "Reset Lab (F5)", show=True),
        Binding("ctrl+l", "clear_screen", "Limpar", show=False),
        Binding("ctrl+q", "quit", "Sair", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.progress = UserProgress()
        self.state = EnvironmentState()
        self.executor = CommandExecutor(self.state)
        self.current_mission: Optional[Mission] = None
        self.show_tip: bool = False
        self.show_solution: bool = False
        self.mission_start_time: float = time.time()
        self.tips_used: int = 0
        self.solution_used: bool = False

    def compose(self) -> ComposeResult:
        # Top Header Bar
        with Horizontal(id="header-bar"):
            yield Label("⚡ DevOpsHero", classes="brand")
            with Vertical(classes="level-box"):
                yield Label("🌱 Nível 1 · Recruta DevOps", id="lbl-level", classes="level-title")
                yield ProgressBar(total=100, show_eta=False, id="xp-bar", classes="xp-bar-container")
            yield Label("🔥 Streak: 0 (+0%)", id="lbl-streak", classes="streak-box")
            with Horizontal(classes="nav-actions"):
                yield Button("🗺️ Trilhas", id="btn-tracks", classes="action-btn")
                yield Button("💡 Dica", id="btn-tip", classes="action-btn")
                yield Button("👁️ Solução", id="btn-solution", classes="action-btn")
                yield Button("🧹 Reset", id="btn-reset", classes="action-btn")

        # Main Body (Split into Mission Card & Terminal Screen)
        with Horizontal(id="main-container"):
            with VerticalScroll(id="mission-panel"):
                yield Label("🐧 Trilha: Linux Essencial", id="lbl-mission-track", classes="mission-track-badge")
                yield Label("Missão 1: Navegação Básica", id="lbl-mission-title", classes="mission-title")
                with Horizontal(classes="meta-row"):
                    yield Label("Iniciante", id="lbl-diff-badge", classes="badge-diff")
                    yield Label("+100 XP", id="lbl-xp-badge", classes="badge-xp")
                    yield Label("⚡ 100% até 5s", id="lbl-speed-badge", classes="badge-speed")
                
                yield Label("📖 CENÁRIO DO MUNDO REAL:", classes="section-label")
                yield Static("", id="box-context", classes="context-box")

                yield Label("🎯 SEU OBJETIVO:", classes="section-label")
                yield Static("", id="box-objective", classes="objective-box")

                yield Label("⚡ REGRA ANTI-COLA (GOOGLE / IA):", classes="section-label")
                yield Static(
                    "⚡ [bold #ffd60a]100% XP[/]: Envie sem dicas nos primeiros [bold #30d158]5 segundos[/]!\n"
                    "⏱️ [dim]> 5 segundos sem dicas: 70% XP (tempo para busca externa)[/]\n"
                    "💡 [dim yellow]A cada dica usada: pontuação reduzida (-60%, -80%...)[/]",
                    id="box-rules",
                    classes="rules-box",
                )

                yield Static("", id="box-tip", classes="tip-box")
                yield Static("", id="box-solution", classes="solution-box")

            with Vertical(id="terminal-panel"):
                with Horizontal(id="term-title-bar"):
                    yield Label("🔴 🟡 🟢", classes="term-dots")
                    yield Label("devopshero-terminal · ops-lab:~ (bash/git/docker/k8s/aws/tf/dd)", classes="term-title-text")
                    yield Label("● Online", classes="term-status-badge")
                yield RichLog(id="term-output-log", highlight=True, markup=True, wrap=True)
                with Horizontal(id="term-input-container"):
                    yield Label("devops@ops-lab:~$", id="term-prompt")
                    yield Input(placeholder="Digite o comando aqui (ex: pwd, ls, docker ps, kubectl get nodes...)", id="term-input")

        with Horizontal(id="footer-bar"):
            yield Label("[bold #5ac8fa]F2[/] Trilhas  │  [bold #ffd60a]F3[/] Dica  │  [bold #ff6961]F4[/] Solução  │  [bold #8e8e93]F5[/] Reset  │  [bold #5ac8fa]Ctrl+L[/] Limpar  │  [bold #8e8e93]Ctrl+Q[/] Sair")

    def on_mount(self) -> None:
        self.load_active_mission()
        self.update_header_stats()
        self.print_welcome_message()
        self.query_one("#term-input", Input).focus()

    def load_active_mission(self) -> None:
        track_id = self.progress.current_track_id
        mission_id = self.progress.current_mission_id
        self.current_mission = get_mission(track_id, mission_id) or ALL_TRACKS[0].missions[0]
        
        # Execute setup if any
        if self.current_mission.initial_setup:
            self.current_mission.initial_setup(self.state)

        self.show_tip = False
        self.show_solution = False
        self.tips_used = 0
        self.solution_used = False
        self.mission_start_time = time.time()
        self.render_mission_panel()

    def render_mission_panel(self) -> None:
        if not self.current_mission:
            return
        m = self.current_mission
        track = TRACKS_MAP.get(m.track_id)
        track_name = track.name if track else m.track_id

        self.query_one("#lbl-mission-track", Label).update(f"{track.icon if track else '⚡'} Trilha: {track_name}")
        self.query_one("#lbl-mission-title", Label).update(f"Missão: {m.title}")
        self.query_one("#lbl-diff-badge", Label).update(m.difficulty)
        self.query_one("#lbl-xp-badge", Label).update(f"+{m.xp} XP")

        self.query_one("#box-context", Static).update(m.context)
        self.query_one("#box-objective", Static).update(f"🎯 {m.objective}")

        # Tip box
        tip_box = self.query_one("#box-tip", Static)
        if self.show_tip:
            tip_box.display = True
            tip_box.update(f"💡 [bold]Dica:[/bold] {m.tip}")
        else:
            tip_box.display = False

        # Solution box
        sol_box = self.query_one("#box-solution", Static)
        if self.show_solution:
            sol_box.display = True
            sol_box.update(f"👁️ [bold red]Gabarito:[/bold red] [bold cyan]{m.solution}[/]")
        else:
            sol_box.display = False

    def update_header_stats(self) -> None:
        lvl, title, icon, min_xp, next_xp = self.progress.get_level_info()
        xp_span = max(1, next_xp - min_xp)
        xp_curr = max(0, self.progress.xp - min_xp)
        pct = min(100, int((xp_curr / xp_span) * 100))

        self.query_one("#lbl-level", Label).update(f"{icon} {title} · {self.progress.xp} XP")
        self.query_one("#xp-bar", ProgressBar).update(progress=pct)

        bonus = self.progress.get_streak_bonus_pct()
        self.query_one("#lbl-streak", Label).update(f"🔥 Streak: {self.progress.streak} (+{bonus}%)")

    def update_prompt(self) -> None:
        cwd = self.state.linux.cwd.replace("/home/devops", "~")
        self.query_one("#term-prompt", Label).update(f"devops@ops-lab:{cwd}$")

    def print_welcome_message(self) -> None:
        log = self.query_one("#term-output-log", RichLog)
        log.write("[bold #007aff]╭──────────────────────────────────────────────────╮[/]")
        log.write("[bold #007aff]│[/] [bold #5ac8fa]⚡ DevOpsHeroCLI[/] [dim]· Treinador Interativo de DevOps[/]  [bold #007aff]│[/]")
        log.write("[bold #007aff]│[/] [dim]Linux · Sysadmin · Git · Docker · K8s · AWS · TF[/]   [bold #007aff]│[/]")
        log.write("[bold #007aff]│[/] [bold #30d158]Comandos:[/] [cyan]'help'[/], [cyan]'dica'[/], [cyan]'trilhas'[/], [cyan]'reset'[/]    [bold #007aff]│[/]")
        log.write("[bold #007aff]╰──────────────────────────────────────────────────╯[/]\n")

    @on(Input.Submitted, "#term-input")
    def handle_terminal_input(self, event: Input.Submitted) -> None:
        cmd_text = event.value.strip()
        inp = self.query_one("#term-input", Input)
        inp.value = ""

        if not cmd_text:
            return

        self.progress.command_history.append(cmd_text)
        log = self.query_one("#term-output-log", RichLog)

        # Print prompt line
        cwd = self.state.linux.cwd.replace("/home/devops", "~")
        log.write(f"[bold cyan]devops@ops-lab[/]:[bold blue]{cwd}[/]$ [bold white]{cmd_text}[/]")

        # Handle built-in meta commands
        lower_cmd = cmd_text.lower()
        if lower_cmd == "help":
            log.write(
                "[bold yellow]Comandos de apoio do DevOpsHeroCLI:[/]\n"
                "  [bold cyan]dica[/]       - Revela a dica da missão atual (F3)\n"
                "  [bold cyan]solucao[/]    - Revela o comando gabarito da missão (F4 - zera streak)\n"
                "  [bold cyan]trilhas[/]    - Abre a seleção de trilhas e missões (F2)\n"
                "  [bold cyan]reset[/]      - Restaura o ambiente da missão atual para o estado inicial\n"
                "  [bold cyan]clear[/]      - Limpa a tela do terminal (Ctrl+L)\n"
                "  [bold cyan]stats[/]      - Mostra seu perfil, XP e conquistas\n"
                "  [bold cyan]proxima[/]    - Pula para a próxima missão\n"
            )
            return
        elif lower_cmd in ["dica", "hint"]:
            self.action_toggle_tip()
            return
        elif lower_cmd in ["solucao", "solution", "gabarito"]:
            self.action_solution()
            return
        elif lower_cmd in ["trilhas", "tracks"]:
            self.action_tracks()
            return
        elif lower_cmd == "reset":
            self.action_reset_lab()
            return
        elif lower_cmd == "clear":
            self.action_clear_screen()
            return
        elif lower_cmd in ["stats", "perfil"]:
            self.show_user_stats(log)
            return
        elif lower_cmd in ["proxima", "next"]:
            self.advance_to_next_mission()
            return

        # Execute in simulated engine
        output = self.executor.execute_command_string(cmd_text)
        self.update_prompt()
        if output:
            log.write(output)

        # Check mission completion
        if self.current_mission and self.current_mission.check_completion:
            completed, feedback = self.current_mission.check_completion(self.state, cmd_text, output)
            if completed:
                elapsed = max(0.1, round(time.time() - self.mission_start_time, 1))
                award = self.progress.award_mission(
                    self.current_mission,
                    elapsed_seconds=elapsed,
                    tips_used=self.tips_used,
                    solution_used=self.solution_used,
                )
                self.update_header_stats()
                
                # Bell ring & celebratory banner
                self.bell()
                log.write("")
                log.write("[bold #30d158]╭─────────────────────────────────────────────────────────────────╮[/]")
                log.write(f"[bold #30d158]│[/] [bold #ffffff]🎉 PARABÉNS! MISSÃO CONCLUÍDA COM SUCESSO![/]")
                log.write(f"[bold #30d158]│[/] [bold #ffd60a]+{award.xp} XP Conquistados![/] · {award.tier_name}")
                log.write(f"[bold #30d158]│[/] ⏱️ [bold cyan]Tempo:[/] {elapsed}s  │  💡 [bold yellow]Dicas:[/] {self.tips_used}  │  🔥 [bold #ff453a]Streak:[/] {self.progress.streak} (+{award.streak_bonus_pct}%)")
                if award.is_ninja:
                    log.write(f"[bold #30d158]│[/] [bold #30d158]⚡ 100% DOS PONTOS! Executado em <5s sem dicas ou cola de IA![/]")
                elif self.tips_used > 0:
                    log.write(f"[bold #30d158]│[/] [dim yellow]⚠️ Dicas utilizadas: Pontuação reduzida ({int(award.factor*100)}% de XP).[/]")
                elif elapsed > 5.0:
                    log.write(f"[bold #30d158]│[/] [dim]ℹ️ Tempo > 5s: 70% de XP (Regra anti-cola de Google/IA).[/]")
                log.write("[bold #30d158]╰─────────────────────────────────────────────────────────────────╯[/]")
                log.write("[dim]Avançando para a próxima missão...[/]\n")

                # Auto advance
                self.set_timer(2.2, self.advance_to_next_mission)

    def advance_to_next_mission(self) -> None:
        if not self.current_mission:
            return
        next_step = get_next_mission(self.current_mission.track_id, self.current_mission.id)
        if next_step:
            t_id, m_id = next_step
            self.progress.current_track_id = t_id
            self.progress.current_mission_id = m_id
            self.progress.save()
            self.load_active_mission()

            log = self.query_one("#term-output-log", RichLog)
            log.write(f"[bold #ffd60a]👉 Nova Missão:[/] [bold #5ac8fa]{self.current_mission.title}[/]")
            log.write("[dim]Confira os objetivos e detalhes no painel à esquerda.[/dim]\n")
        else:
            log = self.query_one("#term-output-log", RichLog)
            log.write("[bold gold1]🏆 PARABÉNS! VOCÊ COMPLETOU TODAS AS MISSÕES DO DEVOPSHEROCLI![/]")

    def show_user_stats(self, log: RichLog) -> None:
        lvl, title, icon, min_xp, next_xp = self.progress.get_level_info()
        completed = len(self.progress.completed_missions)
        total = sum(len(t.missions) for t in ALL_TRACKS)
        log.write(
            f"[bold cyan]Perfil DevOps do Usuário:[/]\n"
            f"  {icon} [bold]{title}[/]\n"
            f"  ⭐ XP Total: {self.progress.xp} XP\n"
            f"  🔥 Streak Atual: {self.progress.streak} (Recorde: {self.progress.max_streak})\n"
            f"  ✅ Missões Concluídas: {completed} / {total}\n"
        )

    # Actions & Buttons
    def action_tracks(self) -> None:
        def on_selection(result):
            if result:
                track_id, mission_id = result
                self.progress.current_track_id = track_id
                self.progress.current_mission_id = mission_id
                self.progress.save()
                self.load_active_mission()

        self.push_screen(TracksModal(self.progress), on_selection)

    def action_toggle_tip(self) -> None:
        self.show_tip = not self.show_tip
        if self.show_tip:
            self.tips_used += 1
            log = self.query_one("#term-output-log", RichLog)
            log.write(f"[dim yellow]💡 Dica revelada (Uso #{self.tips_used})! Atenção: o uso de dicas reduz o XP da missão.[/]")
        self.render_mission_panel()

    def action_solution(self) -> None:
        self.show_solution = True
        self.solution_used = True
        self.progress.break_streak()
        self.update_header_stats()
        self.render_mission_panel()
        log = self.query_one("#term-output-log", RichLog)
        log.write("[bold #ff3b30]👁️ Gabarito revelado![/] [dim yellow]O XP desta missão foi zerado e o streak resetado.[/]")

    def action_reset_lab(self) -> None:
        self.state.reset_all()
        if self.current_mission and self.current_mission.initial_setup:
            self.current_mission.initial_setup(self.state)
        self.mission_start_time = time.time()
        self.tips_used = 0
        self.solution_used = False
        log = self.query_one("#term-output-log", RichLog)
        log.write("[bold green]🧹 Ambiente simulado restaurado para o estado inicial. Cronômetro zerado![/]")

    def action_clear_screen(self) -> None:
        log = self.query_one("#term-output-log", RichLog)
        log.clear()

    @on(Button.Pressed, "#btn-tracks")
    def on_btn_tracks(self) -> None:
        self.action_tracks()

    @on(Button.Pressed, "#btn-tip")
    def on_btn_tip(self) -> None:
        self.action_toggle_tip()

    @on(Button.Pressed, "#btn-solution")
    def on_btn_solution(self) -> None:
        self.action_solution()

    @on(Button.Pressed, "#btn-reset")
    def on_btn_reset(self) -> None:
        self.action_reset_lab()


def launch_app():
    app = DevOpsHeroApp()
    app.run()


if __name__ == "__main__":
    launch_app()
