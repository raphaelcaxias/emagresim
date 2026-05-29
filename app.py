# ============================================================================
# app.py — EmagreSim v30.0 "Presence Core"
# Sistema Psicológico-Comportamental com Persistência Real e Motor Narrativo
# Núcleo: PRESENÇA > PERFEIÇÃO | AÇÃO > RESULTADO | RECAÍDA ≠ FRACASSO
# ============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
from supabase import create_client
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================
st.set_page_config(
    page_title="EmagreSim • Aderência",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# SUPABASE CLIENT
# ============================================================================
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["CHAVE_SUPABASE"]
        return create_client(url, key)
    except:
        return None

supabase = get_supabase()

# ============================================================================
# DESIGN SYSTEM — SLATE + AMBER
# ============================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
    --bg:        #0F1117; --surface:   #181C27; --surface2:  #1E2333;
    --border:    #2A3050; --amber:     #F59E0B; --amber-dim: #92610A;
    --teal:      #14B8A6; --red:       #F87171; --text:      #E2E8F0;
    --muted:     #64748B; --success:   #34D399; --warning:   #F59E0B;
    --info:      #60A5FA; --font:      'DM Sans', sans-serif;
    --display:   'DM Serif Display', serif; --radius:    14px; --radius-sm: 8px;
}
html, body, [data-testid="stAppViewContainer"], section.main {
    background: var(--bg) !important; color: var(--text) !important;
    font-family: var(--font) !important;
}
[data-testid="stSidebar"], #MainMenu, header, footer, .stDeployButton { display: none !important; }
::-webkit-scrollbar { width: 4px; }
.topbar {
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 14px 32px; display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 28px; position: sticky; top: 0; z-index: 100;
}
.logo { font-family: var(--display); font-size: 1.5rem; color: var(--text); }
.logo em { font-style: normal; color: var(--amber); }
.user-badge {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 20px; padding: 6px 14px; font-size: 0.8rem;
    color: var(--muted); display: flex; align-items: center; gap: 8px;
}
.user-badge strong { color: var(--text); }
.mode-badge { font-size: 0.7rem; background: var(--amber-dim); color: #0F1117; border-radius: 999px; padding: 2px 8px; }
.stButton > button {
    background: var(--surface) !important; color: var(--muted) !important;
    border: 1px solid var(--border) !important; border-radius: 10px !important;
    font-family: var(--font) !important; font-size: 0.85rem !important;
    font-weight: 500 !important; padding: 8px 0 !important;
    transition: all .18s ease !important;
}
.stButton > button:hover {
    background: var(--surface2) !important; color: var(--amber) !important;
    border-color: var(--amber-dim) !important; transform: translateY(-1px);
}
.hero-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 28px 32px;
    display: flex; align-items: center; gap: 24px; margin-bottom: 24px;
    position: relative; overflow: hidden;
}
.hero-card::before {
    content: ''; position: absolute; right: -40px; top: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(245,158,11,.08) 0%, transparent 70%);
    border-radius: 50%;
}
.avatar {
    width: 72px; height: 72px; border-radius: 50%;
    background: linear-gradient(135deg, var(--amber-dim), var(--amber));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; flex-shrink: 0;
}
.hero-text h2 { font-family: var(--display); font-size: 1.7rem; color: var(--text); }
.hero-text p { font-size: 0.9rem; color: var(--muted); margin-top: 4px; }
.hero-subtle { font-size: 0.8rem; color: var(--muted); margin-top: 8px; font-style: italic; }
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 20px; }
.kpi {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px 18px;
    position: relative; overflow: hidden;
}
.kpi::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px; }
.kpi-amber::after { background: var(--amber); }
.kpi-teal::after { background: var(--teal); }
.kpi-red::after { background: var(--red); }
.kpi-green::after { background: var(--success); }
.kpi-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
.kpi-value { font-size: 1.7rem; font-weight: 700; color: var(--text); line-height: 1; }
.kpi-delta { font-size: 0.8rem; margin-top: 4px; }
.prog-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 20px; }
.prog-header { display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--muted); margin-bottom: 10px; }
.prog-track { background: var(--surface2); border-radius: 999px; height: 10px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 999px; transition: width .6s ease; }
.prog-fill.consent { background: linear-gradient(90deg, var(--amber-dim), var(--amber)); }
.streak-badge { display: inline-flex; align-items: center; gap: 6px; background: var(--surface2); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; font-size: 0.8rem; color: var(--text); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; margin-bottom: 20px; }
.card-title { font-family: var(--display); font-size: 1.1rem; color: var(--text); margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }
.emotion-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
.emotion-btn {
    background: var(--surface2); border: 2px solid var(--border);
    border-radius: var(--radius-sm); padding: 12px 8px; text-align: center;
    cursor: pointer; transition: all .15s; font-size: 0.8rem; color: var(--text);
}
.emotion-btn:hover, .emotion-btn.selected { border-color: var(--amber); background: rgba(245,158,11,0.1); }
.emotion-icon { font-size: 1.3rem; display: block; margin-bottom: 4px; }
.behavior-entry {
    background: var(--surface2); border-left: 3px solid var(--border);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 14px 16px; margin-bottom: 10px;
}
.behavior-entry.consent { border-left-color: var(--success); }
.behavior-entry.relapse { border-left-color: var(--red); }
.behavior-entry.return { border-left-color: var(--amber); }
.behavior-header { display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--muted); margin-bottom: 6px; }
.behavior-text { font-size: 0.9rem; color: var(--text); }
.behavior-tag { display: inline-block; font-size: 0.7rem; padding: 2px 8px; border-radius: 999px; background: var(--surface); color: var(--muted); margin-top: 6px; }
.level-badge { display: inline-flex; align-items: center; gap: 6px; background: linear-gradient(135deg, var(--amber-dim), var(--amber)); color: #0F1117; font-weight: 700; padding: 4px 12px; border-radius: 999px; font-size: 0.8rem; }
.info-box { border-radius: var(--radius-sm); padding: 16px; font-size: 0.87rem; line-height: 1.5; }
.info-support { background: rgba(20,184,166,.07); border: 1px solid rgba(20,184,166,.2); color: var(--teal); }
.info-tip { background: rgba(245,158,11,.07); border: 1px solid rgba(245,158,11,.2); color: var(--amber); }
.info-return { background: rgba(96,165,250,.07); border: 1px solid rgba(96,165,250,.2); color: var(--info); }
.info-crisis { background: rgba(248,113,113,.07); border: 1px solid rgba(248,113,113,.2); color: var(--red); }
.info-label { font-weight: 700; margin-bottom: 4px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .07em; }
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; border-radius: var(--radius-sm) !important;
    font-family: var(--font) !important;
}
div[data-testid="stExpander"] { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
div[data-testid="stExpander"] summary { color: var(--amber) !important; font-weight: 500 !important; }
[data-testid="stProgress"] > div > div { background: var(--amber) !important; }
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ============================================================================
# CONSTANTES E ENUMS
# ============================================================================
class EventType(Enum):
    CHECKIN = "checkin"
    RELAPSE = "relapse"
    RETURN = "return"
    STREAK_BROKEN = "streak_broken"
    STREAK_RECOVERED = "streak_recovered"
    MICRO_GOAL = "micro_goal"
    LEVEL_UP = "level_up"
    ACHIEVEMENT = "achievement"

class PsychologicalMode(Enum):
    NORMAL = "normal"
    SURVIVAL = "survival"
    RETURNING = "returning"
    STABLE = "stable"

EMOTIONAL_STATES = {
    "motivado": {"icon": "✨", "color": "var(--success)", "label": "Motivado"},
    "neutro": {"icon": "😐", "color": "var(--muted)", "label": "Neutro"},
    "ansioso": {"icon": "😰", "color": "var(--amber)", "label": "Ansioso"},
    "cansado": {"icon": "😔", "color": "var(--red)", "label": "Cansado"},
    "frustrado": {"icon": "😞", "color": "var(--red)", "label": "Frustrado"},
    "confiante": {"icon": "💪", "color": "var(--teal)", "label": "Confiante"},
}

LEVELS = {
    0: {"name": "Semente", "icon": "🌱", "min_consistency": 0, "desc": "Todo começo é válido."},
    1: {"name": "Explorador", "icon": "🗺️", "min_consistency": 15, "desc": "Descobrindo seu ritmo."},
    2: {"name": "Persistente", "icon": "🔥", "min_consistency": 35, "desc": "Construindo presença."},
    3: {"name": "Reconstrutor", "icon": "🧱", "min_consistency": 55, "desc": "Recair faz parte. Voltar é força."},
    4: {"name": "Inabalável", "icon": "⚓", "min_consistency": 75, "desc": "Sua consistência é sua âncora."},
    5: {"name": "Guia", "icon": "🌟", "min_consistency": 90, "desc": "Você inspira pelo exemplo de permanência."},
}

ACHIEVEMENTS = {
    "first_checkin": {"name": "Primeiro Passo", "icon": "👣", "desc": "Primeiro check-in registrado."},
    "courageous_return": {"name": "Retorno Corajoso", "icon": "🔄", "desc": "Voltou após 3+ dias ausente."},
    "seven_days": {"name": "Sete Dias", "icon": "📅", "desc": "Manteve presença por uma semana."},
    "no_guilt": {"name": "Sem Culpa", "icon": "🕊️", "desc": "Registrou uma recaída sem abandonar."},
    "self_awareness": {"name": "Autoconhecimento", "icon": "🪞", "desc": "Identificou um padrão comportamental."},
}

# ============================================================================
# ENGINE DE PERSISTÊNCIA (SEM MOCK)
# ============================================================================
@dataclass
class BehavioralState:
    user_id: str
    consistency_score: float
    current_streak: int
    longest_streak: int
    total_checkins: int
    last_checkin: Optional[datetime]
    current_level: int
    unlocked_achievements: List[str]
    psychological_mode: str
    emotion_history: List[Dict]
    behavioral_memory: Dict

class PersistenceEngine:
    @staticmethod
    def load_state(user_id: str) -> Optional[BehavioralState]:
        if user_id == "demo-user" or not supabase:
            return None
        try:
            result = supabase.table("behavioral_state").select("*").eq("user_id", user_id).execute()
            if result.data:
                data = result.data[0]
                return BehavioralState(
                    user_id=data["user_id"],
                    consistency_score=data["consistency_score"],
                    current_streak=data["current_streak"],
                    longest_streak=data["longest_streak"],
                    total_checkins=data["total_checkins"],
                    last_checkin=datetime.fromisoformat(data["last_checkin"]) if data.get("last_checkin") else None,
                    current_level=data["current_level"],
                    unlocked_achievements=data.get("unlocked_achievements", []),
                    psychological_mode=data.get("psychological_mode", "normal"),
                    emotion_history=data.get("emotion_history", []),
                    behavioral_memory=data.get("behavioral_memory", {}),
                )
            return None
        except:
            return None

    @staticmethod
    def save_state(state: BehavioralState):
        if state.user_id == "demo-user" or not supabase:
            return
        try:
            supabase.table("behavioral_state").upsert({
                "user_id": state.user_id,
                "consistency_score": state.consistency_score,
                "current_streak": state.current_streak,
                "longest_streak": state.longest_streak,
                "total_checkins": state.total_checkins,
                "last_checkin": state.last_checkin.isoformat() if state.last_checkin else None,
                "current_level": state.current_level,
                "unlocked_achievements": state.unlocked_achievements,
                "psychological_mode": state.psychological_mode,
                "emotion_history": state.emotion_history,
                "behavioral_memory": state.behavioral_memory,
                "updated_at": datetime.now().isoformat(),
            }, "user_id").execute()
        except:
            pass

    @staticmethod
    def log_event(user_id: str, event_type: str, metadata: Dict = None):
        if user_id == "demo-user" or not supabase:
            return
        try:
            supabase.table("behavioral_events").insert({
                "user_id": user_id,
                "event_type": event_type,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.now().isoformat(),
            }).execute()
        except:
            pass

# ============================================================================
# ENGINE DE COMPORTAMENTO (CÁLCULOS REAIS)
# ============================================================================
class BehavioralEngine:
    @staticmethod
    def calculate_consistency(actions: List[Dict]) -> float:
        if not actions:
            return 0.0
        score = 0.0
        now = datetime.now()
        for action in actions[-30:]:
            weight = {"checkin": 2, "emotion_log": 3, "meal_log": 1, "weight_log": 1}.get(action.get("type"), 1)
            days_ago = (now - action["timestamp"]).days
            decay = max(0.3, 1 - (days_ago * 0.02))
            score += weight * decay
            if action.get("metadata", {}).get("was_absent"):
                score += 5
        return round(min(100, score / 2.5), 1)

    @staticmethod
    def calculate_streak(last_checkin: Optional[datetime]) -> Tuple[int, bool]:
        if not last_checkin:
            return 1, False
        now = datetime.now()
        delta = (now.date() - last_checkin.date()).days
        if delta == 0:
            return st.session_state.get("current_streak", 0), False
        elif delta == 1:
            return st.session_state.get("current_streak", 0) + 1, False
        else:
            return 1, True

    @staticmethod
    def detect_psychological_mode(actions: List[Dict], consistency: float) -> str:
        if not actions:
            return PsychologicalMode.NORMAL.value
        now = datetime.now()
        last_action = max(actions, key=lambda x: x["timestamp"])
        days_since = (now - last_action["timestamp"]).days
        recent_emotions = [a.get("emotion") for a in actions[-7:] if a.get("emotion")]
        negative_emotions = sum(1 for e in recent_emotions if e in ["ansioso", "frustrado", "cansado"])
        if days_since > 4 or (len(recent_emotions) >= 3 and negative_emotions >= 2) or consistency < 30:
            return PsychologicalMode.SURVIVAL.value
        if days_since > 1 and days_since <= 4:
            return PsychologicalMode.RETURNING.value
        if consistency >= 70 and st.session_state.get("current_streak", 0) >= 5:
            return PsychologicalMode.STABLE.value
        return PsychologicalMode.NORMAL.value

    @staticmethod
    def calculate_level(consistency: float) -> int:
        for level in sorted(LEVELS.keys(), reverse=True):
            if consistency >= LEVELS[level]["min_consistency"]:
                return level
        return 0

    @staticmethod
    def check_achievements(actions: List[Dict], total_checkins: int, streak: int) -> List[str]:
        unlocked = []
        if total_checkins >= 1 and "first_checkin" not in st.session_state.get("unlocked_achievements", []):
            unlocked.append("first_checkin")
        for a in actions:
            if a.get("metadata", {}).get("was_absent") and "courageous_return" not in st.session_state.get("unlocked_achievements", []):
                unlocked.append("courageous_return")
                break
        if streak >= 7 and "seven_days" not in st.session_state.get("unlocked_achievements", []):
            unlocked.append("seven_days")
        if any(a.get("emotion") in ["frustrado", "ansioso"] for a in actions[-10:]):
            if "no_guilt" not in st.session_state.get("unlocked_achievements", []):
                unlocked.append("no_guilt")
        return unlocked

    @staticmethod
    def calculate_risk_score(actions: List[Dict]) -> float:
        if len(actions) < 5:
            return 0.0
        risk = 0.0
        now = datetime.now()
        for i, action in enumerate(actions[:14]):
            days_ago = (now - action["timestamp"]).days
            if days_ago > 3:
                risk += 3 * (1 - (i / 14))
            if action.get("emotion") in ["ansioso", "frustrado", "cansado"]:
                risk += 2 * (1 - (i / 14))
        return min(100, round(risk, 1))

# ============================================================================
# ENGINE NARRATIVO (MENSAGENS PERSISTENTES)
# ============================================================================
class NarrativeEngine:
    @staticmethod
    def get_greeting(state: BehavioralState) -> str:
        hour = datetime.now().hour
        base = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        mode_names = {"normal": "🌿 Equilíbrio", "survival": "🛡️ Sobrevivência", "returning": "🔄 Reencontro", "stable": "⛰️ Constância"}
        return f"{base}. Você está em modo {mode_names.get(state.psychological_mode, 'Equilíbrio')}."

    @staticmethod
    def get_companion_message(state: BehavioralState, risk_score: float) -> str:
        if state.psychological_mode == "survival":
            return "Hoje o objetivo é só se manter presente. Nada além disso importa."
        elif state.psychological_mode == "returning":
            return "Você voltou. Isso importa mais do que qualquer streak ou número."
        elif risk_score > 70:
            return f"Você está há {state.current_streak} dias consistente. Cuidado com o cansaço emocional."
        elif state.current_streak >= 7:
            return f"{state.current_streak} dias seguidos. Isso é presença real."
        else:
            return "Sua presença hoje já é um ato de cuidado. Um dia de cada vez."

    @staticmethod
    def get_micro_goal(mode: str) -> str:
        goals = {
            "survival": ["Hoje só abra o app.", "Beba um copo d'água agora.", "Registre como você está se sentindo."],
            "returning": ["Registre uma refeição hoje.", "Não tente compensar o tempo perdido.", "Olhe para o que você já conquistou."],
            "stable": ["Mantenha o ritmo.", "Adicione uma fruta na sua refeição.", "Continue com a consistência."],
            "normal": ["Registre seu estado emocional.", "Faça uma refeição consciente.", "Anote uma coisa que você fez bem."],
        }
        return random.choice(goals.get(mode, goals["normal"]))

# ============================================================================
# INICIALIZAÇÃO (COM PERSISTÊNCIA REAL)
# ============================================================================
def init_session_state():
    uid = "demo-user"
    state = PersistenceEngine.load_state(uid)
    if state:
        st.session_state.update({
            "user_id": uid,
            "consistency_score": state.consistency_score,
            "current_streak": state.current_streak,
            "longest_streak": state.longest_streak,
            "total_checkins": state.total_checkins,
            "last_checkin": state.last_checkin,
            "current_level": state.current_level,
            "unlocked_achievements": state.unlocked_achievements,
            "psychological_mode": state.psychological_mode,
            "emotion_history": state.emotion_history,
            "behavioral_memory": state.behavioral_memory,
            "pagina": st.session_state.get("pagina", "dashboard"),
            "nome": "Adriano",
            "current_weight": 105.8,
        })
    else:
        st.session_state.setdefault("user_id", uid)
        st.session_state.setdefault("consistency_score", 0.0)
        st.session_state.setdefault("current_streak", 0)
        st.session_state.setdefault("longest_streak", 0)
        st.session_state.setdefault("total_checkins", 0)
        st.session_state.setdefault("last_checkin", None)
        st.session_state.setdefault("current_level", 0)
        st.session_state.setdefault("unlocked_achievements", [])
        st.session_state.setdefault("psychological_mode", "normal")
        st.session_state.setdefault("emotion_history", [])
        st.session_state.setdefault("behavioral_memory", {})
        st.session_state.setdefault("pagina", "dashboard")
        st.session_state.setdefault("nome", "Adriano")
        st.session_state.setdefault("current_weight", 105.8)

init_session_state()
uid = st.session_state["user_id"]

# ============================================================================
# LOAD ACTIONS (SEM MOCK)
# ============================================================================
def load_actions() -> List[Dict]:
    if uid == "demo-user" or not supabase:
        return []
    try:
        result = supabase.table("behavioral_events").select("*").eq("user_id", uid).order("created_at", desc=True).limit(100).execute()
        actions = []
        for row in result.data or []:
            actions.append({
                "type": row["event_type"],
                "timestamp": datetime.fromisoformat(row["created_at"]),
                "emotion": json.loads(row.get("metadata", "{}")).get("emotion"),
                "metadata": json.loads(row.get("metadata", "{}")),
            })
        return sorted(actions, key=lambda x: x["timestamp"])
    except:
        return []

# ============================================================================
# SAVE CHECKIN (COM PERSISTÊNCIA)
# ============================================================================
def save_checkin(emotion: str = None):
    now = datetime.now()
    was_absent = False
    if st.session_state["last_checkin"]:
        last = st.session_state["last_checkin"]
        if isinstance(last, str):
            last = datetime.fromisoformat(last)
        if (now - last).days > 1:
            was_absent = True
    else:
        was_absent = True
    
    PersistenceEngine.log_event(uid, EventType.CHECKIN.value, {"emotion": emotion, "was_absent": was_absent})
    
    st.session_state["last_checkin"] = now
    st.session_state["total_checkins"] += 1
    
    if was_absent:
        PersistenceEngine.log_event(uid, EventType.RETURN.value, {"days_absent": (now - last).days if st.session_state.get("last_checkin") else 0})
    
    if emotion:
        st.session_state["emotion_history"].append({"emotion": emotion, "timestamp": now.isoformat()})
        st.session_state["last_emotion"] = emotion
    
    actions = load_actions()
    consistency = BehavioralEngine.calculate_consistency(actions)
    new_streak, broken = BehavioralEngine.calculate_streak(st.session_state["last_checkin"])
    if broken and new_streak > 0:
        PersistenceEngine.log_event(uid, EventType.STREAK_BROKEN.value, {"old_streak": st.session_state["current_streak"]})
    
    st.session_state["consistency_score"] = consistency
    st.session_state["current_streak"] = new_streak
    st.session_state["longest_streak"] = max(st.session_state["longest_streak"], new_streak)
    
    new_level = BehavioralEngine.calculate_level(consistency)
    if new_level > st.session_state["current_level"]:
        st.session_state["current_level"] = new_level
        PersistenceEngine.log_event(uid, EventType.LEVEL_UP.value, {"old_level": st.session_state["current_level"], "new_level": new_level})
    
    new_achievements = BehavioralEngine.check_achievements(actions, st.session_state["total_checkins"], new_streak)
    for ach in new_achievements:
        if ach not in st.session_state["unlocked_achievements"]:
            st.session_state["unlocked_achievements"].append(ach)
            PersistenceEngine.log_event(uid, EventType.ACHIEVEMENT.value, {"achievement": ach})
    
    mode = BehavioralEngine.detect_psychological_mode(actions, consistency)
    st.session_state["psychological_mode"] = mode
    
    risk = BehavioralEngine.calculate_risk_score(actions)
    
    state = BehavioralState(
        user_id=uid,
        consistency_score=consistency,
        current_streak=new_streak,
        longest_streak=st.session_state["longest_streak"],
        total_checkins=st.session_state["total_checkins"],
        last_checkin=now,
        current_level=st.session_state["current_level"],
        unlocked_achievements=st.session_state["unlocked_achievements"],
        psychological_mode=mode,
        emotion_history=st.session_state["emotion_history"],
        behavioral_memory=st.session_state["behavioral_memory"],
    )
    PersistenceEngine.save_state(state)

# ============================================================================
# UI COMPONENTS
# ============================================================================
def render_topbar():
    mode = st.session_state["psychological_mode"]
    mode_names = {"normal": "🌿 Equilíbrio", "survival": "🛡️ Sobrevivência", "returning": "🔄 Reencontro", "stable": "⛰️ Constância"}
    st.markdown(f"""
    <div class="topbar">
        <div class="logo">Emagre<em>Sim</em></div>
        <div class="user-badge">
            <span>👤</span>
            <strong>{st.session_state['nome']}</strong>
            <span class="mode-badge">{mode_names.get(mode, '🌿 Equilíbrio')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    nav_cols = st.columns(4)
    nav_items = [("🏠 Início", "dashboard"), ("📝 Check-in", "checkin"), ("📊 Jornada", "journey"), ("👤 Perfil", "perfil")]
    for col, (label, key) in zip(nav_cols, nav_items):
        with col:
            if st.button(label, use_container_width=True, key=f"nav_{key}"):
                st.session_state["pagina"] = key
                st.rerun()

def pagina_dashboard():
    actions = load_actions()
    consistency = BehavioralEngine.calculate_consistency(actions)
    risk = BehavioralEngine.calculate_risk_score(actions)
    mode = st.session_state["psychological_mode"]
    
    emoji = LEVELS.get(st.session_state["current_level"], LEVELS[0])["icon"]
    greeting = NarrativeEngine.get_greeting(st.session_state)
    companion_msg = NarrativeEngine.get_companion_message(st.session_state, risk)
    
    st.markdown(f"""
    <div class="hero-card">
        <div class="avatar">{emoji}</div>
        <div class="hero-text">
            <h2>{greeting}</h2>
            <p>{companion_msg}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi kpi-amber">
            <div class="kpi-label">🔥 Consistência</div>
            <div class="kpi-value">{consistency:.0f}<span style="font-size:1rem">/100</span></div>
            <div class="kpi-delta delta-neu">baseado em suas ações</div>
        </div>
        <div class="kpi kpi-teal">
            <div class="kpi-label">📅 Presença</div>
            <div class="kpi-value">{st.session_state['current_streak']} dias</div>
            <div class="kpi-delta"><span class="streak-badge"><span class="streak-fire">🔥</span> atual</span></div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">🏆 Nível</div>
            <div class="kpi-value">{LEVELS[st.session_state['current_level']]['icon']} {LEVELS[st.session_state['current_level']]['name']}</div>
            <div class="kpi-delta delta-neu">{len(st.session_state['unlocked_achievements'])} conquistas</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">⚠️ Risco</div>
            <div class="kpi-value">{risk:.0f}<span style="font-size:1rem">/100</span></div>
            <div class="kpi-delta delta-neu">abandono</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    micro_goal = NarrativeEngine.get_micro_goal(mode)
    st.markdown(f"""
    <div class="info-box info-tip">
        <div class="info-label">🎯 Micro-objetivo do dia</div>
        <p>{micro_goal}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("✨ Check-in rápido — como você está?"):
        emotion_cols = st.columns(3)
        selected_emotion = None
        for idx, (key, data) in enumerate(EMOTIONAL_STATES.items()):
            with emotion_cols[idx % 3]:
                if st.button(f"{data['icon']}<br>{data['label']}", key=f"emo_{key}", help=data['label']):
                    selected_emotion = key
        if st.button("✅ Registrar presença", key="btn_quick_checkin", type="primary"):
            save_checkin(selected_emotion)
            st.success("✓ Presença registrada. Isso já é vitória.")
            st.rerun()
    
    if st.session_state["unlocked_achievements"]:
        st.markdown('<div class="card"><div class="card-title">🏆 Conquistas</div>', unsafe_allow_html=True)
        ach_cols = st.columns(min(4, len(st.session_state["unlocked_achievements"])))
        for idx, ach_key in enumerate(st.session_state["unlocked_achievements"]):
            ach = ACHIEVEMENTS.get(ach_key, {})
            with ach_cols[idx % 4]:
                st.markdown(f'<div style="text-align:center;padding:12px;background:var(--surface2);border-radius:var(--radius-sm);"><div style="font-size:1.5rem">{ach.get("icon", "🏅")}</div><div style="font-weight:600;font-size:0.8rem">{ach.get("name", "")}</div><div style="font-size:0.7rem;color:var(--muted)">{ach.get("desc", "")}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def pagina_checkin():
    st.markdown('<div class="card"><div class="card-title">📝 Check-in Comportamental</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);margin-bottom:20px">Registre como você está. Sua experiência emocional é o que realmente importa.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-label">1. Como você está se sentindo agora?</div>', unsafe_allow_html=True)
    emotion_cols = st.columns(3)
    selected_emotion = None
    for idx, (key, data) in enumerate(EMOTIONAL_STATES.items()):
        with emotion_cols[idx % 3]:
            if st.button(f"{data['icon']}<br>{data['label']}", key=f"checkin_emo_{key}", help=data['label']):
                selected_emotion = key
    
    st.markdown('<div class="info-label" style="margin-top:20px">2. O que você conseguiu fazer hoje?</div>', unsafe_allow_html=True)
    behavioral_actions = st.multiselect("Marque o que se aplica:", ["🚶 Me movi", "💧 Bebi água", "😴 Dormi bem", "🧘 Respirei", "📝 Registrei algo", "🗣️ Conversei", "🚫 Evitei gatilho", "🔄 Voltei"], key="checkin_actions")
    
    with st.expander("💬 Quer compartilhar algo mais? (opcional)"):
        reflection = st.text_area("Espaço livre:", placeholder="Ex: 'Hoje foi difícil, mas não desisti'...", height=80)
    
    if st.button("✅ Salvar check-in", key="btn_save_checkin", type="primary", use_container_width=True):
        save_checkin(selected_emotion)
        st.success("✓ Check-in registrado. Sua presença hoje importa.")
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def pagina_journey():
    st.markdown('<div class="card"><div class="card-title">📊 Sua Jornada</div>', unsafe_allow_html=True)
    actions = load_actions()
    if not actions:
        st.info("Nenhuma ação registrada ainda.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    df = pd.DataFrame([{"data": a["timestamp"], "tipo": a["type"]} for a in actions if a["type"] == "checkin"])
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["checkin"] = 1
        df_weekly = df.set_index("data").resample("D").sum().fillna(0)
        fig = go.Figure([go.Bar(x=df_weekly.index, y=df_weekly["checkin"], marker_color="#F59E0B")])
        fig.update_layout(paper_bgcolor="#181C27", plot_bgcolor="#181C27", font=dict(color="#64748B"), height=300, xaxis_title="Data", yaxis_title="Check-ins")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    c1, c2, c3 = st.columns(3)
    c1.metric("Total check-ins", st.session_state["total_checkins"])
    c2.metric("Maior streak", f"{st.session_state['longest_streak']} dias")
    c3.metric("Consistência atual", f"{st.session_state['consistency_score']:.0f}/100")
    st.markdown('</div>', unsafe_allow_html=True)

def pagina_perfil():
    st.markdown('<div class="card"><div class="card-title">👤 Perfil</div>', unsafe_allow_html=True)
    with st.form("perfil_form"):
        nome = st.text_input("Nome", st.session_state.get("nome", "Adriano"))
        if st.form_submit_button("Salvar"):
            st.session_state["nome"] = nome
            st.success("Perfil atualizado!")
    st.markdown(f"<div class='info-box info-tip'>🎯 Nível: {LEVELS[st.session_state['current_level']]['name']} — {LEVELS[st.session_state['current_level']]['desc']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    render_topbar()
    render_navigation()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    paginas = {"dashboard": pagina_dashboard, "checkin": pagina_checkin, "journey": pagina_journey, "perfil": pagina_perfil}
    paginas.get(st.session_state["pagina"], pagina_dashboard)()

if __name__ == "__main__":
    main()