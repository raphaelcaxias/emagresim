from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

from models.state import PsychologicalMode, _NEGATIVE_EMOTIONS

DEFAULT_TZ = timezone.utc


class BehavioralEngine:
    CONFIG: Dict = {
        "consistency": {
            "window_days": 30, "decay_rate": 0.02, "min_decay": 0.3,
            "weights": {"checkin": 2, "return": 3, "achievement": 1},
            "return_bonus": 5, "normalizer": 2.5,
        },
        "risk": {
            "window_events": 14, "absence_threshold_days": 3,
            "negative_emotion_weight": 2, "absence_weight": 3,
        },
        "patterns": {"risky_hours_ratio": 0.5},
    }

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(DEFAULT_TZ)

    @staticmethod
    def _parse_utc(iso: Optional[str]) -> Optional[datetime]:
        if not iso:
            return None
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))

    @classmethod
    def calculate_consistency(cls, events: List[Dict], now_utc: Optional[datetime] = None) -> float:
        if not events:
            return 0.0
        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["consistency"]
        score = 0.0
        for event in events[-(cfg["window_days"] * 2):]:
            event_type = event.get("event_type", "")
            weight = cfg["weights"].get(event_type, 1)
            event_ts = cls._parse_utc(event.get("created_at_utc"))
            if not event_ts:
                continue
            days_ago = (now - event_ts).days
            decay = max(cfg["min_decay"], 1 - days_ago * cfg["decay_rate"])
            score += weight * decay
            if event.get("metadata", {}).get("was_absent"):                score += cfg["return_bonus"]
        return round(min(100.0, score / cfg["normalizer"]), 1)

    @classmethod
    def calculate_streak(
        cls, last_checkin_utc: Optional[str], current_streak: int, now_utc: Optional[datetime] = None
    ) -> Tuple[int, bool, bool]:
        now = now_utc or cls._now_utc()
        last = cls._parse_utc(last_checkin_utc)
        if not last:
            return 1, False, False
        delta = (now.date() - last.date()).days
        if delta == 0:
            return current_streak, False, False
        if delta == 1:
            return current_streak + 1, False, False
        return 1, True, True

    @staticmethod
    def update_longest_streak(current: int, longest: int) -> int:
        return max(longest, current)

    @classmethod
    def detect_psychological_mode(
        cls, events: List[Dict], consistency: float, current_streak: int
    ) -> str:
        if not events:
            return PsychologicalMode.NORMAL.value
        recent_neg = sum(
            1 for e in events[-7:]
            if e.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS
        )
        neg_ratio = recent_neg / 7 if len(events) >= 7 else 0
        if neg_ratio > 0.4 or consistency < 30:
            return PsychologicalMode.SURVIVAL.value
        if consistency >= 70 and current_streak >= 5:
            return PsychologicalMode.STABLE.value
        return PsychologicalMode.NORMAL.value

    @staticmethod
    def calculate_level(consistency: float) -> int:
        thresholds = {5: 90, 4: 75, 3: 55, 2: 35, 1: 15, 0: 0}
        for lvl, threshold in sorted(thresholds.items(), reverse=True):
            if consistency >= threshold:
                return lvl
        return 0

    @staticmethod
    def check_achievements(
        events: List[Dict], total_checkins: int, streak: int,        has_return: bool, unlocked_set: frozenset
    ) -> List[str]:
        unlocked: List[str] = []
        if total_checkins >= 1 and "first_checkin" not in unlocked_set:
            unlocked.append("first_checkin")
        if has_return and "courageous_return" not in unlocked_set:
            unlocked.append("courageous_return")
        if streak >= 7 and "seven_days" not in unlocked_set:
            unlocked.append("seven_days")
        if streak >= 14 and "fourteen_days" not in unlocked_set:
            unlocked.append("fourteen_days")
        recent_neg = sum(
            1 for e in events[-10:]
            if e.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS
        )
        if recent_neg >= 2 and "no_guilt" not in unlocked_set:
            unlocked.append("no_guilt")
        return unlocked

    @classmethod
    def calculate_risk_score(cls, events: List[Dict], now_utc: Optional[datetime] = None) -> float:
        if len(events) < 5:
            return 0.0
        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["risk"]
        risk = 0.0
        for i, event in enumerate(events[:cfg["window_events"]]):
            event_ts = cls._parse_utc(event.get("created_at_utc"))
            days_ago = (now - event_ts).days if event_ts else 0
            weight = 1 - i / cfg["window_events"]
            if days_ago > cfg["absence_threshold_days"]:
                risk += cfg["absence_weight"] * weight
            if event.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS:
                risk += cfg["negative_emotion_weight"] * weight
        return min(100.0, round(risk, 1))

    @classmethod
    def detect_patterns(cls, events: List[Dict]) -> Dict:
        patterns: Dict = {"risky_hours": [], "weekday_tendency": {}, "return_pattern": None}
        if len(events) < 10:
            return patterns
        hour_activity: Dict[int, int] = {h: 0 for h in range(24)}
        for e in events:
            if e.get("event_type") == "checkin":
                ts = cls._parse_utc(e.get("created_at_utc"))
                if ts:
                    hour_activity[ts.hour] += 1
        active = {h: c for h, c in hour_activity.items() if c > 0}
        if active:
            avg = sum(active.values()) / len(active)            ratio = cls.CONFIG["patterns"]["risky_hours_ratio"]
            risky = [h for h, c in active.items() if c < avg * ratio]
            patterns["risky_hours"] = risky or [min(active, key=active.get)]
        weekday: Dict[int, int] = {i: 0 for i in range(7)}
        for e in events:
            ts = cls._parse_utc(e.get("created_at_utc"))
            if ts:
                weekday[ts.weekday()] += 1
        patterns["weekday_tendency"] = weekday
        returns = [e for e in events if e.get("event_type") == "return"]
        if returns:
            patterns["return_pattern"] = {
                "count": len(returns),
                "last_return_utc": returns[-1].get("created_at_utc"),
            }
        return patterns