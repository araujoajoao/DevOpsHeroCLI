#!/usr/bin/env python3
"""Export DevOpsHero missions into a rich interactive mobile dataset for iOS and Android."""
from __future__ import annotations

import json
import random
import shlex
from pathlib import Path
from typing import Any, Dict, List

from devopsherocli.tracks import ALL_TRACKS

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE_RN = REPO_ROOT / "devopshero-mobile" / "assets" / "data" / "missions.json"
OUTPUT_FILE_SWIFT = REPO_ROOT / "devopshero-ios-swiftui" / "Sources" / "Resources" / "missions.json"

DISTRACTORS_BY_TRACK = {
    "linux": [
        "pwd", "ls", "cd", "cat", "grep", "touch", "mkdir", "rm", "-la", "-rf", "-h",
        "sudo", "chmod", "600", "755", "head", "tail", "whoami", "uname", "uptime"
    ],
    "sysadmin": [
        "systemctl", "journalctl", "restart", "status", "enable", "disable", "stop", "start",
        "-u", "ps", "kill", "-9", "free", "df", "ss", "-tulpn", "top", "crontab"
    ],
    "git": [
        "git", "init", "status", "add", "commit", "push", "pull", "checkout", "branch",
        "merge", "-m", "-b", "origin", "main", "reset", "stash", "log", "--staged"
    ],
    "docker": [
        "docker", "run", "ps", "images", "build", "stop", "rm", "exec", "logs", "-d",
        "-it", "-p", "--name", "-v", "--rm", "alpine", "latest", "pull", "restart"
    ],
    "k8s": [
        "kubectl", "get", "describe", "apply", "delete", "logs", "exec", "pods",
        "services", "deployments", "-n", "-f", "-A", "--all-namespaces", "--dry-run=client"
    ],
    "aws": [
        "aws", "s3", "ec2", "iam", "sts", "ls", "cp", "mb", "describe-instances",
        "get-caller-identity", "--region", "us-east-1", "--output", "json"
    ],
    "terraform": [
        "terraform", "init", "plan", "apply", "destroy", "validate", "fmt", "show",
        "output", "-auto-approve", "-var", "main.tf", "-target"
    ],
    "datadog": [
        "datadog-agent", "status", "health", "version", "check", "flare", "configcheck",
        "DD_API_KEY", "DD_SITE", "DD_ENV", "DD_SERVICE", "datadoghq.com"
    ]
}


def build_dataset() -> Dict[str, Any]:
    random.seed(42)
    tracks_list: List[Dict[str, Any]] = []
    total_missions = 0

    for track in ALL_TRACKS:
        track_data: Dict[str, Any] = {
            "id": track.id,
            "name": track.name,
            "icon": track.icon,
            "description": track.description,
            "required_xp": getattr(track, "required_xp", 0),
            "required_seniority": getattr(track, "required_seniority", "Nível 1 · Recruta"),
            "missions_count": len(track.missions),
            "missions": []
        }

        pool = DISTRACTORS_BY_TRACK.get(track.id, ["--help", "status", "info"])

        for mission in track.missions:
            tokens = shlex.split(mission.solution)

            # Generate distractors for word bank
            candidate_distractors = [d for d in pool if d not in tokens]
            distractor_sample_size = min(4, len(candidate_distractors))
            distractors = random.sample(candidate_distractors, distractor_sample_size)

            all_chips = list(tokens) + distractors
            random.shuffle(all_chips)

            # 1. Fill-in-the-Blank: select the most instructional token (flag, subcommand or arg)
            blank_idx = 1 if len(tokens) > 1 else 0
            for i, tok in enumerate(tokens):
                if tok.startswith("-") or (i == 1 and not tok.startswith("-")):
                    blank_idx = i
                    break

            blank_target = tokens[blank_idx]
            blank_tokens = list(tokens)
            blank_tokens[blank_idx] = "____"
            blank_sentence = " ".join(blank_tokens)

            blank_choices = [blank_target] + random.sample(candidate_distractors, 3)
            random.shuffle(blank_choices)

            # 2. Multiple Choice: generate 3 plausible wrong options
            mc_options = [mission.solution]
            for dist in distractors[:3]:
                fake_tokens = list(tokens)
                if len(fake_tokens) > 1:
                    fake_tokens[blank_idx] = dist
                else:
                    fake_tokens = [dist]
                fake_cmd = " ".join(fake_tokens)
                if fake_cmd not in mc_options:
                    mc_options.append(fake_cmd)

            while len(mc_options) < 4:
                mc_options.append(f"{tokens[0]} --help")

            random.shuffle(mc_options)

            mission_entry: Dict[str, Any] = {
                "id": mission.id,
                "track_id": track.id,
                "track_name": track.name,
                "track_icon": track.icon,
                "title": mission.title,
                "difficulty": mission.difficulty,
                "xp": mission.xp,
                "scenario": mission.context,
                "objective": mission.objective,
                "tip": mission.tip,
                "solution": mission.solution,
                "exercise_types": {
                    "word_bank": {
                        "instruction": "Monte o comando correto tocando nos blocos em ordem:",
                        "target_tokens": tokens,
                        "chips": all_chips
                    },
                    "fill_in_the_blank": {
                        "instruction": "Complete o comando com o parâmetro correto:",
                        "sentence": blank_sentence,
                        "correct_choice": blank_target,
                        "choices": blank_choices
                    },
                    "multiple_choice": {
                        "question": mission.objective,
                        "options": mc_options,
                        "correct_index": mc_options.index(mission.solution),
                        "explanation": mission.tip
                    }
                }
            }

            track_data["missions"].append(mission_entry)
            total_missions += 1

        tracks_list.append(track_data)

    return {
        "app_title": "DevOpsHero",
        "tagline": "Aprenda DevOps, Linux, Docker, Kubernetes, AWS, Terraform e Datadog na prática",
        "total_tracks": len(tracks_list),
        "total_missions": total_missions,
        "tracks": tracks_list
    }


def main():
    dataset = build_dataset()

    OUTPUT_FILE_RN.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE_RN, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"✓ [DevOpsHero Mobile] Dataset exportado para {OUTPUT_FILE_RN}")

    if OUTPUT_FILE_SWIFT.parent.exists():
        with open(OUTPUT_FILE_SWIFT, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"✓ [DevOpsHero SwiftUI] Dataset exportado para {OUTPUT_FILE_SWIFT}")

    print(f"  • {dataset['total_tracks']} Trilhas reordenadas pelo fluxo oficial de ferramentas")
    print(f"  • {dataset['total_missions']} Missões com travas por Senioridade e XP!")


if __name__ == "__main__":
    main()

