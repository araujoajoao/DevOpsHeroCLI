"""Data models and progress tracking for DevOpsHeroCLI."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


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


class UserProgress:
    """Manages XP, Streaks, Completed Missions and Save State."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            config_dir = Path.home() / ".devopsherocli"
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

    def award_mission(self, mission: Mission) -> int:
        """Awards XP with streak bonus and marks mission as completed. Returns gained XP."""
        bonus_pct = self.get_streak_bonus_pct()
        earned_xp = int(mission.xp * (1 + bonus_pct / 100.0))
        
        # If already completed before, only grant half XP
        if mission.id in self.completed_missions:
            earned_xp = max(10, earned_xp // 2)
        else:
            self.completed_missions.add(mission.id)

        self.xp += earned_xp
        self.streak += 1
        if self.streak > self.max_streak:
            self.max_streak = self.streak
            
        self.save()
        return earned_xp

    def break_streak(self):
        """Called when user asks for explicit solution or skips."""
        self.streak = 0
        self.save()

    def save(self):
        try:
            data = {
                "xp": self.xp,
                "streak": self.streak,
                "max_streak": self.max_streak,
                "completed_missions": list(self.completed_missions),
                "current_track_id": self.current_track_id,
                "current_mission_id": self.current_mission_id,
                "command_history": self.command_history[-100:],
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def load(self):
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.xp = data.get("xp", 0)
                self.streak = data.get("streak", 0)
                self.max_streak = data.get("max_streak", 0)
                self.completed_missions = set(data.get("completed_missions", []))
                self.current_track_id = data.get("current_track_id", "linux")
                self.current_mission_id = data.get("current_mission_id", "linux-01")
                self.command_history = data.get("command_history", [])
        except Exception:
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
