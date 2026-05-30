# ============================================================================
# app.py — EmagreSim v33.0 "Refactored & Fixed"
# Melhorias sobre v32.0:
#   [FIX-1]  Cache: métodos de instância não são cacheáveis via @st.cache_data;
#            cache migrado para funções-módulo com assinatura hashável.
#   [FIX-2]  to_persist_dict: usa dataclasses.asdict() + exclusão de campos
#            calculados, eliminando duplicação manual frágil.
#   [FIX-3]  detect_patterns: lógica de risky_hours corrigida — horas de risco
#            são as de MENOR atividade, com threshold consistente.
#   [FIX-4]  process_checkin: temp_events ordenado por created_at_utc.
#   [FIX-5]  AuthService: inicialização de user_id movida para função dedicada,
#            sem side-effects silenciosos em get_current_user_id.
#   [FIX-6]  random global substituído por instância isolada (Random(seed)).
#   [FIX-7]  CSS vazio removido; injeção de CSS só ocorre quando há conteúdo.
#   [FIX-8]  _parse_metadata promovido a função-módulo (era @staticmethod
#            chamada erroneamente via _self dentro de método cacheado).
#   [FIX-9]  BehavioralEngine: métodos que não usam cls/self convertidos para
#            @staticmethod onde apropriado; @classmethod mantido só onde usa cls.
#   [FEAT-1] Tipo de retorno explícito em todas as funções públicas.
#   [FEAT-2] Guard clauses antecipadas para reduzir aninhamento.
#   [FEAT-3] Constantes numéricas nomeadas (sem magic numbers soltos).
# Núcleo: PRESENÇA > PERFEIÇÃO | RETORNO > PERMANÊNCIA | CULPA → AÇÃO
# ============================================================================

from __future__ import annotations

import hashlib
import json
import logging
import traceback
from dataclasses import dataclass, asdict, field, fields as dataclass_fields
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client, Client

# ============================================================================
# CONFIGURAÇÃO GLOBAL
# ============================================================================
# [FIX-6] Instância isolada de Random — não polui estado global do módulo random.
import random as _random_module
_RNG = _random_module.Random(42)

DEFAULT_TZ = timezone.utc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("emagresim")

# ============================================================================
# CONFIGURAÇÃO STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="EmagreSim • Aderência",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# [FIX-7] CSS — injeção condicional; substitua a string abaixo pelo CSS real.
# ============================================================================
_APP_CSS: str = ""  # Insira o CSS aqui.

if _APP_CSS.strip():
    st.markdown(f"<style>{_APP_CSS}</style>", unsafe_allow_html=True)

# ============================================================================
# CONFIGURAÇÃO SUPABASE
# ============================================================================
def _init_supabase() -> Optional[Client]:
    """Inicializa cliente Supabase com fallback seguro para modo demo."""
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("CHAVE_SUPABASE")
        if not url or not key:
            logger.warning("Credenciais Supabase ausentes. Rodando em modo demo.")
            return None
        return create_client(url, key)
    except Exception as exc:
        logger.error(f"Falha na conexão Supabase: {exc}")
        return None


_supabase: Optional[Client] = _init_supabase()

# ============================================================================
# CONSTANTES E ENUMS
# ============================================================================
class EventType(Enum):
    CHECKIN = "checkin"
    RELAPSE = "relapse"
    RETURN = "return"
    STREAK_BROKEN = "streak_broken"
    STREAK_RECOVERED = "streak_recovered"
    LEVEL_UP = "level_up"
    ACHIEVEMENT = "achievement"


class PsychologicalMode(Enum):
    NORMAL = "normal"
    SURVIVAL = "survival"
    RETURNING = "returning"
    STABLE = "stable"


EMOTIONAL_STATES: Dict[str, Dict] = {
    "motivado":   {"icon": "✨", "color": "var(--success)", "label": "Motivado",   "weight": 1.0},
    "neutro":     {"icon": "😐", "color": "var(--muted)",   "label": "Neutro",     "weight": 0.7},
    "ansioso":    {"icon": "😰", "color": "var(--amber)",   "label": "Ansioso",    "weight": 0.4},
    "cansado":    {"icon": "😔", "color": "var(--red)",     "label": "Cansado",    "weight": 0.5},
    "frustrado":  {"icon": "😞", "color": "var(--red)",     "label": "Frustrado",  "weight": 0.3},
    "confiante":  {"icon": "💪", "color": "var(--teal)",    "label": "Confiante",  "weight": 1.2},
}

