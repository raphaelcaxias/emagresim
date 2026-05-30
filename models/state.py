from __future__ import annotations
from dataclasses import dataclass, field, asdict, fields as dc_fields
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

SCHEMA_VERSION = "1.0.0"
DEFAULT_TZ = timezone.utc
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


EMOTIONAL_STATES: Dict[str, Dict] = {
    "motivado":  {"icon": "✨", "color": "#00b894", "label": "Motivado",  "weight": 1.0},
    "neutro":    {"icon": "😐", "color": "#636e72", "label": "Neutro",    "weight": 0.7},
    "ansioso":   {"icon": "😰", "color": "#fdcb6e", "label": "Ansioso",   "weight": 0.4},
    "cansado":   {"icon": "😔", "color": "#d63031", "label": "Cansado",   "weight": 0.5},
    "frustrado": {"icon": "😞", "color": "#d63031", "label": "Frustrado", "weight": 0.3},
    "confiante": {"icon": "💪", "color": "#00cec9", "label": "Confiante", "weight": 1.2},
}

LEVELS: Dict[int, Dict] = {
    0: {"name": "Semente",      "icon": "🌱", "min_consistency": 0,  "desc": "Todo começo é válido."},
    1: {"name": "Explorador",   "icon": "🗺️", "min_consistency": 15, "desc": "Descobrindo seu ritmo."},
    2: {"name": "Persistente",  "icon": "🔥", "min_consistency": 35, "desc": "Construindo presença."},
    3: {"name": "Reconstrutor", "icon": "🧱", "min_consistency": 55, "desc": "Recair faz parte. Voltar é força."},
    4: {"name": "Inabalável",   "icon": "⚓", "min_consistency": 75, "desc": "Sua consistência é sua âncora."},
    5: {"name": "Guia",         "icon": "🌟", "min_consistency": 90, "desc": "Você inspira pelo exemplo."},
}

ACHIEVEMENTS: Dict[str, Dict] = {
    "first_checkin":     {"name": "Primeiro Passo",   "icon": "👣", "desc": "Primeiro check-in registrado."},
    "courageous_return": {"name": "Retorno Corajoso", "icon": "🔄", "desc": "Voltou após 3+ dias ausente."},
    "seven_days":        {"name": "Sete Dias",        "icon": "📅", "desc": "Uma semana de presença."},
    "fourteen_days":     {"name": "Quatorze Dias",    "icon": "🌟", "desc": "Duas semanas de presença."},
    "no_guilt":          {"name": "Sem Culpa",        "icon": "🕊️", "desc": "Registrou emoção negativa sem abandonar."},
}


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
        return {
            k: v for k, v in asdict(self).items()
            if k not in _COMPUTED_FIELDS
        }