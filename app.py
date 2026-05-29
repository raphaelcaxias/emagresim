import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
import random
import json
import logging
import traceback
import hashlib
from typing import Optional, Dict, List, Tuple, Protocol, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum
from supabase import create_client, Client

# ============================================================================
# CONFIGURAÇÃO GLOBAL & LOGGING
# ============================================================================
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
DEFAULT_TZ = timezone.utc

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("emagresim")

# ============================================================================
# CONFIGURAÇÃO STREAMLIT (LAYOUT COMPACTO & CLEAN)
# ============================================================================
st.set_page_config(
    page_title="EmagreSim • Aderência",
    page_icon="🌱",
    layout="centered", # Mudado para centered para criar foco e intimidade de app mobile
    initial_sidebar_state="collapsed",
)

# INJEÇÃO DE CSS AVANÇADO (Visual Minimalista, Foco em Psicologia e Acolhimento)
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    /* Remover blocos e paddings excessivos do Streamlit */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 760px !important;
    }
    
    /* Card de Acolhimento Humano */
    .narrative-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .narrative-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #14532d;
        margin-bottom: 8px;
    }
    .narrative-text {
        font-size: 1rem;
        color: #166534;
        line-height: 1.5;
    }
    
    /* Grid de Métricas em Estilo Bento-Box */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .bento-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .bento-val {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .bento-lbl {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Customização Discreta do Form de Check-in */
    [data-testid="stForm"] {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02) !important;
    }
    
    /* Esconder elementos poluentes nativos do Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================================
# CONFIGURAÇÃO SUPABASE
# ============================================================================
def get_supabase() -> Optional[Client]:
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("CHAVE_SUPABASE")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
        return None

supabase: Optional[Client] = get_supabase()

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

EMOTIONAL_STATES = {
    "motivado": {"icon": "✨", "color": "#22c55e", "label": "Motivado"}, # Cores hexadecimais explícitas para o Plotly
    "neutro": {"icon": "😐", "color": "#94a3b8", "label": "Neutro"},
    "ansioso": {"icon": "😰", "color": "#f59e0b", "label": "Ansioso"},
    "cansado": {"icon": "😔", "color": "#ef4444", "label": "Cansado"},
    "frustrado": {"icon": "😞", "color": "#b91c1c", "label": "Frustrado"},
    "confiante": {"icon": "💪", "color": "#0d9488", "label": "Confiante"},
}

LEVELS = {
    0: {"name": "Semente", "icon": "🌱", "min_consistency": 0, "desc": "Todo começo é válido."},
    1: {"name": "Explorador", "icon": "🗺️", "min_consistency": 15, "desc": "Descobrindo seu ritmo."},
    2: {"name": "Persistente", "icon": "🔥", "min_consistency": 35, "desc": "Construindo presença."},
    3: {"name": "Reconstrutor", "icon": "🧱", "min_consistency": 55, "desc": "Recair faz parte. Voltar é força."},
    4: {"name": "Inabalável", "icon": "⚓", "min_consistency": 75, "desc": "Sua consistência é sua âncora."},
    5: {"name": "Guia", "icon": "🌟", "min_consistency": 90, "desc": "Você inspira pelo exemplo de permanência."},
}

SCHEMA_VERSION = "1.0.0"

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
    last_updated_utc: str = field(default_factory=lambda: datetime.now(DEFAULT_TZ).isoformat())
    
    @property
    def last_checkin(self) -> Optional[datetime]:
        if not self.last_checkin_utc:
            return None
        return datetime.fromisoformat(self.last_checkin_utc.replace('Z', '+00:00'))
    
    def to_persist_dict(self) -> Dict:
        return {
            "schema_version": self.schema_version,
            "user_id": self.user_id,
            "consistency_score": self.consistency_score,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "total_checkins": self.total_checkins,
            "last_checkin_utc": self.last_checkin_utc,
            "current_level": self.current_level,
            "unlocked_achievements": self.unlocked_achievements,
            "psychological_mode": self.psychological_mode,
            "emotion_history": self.emotion_history,
            "behavioral_memory": self.behavioral_memory,
            "risk_score": self.risk_score,
            "last_updated_utc": self.last_updated_utc,
        }

# ============================================================================
# REPOSITORY PATTERN
# ============================================================================
@runtime_checkable
class StateRepository(Protocol):
    def load_state(self, user_id: str) -> Optional[BehavioralState]: ...
    def save_state(self, state: BehavioralState) -> bool: ...
    def log_event(self, user_id: str, event_type: str, metadata: Dict) -> bool: ...
    def load_events(self, user_id: str, limit: int = 200) -> List[Dict]: ...

class SupabaseRepository:
    def __init__(self, client: Optional[Client], use_cache: bool = True):
        self.client = client
        self.use_cache = use_cache
    
    @staticmethod
    def _parse_metadata(raw: any) -> Dict:
        if isinstance(raw, dict): return raw
        if isinstance(raw, str):
            try: return json.loads(raw)
            except json.JSONDecodeError: return {}
        return {}
    
    @st.cache_data(ttl=300)
    def _cached_events(_self, user_id: str, cache_key: str, limit: int = 200) -> List[Dict]:
        if not _self.client: return []
        result = _self.client.table("behavioral_events").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        events = []
        for row in result.data or []:
            events.append({
                "event_type": row["event_type"],
                "created_at_utc": row["created_at"],
                "metadata": _self._parse_metadata(row.get("metadata")),
            })
        return sorted(events, key=lambda x: x["created_at_utc"])
    
    def load_events(self, user_id: str, limit: int = 200) -> List[Dict]:
        if user_id == "demo-user" or not self.client: return []
        cache_key = hashlib.md5(f"{user_id}:{limit}".encode()).hexdigest()
        return self._cached_events(self, user_id, cache_key, limit)
    
    @st.cache_data(ttl=120)
    def _cached_state(_self, user_id: str, cache_key: str) -> Optional[BehavioralState]:
        if not _self.client: return None
        result = _self.client.table("behavioral_state").select("*").eq("user_id", user_id).execute()
        if not result.data: return None
        data = result.data[0]
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
            last_updated_utc=data.get("last_updated_utc"),
        )
    
    def load_state(self, user_id: str) -> Optional[BehavioralState]:
        if user_id == "demo-user" or not self.client: return None
        cache_key = hashlib.md5(f"{user_id}:state".encode()).hexdigest()
        return self._cached_state(self, user_id, cache_key)
    
    def save_state(self, state: BehavioralState) -> bool:
        if state.user_id == "demo-user" or not self.client: return False
        try:
            state.last_updated_utc = datetime.now(DEFAULT_TZ).isoformat()
            self.client.table("behavioral_state").upsert(
                state.to_persist_dict(), 
                on_conflict="user_id"
            ).execute()
            if self.use_cache:
                self._cached_state.clear(self, state.user_id, hashlib.md5(f"{state.user_id}:state".encode()).hexdigest())
            return True
        except Exception as e:
            logger.error(f"save_state failed: {e}\n{traceback.format_exc()}")
            return False
    
    def log_event(self, user_id: str, event_type: str, metadata: Dict) -> bool:
        if user_id == "demo-user" or not self.client: return False
        try:
            self.client.table("behavioral_events").insert({
                "user_id": user_id,
                "event_type": event_type,
                "metadata": json.dumps(metadata, ensure_ascii=False),
                "created_at": datetime.now(DEFAULT_TZ).isoformat(),
            }).execute()
            if self.use_cache:
                cache_key = hashlib.md5(f"{user_id}:200".encode()).hexdigest()
                self._cached_events.clear(self, user_id, cache_key, 200)
            return True
        except Exception as e:
            logger.error(f"log_event failed: {e}")
            return False

repository: StateRepository = SupabaseRepository(supabase)

# ============================================================================
# ENGINE DE COMPORTAMENTO
# ============================================================================
class BehavioralEngine:
    CONFIG = {
        "consistency": {
            "window_days": 30,
            "decay_rate": 0.02,
            "min_decay": 0.3,
            "weights": {"checkin": 2, "return": 3, "achievement": 1, "level_up": 1},
            "return_bonus": 5,
            "normalizer": 2.5,
        },
        "streak": {"max_gap_days": 1},
        "risk": {
            "window_events": 14,
            "absence_threshold_days": 3,
            "negative_emotion_weight": 2,
            "absence_weight": 3,
        }
    }
    
    @staticmethod
    def _now_utc() -> datetime: return datetime.now(DEFAULT_TZ)
    
    @staticmethod
    def _parse_utc_iso(iso_str: Optional[str]) -> Optional[datetime]:
        if not iso_str: return None
        return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    
    @classmethod
    def calculate_consistency(cls, events: List[Dict], now_utc: Optional[datetime] = None) -> float:
        if not events: return 0.0
        now = now_utc or cls._now_utc()
        score = 0.0
        cfg = cls.CONFIG["consistency"]
        
        for event in events[-cfg["window_days"]*2:]:
            event_type = event.get("event_type")
            weight = cfg["weights"].get(event_type, 1)
            event_ts = cls._parse_utc_iso(event.get("created_at_utc"))
            if not event_ts: continue
                
            days_ago = (now - event_ts).days
            decay = max(cfg["min_decay"], 1 - (days_ago * cfg["decay_rate"]))
            score += weight * decay
            if event.get("metadata", {}).get("was_absent"):
                score += cfg["return_bonus"]
        
        return round(min(100.0, score / cfg["normalizer"]), 1)
    
    @classmethod
    def calculate_streak(cls, last_checkin_utc: Optional[str], current_streak: int, now_utc: Optional[datetime] = None) -> Tuple[int, bool, bool]:
        now = now_utc or cls._now_utc()
        last_checkin = cls._parse_utc_iso(last_checkin_utc)
        if not last_checkin: return 1, False, False
        
        delta_days = (now.date() - last_checkin.date()).days
        if delta_days == 0: return current_streak, False, False
        elif delta_days == 1: return current_streak + 1, False, False
        else: return 1, True, True
    
    @classmethod
    def detect_psychological_mode(cls, events: List[Dict], consistency: float, current_streak: int, now_utc: Optional[datetime] = None) -> str:
        if not events: return PsychologicalMode.NORMAL.value
        now = now_utc or cls._now_utc()
        
        last_event = next((e for e in sorted(events, key=lambda x: x.get("created_at_utc", ""), reverse=True) if e.get("event_type") in ["checkin", "return"]), None)
        days_since = (now - cls._parse_utc_iso(last_event.get("created_at_utc"))).days if last_event else 5
        
        negative_emotions = {"ansioso", "frustrado", "cansado"}
        recent_negatives = sum(1 for e in events[-7:] if e.get("metadata", {}).get("emotion") in negative_emotions)
        negative_ratio = recent_negatives / 7 if len(events) >= 7 else 0
        
        if days_since > 4 or negative_ratio > 0.4 or consistency < 30: return PsychologicalMode.SURVIVAL.value
        if 1 < days_since <= 4: return PsychologicalMode.RETURNING.value
        if consistency >= 70 and current_streak >= 5: return PsychologicalMode.STABLE.value
        return PsychologicalMode.NORMAL.value
    
    @staticmethod
    def calculate_level(consistency: float) -> int:
        for level in sorted(LEVELS.keys(), reverse=True):
            if consistency >= LEVELS[level]["min_consistency"]: return level
        return 0
    
    @classmethod
    def calculate_risk_score(cls, events: List[Dict], now_utc: Optional[datetime] = None) -> float:
        if len(events) < 5: return 0.0
        now = now_utc or cls._now_utc()
        risk = 0.0
        cfg = cls.CONFIG["risk"]
        negative_emotions = {"ansioso", "frustrado", "cansado"}
        
        for i, event in enumerate(events[:cfg["window_events"]]):
            event_ts = cls._parse_utc_iso(event.get("created_at_utc"))
            days_ago = (now - event_ts).days if event_ts else 0
            weight_decay = 1 - (i / cfg["window_events"])
            
            if days_ago > cfg["absence_threshold_days"]: risk += cfg["absence_weight"] * weight_decay
            if event.get("metadata", {}).get("emotion") in negative_emotions: risk += cfg["negative_emotion_weight"] * weight_decay
        
        return min(100.0, round(risk, 1))

    @classmethod
    def detect_patterns(cls, events: List[Dict]) -> Dict:
        patterns = {"risky_hours": [], "weekday_tendency": {}, "return_pattern": None}
        if len(events) < 10: return patterns
        
        hour_activity = {h: 0 for h in range(24)}
        weekday_counts = {i: 0 for i in range(7)}
        returns = []
        
        for e in events:
            event_ts = cls._parse_utc_iso(e.get("created_at_utc"))
            if not event_ts: continue
            if e.get("event_type") == "checkin":
                hour_activity[event_ts.hour] += 1
            weekday_counts[event_ts.weekday()] += 1
            if e.get("event_type") == "return":
                returns.append(e)
                
        if any(hour_activity.values()):
            avg = sum(hour_activity.values()) / 24
            patterns["risky_hours"] = [h for h, c in hour_activity.items() if c < avg * 0.5 and c > 0] or [min(hour_activity, key=hour_activity.get)]
        
        patterns["weekday_tendency"] = weekday_counts
        if returns:
            patterns["return_pattern"] = {"count": len(returns), "last_return_utc": returns[0].get("created_at_utc")}
        return patterns

# ============================================================================
# NARRATIVE ENGINE
# ============================================================================
class NarrativeEngine:
    @staticmethod
    def _get_random_choice(choices: List[str], seed_suffix: str = "") -> str:
        local_seed = hashlib.md5(f"{RANDOM_SEED}:{seed_suffix}".encode()).hexdigest()
        rng = random.Random(int(local_seed[:8], 16))
        return rng.choice(choices)
    
    @classmethod
    def get_greeting(cls, state: BehavioralState, patterns: Dict) -> str:
        hour = datetime.now(DEFAULT_TZ).hour
        base = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        mode_names = {"normal": "🌿 Equilíbrio", "survival": "🛡️ Sobrevivência", "returning": "🔄 Reencontro", "stable": "⚓ Constância"}
        
        memory_line = ""
        return_data = patterns.get("return_pattern")
        if return_data and return_data.get("count", 0) >= 2:
            memory_line = " Você já voltou outras vezes. Isso mostra resiliência real."
        elif patterns.get("risky_hours"):
            hours_str = ", ".join(f"{h}:00" for h in patterns["risky_hours"][:2])
            memory_line = f" Seu padrão indica atenção por volta de: {hours_str}."
        
        return f"{base}. Modo atual: {mode_names.get(state.psychological_mode, 'Equilíbrio')}.{memory_line}"
    
    @classmethod
    def get_companion_message(cls, state: BehavioralState, patterns: Dict) -> str:
        if state.psychological_mode == "survival":
            return "Hoje o único objetivo é registrar presença. Nada além disso importa."
        if state.psychological_mode == "returning":
            return "Você escolheu voltar. Esse ato vale mais do que qualquer número de streak."
        if state.risk_score > 70:
            return "Você está sustentando consistência alta, mas detectamos cansaço emocional. Vá com calma hoje."
        if state.current_streak >= 7:
            return f"Impressionante: {state.current_streak} dias construindo sua presença contínua."
        return "Sua presença hoje é uma escolha ativa de cuidado próprio. Um passo de cada vez."

# ============================================================================
# AUTH SERVICE
# ============================================================================
class AuthService:
    @staticmethod
    def get_current_user_id(session_state: Dict) -> str:
        if "user_id" not in session_state: session_state["user_id"] = "demo-user"
        return session_state["user_id"]

# ============================================================================
# SERVICE LAYER (ORQUESTRAÇÃO)
# ============================================================================
def load_user_state(user_id: str) -> BehavioralState:
    state = repository.load_state(user_id)
    return state or BehavioralState(user_id=user_id)

def process_checkin(user_id: str, emotion: str, actions: List[str], reflection: str) -> BehavioralState:
    now_utc = datetime.now(DEFAULT_TZ)
    state = load_user_state(user_id)
    events = repository.load_events(user_id, limit=100)
    
    new_streak, _, is_return = BehavioralEngine.calculate_streak(state.last_checkin_utc, state.current_streak, now_utc)
    metadata = {"emotion": emotion, "actions_taken": actions, "reflection": reflection, "was_absent": is_return, "streak_after": new_streak}
    
    temp_events = events + [{"event_type": "checkin", "created_at_utc": now_utc.isoformat(), "metadata": metadata}]
    
    state.consistency_score = BehavioralEngine.calculate_consistency(temp_events, now_utc)
    state.current_streak = new_streak
    state.longest_streak = BehavioralEngine.update_longest_streak(new_streak, state.longest_streak)
    state.total_checkins += 1
    state.last_checkin_utc = now_utc.isoformat()
    state.current_level = BehavioralEngine.calculate_level(state.consistency_score)
    state.psychological_mode = BehavioralEngine.detect_psychological_mode(temp_events, state.consistency_score, new_streak, now_utc)
    state.risk_score = BehavioralEngine.calculate_risk_score(temp_events, now_utc)
    
    state.emotion_history.append({"emotion": emotion, "timestamp_utc": now_utc.isoformat(), "streak_at_time": new_streak})
    state.emotion_history = state.emotion_history[-50:]
    
    repository.save_state(state)
    repository.log_event(user_id, "return" if is_return else "checkin", metadata)
    return state

# ============================================================================
# UI LAYER (APRESENTAÇÃO ENXUTA)
# ============================================================================
def render_dashboard(state: BehavioralState, patterns: Dict):
    # Card de Notificação Psicológica (Acolhimento Customizado via HTML/CSS)
    greeting = NarrativeEngine.get_greeting(state, patterns)
    companion_msg = NarrativeEngine.get_companion_message(state, patterns)
    
    st.markdown(f"""
    <div class="narrative-card">
        <div class="narrative-title">{greeting}</div>
        <div class="narrative-text">💬 {companion_msg}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bento Grid de Métricas (HTML injetado para alto controle estético)
    level_info = LEVELS.get(state.current_level, {})
    st.markdown(f"""
    <div class="bento-grid">
        <div class="bento-item">
            <div class="bento-lbl">🎯 Consistência</div>
            <div class="bento-val">{state.consistency_score:.1f}%</div>
        </div>
        <div class="bento-item">
            <div class="bento-lbl">🔥 Streak Atual</div>
            <div class="bento-val">{state.current_streak} dias</div>
        </div>
        <div class="bento-item">
            <div class="bento-lbl">Jornada</div>
            <div class="bento-val">{level_info.get('icon', '🌱')} {level_info.get('name')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Renderização Discreta do Gráfico Histórico
    if state.emotion_history:
        df = pd.DataFrame(state.emotion_history[-14:])
        df["date"] = pd.to_datetime(df["timestamp_utc"]).dt.date
        emotion_counts = df.groupby(["date", "emotion"]).size().unstack(fill_value=0)
        
        fig = go.Figure()
        for emo in emotion_counts.columns:
            if emo in EMOTIONAL_STATES:
                fig.add_trace(go.Bar(
                    name=EMOTIONAL_STATES[emo]["label"],
                    x=emotion_counts.index,
                    y=emotion_counts[emo],
                    marker_color=EMOTIONAL_STATES[emo]["color"] # Aplicação direta da paleta do app
                ))
        
        fig.update_layout(
            barmode="stack",
            height=240,
            margin=dict(l=20, r=20, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    user_id = AuthService.get_current_user_id(st.session_state)
    
    # Estado Único de Verdade: Carrega da persistência
    state = load_user_state(user_id)
    events = repository.load_events(user_id, limit=100)
    patterns = BehavioralEngine.detect_patterns(events)
    
    # UI Element 1: Dashboard Principal (Acolhimento + Dados)
    render_dashboard(state, patterns)
    
    # UI Element 2: Ação do Usuário posicionada abaixo em formato recolhível/limpo
    with st.expander("📝 Registrar Presença e Sentimentos", expanded=True):
        with st.form("checkin_form", clear_on_submit=True):
            emotion = st.selectbox(
                "Como se define seu estado emocional hoje?", 
                options=list(EMOTIONAL_STATES.keys()), 
                format_func=lambda x: f"{EMOTIONAL_STATES[x]['icon']} {EMOTIONAL_STATES[x]['label']}"
            )
            actions = st.multiselect("Esforços conscientes do dia:", ["Hidratação", "Movimento/Treino", "Pausa Consciente", "Expressão de Sentimentos", "Alimentação Atenta"])
            reflection = st.text_area("Desabafo ou reflexão rápida (opcional):", height=80, max_chars=300)
            submitted = st.form_submit_button("✅ Marcar Presença")
            
            if submitted:
                process_checkin(user_id, emotion, actions, reflection)
                st.success("Presença Computada com Sucesso! 🌱")
                st.rerun() # Ciclo limpo: força o Streamlit a redesenhar os Bento Boxes imediatamente
                
    st.markdown("---")
    st.caption(f"EmagreSim Core v32.1 • Ambiente: {'🧪 Demonstração Local' if user_id == 'demo-user' else '🔐 Produção Conectada'} • Horário Base: {datetime.now(DEFAULT_TZ).strftime('%H:%M')} UTC")

if __name__ == "__main__":
    main()
