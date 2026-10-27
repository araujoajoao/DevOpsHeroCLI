"""Tracks catalog registry for DevOpsHeroCLI."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from devopsherocli.models import Mission, Track
from devopsherocli.tracks.datadog_track import DATADOG_TRACK
from devopsherocli.tracks.docker_track import DOCKER_TRACK
from devopsherocli.tracks.k8s_track import K8S_TRACK
from devopsherocli.tracks.linux_track import LINUX_TRACK
from devopsherocli.tracks.sysadmin_track import SYSADMIN_TRACK

ALL_TRACKS: List[Track] = [
    LINUX_TRACK,
    SYSADMIN_TRACK,
    DOCKER_TRACK,
    K8S_TRACK,
    DATADOG_TRACK,
]

TRACKS_MAP: Dict[str, Track] = {t.id: t for t in ALL_TRACKS}


def get_mission(track_id: str, mission_id: str) -> Optional[Mission]:
    track = TRACKS_MAP.get(track_id)
    if not track:
        return None
    for m in track.missions:
        if m.id == mission_id:
            return m
    return None


def get_next_mission(current_track_id: str, current_mission_id: str) -> Optional[Tuple[str, str]]:
    track = TRACKS_MAP.get(current_track_id)
    if not track:
        return None

    # Try next mission in same track
    for i, m in enumerate(track.missions):
        if m.id == current_mission_id:
            if i + 1 < len(track.missions):
                return current_track_id, track.missions[i + 1].id
            break

    # If completed all missions in this track, jump to first mission of next track
    track_keys = [t.id for t in ALL_TRACKS]
    if current_track_id in track_keys:
        curr_idx = track_keys.index(current_track_id)
        if curr_idx + 1 < len(track_keys):
            next_t = ALL_TRACKS[curr_idx + 1]
            if next_t.missions:
                return next_t.id, next_t.missions[0].id

    return None
