"""Data models and progress tracking for DevOpsHeroCLI."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, List, Optional, Set, Tuple


@dataclass
class Mission:
    id: str
    track_id: str
    title: str
    difficulty: str  # "Iniciante", "Intermediário", "Avançado"
    xp: int
    context: str
    objective: str
    tip: str
    solution: str
    initial_setup: Optional[Callable[[Any], None]] = None
    # check_completion returns (is_completed: bool, feedback_message: str)
    check_completion: Optional[Callable[[Any, str, str], Tuple[bool, str]]] = None


@dataclass
class Track:
    id: str
    name: str
    icon: str
    description: str
    missions: List[Mission] = field(default_factory=list)


LEVELS = [
    (0, "Nível 1 · Recruta DevOps", "🌱"),
    (250, "Nível 2 · Sysadmin Básico", "🛠️"),
    (600, "Nível 3 · Linux Explorer", "🐧"),
    (1100, "Nível 4 · Git Codecrafter", "🌿"),
    (1700, "Nível 5 · Container Captain", "🐳"),
    (2500, "Nível 6 · Cluster Commander", "☸️"),
    (3500, "Nível 7 · Cloud Architect", "☁️"),
    (4700, "Nível 8 · IaC Master", "🏗️"),
    (6200, "Nível 9 · Observability Guru", "🐕"),
    (8000, "Nível 10 · DevOps Titan", "⚡"),
]


class AwardResult(int):
    """Result of completing a mission, inheriting from int for total backward-compatibility."""

    def __new__(
        cls,
        xp: int,
        base_xp: int = 0,
        factor: float = 1.0,
        tier_name: str = "",
        elapsed_seconds: float = 0.0,
        tips_used: int = 0,
        streak_bonus_pct: int = 0,
        is_ninja: bool = False,
        is_repeat: bool = False,
        solution_used: bool = False,
    ):
        obj = super().__new__(cls, xp)
        obj.xp = xp
        obj.base_xp = base_xp
        obj.factor = factor
        obj.tier_name = tier_name
        obj.elapsed_seconds = elapsed_seconds
        obj.tips_used = tips_used
        obj.streak_bonus_pct = streak_bonus_pct
        obj.is_ninja = is_ninja
        obj.is_repeat = is_repeat
        obj.solution_used = solution_used
        return obj


class UserProgress:
    """Manages XP, Streaks, Completed Missions and Save State."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            config_dir = Path.home() / ".devopsherocli"
            try:
                config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            except OSError:
                config_dir.mkdir(parents=True, exist_ok=True)
            self.storage_path = config_dir / "progress.json"
        else:
            self.storage_path = storage_path

        self.xp: int = 0
        self.streak: int = 0
        self.max_streak: int = 0
        self.completed_missions: Set[str] = set()
        self.current_track_id: str = "linux"
        self.current_mission_id: str = "linux-01"
        self.command_history: List[str] = []
        self.load()

    def get_level_info(self) -> Tuple[int, str, str, int, int]:
        """Returns (current_level_num, title, icon, current_level_xp, next_level_xp)."""
        current_lvl = 1
        current_title = LEVELS[0][1]
        current_icon = LEVELS[0][2]
        current_min = 0
        next_min = LEVELS[1][0]

        for i, (req_xp, title, icon) in enumerate(LEVELS):
            if self.xp >= req_xp:
                current_lvl = i + 1
                current_title = title
                current_icon = icon
                current_min = req_xp
                if i + 1 < len(LEVELS):
                    next_min = LEVELS[i + 1][0]
                else:
                    next_min = req_xp + 1000
            else:
                break

        return current_lvl, current_title, current_icon, current_min, next_min

    def get_streak_bonus_pct(self) -> int:
        if self.streak <= 1:
            return 0
        elif self.streak == 2:
            return 10
        elif self.streak == 3:
            return 20
        elif self.streak == 4:
            return 30
        elif self.streak == 5:
            return 40
        else:
            return 50

    def award_mission(
        self,
        mission: Mission,
        elapsed_seconds: float = 0.0,
        tips_used: int = 0,
        solution_used: bool = False,
    ) -> AwardResult:
        """
        Awards XP with anti-cheat/anti-Google speed penalty, hints penalty, and streak bonus.

        Rules:
        - 100% of base points ONLY if: tips_used == 0 AND elapsed_seconds <= 5.0
        - If solution_used == True (F4/gabarito): 0 XP awarded, streak broken.
        - If tips_used == 0 and elapsed_seconds > 5.0:
            Deducts points for excessive delay (anti-copy from Google/AI): 70% base XP.
        - If tips_used > 0:
            Points decrease with each tip requested:
            - 1 tip: 40% base XP (-60%)
            - 2 tips: 20% base XP (-80%)
            - 3+ tips: 10% base XP (-90%)
        - Streak bonus is applied on top of the earned base.
        - Repeating an already completed mission awards half of the computed XP.
        """
        if solution_used:
            self.break_streak()
            return AwardResult(
                xp=0,
                base_xp=mission.xp,
                factor=0.0,
                tier_name="👁️ Gabarito Revelado (0 XP)",
                elapsed_seconds=elapsed_seconds,
                tips_used=tips_used,
                streak_bonus_pct=0,
                is_ninja=False,
                is_repeat=mission.id in self.completed_missions,
                solution_used=True,
            )

        is_ninja = False
        if tips_used == 0:
            if elapsed_seconds <= 5.0:
                factor = 1.0
                is_ninja = True
                tier_name = "⚡ 100% Ninja Reflex (<5s sem dicas!)"
            else:
                factor = 0.70
                tier_name = f"⏱️ Tempo > 5s ({elapsed_seconds:.1f}s) - 70% XP"
        else:
            if tips_used == 1:
                factor = 0.40
                tier_name = "💡 1 Dica Usada - 40% XP (-60%)"
            elif tips_used == 2:
                factor = 0.20
                tier_name = "💡 2 Dicas Usadas - 20% XP (-80%)"
            else:
                factor = 0.10
                tier_name = f"💡 {tips_used} Dicas Usadas - 10% XP (-90%)"

        bonus_pct = self.get_streak_bonus_pct()
        calc_xp = int(mission.xp * factor * (1 + bonus_pct / 100.0))
        earned_xp = max(5, calc_xp)

        # If already completed before, only grant half XP
        is_repeat = mission.id in self.completed_missions
        if is_repeat:
            earned_xp = max(5, earned_xp // 2)
        else:
            self.completed_missions.add(mission.id)

        self.xp += earned_xp
        self.streak += 1
        if self.streak > self.max_streak:
            self.max_streak = self.streak

        self.save()
        return AwardResult(
            xp=earned_xp,
            base_xp=mission.xp,
            factor=factor,
            tier_name=tier_name,
            elapsed_seconds=elapsed_seconds,
            tips_used=tips_used,
            streak_bonus_pct=bonus_pct,
            is_ninja=is_ninja,
            is_repeat=is_repeat,
            solution_used=False,
        )

    def break_streak(self):
        """Called when user asks for explicit solution or skips."""
        self.streak = 0
        self.save()

    def save(self):
        """Atomically saves progress state to disk with secure permissions."""
        try:
            data = {
                "xp": int(self.xp),
                "streak": int(self.streak),
                "max_streak": int(self.max_streak),
                "completed_missions": sorted(list(self.completed_missions)),
                "current_track_id": str(self.current_track_id),
                "current_mission_id": str(self.current_mission_id),
                "command_history": [str(c) for c in self.command_history[-100:]],
            }
            parent = self.storage_path.parent
            parent.mkdir(parents=True, exist_ok=True)
            tmp_path = parent / f".{self.storage_path.name}.tmp"

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            try:
                os.chmod(tmp_path, 0o600)
            except OSError:
                pass

            os.replace(tmp_path, self.storage_path)
        except (OSError, TypeError, ValueError):
            pass

    def load(self):
        """Loads and safely validates progress state from storage."""
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return
            self.xp = max(0, int(data.get("xp", 0)))
            self.streak = max(0, int(data.get("streak", 0)))
            self.max_streak = max(self.streak, int(data.get("max_streak", 0)))
            raw_completed = data.get("completed_missions", [])
            if isinstance(raw_completed, (list, set, tuple)):
                self.completed_missions = {str(m) for m in raw_completed if isinstance(m, (str, int))}
            self.current_track_id = str(data.get("current_track_id", "linux"))
            self.current_mission_id = str(data.get("current_mission_id", "linux-01"))
            raw_hist = data.get("command_history", [])
            if isinstance(raw_hist, list):
                self.command_history = [str(c) for c in raw_hist if isinstance(c, str)]
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    def reset_progress(self):
        self.xp = 0
        self.streak = 0
        self.max_streak = 0
        self.completed_missions.clear()
        self.current_track_id = "linux"
        self.current_mission_id = "linux-01"
        self.command_history.clear()
        self.save()
