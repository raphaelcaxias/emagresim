from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

from models.state import PsychologicalMode, _NEGATIVE_EMOTIONS

DEFAULT_TZ = timezone.utc


class BehavioralEngine:

    CONFIG = {
        "consistency": {
            "window_days": 30,
            "decay_rate": 0.02,
            "min_decay": 0.3,
            "weights": {"checkin": 2, "return": 3, "achievement": 1},
            "return_bonus": 5,
            "normalizer": 2.5,
        },
        "risk": {
            "window_events": 14,
            "absence_threshold_days": 3,
            "negative_emotion_weight": 2,
            "absence_weight": 3,
        },
        "patterns": {
            "risky_hours_ratio": 0.5,
        },
    }

    @staticmethod
    def _now_utc():
        return datetime.now(DEFAULT_TZ)

    @staticmethod
    def _parse_utc(iso):
        if not iso:
            return None
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))

    @classmethod
    def calculate_consistency(cls, events, now_utc=None):
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

            if event.get("metadata", {}).get("was_absent"):
                score += cfg["return_bonus"]

        result = score / cfg["normalizer"]
        return round(min(100.0, result), 1)

    @classmethod
    def calculate_streak(cls, last_checkin_utc, current_streak, now_utc=None):
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
    def update_longest_streak(current, longest):
        return max(longest, current)

    @classmethod
    def detect_psychological_mode(cls, events, consistency, current_streak):
        if not events:
            return PsychologicalMode.NORMAL.value

        recent_neg = 0
        for e in events[-7:]:
            emotion = e.get("metadata", {}).get("emotion")
            if emotion in _NEGATIVE_EMOTIONS:                recent_neg += 1

        neg_ratio = recent_neg / 7 if len(events) >= 7 else 0

        if neg_ratio > 0.4 or consistency < 30:
            return PsychologicalMode.SURVIVAL.value

        if consistency >= 70 and current_streak >= 5:
            return PsychologicalMode.STABLE.value

        return PsychologicalMode.NORMAL.value

    @staticmethod
    def calculate_level(consistency):
        thresholds = {5: 90, 4: 75, 3: 55, 2: 35, 1: 15, 0: 0}
        for lvl in sorted(thresholds.keys(), reverse=True):
            if consistency >= thresholds[lvl]:
                return lvl
        return 0

    @staticmethod
    def check_achievements(events, total_checkins, streak, has_return, unlocked_set):
        unlocked = []

        if total_checkins >= 1 and "first_checkin" not in unlocked_set:
            unlocked.append("first_checkin")

        if has_return and "courageous_return" not in unlocked_set:
            unlocked.append("courageous_return")

        if streak >= 7 and "seven_days" not in unlocked_set:
            unlocked.append("seven_days")

        if streak >= 14 and "fourteen_days" not in unlocked_set:
            unlocked.append("fourteen_days")

        recent_neg = 0
        for e in events[-10:]:
            emotion = e.get("metadata", {}).get("emotion")
            if emotion in _NEGATIVE_EMOTIONS:
                recent_neg += 1

        if recent_neg >= 2 and "no_guilt" not in unlocked_set:
            unlocked.append("no_guilt")

        return unlocked

    @classmethod
    def calculate_risk_score(cls, events, now_utc=None):
        if len(events) < 5:            return 0.0

        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["risk"]
        risk = 0.0

        for i, event in enumerate(events[:cfg["window_events"]]):
            event_ts = cls._parse_utc(event.get("created_at_utc"))
            days_ago = (now - event_ts).days if event_ts else 0
            weight = 1 - i / cfg["window_events"]

            if days_ago > cfg["absence_threshold_days"]:
                risk += cfg["absence_weight"] * weight

            emotion = event.get("metadata", {}).get("emotion")
            if emotion in _NEGATIVE_EMOTIONS:
                risk += cfg["negative_emotion_weight"] * weight

        return min(100.0, round(risk, 1))

    @classmethod
    def detect_patterns(cls, events):
        patterns = {
            "risky_hours": [],
            "weekday_tendency": {},
            "return_pattern": None,
        }

        if len(events) < 10:
            return patterns

        hour_activity = {}
        for h in range(24):
            hour_activity[h] = 0

        for e in events:
            if e.get("event_type") == "checkin":
                ts = cls._parse_utc(e.get("created_at_utc"))
                if ts:
                    hour_activity[ts.hour] += 1

        active = {}
        for h, c in hour_activity.items():
            if c > 0:
                active[h] = c

        if active:
            avg = sum(active.values()) / len(active)
            ratio = cls.CONFIG["patterns"]["risky_hours_ratio"]
            risky = []            for h, c in active.items():
                if c < avg * ratio:
                    risky.append(h)

            if risky:
                patterns["risky_hours"] = risky
            else:
                min_hour = min(active, key=active.get)
                patterns["risky_hours"] = [min_hour]

        weekday = {}
        for i in range(7):
            weekday[i] = 0

        for e in events:
            ts = cls._parse_utc(e.get("created_at_utc"))
            if ts:
                weekday[ts.weekday()] += 1

        patterns["weekday_tendency"] = weekday

        returns = []
        for e in events:
            if e.get("event_type") == "return":
                returns.append(e)

        if returns:
            patterns["return_pattern"] = {
                "count": len(returns),
                "last_return_utc": returns[-1].get("created_at_utc"),
            }

        return patterns