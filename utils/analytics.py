from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

from models.state import BehavioralState, PsychologicalMode, _NEGATIVE_EMOTIONS

DEFAULT_TZ = timezone.utc


class BehavioralEngine:
    """Engine pura para cálculos comportamentais - sem side effects."""

    CONFIG: Dict = {
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
            "risky_hours_ratio": 0.5,  # <50% da média = hora de risco
        },
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
    def calculate_consistency(
        cls, events: List[Dict], now_utc: Optional[datetime] = None
    ) -> float:
        if not events:
            return 0.0        now = now_utc or cls._now_utc()
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

        return round(min(100.0, score / cfg["normalizer"]), 1)

    @classmethod
    def calculate_streak(
        cls,
        last_checkin_utc: Optional[str],
        current_streak: int,
        now_utc: Optional[datetime] = None,
    ) -> Tuple[int, bool, bool]:
        """Retorna (novo_streak, was_broken, is_return)."""
        now = now_utc or cls._now_utc()
        last = cls._parse_utc(last_checkin_utc)

        if not last:
            return 1, False, False

        delta = (now.date() - last.date()).days
        if delta == 0:
            return current_streak, False, False
        if delta == 1:
            return current_streak + 1, False, False
        return 1, True, True  # Quebrou, mas usuário está presente

    @staticmethod
    def detect_psychological_mode(
        events: List[Dict], consistency: float, current_streak: int
    ) -> str:
        if not events:
            return PsychologicalMode.NORMAL.value

        recent_neg = sum(
            1 for e in events[-7:]
            if e.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS
        )        neg_ratio = recent_neg / 7 if len(events) >= 7 else 0

        if neg_ratio > 0.4 or consistency < 30:
            return PsychologicalMode.SURVIVAL.value
        if consistency >= 70 and current_streak >= 5:
            return PsychologicalMode.STABLE.value
        return PsychologicalMode.NORMAL.value

    @staticmethod
    def calculate_level(consistency: float) -> int:
        LEVELS = {
            0: 0, 1: 15, 2: 35, 3: 55, 4: 75, 5: 90
        }
        for lvl in sorted(LEVELS.keys(), reverse=True):
            if consistency >= LEVELS[lvl]:
                return lvl
        return 0

    @classmethod
    def calculate_risk_score(
        cls, events: List[Dict], now_utc: Optional[datetime] = None
    ) -> float:
        if len(events) < 5:
            return 0.0
        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["risk"]
        risk = 0.0

        for i, event in enumerate(events[: cfg["window_events"]]):
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
        patterns = {"risky_hours": [], "weekday_tendency": {}, "return_pattern": None}
        if len(events) < 10:
            return patterns

        hour_activity = {h: 0 for h in range(24)}
        for e in events:
            if e.get("event_type") == "checkin":
                ts = cls._parse_utc(e.get("created_at_utc"))                if ts:
                    hour_activity[ts.hour] += 1

        active = {h: c for h, c in hour_activity.items() if c > 0}
        if active:
            avg = sum(active.values()) / len(active)
            ratio = cls.CONFIG["patterns"]["risky_hours_ratio"]
            risky = [h for h, c in active.items() if c < avg * ratio]
            patterns["risky_hours"] = risky or [min(active, key=active.get)]

        weekday = {i: 0 for i in range(7)}
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