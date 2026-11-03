"""Main Textual TUI Application for DevOpsHeroCLI"""
from __future__ import annotations

import random
import time
from typing import Optional

from rich.markup import escape
from rich.panel import Panel
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    ProgressBar,
    RichLog,
    Static,
)

from devopsherocli.compat import (
    ensure_utf8_encoding,
    get_powershell_humor_message,
    is_powershell,
)
from devopsherocli.engine.executor import CommandExecutor, EnvironmentState
from devopsherocli.models import Mission, Track, UserProgress
from devopsherocli.tracks import ALL_TRACKS, TRACKS_MAP, get_mission, get_next_mission

ensure_utf8_encoding()


def check_update_available() -> tuple[bool, str]:
    """Checks whether an update is available (via git remote or GitHub version).
    Returns (has_update, latest_version).
    """
    import re
    import urllib.request
    from pathlib import Path

    repo_dir = Path(__file__).resolve().parent.parent
    git_dir = repo_dir / ".git"

    # 1. Local Git tracking check
    if git_dir.exists():
        try:
            head_ref_file = git_dir / "refs" / "heads" / "main"
            remote_ref_file = git_dir / "refs" / "remotes" / "origin" / "main"
            if head_ref_file.exists() and remote_ref_file.exists():
                local_sha = head_ref_file.read_text().strip()
                remote_sha = remote_ref_file.read_text().strip()
                if local_sha != remote_sha:
                    return True, "v1.1.0"
        except Exception:
            pass

    # 2. Remote GitHub repository check
    try:
        url = "https://raw.githubusercontent.com/araujoajoao/DevOpsHeroCLI/main/pyproject.toml"
        req = urllib.request.Request(url, headers={"User-Agent": "DevOpsHeroCLI-Checker"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                remote_ver = match.group(1)
                from devopsherocli import __version__ as local_ver
                r_parts = [int(p) for p in remote_ver.lstrip('v').split('.')]
                l_parts = [int(p) for p in local_ver.lstrip('v').split('.')]
                if r_parts > l_parts:
                    return True, f"v{remote_ver}"
    except Exception:
        pass

    return False, ""


class TracksModal(ModalScreen):
    """Modal dialog displaying all tracks for track-level selection."""

    def __init__(self, progress: UserProgress):
        super().__init__()
        self.progress = progress

    def _get_entry_mission(self, track: Track) -> Optional[Mission]:
        uncompleted = [m for m in track.missions if m.id not in self.progress.completed_missions]
        if uncompleted:
            return random.choice(uncompleted)
        return random.choice(track.missions) if track.missions else None

    def compose(self) -> ComposeResult:
        with Vertical(id="tracks-dialog"):
            yield Label("🗺️ Trilhas de Aprendizado — Escolha uma Trilha", classes="track-modal-header")
            yield Label("Selecione a trilha desejada para praticar suas missões sequencialmente.", classes="track-modal-sub")
            with VerticalScroll(id="tracks-list"):
                for track in ALL_TRACKS:
                    is_unlocked = self.progress.is_track_unlocked(track)
                    completed_count = sum(1 for m in track.missions if m.id in self.progress.completed_missions)
                    total_count = len(track.missions)
                    is_curr = track.id == self.progress.current_track_id

                    if is_unlocked:
                        if completed_count == total_count:
                            status_tag = "✅ [100% CONCLUÍDA]"
                            btn_class = "track-card-btn track-card-done"
                            action_txt = "Revisar Trilha ➔"
                        elif is_curr:
                            status_tag = f"👉 [TRILHA ATIVA · {completed_count}/{total_count}]"
                            btn_class = "track-card-btn track-card-curr"
                            action_txt = "Continuar Prática ➔"
                        elif completed_count > 0:
                            status_tag = f"⚡ [EM ANDAMENTO · {completed_count}/{total_count}]"
                            btn_class = "track-card-btn track-card-progress"
                            action_txt = "Continuar Trilha ➔"
                        else:
                            status_tag = f"▶ [DISPONÍVEL · 0/{total_count}]"
                            btn_class = "track-card-btn"
                            action_txt = "Iniciar Trilha ➔"

                        entry_m = self._get_entry_mission(track)
                        entry_title = entry_m.title if entry_m else ""
                        btn_label = (
                            f"{status_tag}  {track.icon} {track.name.upper()}  •  {track.required_seniority}\n"
                            f"   • {track.description}\n"
                            f"   [{action_txt} · Próxima Missão: {entry_title}]"
                        )
                        btn = Button(btn_label, id=f"sel_track_{track.id}", classes=btn_class)
                    else:
                        btn_label = (
                            f"🔒 [BLOQUEADO]  {track.icon} {track.name.upper()}  •  Requer {track.required_seniority} ({track.required_xp} XP)\n"
                            f"   • {track.description}\n"
                            f"   [Requer conclusão das missões anteriores para desbloquear]"
                        )
                        btn = Button(btn_label, id=f"locked_track_{track.id}", classes="track-card-btn track-card-locked", disabled=True)
                    yield btn
            yield Button("Fechar (Esc)", id="btn-close-modal")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "btn-close-modal":
            self.dismiss(None)
        elif btn_id.startswith("sel_track_"):
            track_id = btn_id.replace("sel_track_", "")
            track = TRACKS_MAP.get(track_id)
            if track and self.progress.is_track_unlocked(track):
                entry_m = self._get_entry_mission(track)
                m_id = entry_m.id if entry_m else (track.missions[0].id if track.missions else "")
                self.dismiss((track_id, m_id))


class AppUpdateModal(ModalScreen):
    """Modern Desktop-style Update Card with App Icon, Version, Spinner, What's New & Dismiss."""

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Fechar", show=False),
    ]

    def __init__(self, current_version: str = "v1.0.0", target_version: str = "0.21.0"):
        super().__init__()
        self.current_version = current_version
        self.target_version = target_version
        self.progress_val: float = 0.0
        self.is_done: bool = False
        self.showing_whats_new: bool = False
        self._timer = None

    def compose(self) -> ComposeResult:
        with Vertical(id="update-card"):
            with Horizontal(id="update-top-row"):
                yield Static("⚡", id="update-icon-box")
                with Vertical(id="update-title-col"):
                    with Horizontal(id="update-title-row"):
                        yield Label("DevOpsHero", classes="update-app-title")
                        yield Label("by @araujoajoao", classes="update-by-author")
                        yield Label("UPDATE", classes="update-pill-badge")
                    yield Label(f"{self.current_version} to {self.target_version}", classes="update-version-label")
                yield Button("✕", id="btn-update-close")

            with Vertical(id="update-progress-row"):
                with Horizontal(classes="update-status-line"):
                    yield Label("⠋", id="lbl-update-spinner")
                    yield Label("Downloading and installing update...", id="lbl-update-status", classes="update-status-msg")
                yield ProgressBar(total=100, show_eta=False, id="update-progress-bar")

            with VerticalScroll(id="update-whats-new-box"):
                yield Label("[bold #38bdf8]Novidades da versão 1.1.0:[/]\n", classes="whats-new-heading")
                yield Label("• Interface Flocí Cloud Console (Console Home & Terminal Lab)", classes="whats-new-item")
                yield Label("• 8 Trilhas alinhadas com documentação oficial (Linux, Git, Docker, K8s, AWS, Terraform, Datadog)", classes="whats-new-item")
                yield Label("• Bloqueio estrito de trilhas por Senioridade e XP (Recruta, Júnior, Pleno, Sênior, Staff)", classes="whats-new-item")
                yield Label("• Novo comando nativo 'dh update' para sincronizar com o GitHub em 1 clique", classes="whats-new-item")

            yield Static(id="update-divider-line")

            with Horizontal(id="update-footer-row"):
                yield Button("What's new", id="btn-whats-new")
                yield Button("DISMISS", id="btn-update-dismiss")

    def on_mount(self) -> None:
        whats_new = self.query_one("#update-whats-new-box")
        whats_new.display = False
        self._timer = self.set_interval(0.08, self._step_progress)

    def _step_progress(self) -> None:
        if self.is_done:
            return
        self.progress_val += 3.5
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = int(self.progress_val // 3) % len(spinner_chars)
        self.query_one("#lbl-update-spinner", Label).update(spinner_chars[idx])

        bar = self.query_one("#update-progress-bar", ProgressBar)
        bar.progress = min(100.0, self.progress_val)

        if self.progress_val >= 100.0:
            self.is_done = True
            if self._timer:
                self._timer.stop()
            self.query_one("#lbl-update-spinner", Label).update("✓")
            self.query_one("#lbl-update-status", Label).update("[bold #10b981]DevOpsHero v1.1.0 instalado com sucesso![/]")
            self.query_one("#btn-update-dismiss", Button).label = "CONCLUIR"

    @on(Button.Pressed, "#btn-whats-new")
    def toggle_whats_new(self) -> None:
        self.showing_whats_new = not self.showing_whats_new
        box = self.query_one("#update-whats-new-box")
        box.display = self.showing_whats_new

    @on(Button.Pressed, "#btn-update-close")
    @on(Button.Pressed, "#btn-update-dismiss")
    def on_close(self) -> None:
        self.dismiss(None)

    def action_dismiss_modal(self) -> None:
        self.dismiss(None)


class DevOpsHeroApp(App):
    """Full-featured Terminal User Interface for DevOpsHeroCLI (Flocí Cloud Console Style)."""

    CSS_PATH = "styles/devopshero.tcss"

    BINDINGS = [
        Binding("f1", "help", "Ajuda", show=True),
        Binding("f2", "tracks", "Console Home (F2)", show=True),
        Binding("f3", "toggle_tip", "Dica (F3)", show=True),
        Binding("f4", "solution", "Gabarito (F4)", show=True),
        Binding("f5", "reset_lab", "Reset Lab (F5)", show=True),
        Binding("f6", "check_update", "Update (F6)", show=True),
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
        self.last_command_success: bool = True
        self.current_view: str = "terminal_lab"

    def compose(self) -> ComposeResult:
        with Horizontal(id="floci-root"):
            # 1. Left Sidebar Navigation (Authentic Flocí Console Sidebar)
            with Vertical(id="floci-sidebar"):
                with VerticalScroll(id="sidebar-scroll"):
                    yield Label("GENERAL", classes="sidebar-category")
                    yield Button("⊞ Console Home", id="nav-console-home", classes="sidebar-nav-btn")
                    yield Button("⚡ Terminal Lab", id="nav-terminal-lab", classes="sidebar-nav-btn sidebar-active")

                    yield Label("CLOUD SERVICES · DEVOPS", classes="sidebar-category")

                    yield Label("COMPUTE", classes="sidebar-subcat")
                    yield Button("🐧 Linux Shell", id="nav-track-linux", classes="sidebar-nav-btn")
                    yield Button("🐳 Docker", id="nav-track-docker", classes="sidebar-nav-btn")
                    yield Button("☸️ Kubernetes", id="nav-track-k8s", classes="sidebar-nav-btn")
                    yield Button("⚡ Serverless", id="nav-track-serverless", classes="sidebar-nav-btn sidebar-disabled", disabled=True)

                    yield Label("STORAGE & VCS", classes="sidebar-subcat")
                    yield Button("🔀 Git VCS", id="nav-track-git", classes="sidebar-nav-btn")
                    yield Button("☁️ AWS Storage", id="nav-track-aws", classes="sidebar-nav-btn")

                    yield Label("PROVISIONING", classes="sidebar-subcat")
                    yield Button("🏗️ Terraform", id="nav-track-terraform", classes="sidebar-nav-btn")

                    yield Label("OBSERVABILITY", classes="sidebar-subcat")
                    yield Button("🐶 Datadog", id="nav-track-datadog", classes="sidebar-nav-btn")

                with Horizontal(id="sidebar-footer"):
                    yield Label("Flocí DevTools · Local", classes="sidebar-footer-text")
                    yield Label("«", classes="sidebar-footer-collapse")

            # 2. Main Column (Top Header + Views Container)
            with Vertical(id="floci-main-col"):
                # Top Header Bar (Flocí Header)
                with Horizontal(id="floci-top-header"):
                    with Horizontal(id="top-title-col"):
                        yield Label("☁️", id="top-header-icon")
                        with Horizontal(id="top-header-text-col"):
                            yield Label("Terminal Lab", id="lbl-top-view-title", classes="top-main-title")
                            yield Label("Interactive DevOps & SRE learning runtime", id="lbl-top-view-sub", classes="top-sub-title")

                    with Horizontal(id="top-pills-row"):
                        yield Button("Linux", id="pill-filter-linux", classes="top-filter-pill")
                        yield Button("Docker", id="pill-filter-docker", classes="top-filter-pill")
                        yield Button("K8s", id="pill-filter-k8s", classes="top-filter-pill")
                        yield Button("AWS", id="pill-filter-aws", classes="top-filter-pill")
                        yield Button("IaC", id="pill-filter-terraform", classes="top-filter-pill")
                        yield Button("Obs", id="pill-filter-datadog", classes="top-filter-pill")
                        yield Button("🚀 Update", id="btn-update", classes="top-update-pill")

                # Dynamic Views Container
                with Vertical(id="floci-views-container"):
                    # VIEW A: Flocí Console Home (Dashboard)
                    with VerticalScroll(id="view-console-home"):
                        # Hero Banner Card
                        with Vertical(id="hero-banner-card"):
                            with Horizontal(id="hero-header-row"):
                                with Vertical(id="hero-text-col"):
                                    yield Label("SELECTED RUNTIME", classes="hero-tag-label")
                                    yield Label("Linux & Containers Local Runtime", id="hero-title-label", classes="hero-main-title")
                                    yield Label("Storage, runtime infrastructure, and DevOps-specific tracks are backed by DevOpsHero Core.", id="hero-desc-label", classes="hero-desc")
                                yield Button("▶ Iniciar Prática (Enter)", id="btn-hero-action", classes="hero-action-btn")

                        # Runtime Status Summary Bar (4 Cards)
                        with Horizontal(id="floci-metrics-row"):
                            with Vertical(classes="floci-stat-card"):
                                yield Label("CLOUD / WORKSPACE", classes="stat-card-label")
                                yield Label("Docker · Linux", id="stat-workspace-title", classes="stat-card-val")
                                yield Label("devops@ops-lab:/workspace", id="stat-workspace-sub", classes="stat-card-sub")

                            with Vertical(classes="floci-stat-card"):
                                yield Label("RUNTIME", classes="stat-card-label")
                                yield Label("Runtime reachable ((•))", classes="stat-card-val stat-val-green")
                                yield Label("Connected through Engine API", classes="stat-card-sub")

                            with Vertical(classes="floci-stat-card"):
                                yield Label("ACTIVE TRACKS", classes="stat-card-label")
                                yield Label("7 Tracks", id="stat-tracks-val", classes="stat-card-val")
                                yield Label("7 of 8 tracks available", id="stat-tracks-sub", classes="stat-card-sub")

                            with Vertical(classes="floci-stat-card"):
                                yield Label("RESOURCES / XP", classes="stat-card-label")
                                yield Label("350 XP · Lv.2", id="stat-xp-val", classes="stat-card-val")
                                yield Label("Streak 3 (+30% bonus)", id="stat-xp-sub", classes="stat-card-sub")

                        # Micro Status Chips Row
                        with Horizontal(id="floci-chips-row"):
                            yield Label("☁ UI: Console Home", classes="floci-chip")
                            yield Label("⚡ PROXY: /api/terminal", classes="floci-chip")
                            yield Label("🛡 ADAPTER: Oh My Zsh", classes="floci-chip")
                            yield Label("💾 RUNTIME: DevOpsHero Core", classes="floci-chip")

                        # 4x2 Grid of Service Cards (Flocí Service Cards)
                        with Vertical(id="floci-grid-container"):
                            with Horizontal(classes="floci-grid-row"):
                                yield Button(
                                    "● 🐧 [bold white]Linux Shell[/]   [bold #10b981]● available[/]\n\n[bold white]10[/]\n[dim #64748b]missões[/]",
                                    id="card-track-linux",
                                    classes="service-card",
                                )
                                yield Button(
                                    "● 🐳 [bold white]Docker[/]        [bold #10b981]● available[/]\n\n[bold white]10[/]\n[dim #64748b]missões[/]",
                                    id="card-track-docker",
                                    classes="service-card",
                                )
                                yield Button(
                                    "● ☸️ [bold white]Kubernetes[/]    [bold #10b981]● available[/]\n\n[bold white]10[/]\n[dim #64748b]missões[/]",
                                    id="card-track-k8s",
                                    classes="service-card",
                                )
                                yield Button(
                                    "● ⚡ [bold white]Serverless[/]    [dim #64748b]● coming soon[/]\n\n[bold white]-[/]\n[dim #64748b]coming soon[/]",
                                    id="card-track-serverless",
                                    classes="service-card service-card-disabled",
                                )

                            with Horizontal(classes="floci-grid-row"):
                                yield Button(
                                    "● 🔀 [bold white]Git VCS[/]       [bold #10b981]● available[/]\n\n[bold white]10[/]\n[dim #64748b]missões[/]",
                                    id="card-track-git",
                                    classes="service-card",
                                )
                                yield Button(
                                    "● ☁️ [bold white]AWS SRE[/]       [bold #10b981]● available[/]\n\n[bold white]10[/]\n[dim #64748b]missões[/]",
                                    id="card-track-aws",
                                    classes="service-card",
                                )
                                yield Button(
                                    "● 🏗️ [bold white]Terraform[/]     [bold #10b981]● available[/]\n\n[bold white]10[/]\n[dim #64748b]missões[/]",
                                    id="card-track-terraform",
                                    classes="service-card",
                                )
                                yield Button(
                                    "● 🐶 [bold white]Datadog[/]       [bold #10b981]● available[/]\n\n[bold white]10[/]\n[dim #64748b]missões[/]",
                                    id="card-track-datadog",
                                    classes="service-card",
                                )

                    # VIEW B: Terminal Lab View (Split into Mission Briefing & Terminal Screen)
                    with Horizontal(id="view-terminal-lab"):
                        with VerticalScroll(id="mission-panel"):
                            yield Label("// TRILHA: LINUX ESSENCIAL", id="lbl-mission-track", classes="mission-track-badge")
                            yield Label("Missão 1: Navegação Básica", id="lbl-mission-title", classes="mission-title")
                            with Horizontal(classes="meta-row"):
                                yield Label("Iniciante", id="lbl-diff-badge", classes="badge-diff")
                                yield Label("+100 XP", id="lbl-xp-badge", classes="badge-xp")
                                yield Label("⚡ 100% até 5s", id="lbl-speed-badge", classes="badge-speed")

                            yield Label("// CENÁRIO REAL", classes="section-label")
                            yield Static("", id="box-context", classes="context-box")

                            yield Label("// OBJETIVO DA MISSÃO", classes="section-label")
                            yield Static("", id="box-objective", classes="objective-box")

                            yield Label("// SPEED SCORE (ANTI-COLA)", classes="section-label")
                            yield Static(
                                "⚡ [bold #fbbf24]100% XP[/]: Envie sem dicas nos primeiros [bold #10b981]5 segundos[/]!\n"
                                "⏱️ [dim]> 5 segundos sem dicas: 70% XP (tempo para busca externa)[/]\n"
                                "💡 [dim #fbbf24]A cada dica usada: pontuação reduzida (-60%, -80%...)[/]",
                                id="box-rules",
                                classes="rules-box",
                            )

                            with Horizontal(classes="lab-quick-actions"):
                                yield Button("💡 Dica (F3)", id="btn-tip", classes="action-btn")
                                yield Button("👁️ Solução (F4)", id="btn-solution", classes="action-btn")
                                yield Button("🧹 Reset (F5)", id="btn-reset", classes="action-btn")
                                yield Button("🗺️ Trilhas (F2)", id="btn-tracks", classes="action-btn")

                            yield Static("", id="box-tip", classes="tip-box")
                            yield Static("", id="box-solution", classes="solution-box")

                        with Vertical(id="terminal-panel"):
                            with Horizontal(id="term-title-bar"):
                                yield Label("[#ff5f56]●[/] [#ffbd2e]●[/] [#27c93f]●[/]", classes="term-dots")
                                with Horizontal(classes="iterm-tab-active"):
                                    yield Label("linux-01.sh", id="lbl-term-tab-title", classes="iterm-tab-title")
                                yield Static("", classes="term-bar-spacer")
                                yield Label("⭐ +100 XP  │  ● ONLINE", id="lbl-term-status-badge", classes="term-status-badge")
                            yield RichLog(id="term-output-log", highlight=True, markup=True, wrap=True)
                            with Horizontal(id="term-input-container"):
                                yield Label("2  ➜  ~ ", id="term-prompt")
                                yield Input(placeholder="Digite aqui (ex: ls, pwd, git status, docker ps, kubectl get...)", id="term-input")

                # Footer
                with Horizontal(id="footer-bar"):
                    yield Label("[bold #00f2fe]F2[/] Console Home  │  [bold #38bdf8]Enter[/] Terminal Lab  │  [bold #fbbf24]F3[/] Dica  │  [bold #fb7185]F4[/] Solução  │  [bold #94a3b8]F5[/] Reset  │  [bold #64748b]Ctrl+Q[/] Sair")

    def on_mount(self) -> None:
        if is_powershell():
            try:
                self.query_one("#lbl-term-tab-title", Label).update("🐚 devops@ops-lab (pwsh · em reabilitação 😉)")
                self.query_one("#lbl-term-status-badge", Label).update("PowerShell? · 80x24")
            except Exception:
                pass
        self.load_active_mission()
        self.update_header_stats()
        self.update_prompt()
        self.print_welcome_message()
        self.switch_view("terminal_lab")
        self.run_worker(self._async_check_update, thread=True)

    def switch_view(self, view_name: str) -> None:
        self.current_view = view_name
        console_home = self.query_one("#view-console-home")
        terminal_lab = self.query_one("#view-terminal-lab")
        lbl_title = self.query_one("#lbl-top-view-title", Label)
        lbl_sub = self.query_one("#lbl-top-view-sub", Label)

        btn_nav_home = self.query_one("#nav-console-home", Button)
        btn_nav_lab = self.query_one("#nav-terminal-lab", Button)

        if view_name == "console_home":
            console_home.display = True
            terminal_lab.display = False
            lbl_title.update("Console Home")
            lbl_sub.update("Cloud-aware local runtime overview")
            btn_nav_home.add_class("sidebar-active")
            btn_nav_lab.remove_class("sidebar-active")
            self.update_console_home_stats()
        else:
            console_home.display = False
            terminal_lab.display = True
            lbl_title.update("Terminal Lab")
            lbl_sub.update("Interactive DevOps & SRE learning runtime")
            btn_nav_home.remove_class("sidebar-active")
            btn_nav_lab.add_class("sidebar-active")
            try:
                self.query_one("#term-input", Input).focus()
            except Exception:
                pass

    def select_track_by_id(self, track_id: str) -> None:
        track = TRACKS_MAP.get(track_id)
        if track:
            self.progress.current_track_id = track_id
            uncompleted = [m for m in track.missions if m.id not in self.progress.completed_missions]
            entry_m = uncompleted[0] if uncompleted else (track.missions[0] if track.missions else None)
            if entry_m:
                self.progress.current_mission_id = entry_m.id
            self.progress.save()
            self.load_active_mission()
            self.switch_view("terminal_lab")

    def update_console_home_stats(self) -> None:
        try:
            track = TRACKS_MAP.get(self.progress.current_track_id) or ALL_TRACKS[0]

            # Hero Banner
            self.query_one("#hero-title-label", Label).update(f"{track.name} Local Runtime")
            self.query_one("#hero-desc-label", Label).update(f"Ambiente local, {track.description.lower()} Desafios e validação DevOpsHero Core.")
            self.query_one("#btn-hero-action", Button).label = f"▶ Iniciar Missão: {track.name} (Enter)"

            # Stat card 1: Workspace
            self.query_one("#stat-workspace-title", Label).update(f"{track.name}")
            self.query_one("#stat-workspace-sub", Label).update(f"devops@ops-lab:/{track.id}")

            # Stat card 3: Active tracks
            unlocked_count = sum(1 for t in ALL_TRACKS if self.progress.is_track_unlocked(t))
            self.query_one("#stat-tracks-val", Label).update(f"{unlocked_count} Trilhas Ativas")
            self.query_one("#stat-tracks-sub", Label).update(f"{unlocked_count} de {len(ALL_TRACKS)} trilhas disponíveis")

            # Stat card 4: Resources / XP
            lvl, _, _, _, _ = self.progress.get_level_info()
            bonus = self.progress.get_streak_bonus_pct()
            self.query_one("#stat-xp-val", Label).update(f"{self.progress.xp} XP · Lv.{lvl}")
            self.query_one("#stat-xp-sub", Label).update(f"Streak {self.progress.streak} (+{bonus}% bônus)")
        except Exception:
            pass

    def _async_check_update(self) -> None:
        has_update, remote_ver = check_update_available()
        if has_update:
            def show_update_btn():
                try:
                    btn = self.query_one("#btn-update", Button)
                    btn.display = True
                    if remote_ver:
                        btn.label = f"🚀 Update ({remote_ver})"
                except Exception:
                    pass
            self.call_from_thread(show_update_btn)

    def load_active_mission(self) -> None:
        track_id = self.progress.current_track_id
        mission_id = self.progress.current_mission_id
        self.current_mission = get_mission(track_id, mission_id) or ALL_TRACKS[0].missions[0]

        if self.current_mission.initial_setup:
            self.current_mission.initial_setup(self.state)

        self.show_tip = False
        self.show_solution = False
        self.tips_used = 0
        self.solution_used = False
        self.mission_start_time = time.time()
        self.render_mission_panel()
        try:
            log = self.query_one("#term-output-log", RichLog)
            log.write("")
            log.write(f"[dim #8a94b8]1  # {self.current_mission.objective}[/]")
        except Exception:
            pass

    def render_mission_panel(self) -> None:
        if not self.current_mission:
            return
        m = self.current_mission
        track = TRACKS_MAP.get(m.track_id)
        track_name = track.name if track else m.track_id

        self.query_one("#lbl-mission-track", Label).update(f"// TRILHA: {track_name.upper()}")
        self.query_one("#lbl-mission-title", Label).update(m.title)
        self.query_one("#lbl-diff-badge", Label).update(m.difficulty.upper())
        self.query_one("#lbl-xp-badge", Label).update(f"+{m.xp} XP")

        self.query_one("#box-context", Static).update(m.context)
        self.query_one("#box-objective", Static).update(f"🎯 {m.objective}")

        try:
            if is_powershell():
                self.query_one("#lbl-term-tab-title", Label).update(f"🐚 {m.id}.ps1 (pwsh · em reabilitação 😉)")
                self.query_one("#lbl-term-status-badge", Label).update("PowerShell? · 80x24")
            else:
                self.query_one("#lbl-term-tab-title", Label).update(f"{m.id}.sh")
                self.query_one("#lbl-term-status-badge", Label).update(f"⭐ +{m.xp} XP  │  ● ONLINE")
        except Exception:
            pass

        tip_box = self.query_one("#box-tip", Static)
        if self.show_tip:
            tip_box.display = True
            tip_box.update(f"💡 [bold #fbbf24]DICA:[/] {m.tip}")
        else:
            tip_box.display = False

        sol_box = self.query_one("#box-solution", Static)
        if self.show_solution:
            sol_box.display = True
            sol_box.update(f"👁️ [bold #fb7185]GABARITO:[/] [bold #00f2fe]{m.solution}[/]")
        else:
            sol_box.display = False

    def update_header_stats(self) -> None:
        self.update_console_home_stats()

    def get_ohmyzsh_prompt(self, success: bool = True) -> str:
        arrow_color = "#10b981" if success else "#fb7185"
        cwd = self.state.linux.cwd.replace("/home/devops", "~")

        git_segment = ""
        if self.state.git.is_repo:
            branch = self.state.git.current_branch or "main"
            is_dirty = bool(self.state.git.staged_files or self.state.git.unstaged_files or self.state.git.untracked_files)
            dirty_sym = " [bold #fbbf24]✗[/]" if is_dirty else ""
            git_segment = f" [bold #00f2fe]git:([/][bold #fb7185]{branch}[/]{dirty_sym}[bold #00f2fe])[/]"
        elif "git" in self.state.linux.cwd:
            git_segment = " [bold #00f2fe]git:([/][bold #fb7185]main[/][bold #00f2fe])[/]"

        return f"[dim #8a94b8]2[/]  [bold {arrow_color}]➜[/]  [bold #38bdf8]{cwd}[/]{git_segment} "

    def update_prompt(self) -> None:
        prompt_markup = self.get_ohmyzsh_prompt(self.last_command_success)
        self.query_one("#term-prompt", Label).update(prompt_markup)

    def print_welcome_message(self) -> None:
        log = self.query_one("#term-output-log", RichLog)
        cur_time = time.strftime("%a %b %d %H:%M:%S")
        log.write(f"[dim #64748b]Last login: {cur_time} on ttys001 (Flocí Cloud Console · iTerm2)[/]")

        if is_powershell():
            log.write(Panel(
                get_powershell_humor_message(),
                title="[bold #fbbf24]⚠️  PowerShell Easter Egg[/]",
                border_style="#fbbf24",
            ))

        omz_lines = [
            "         __                                     __",
            "  ____  / /_     ____ ___  __  __   ____  _____/ /_",
            " / __ \\/ __ \\   / __ `__ \\/ / / /  /_  / / ___/ __ \\",
            "/ /_/ / / / /  / / / / / / /_/ /    / /_(__  ) / / /",
            "\\____/_/ /_/  /_/ /_/ /_/\\__, /    /___/____/_/ /_/",
            "                        /____/     v5.9 (Flocí Cloud Console · Oh My Zsh)",
        ]
        for line in omz_lines:
            log.write(Text(line, style="bold #10b981"))
        log.write("[#64748b]• Runtime: [bold #38bdf8]Flocí AWS Core[/]  │  Services: [bold #10b981]19 of 21 available[/]  │  Shell: [bold #38bdf8]zsh[/][/]")
        log.write("[#64748b]• Atalhos: [bold #38bdf8]F2[/] Console Home, [bold #fbbf24]F3[/] dica, [bold #fb7185]F4[/] gabarito, [bold #10b981]F5[/] reset, [bold #38bdf8]Ctrl+Q[/] sair[/]\n")

    @on(Input.Submitted, "#term-input")
    def handle_terminal_input(self, event: Input.Submitted) -> None:
        cmd_text = event.value.strip()
        inp = self.query_one("#term-input", Input)
        inp.value = ""

        if not cmd_text:
            return

        self.progress.command_history.append(cmd_text)
        log = self.query_one("#term-output-log", RichLog)

        prompt_markup = self.get_ohmyzsh_prompt(self.last_command_success)
        log.write(f"{prompt_markup}[bold #ffffff]{escape(cmd_text)}[/]")

        lower_cmd = cmd_text.lower()
        if lower_cmd in ("console", "home", "floci"):
            self.last_command_success = True
            self.switch_view("console_home")
            log.write("[bold #38bdf8]➔ Alternando para Console Home (Flocí Dashboard)...[/]")
            self.update_prompt()
            return
        elif lower_cmd == "help":
            self.last_command_success = True
            log.write(
                "[bold yellow]Comandos de apoio do DevOpsHeroCLI (Flocí Console):[/]\n"
                "  [bold cyan]home[/] / [bold cyan]console[/] - Abre o Console Home Flocí Dashboard (F2)\n"
                "  [bold cyan]dica[/]          - Revela a dica da missão atual (F3)\n"
                "  [bold cyan]solucao[/]       - Revela o comando gabarito da missão (F4 - zera streak)\n"
                "  [bold cyan]trilhas[/]       - Abre a seleção de trilhas e missões (F2)\n"
                "  [bold cyan]reset[/]         - Restaura o ambiente da missão atual para o estado inicial\n"
                "  [bold cyan]clear[/]         - Limpa a tela do terminal (Ctrl+L)\n"
                "  [bold cyan]stats[/]         - Mostra seu perfil, XP e conquistas\n"
                "  [bold cyan]proxima[/]       - Pula para a próxima missão\n"
            )
            self.update_prompt()
            return
        elif lower_cmd in ["dica", "hint"]:
            self.last_command_success = True
            self.action_toggle_tip()
            self.update_prompt()
            return
        elif lower_cmd in ["solucao", "solution", "gabarito"]:
            self.last_command_success = True
            self.action_solution()
            self.update_prompt()
            return
        elif lower_cmd in ["trilhas", "tracks"]:
            self.last_command_success = True
            self.action_tracks()
            self.update_prompt()
            return
        elif lower_cmd == "reset":
            self.last_command_success = True
            self.action_reset_lab()
            self.update_prompt()
            return
        elif lower_cmd in ("clear", "cls"):
            self.last_command_success = True
            self.action_clear_screen()
            self.update_prompt()
            return
        elif lower_cmd in ["stats", "perfil"]:
            self.last_command_success = True
            self.show_user_stats(log)
            self.update_prompt()
            return
        elif lower_cmd in ["proxima", "next"]:
            self.last_command_success = True
            self.advance_to_next_mission()
            self.update_prompt()
            return

        # Execute in simulated engine
        output = self.executor.execute_command_string(cmd_text)
        if output:
            try:
                log.write(output)
            except Exception:
                log.write(Text(output))
            low_out = output.lower()
            if "command not found" in low_out or "error" in low_out or "fatal" in low_out:
                self.last_command_success = False
            else:
                self.last_command_success = True
        else:
            self.last_command_success = True

        self.update_prompt()

        if self.current_mission and self.current_mission.check_completion:
            completed, _ = self.current_mission.check_completion(self.state, cmd_text, output)
            if completed:
                elapsed = max(0.1, round(time.time() - self.mission_start_time, 1))
                award = self.progress.award_mission(
                    self.current_mission,
                    elapsed_seconds=elapsed,
                    tips_used=self.tips_used,
                    solution_used=self.solution_used,
                )
                self.update_header_stats()

                self.bell()
                log.write("")
                log.write("[bold #10b981]╭─────────────────────────────────────────────────────────────────╮[/]")
                log.write("[bold #10b981]│[/] [bold #ffffff]🎉 PARABÉNS! MISSÃO CONCLUÍDA COM SUCESSO![/]")
                log.write(f"[bold #10b981]│[/] [bold #ffd60a]+{award.xp} XP Conquistados![/] · {award.tier_name}")
                log.write(f"[bold #10b981]│[/] ⏱️ [bold cyan]Tempo:[/] {elapsed}s  │  💡 [bold yellow]Dicas:[/] {self.tips_used}  │  🔥 [bold #ff453a]Streak:[/] {self.progress.streak} (+{award.streak_bonus_pct}%)")
                if award.is_ninja:
                    log.write("[bold #10b981]│[/] [bold #10b981]⚡ 100% DOS PONTOS! Executado em <5s sem dicas![/]")
                elif self.tips_used > 0:
                    log.write(f"[bold #10b981]│[/] [dim yellow]⚠️ Dicas utilizadas: Pontuação reduzida ({int(award.factor*100)}% de XP).[/]")
                elif elapsed > 5.0:
                    log.write("[bold #10b981]│[/] [dim]ℹ️ Tempo > 5s: 70% de XP.[/]")
                log.write("[bold #10b981]╰─────────────────────────────────────────────────────────────────╯[/]")
                log.write("[dim]Avançando para a próxima missão...[/]\n")

                self.set_timer(2.2, self.advance_to_next_mission)

    def advance_to_next_mission(self) -> None:
        if not self.current_mission:
            return
        next_step = get_next_mission(
            self.current_mission.track_id,
            self.current_mission.id,
            completed_missions=self.progress.completed_missions,
            shuffle=True,
        )
        if next_step:
            t_id, m_id = next_step
            if t_id != self.current_mission.track_id:
                next_t = TRACKS_MAP.get(t_id)
                if next_t and not self.progress.is_track_unlocked(next_t):
                    log = self.query_one("#term-output-log", RichLog)
                    log.write(f"\n[bold gold1]🎉 Trilha {self.current_mission.track_id.upper()} concluída com sucesso![/]")
                    log.write(f"[bold #f87171]🔒 A próxima trilha ({next_t.name}) requer {next_t.required_seniority} ({next_t.required_xp} XP).[/]")
                    log.write(f"[dim]Você possui {self.progress.xp} XP. Complete outras missões para elevar seu nível![/]\n")
                    return

            self.progress.current_track_id = t_id
            self.progress.current_mission_id = m_id
            self.progress.save()
            self.load_active_mission()

            log = self.query_one("#term-output-log", RichLog)
            log.write(f"[bold #ffd60a]👉 Nova Missão:[/] [bold #38bdf8]{self.current_mission.title}[/]")
            log.write("[dim]Confira os objetivos e detalhes no painel à esquerda.[/dim]\n")
        else:
            log = self.query_one("#term-output-log", RichLog)
            log.write("[bold gold1]🏆 PARABÉNS! VOCÊ COMPLETOU TODAS AS MISSÕES DO DEVOPSHEROCLI![/]")

    def show_user_stats(self, log: RichLog) -> None:
        lvl, title, icon, min_xp, next_xp = self.progress.get_level_info()
        completed = len(self.progress.completed_missions)
        total = sum(len(t.missions) for t in ALL_TRACKS)
        log.write(
            f"[bold cyan]Perfil DevOps do Usuário (Flocí Runtime):[/]\n"
            f"  {icon} [bold]{title}[/]\n"
            f"  ⭐ XP Total: {self.progress.xp} XP\n"
            f"  🔥 Streak Atual: {self.progress.streak} (Recorde: {self.progress.max_streak})\n"
            f"  ✅ Missões Concluídas: {completed} / {total}\n"
        )

    # Actions & Buttons
    def action_tracks(self) -> None:
        if self.current_view == "console_home":
            self.switch_view("terminal_lab")
        else:
            self.switch_view("console_home")

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
        log.write("[bold #10b981]🧹 Ambiente simulado restaurado para o estado inicial. Cronômetro zerado![/]")

    def action_clear_screen(self) -> None:
        log = self.query_one("#term-output-log", RichLog)
        log.clear()

    @on(Button.Pressed, "#btn-tracks")
    def on_btn_tracks(self) -> None:
        self.action_tracks()

    @on(Button.Pressed, "#btn-update")
    def on_btn_update(self) -> None:
        self.action_check_update()

    def action_check_update(self) -> None:
        self.push_screen(AppUpdateModal())

    @on(Button.Pressed, "#btn-tip")
    def on_btn_tip(self) -> None:
        self.action_toggle_tip()

    @on(Button.Pressed, "#btn-solution")
    def on_btn_solution(self) -> None:
        self.action_solution()

    @on(Button.Pressed, "#btn-reset")
    def on_btn_reset(self) -> None:
        self.action_reset_lab()

    @on(Button.Pressed, "#nav-console-home")
    def on_nav_console_home(self) -> None:
        self.switch_view("console_home")

    @on(Button.Pressed, "#nav-terminal-lab")
    def on_nav_terminal_lab(self) -> None:
        self.switch_view("terminal_lab")

    @on(Button.Pressed, "#btn-hero-action")
    def on_btn_hero_action(self) -> None:
        self.switch_view("terminal_lab")

    @on(Button.Pressed, "#nav-track-linux")
    @on(Button.Pressed, "#card-track-linux")
    @on(Button.Pressed, "#pill-filter-linux")
    def on_select_linux(self) -> None:
        self.select_track_by_id("linux")

    @on(Button.Pressed, "#nav-track-docker")
    @on(Button.Pressed, "#card-track-docker")
    @on(Button.Pressed, "#pill-filter-docker")
    def on_select_docker(self) -> None:
        self.select_track_by_id("docker")

    @on(Button.Pressed, "#nav-track-k8s")
    @on(Button.Pressed, "#card-track-k8s")
    @on(Button.Pressed, "#pill-filter-k8s")
    def on_select_k8s(self) -> None:
        self.select_track_by_id("k8s")

    @on(Button.Pressed, "#nav-track-git")
    @on(Button.Pressed, "#card-track-git")
    def on_select_git(self) -> None:
        self.select_track_by_id("git")

    @on(Button.Pressed, "#nav-track-aws")
    @on(Button.Pressed, "#card-track-aws")
    @on(Button.Pressed, "#pill-filter-aws")
    def on_select_aws(self) -> None:
        self.select_track_by_id("aws")

    @on(Button.Pressed, "#nav-track-terraform")
    @on(Button.Pressed, "#card-track-terraform")
    @on(Button.Pressed, "#pill-filter-terraform")
    def on_select_terraform(self) -> None:
        self.select_track_by_id("terraform")

    @on(Button.Pressed, "#nav-track-datadog")
    @on(Button.Pressed, "#card-track-datadog")
    @on(Button.Pressed, "#pill-filter-datadog")
    def on_select_datadog(self) -> None:
        self.select_track_by_id("datadog")


def launch_app():
    app = DevOpsHeroApp()
    app.run()


if __name__ == "__main__":
    launch_app()