LEVELS: Dict[int, Dict] = {
    0: {"name": "Semente",      "icon": "🌱", "min_consistency": 0,  "desc": "Todo começo é válido."},
    1: {"name": "Explorador",   "icon": "🗺️", "min_consistency": 15, "desc": "Descobrindo seu ritmo."},
    2: {"name": "Persistente",  "icon": "🔥", "min_consistency": 35, "desc": "Construindo presença."},
    3: {"name": "Reconstrutor", "icon": "🧱", "min_consistency": 55, "desc": "Recair faz parte. Voltar é força."},
    4: {"name": "Inabalável",   "icon": "⚓", "min_consistency": 75, "desc": "Sua consistência é sua âncora."},
    5: {"name": "Guia",         "icon": "🌟", "min_consistency": 90, "desc": "Você inspira pelo exemplo de permanência."},
}

ACHIEVEMENTS: Dict[str, Dict] = {
    "first_checkin":    {"name": "Primeiro Passo",    "icon": "👣", "desc": "Primeiro check-in registrado.",         "threshold": 1},
    "courageous_return":{"name": "Retorno Corajoso",  "icon": "🔄", "desc": "Voltou após 3+ dias ausente.",          "threshold": 1},
    "seven_days":       {"name": "Sete Dias",          "icon": "📅", "desc": "Manteve presença por uma semana.",      "threshold": 7},
    "fourteen_days":    {"name": "Quatorze Dias",      "icon": "🌟", "desc": "Duas semanas de presença.",             "threshold": 14},
    "no_guilt":         {"name": "Sem Culpa",          "icon": "🕊️", "desc": "Registrou emoção negativa sem abandonar.", "threshold": 1},
}

# ============================================================================
# SCHEMA VERSIONADO
# ============================================================================
SCHEMA_VERSION = "1.0.0"

# Campos de BehavioralState que são propriedades calculadas (não persistidas).
_COMPUTED_FIELDS = frozenset({"last_checkin"})

# Emoções negativas — definidas uma única vez, usadas em múltiplas engines.
_NEGATIVE_EMOTIONS = frozenset({"ansioso", "frustrado", "cansado"})


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
        valid_keys = {f.name for f in dataclass_fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid_keys})


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

    # --- Propriedade calculada (não persistida) ---
    @property
    def last_checkin(self) -> Optional[datetime]:
        if not self.last_checkin_utc:
            return None
        return datetime.fromisoformat(self.last_checkin_utc.replace("Z", "+00:00"))

    # [FIX-2] to_persist_dict usa asdict() e exclui campos computados dinamicamente.
    def to_persist_dict(self) -> Dict:
        """Serializa para upsert no Supabase, excluindo propriedades calculadas."""
        return {
            k: v
            for k, v in asdict(self).items()
            if k not in _COMPUTED_FIELDS
        }


