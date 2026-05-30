from __future__ import annotations
from dataclasses import dataclass, field, asdict, fields as dc_fields
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set

SCHEMA_VERSION = "1.0.0"
DEFAULT_TZ = timezone.utc

# Campos calculados (não persistem no banco)
_COMPUTED_FIELDS = frozenset({"last_checkin"})
_NEGATIVE_EMOTIONS = frozenset({"ansioso", "frustrado", "cansado"})


class PsychologicalMode(Enum):
    NORMAL = "normal"
    SURVIVAL = "survival"
    RETURNING = "returning"
    STABLE = "stable"


class EventType(Enum):
    CHECKIN = "checkin"
    RELAPSE = "relapse"
    RETURN = "return"
    STREAK_BROKEN = "streak_broken"
    LEVEL_UP = "level_up"
    ACHIEVEMENT = "achievement"


@dataclass
class PsychologicalOnboarding:
    emotional_goal: Optional[str] = None
    trigger_times: List[int] = field(default_factory=list)
    difficult_patterns: List[str] = field(default_factory=list)
    guilt_relationship: str = "neutral"
    abandonment_history: bool = False
    preferred_support_style: str = "gentle"

    @classmethod
    def from_dict(cls, data: dict) -> "PsychologicalOnboarding":
        valid = {f.name for f in dc_fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid})


@dataclass
class BehavioralState:
    """Estado comportamental do usuário - serializável para Supabase."""
    schema_version: str = SCHEMA_VERSION
    user_id: str = ""
    consistency_score: float = 0.0
    current_streak: int = 0
    longest_streak: int = 0
    total_checkins: int = 0
    last_checkin_utc: Optional[str] = None
    current_level: int = 0
    unlocked_achievements: List[str] = field(default_factory=list)
    psychological_mode: str = PsychologicalMode.NORMAL.value
    emotion_history: List[Dict] = field(default_factory=list)
    behavioral_memory: Dict = field(default_factory=dict)
    risk_score: float = 0.0
    last_updated_utc: str = field(
        default_factory=lambda: datetime.now(DEFAULT_TZ).isoformat()
    )

    @property
    def last_checkin(self) -> Optional[datetime]:
        if not self.last_checkin_utc:
            return None
        return datetime.fromisoformat(self.last_checkin_utc.replace("Z", "+00:00"))

    def to_persist_dict(self) -> Dict:
        """Serializa excluindo campos calculados."""
        return {
            k: v for k, v in asdict(self).items()
            if k not in _COMPUTED_FIELDS
        }