from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from models.state import BehavioralState, EventType
from core.database import SupabaseRepository
from utils.analytics import BehavioralEngine

logger = logging.getLogger(__name__)
DEFAULT_TZ = timezone.utc


class AuthService:
    @staticmethod
    def initialize_session(session_state) -> None:
        if "user_id" not in session_state:
            session_state["user_id"] = "demo-user"

    @staticmethod
    def get_current_user_id(session_state) -> str:
        return (
            session_state.get("auth_user_id")
            or session_state.get("user_id")
            or "demo-user"
        )

    @staticmethod
    def is_demo_mode(user_id: str) -> bool:
        return user_id == "demo-user"


def load_user_state(repo: SupabaseRepository, user_id: str) -> BehavioralState:
    """Load state from DB, falling back to a fresh state for demo/new users."""
    return repo.load_state(user_id) or BehavioralState(user_id=user_id)


def process_checkin(
    repo: SupabaseRepository,
    user_id: str,
    emotion: Optional[str] = None,
    actions_taken: Optional[List[str]] = None,
    reflection: Optional[str] = None,
) -> BehavioralState:
    """
    Orchestrate a full check-in cycle.

    Steps:
    1. Load current state + event history from DB
    2. Compute all new metrics via pure BehavioralEngine functions
    3. Build the new event's metadata (including was_absent flag)
    4. Merge temporary event into history for metric calculations
       (avoids a round-trip that would miss the new event in analytics)
    5. Persist new state atomically; log event(s) separately
    6. Return updated state to the caller (no DB re-fetch needed)
    """
    now_utc = datetime.now(DEFAULT_TZ)
    state = load_user_state(repo, user_id)
    events = repo.load_events(user_id, limit=100)

    # --- Streak ---
    new_streak, was_broken, is_return = BehavioralEngine.calculate_streak(
        last_checkin_utc=state.last_checkin_utc,
        current_streak=state.current_streak,
        now_utc=now_utc,
    )
    new_longest = BehavioralEngine.update_longest_streak(new_streak, state.longest_streak)

    # --- Build metadata for this event ---
    metadata: Dict = {
        "emotion": emotion,
        "actions_taken": actions_taken or [],
        "reflection": reflection or "",
        "was_absent": is_return,
        "streak_after": new_streak,
    }

    # --- Merge new event into history for downstream calculations ---
    event_type_str = EventType.RETURN.value if is_return else EventType.CHECKIN.value
    temp_event = {
        "event_type": event_type_str,
        "created_at_utc": now_utc.isoformat(),
        "metadata": metadata,
    }
    temp_events = sorted(
        events + [temp_event],
        key=lambda x: x.get("created_at_utc", ""),
    )

    # --- Recalculate all metrics with merged history ---
    new_consistency = BehavioralEngine.calculate_consistency(temp_events, now_utc)
    new_mode = BehavioralEngine.detect_psychological_mode(temp_events, new_consistency, new_streak)
    new_level = BehavioralEngine.calculate_level(new_consistency)
    new_risk = BehavioralEngine.calculate_risk_score(temp_events, now_utc)

    unlocked = BehavioralEngine.check_achievements(
        events=temp_events,
        total_checkins=state.total_checkins + 1,
        streak=new_streak,
        has_return=is_return,
        unlocked_set=frozenset(state.unlocked_achievements),
    )

    # --- Mutate state ---
    state.consistency_score = new_consistency
    state.current_streak = new_streak
    state.longest_streak = new_longest
    state.total_checkins += 1
    state.last_checkin_utc = now_utc.isoformat()
    state.current_level = new_level
    state.psychological_mode = new_mode
    state.risk_score = new_risk
    # Extend achievements, avoiding duplicates
    existing = set(state.unlocked_achievements)
    state.unlocked_achievements.extend(a for a in unlocked if a not in existing)

    if emotion:
        state.emotion_history.append({
            "emotion": emotion,
            "timestamp_utc": now_utc.isoformat(),
            "streak_at_time": new_streak,
        })
        # Keep only most recent 50 to avoid bloating the DB column
        state.emotion_history = state.emotion_history[-50:]

    # --- Persist ---
    repo.save_state(state)
    repo.log_event(user_id, event_type_str, metadata)
    for ach in unlocked:
        repo.log_event(user_id, EventType.ACHIEVEMENT.value, {"achievement": ach})

    return state
