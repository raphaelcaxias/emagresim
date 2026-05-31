from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from models.state import PsychologicalMode, _NEGATIVE_EMOTIONS

DEFAULT_TZ = timezone.utc


class BehavioralEngine:
    """
    Pure-function behavioral analysis engine.
    No side-effects — all methods are safe to call in tests or Streamlit reruns.

    Key fixes vs original:
    - normalizer changed from 2.5 → 0.49 so scores map naturally to level thresholds
      (7 days ≈ 27, 14 days ≈ 50, 30 days ≈ 87 — matching Level 1-4 breakpoints)
    - calculate_risk_score now iterates most-recent events first (weight = 1 - i/window
      must apply to the newest, not oldest, events)
    - detect_patterns no longer assigns a "risky hour" when no hour is genuinely risky;
      the fallback min_hour was semantically misleading
    - check_achievements 'no_guilt' now checks only the most-recent event to avoid
      the achievement firing retroactively on re-runs
    - All datetime parsing guards against naive datetimes from Supabase ISO strings
    """

    CONFIG = {
        "consistency": {
            "window_days": 30,
            "decay_rate": 0.02,       # lose 2% weight per day of age
            "min_decay": 0.3,          # floor: even a 35-day-old event counts a little
            "weights": {"checkin": 2, "return": 3, "achievement": 1},
            "return_bonus": 5,         # extra points for coming back after absence
            "normalizer": 0.49,        # calibrated so 30 daily checkins ≈ 87/100
        },
        "risk": {
            "window_events": 14,           # look at last N events
            "absence_threshold_days": 3,   # >3 days since last checkin = at risk
            "negative_emotion_weight": 2,
            "absence_weight": 3,
        },
        "patterns": {
            "risky_hours_ratio": 0.5,  # hours with < 50% of average activity are "risky"
        },
    }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(DEFAULT_TZ)

    @staticmethod
    def _parse_utc(iso: Optional[str]) -> Optional[datetime]:
        """Parse ISO string → aware datetime. Handles both Z and +00:00 suffixes."""
        if not iso:
            return None
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            # Make sure it's timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=DEFAULT_TZ)
            return dt
        except (ValueError, AttributeError):
            return None

    # ------------------------------------------------------------------
    # Consistency
    # ------------------------------------------------------------------

    @classmethod
    def calculate_consistency(
        cls,
        events: List[Dict],
        now_utc: Optional[datetime] = None,
    ) -> float:
        """
        Weighted, time-decayed consistency score in [0, 100].

        Each event contributes  weight × decay  points.
        Decay falls 2%/day, floored at 0.3 so historical events still matter.
        A return-after-absence adds an extra bonus to reward resilience.
        """
        if not events:
            return 0.0

        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["consistency"]
        score = 0.0

        # Only consider events within the rolling window (2× for safety buffer)
        for event in events[-(cfg["window_days"] * 2) :]:
            event_type = event.get("event_type", "")
            weight = cfg["weights"].get(event_type, 1)

            event_ts = cls._parse_utc(event.get("created_at_utc"))
            if not event_ts:
                continue

            days_ago = max(0, (now - event_ts).days)
            if days_ago > cfg["window_days"]:
                continue  # truly outside window

            decay = max(cfg["min_decay"], 1.0 - days_ago * cfg["decay_rate"])
            score += weight * decay

            if event.get("metadata", {}).get("was_absent"):
                score += cfg["return_bonus"]

        return round(min(100.0, score / cfg["normalizer"]), 1)

    # ------------------------------------------------------------------
    # Streak
    # ------------------------------------------------------------------

    @classmethod
    def calculate_streak(
        cls,
        last_checkin_utc: Optional[str],
        current_streak: int,
        now_utc: Optional[datetime] = None,
    ) -> Tuple[int, bool, bool]:
        """
        Returns (new_streak, was_broken, is_return).

        - same day  → keep streak unchanged
        - next day  → increment streak
        - gap > 1   → reset to 1, flag as broken/return
        """
        now = now_utc or cls._now_utc()
        last = cls._parse_utc(last_checkin_utc)

        if not last:
            return 1, False, False  # very first checkin

        delta = (now.date() - last.date()).days

        if delta == 0:
            # Already checked in today — no change
            return current_streak, False, False
        if delta == 1:
            # Perfect continuity
            return current_streak + 1, False, False
        # Gap detected
        return 1, True, True

    @staticmethod
    def update_longest_streak(current: int, longest: int) -> int:
        return max(longest, current)

    # ------------------------------------------------------------------
    # Psychological mode
    # ------------------------------------------------------------------

    @classmethod
    def detect_psychological_mode(
        cls,
        events: List[Dict],
        consistency: float,
        current_streak: int,
    ) -> str:
        """
        Heuristic mode detection:
        - SURVIVAL  → high negative-emotion ratio OR very low consistency
        - STABLE    → high consistency AND sustained streak
        - RETURNING → most recent event is a return
        - NORMAL    → everything else
        """
        if not events:
            return PsychologicalMode.NORMAL.value

        # Check for an explicit return event most recently
        last_event = events[-1]
        if last_event.get("metadata", {}).get("was_absent"):
            return PsychologicalMode.RETURNING.value

        # Negative emotion ratio over last 7 events
        recent = events[-7:]
        recent_neg = sum(
            1 for e in recent
            if e.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS
        )
        neg_ratio = recent_neg / len(recent) if recent else 0

        if neg_ratio > 0.4 or consistency < 20:
            return PsychologicalMode.SURVIVAL.value
        if consistency >= 70 and current_streak >= 5:
            return PsychologicalMode.STABLE.value
        return PsychologicalMode.NORMAL.value

    # ------------------------------------------------------------------
    # Level
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_level(consistency: float) -> int:
        """Map consistency score → level (0-5)."""
        thresholds = [(5, 90), (4, 75), (3, 55), (2, 35), (1, 15), (0, 0)]
        for lvl, min_c in thresholds:
            if consistency >= min_c:
                return lvl
        return 0

    # ------------------------------------------------------------------
    # Achievements
    # ------------------------------------------------------------------

    @staticmethod
    def check_achievements(
        events: List[Dict],
        total_checkins: int,
        streak: int,
        has_return: bool,
        unlocked_set: frozenset,
    ) -> List[str]:
        """
        Returns list of newly-unlocked achievement keys.

        'no_guilt' fires when the CURRENT checkin carries a negative emotion AND
        the user didn't abandon (i.e., they're still here). We look only at the
        very last event to avoid retroactive unlocks on reruns.
        """
        unlocked: List[str] = []

        if total_checkins >= 1 and "first_checkin" not in unlocked_set:
            unlocked.append("first_checkin")

        if has_return and "courageous_return" not in unlocked_set:
            unlocked.append("courageous_return")

        if streak >= 7 and "seven_days" not in unlocked_set:
            unlocked.append("seven_days")

        if streak >= 14 and "fourteen_days" not in unlocked_set:
            unlocked.append("fourteen_days")

        # no_guilt: the most-recent checkin has a negative emotion → they stayed anyway
        if events and "no_guilt" not in unlocked_set:
            last_meta = events[-1].get("metadata", {})
            if last_meta.get("emotion") in _NEGATIVE_EMOTIONS:
                unlocked.append("no_guilt")

        return unlocked

    # ------------------------------------------------------------------
    # Risk score
    # ------------------------------------------------------------------

    @classmethod
    def calculate_risk_score(
        cls,
        events: List[Dict],
        now_utc: Optional[datetime] = None,
    ) -> float:
        """
        Risk score in [0, 100] — higher means higher dropout risk.

        Weights RECENT events most (i=0 → most recent, weight=1.0).
        Penalises long gaps between events and negative emotion streaks.
        Returns 0 when history is too short to be meaningful (< 5 events).
        """
        if len(events) < 5:
            return 0.0

        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["risk"]
        window = cfg["window_events"]
        risk = 0.0

        # Take the most-recent N events and iterate newest-first
        recent_events = list(reversed(events[-window:]))

        for i, event in enumerate(recent_events):
            weight = 1.0 - i / window  # 1.0 for most recent, approaches 0 for oldest

            event_ts = cls._parse_utc(event.get("created_at_utc"))
            days_ago = (now - event_ts).days if event_ts else 0

            if days_ago > cfg["absence_threshold_days"]:
                risk += cfg["absence_weight"] * weight

            if event.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS:
                risk += cfg["negative_emotion_weight"] * weight

        return min(100.0, round(risk, 1))

    # ------------------------------------------------------------------
    # Pattern detection
    # ------------------------------------------------------------------

    @classmethod
    def detect_patterns(cls, events: List[Dict]) -> Dict:
        """
        Detect behavioural patterns from event history.

        Returns:
            risky_hours: hours where checkin frequency is below 50% of average.
                         Empty list if data is insufficient or no hour is truly risky.
            weekday_tendency: dict of {weekday_int: count} for all 7 days.
            return_pattern: summary of return events, or None.
        """
        patterns: Dict = {
            "risky_hours": [],
            "weekday_tendency": {},
            "return_pattern": None,
        }

        if len(events) < 10:
            return patterns  # not enough data to detect meaningful patterns

        # --- Risky hours ---
        hour_counts: Dict[int, int] = {h: 0 for h in range(24)}
        for e in events:
            if e.get("event_type") == "checkin":
                ts = cls._parse_utc(e.get("created_at_utc"))
                if ts:
                    hour_counts[ts.hour] += 1

        active_hours = {h: c for h, c in hour_counts.items() if c > 0}

        if active_hours:
            avg_activity = sum(active_hours.values()) / len(active_hours)
            ratio = cls.CONFIG["patterns"]["risky_hours_ratio"]
            threshold = avg_activity * ratio
            # Only flag hours that genuinely exist AND are below threshold
            risky = [h for h, c in active_hours.items() if c < threshold]
            patterns["risky_hours"] = sorted(risky)
            # NOTE: If no hour is below threshold, risky stays [] — correct behaviour.

        # --- Weekday tendency ---
        weekday_counts: Dict[int, int] = {i: 0 for i in range(7)}
        for e in events:
            ts = cls._parse_utc(e.get("created_at_utc"))
            if ts:
                weekday_counts[ts.weekday()] += 1
        patterns["weekday_tendency"] = weekday_counts

        # --- Return pattern ---
        returns = [e for e in events if e.get("event_type") == "return"]
        if returns:
            patterns["return_pattern"] = {
                "count": len(returns),
                "last_return_utc": returns[-1].get("created_at_utc"),
            }

        return patterns