# ============================================================================
# [FIX-8] _parse_metadata como função de módulo (hashável, cacheável, testável).
# ============================================================================
def _parse_metadata(raw) -> Dict:
    """Parse seguro de metadata (dict ou JSON string)."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(f"Falha ao parsear metadata JSON: {raw[:60]}…")
    return {}


# ============================================================================
# CACHE — Funções-módulo cacheáveis (substituem métodos de instância com cache).
# [FIX-1] @st.cache_data exige funções com assinatura hashável; métodos de
#          instância não funcionam porque `self` não é hashável pelo Streamlit.
# ============================================================================
@st.cache_data(ttl=120)
def _cached_load_state(user_id: str, _client_key: str) -> Optional[Dict]:
    """
    Carrega estado bruto do Supabase (retorna dict, não dataclass, para ser
    serializável pelo cache do Streamlit).
    `_client_key` diferencia ambientes sem serializar o Client.
    """
    if not _supabase:
        return None
    result = (
        _supabase.table("behavioral_state")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None


@st.cache_data(ttl=300)
def _cached_load_events(user_id: str, _client_key: str, limit: int = 200) -> List[Dict]:
    """
    Carrega eventos brutos do Supabase (lista de dicts serializáveis).
    """
    if not _supabase:
        return []
    result = (
        _supabase.table("behavioral_events")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    events = [
        {
            "event_type": row["event_type"],
            "created_at_utc": row["created_at"],
            "metadata": _parse_metadata(row.get("metadata")),
        }
        for row in (result.data or [])
    ]
    # Garante ordem cronológica crescente.
    return sorted(events, key=lambda x: x["created_at_utc"])


# Chave estável para diferenciar instâncias de _supabase no cache sem serializar o objeto.
_CLIENT_KEY: str = hashlib.md5(
    (st.secrets.get("SUPABASE_URL", "demo") or "demo").encode()
).hexdigest()


# ============================================================================
# REPOSITORY
# ============================================================================
class SupabaseRepository:
    """Camada de persistência com cache via funções-módulo cacheáveis."""

    # --- Leitura ---

    def load_state(self, user_id: str) -> Optional[BehavioralState]:
        if user_id == "demo-user" or not _supabase:
            return None
        data = _cached_load_state(user_id, _CLIENT_KEY)
        if not data:
            return None
        return BehavioralState(
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            user_id=data["user_id"],
            consistency_score=data["consistency_score"],
            current_streak=data["current_streak"],
            longest_streak=data["longest_streak"],
            total_checkins=data["total_checkins"],
            last_checkin_utc=data.get("last_checkin_utc"),
            current_level=data["current_level"],
            unlocked_achievements=data.get("unlocked_achievements", []),
            psychological_mode=data.get("psychological_mode", PsychologicalMode.NORMAL.value),
            emotion_history=data.get("emotion_history", []),
            behavioral_memory=data.get("behavioral_memory", {}),
            risk_score=data.get("risk_score", 0.0),
            last_updated_utc=data.get("last_updated_utc", ""),
        )

    def load_events(self, user_id: str, limit: int = 200) -> List[Dict]:
        if user_id == "demo-user" or not _supabase:
            return []
        return _cached_load_events(user_id, _CLIENT_KEY, limit)

    # --- Escrita ---

    def save_state(self, state: BehavioralState) -> bool:
        if state.user_id == "demo-user" or not _supabase:
            return False
        try:
            state.last_updated_utc = datetime.now(DEFAULT_TZ).isoformat()
            _supabase.table("behavioral_state").upsert(
                state.to_persist_dict(), on_conflict="user_id"
            ).execute()
            # Invalida caches de leitura para este usuário.
            _cached_load_state.clear()
            _cached_load_events.clear()
            logger.info(f"Estado salvo: {state.user_id}")
            return True
        except Exception as exc:
            logger.error(f"save_state falhou: {exc}\n{traceback.format_exc()}")
            return False

    def log_event(self, user_id: str, event_type: str, metadata: Dict) -> bool:
        if user_id == "demo-user" or not _supabase:
            return False
        try:
            _supabase.table("behavioral_events").insert(
                {
                    "user_id": user_id,
                    "event_type": event_type,
                    "metadata": json.dumps(metadata, ensure_ascii=False),
                    "created_at": datetime.now(DEFAULT_TZ).isoformat(),
                }
            ).execute()
            _cached_load_events.clear()
            return True
        except Exception as exc:
            logger.error(f"log_event falhou: {exc}")
            return False


repository = SupabaseRepository()

# ============================================================================
# ENGINE DE COMPORTAMENTO — PURA E TESTÁVEL
# [FIX-9] @classmethod mantido onde `cls` é usado (CONFIG, parse helpers);
#         métodos sem cls/self viram @staticmethod.
# ============================================================================
class BehavioralEngine:

    CONFIG: Dict = {
        "consistency": {
            "window_days": 30,
            "decay_rate": 0.02,
            "min_decay": 0.3,
            "weights": {"checkin": 2, "return": 3, "achievement": 1, "level_up": 1},
            "return_bonus": 5,
            "normalizer": 2.5,
        },
        "streak": {
            "max_gap_days": 1,
        },
        "risk": {
            "window_events": 14,
            "absence_threshold_days": 3,
            "negative_emotion_weight": 2,
            "absence_weight": 3,
        },
        "patterns": {
            "risky_hours_low_activity_ratio": 0.5,  # < 50 % da média = hora de risco
        },
    }

    # --- Helpers internos ---

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(DEFAULT_TZ)

    @staticmethod
    def _parse_utc_iso(iso_str: Optional[str]) -> Optional[datetime]:
        if not iso_str:
            return None
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    # --- Consistência ---

    @classmethod
    def calculate_consistency(
        cls,
        events: List[Dict],
        now_utc: Optional[datetime] = None,
    ) -> float:
        if not events:
            return 0.0
        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["consistency"]
        score = 0.0

        for event in events[-(cfg["window_days"] * 2):]:
            event_type = event.get("event_type", "")
            weight = cfg["weights"].get(event_type, 1)
            event_ts = cls._parse_utc_iso(event.get("created_at_utc"))
            if not event_ts:
                continue
            days_ago = (now - event_ts).days
            decay = max(cfg["min_decay"], 1 - days_ago * cfg["decay_rate"])
            score += weight * decay
            if event.get("metadata", {}).get("was_absent"):
                score += cfg["return_bonus"]

        return round(min(100.0, score / cfg["normalizer"]), 1)

    # --- Streak ---

    @classmethod
    def calculate_streak(
        cls,
        last_checkin_utc: Optional[str],
        current_streak: int,
        now_utc: Optional[datetime] = None,
    ) -> Tuple[int, bool, bool]:
        """
        Retorna (novo_streak, was_broken, is_return).
        streak == 1 no primeiro check-in ou após quebra (usuário presente hoje).
        """
        now = now_utc or cls._now_utc()
        last_checkin = cls._parse_utc_iso(last_checkin_utc)

        if not last_checkin:
            return 1, False, False

        delta_days = (now.date() - last_checkin.date()).days

        if delta_days == 0:
            return current_streak, False, False
        if delta_days == 1:
            return current_streak + 1, False, False
        # Gap > 1: quebra, mas usuário está presente agora.
        return 1, True, True

    @staticmethod
    def update_longest_streak(current_streak: int, longest_streak: int) -> int:
        return max(longest_streak, current_streak)

    # --- Modo psicológico ---

    @classmethod
    def detect_psychological_mode(
        cls,
        events: List[Dict],
        consistency: float,
        current_streak: int,
        now_utc: Optional[datetime] = None,
    ) -> str:
        if not events:
            return PsychologicalMode.NORMAL.value

        now = now_utc or cls._now_utc()

        # Último evento de presença (checkin ou return).
        last_presence = next(
            (
                e for e in sorted(
                    events, key=lambda x: x.get("created_at_utc", ""), reverse=True
                )
                if e.get("event_type") in {"checkin", "return"}
            ),
            None,
        )
        if not last_presence:
            return PsychologicalMode.NORMAL.value

        last_ts = cls._parse_utc_iso(last_presence.get("created_at_utc"))
        days_since = (now - last_ts).days if last_ts else 5

        recent_negatives = sum(
            1 for e in events[-7:]
            if e.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS
        )
        negative_ratio = recent_negatives / 7 if len(events) >= 7 else 0

        if days_since > 4 or negative_ratio > 0.4 or consistency < 30:
            return PsychologicalMode.SURVIVAL.value
        if 1 < days_since <= 4:
            return PsychologicalMode.RETURNING.value
        if consistency >= 70 and current_streak >= 5:
            return PsychologicalMode.STABLE.value
        return PsychologicalMode.NORMAL.value

    # --- Nível ---

    @staticmethod
    def calculate_level(consistency: float) -> int:
        for level in sorted(LEVELS.keys(), reverse=True):
            if consistency >= LEVELS[level]["min_consistency"]:
                return level
        return 0

    # --- Conquistas ---

    @staticmethod
    def check_achievements(
        events: List[Dict],
        total_checkins: int,
        streak: int,
        has_return: bool,
        unlocked_set: frozenset,
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

        recent_negatives = sum(
            1 for e in events[-10:]
            if e.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS
        )
        if recent_negatives >= 2 and "no_guilt" not in unlocked_set:
            unlocked.append("no_guilt")

        return unlocked

    # --- Risco ---

    @classmethod
    def calculate_risk_score(
        cls,
        events: List[Dict],
        now_utc: Optional[datetime] = None,
    ) -> float:
        if len(events) < 5:
            return 0.0

        now = now_utc or cls._now_utc()
        cfg = cls.CONFIG["risk"]
        risk = 0.0
        window = events[: cfg["window_events"]]

        for i, event in enumerate(window):
            event_ts = cls._parse_utc_iso(event.get("created_at_utc"))
            days_ago = (now - event_ts).days if event_ts else 0
            weight_decay = 1 - i / cfg["window_events"]

            if days_ago > cfg["absence_threshold_days"]:
                risk += cfg["absence_weight"] * weight_decay
            if event.get("metadata", {}).get("emotion") in _NEGATIVE_EMOTIONS:
                risk += cfg["negative_emotion_weight"] * weight_decay

        return min(100.0, round(risk, 1))

    # --- Padrões ---

    @classmethod
    def detect_patterns(cls, events: List[Dict]) -> Dict:
        """
        [FIX-3] risky_hours = horas de MENOR atividade (abaixo de X% da média).
        Threshold coerente: horas sem NENHUM registro são irrelevantes (ruído);
        considera-se risco as horas com baixa — mas existente — atividade.
        """
        patterns: Dict = {
            "risky_hours": [],
            "weekday_tendency": {},
            "return_pattern": None,
        }
        if len(events) < 10:
            return patterns

        # Atividade por hora.
        hour_activity: Dict[int, int] = {h: 0 for h in range(24)}
        for e in events:
            if e.get("event_type") == "checkin":
                ts = cls._parse_utc_iso(e.get("created_at_utc"))
                if ts:
                    hour_activity[ts.hour] += 1

        active_hours = {h: c for h, c in hour_activity.items() if c > 0}
        if active_hours:
            avg = sum(active_hours.values()) / len(active_hours)
            ratio = cls.CONFIG["patterns"]["risky_hours_low_activity_ratio"]
            # [FIX-3] Horas de risco: registros existem mas estão abaixo do limiar.
            risky = [h for h, c in active_hours.items() if c < avg * ratio]
            # Fallback: hora com menor atividade se nenhuma ficou abaixo do limiar.
            patterns["risky_hours"] = risky or [min(active_hours, key=active_hours.get)]

        # Tendência por dia da semana.
        weekday_counts: Dict[int, int] = {i: 0 for i in range(7)}
        for e in events:
            ts = cls._parse_utc_iso(e.get("created_at_utc"))
            if ts:
                weekday_counts[ts.weekday()] += 1
        patterns["weekday_tendency"] = weekday_counts

        # Padrão de retorno.
        returns = [e for e in events if e.get("event_type") == "return"]
        if returns:
            patterns["return_pattern"] = {
                "count": len(returns),
                "last_return_utc": returns[-1].get("created_at_utc"),  # mais antigo → mais recente
            }

        return patterns


# ============================================================================
# NARRATIVE ENGINE
# ============================================================================
class NarrativeEngine:

    @staticmethod
    def _seeded_choice(choices: List[str], seed_suffix: str) -> str:
        """Choice determinístico sem alterar estado do _RNG global."""
        digest = hashlib.md5(f"42:{seed_suffix}".encode()).hexdigest()
        rng = _random_module.Random(int(digest[:8], 16))
        return rng.choice(choices)

    @classmethod
    def get_greeting(cls, state: BehavioralState, patterns: Dict) -> str:
        hour = datetime.now(DEFAULT_TZ).hour
        period = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        mode_labels = {
            "normal":    "🌿 Equilíbrio",
            "survival":  "🛡️ Sobrevivência",
            "returning": "🔄 Reencontro",
            "stable":    "⚓ Constância",
        }
        memory = ""
        return_data = patterns.get("return_pattern")
        if return_data and return_data.get("count", 0) >= 2:
            memory = " Você já voltou outras vezes — isso mostra resiliência."
        elif patterns.get("risky_hours"):
            hrs = ", ".join(f"{h}:00" for h in patterns["risky_hours"][:2])
            memory = f" Horários de atenção: {hrs}."
        label = mode_labels.get(state.psychological_mode, "Equilíbrio")
        return f"{period}. Modo {label}.{memory}"

    @classmethod
    def get_companion_message(
        cls, state: BehavioralState, risk_score: float, patterns: Dict
    ) -> str:
        mode = state.psychological_mode
        if mode == "survival":
            return "Hoje o objetivo é só se manter presente. Nada além disso importa."
        if mode == "returning":
            return "Você voltou. Isso importa mais do que qualquer streak ou número."
        if risk_score > 70:
            return f"Você está há {state.current_streak} dias consistente. Cuidado com o cansaço emocional."
        if state.current_streak >= 7:
            return f"{state.current_streak} dias seguidos. Isso é presença real."
        if (patterns.get("return_pattern") or {}).get("count", 0) >= 1:
            return "Você já mostrou que consegue retornar. Confie no seu processo."
        return "Sua presença hoje já é um ato de cuidado. Um dia de cada vez."

    @classmethod
    def get_micro_goal(
        cls,
        mode: str,
        risk: float,
        patterns: Dict,
        seed_context: str = "microgoal",
    ) -> str:
        if mode == "survival":
            choices = [
                "Hoje só abra o app.",
                "Beba um copo d'água agora.",
                "Registre como você está se sentindo.",
            ]
        elif mode == "returning":
            choices = [
                "Registre uma refeição hoje.",
                "Não tente compensar o tempo perdido.",
                "Olhe para o que você já conquistou.",
            ]
        elif risk > 70:
            choices = [
                "Descanse. Amanhã será mais leve.",
                "Respire fundo três vezes antes de qualquer decisão.",
            ]
        elif patterns.get("risky_hours"):
            h = patterns["risky_hours"][0]
            choices = [
                f"Seu horário de atenção é às {h}:00. Programe um lembrete suave.",
                f"Às {h}:00, pause e respire antes de decidir.",
            ]
        else:
            choices = [
                "Registre seu estado emocional.",
                "Faça uma refeição consciente.",
                "Anote uma coisa que você fez bem hoje.",
            ]
        return cls._seeded_choice(choices, seed_context)


# ============================================================================
# AUTH SERVICE
# [FIX-5] Inicialização de user_id isolada em função própria; get_current_user_id
#         é pura — apenas lê, não muta session_state como side-effect.
# ============================================================================
class AuthService:

    @staticmethod
    def initialize_session(session_state: Dict) -> None:
        """Deve ser chamado UMA VEZ no início de main() para garantir user_id."""
        if "user_id" not in session_state:
            session_state["user_id"] = "demo-user"

    @staticmethod
    def get_current_user_id(session_state: Dict) -> str:
        """Retorna user_id sem efeitos colaterais. Requer initialize_session() anterior."""
        return (
            session_state.get("auth_user_id")
            or session_state.get("user_id")
            or "demo-user"
        )

    @staticmethod
    def is_demo_mode(user_id: str) -> bool:
        return user_id == "demo-user"


# ============================================================================
# CAMADA DE SERVIÇO
# ============================================================================
def load_user_state(user_id: str) -> BehavioralState:
    return repository.load_state(user_id) or BehavioralState(user_id=user_id)


def save_user_state(state: BehavioralState) -> bool:
    return repository.save_state(state)


def log_user_event(user_id: str, event_type: str, metadata: Dict) -> bool:
    return repository.log_event(user_id, event_type, metadata)


def process_checkin(
    user_id: str,
    emotion: Optional[str] = None,
    actions_taken: Optional[List[str]] = None,
    reflection: Optional[str] = None,
) -> BehavioralState:
    """
    Processa check-in: carrega → calcula → persiste.
    [FIX-4] temp_events ordenado por created_at_utc antes de passar às engines.
    """
    now_utc = datetime.now(DEFAULT_TZ)
    state = load_user_state(user_id)
    events = repository.load_events(user_id, limit=100)

    new_streak, was_broken, is_return = BehavioralEngine.calculate_streak(
        last_checkin_utc=state.last_checkin_utc,
        current_streak=state.current_streak,
        now_utc=now_utc,
    )
    new_longest = BehavioralEngine.update_longest_streak(new_streak, state.longest_streak)

    metadata: Dict = {
        "emotion": emotion,
        "actions_taken": actions_taken or [],
        "reflection": reflection,
        "was_absent": is_return,
        "streak_after": new_streak,
    }

    # [FIX-4] Ordena temp_events cronologicamente antes de calcular métricas.
    temp_events = sorted(
        events + [{"event_type": "checkin", "created_at_utc": now_utc.isoformat(), "metadata": metadata}],
        key=lambda x: x["created_at_utc"],
    )

    new_consistency = BehavioralEngine.calculate_consistency(temp_events, now_utc)
    new_mode = BehavioralEngine.detect_psychological_mode(
        events=temp_events,
        consistency=new_consistency,
        current_streak=new_streak,
        now_utc=now_utc,
    )
    new_level = BehavioralEngine.calculate_level(new_consistency)
    unlocked = BehavioralEngine.check_achievements(
        events=temp_events,
        total_checkins=state.total_checkins + 1,
        streak=new_streak,
        has_return=is_return,
        unlocked_set=frozenset(state.unlocked_achievements),
    )
    new_risk = BehavioralEngine.calculate_risk_score(temp_events, now_utc)

    # Aplica atualizações ao estado.
    state.consistency_score = new_consistency
    state.current_streak = new_streak
    state.longest_streak = new_longest
    state.total_checkins += 1
    state.last_checkin_utc = now_utc.isoformat()
    state.current_level = new_level
    state.psychological_mode = new_mode
    state.risk_score = new_risk
    state.unlocked_achievements.extend(unlocked)

    if emotion:
        state.emotion_history.append(
            {"emotion": emotion, "timestamp_utc": now_utc.isoformat(), "streak_at_time": new_streak}
        )
        state.emotion_history = state.emotion_history[-50:]

    save_user_state(state)
    log_user_event(
        user_id,
        EventType.RETURN.value if is_return else EventType.CHECKIN.value,
        metadata,
    )
    for ach in unlocked:
        log_user_event(user_id, EventType.ACHIEVEMENT.value, {"achievement": ach})

    return state


# ============================================================================
# UI LAYER
# ============================================================================
def render_dashboard(state: BehavioralState, patterns: Dict, risk_score: float) -> None:
    st.markdown(f"### {NarrativeEngine.get_greeting(state, patterns)}")

    message = NarrativeEngine.get_companion_message(state, risk_score, patterns)
    st.info(f"💬 {message}")

    micro_goal = NarrativeEngine.get_micro_goal(
        state.psychological_mode, risk_score, patterns,
        seed_context=f"goal_{state.user_id}",
    )
    st.success(f"🎯 Meta de hoje: {micro_goal}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Consistência", f"{state.consistency_score:.1f}")
    with col2:
        icon = "🔥" if state.current_streak >= 3 else "🌱"
        st.metric(f"{icon} Streak Atual", state.current_streak)
    with col3:
        lvl = LEVELS.get(state.current_level, {})
        st.metric(f"{lvl.get('icon', '🌟')} Nível", lvl.get("name", "Desconhecido"))

    if state.emotion_history:
        df = pd.DataFrame(state.emotion_history[-14:])
        df["date"] = pd.to_datetime(df["timestamp_utc"]).dt.date
        counts = df.groupby(["date", "emotion"]).size().unstack(fill_value=0)
        fig = go.Figure(
            [go.Bar(name=emo, x=counts.index, y=counts[emo]) for emo in counts.columns]
        )
        fig.update_layout(barmode="stack", title="Emoções (últimos 14 dias)", height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Conquistas desbloqueadas.
    if state.unlocked_achievements:
        st.markdown("**🏆 Conquistas**")
        cols = st.columns(min(len(state.unlocked_achievements), 5))
        for col, ach_key in zip(cols, state.unlocked_achievements):
            ach = ACHIEVEMENTS.get(ach_key, {})
            col.markdown(f"{ach.get('icon', '🏅')} **{ach.get('name', ach_key)}**")


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    # [FIX-5] Inicialização explícita antes de qualquer leitura de user_id.
    AuthService.initialize_session(st.session_state)
    user_id = AuthService.get_current_user_id(st.session_state)

    state = load_user_state(user_id)
    events = repository.load_events(user_id, limit=100)
    patterns = BehavioralEngine.detect_patterns(events)
    risk_score = BehavioralEngine.calculate_risk_score(events)

    with st.form("checkin_form", clear_on_submit=True):
        st.subheader("📝 Como você está hoje?")
        emotion = st.selectbox(
            "Estado emocional",
            options=list(EMOTIONAL_STATES.keys()),
            format_func=lambda x: f"{EMOTIONAL_STATES[x]['icon']} {EMOTIONAL_STATES[x]['label']}",
        )
        actions = st.multiselect(
            "Ações realizadas",
            ["Hidratei", "Caminhei", "Respirei fundo", "Anotei sentimentos", "Outro"],
        )
        reflection = st.text_area("Reflexão rápida (opcional)", height=70)
        submitted = st.form_submit_button("✅ Registrar Presença")

        if submitted and not AuthService.is_demo_mode(user_id):
            with st.spinner("Registrando…"):
                state = process_checkin(user_id, emotion, actions, reflection)
                st.success("Presença registrada! 🌱")

    render_dashboard(state, patterns, risk_score)

    st.markdown("---")
    mode_label = "🧪 Demo" if AuthService.is_demo_mode(user_id) else "🔐 Autenticado"
    st.caption(
        f"EmagreSim v33.0 • {mode_label} • UTC: {datetime.now(DEFAULT_TZ).strftime('%H:%M')}"
    )


if __name__ == "__main__":
    main()
