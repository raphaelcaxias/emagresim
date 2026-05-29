# app.py — EmagreSim v33.0 "Mindful Eating & Growth Core"
# Foco: Emagrecimento/Ganho de Massa + Consciência Alimentar + Foto do Prato + Evolução Real

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, date, timedelta
import random
import json
import logging
import traceback
import hashlib
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from supabase import create_client, Client

# ============================================================================
# CONFIGURAÇÃO GLOBAL
# ============================================================================
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
DEFAULT_TZ = timezone.utc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("emagresim")

st.set_page_config(
    page_title="EmagreSim • Transformação",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# CSS MODERNO
# ============================================================================
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 680px !important;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Níveis */
    .level-badge {
        background: linear-gradient(135deg, #f59e0b, #ea580c);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Refeição */
    .meal-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    .meal-card:hover {
        border-color: #f59e0b;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .meal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .meal-type {
        font-weight: 600;
        color: #f59e0b;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    .meal-time {
        font-size: 0.7rem;
        color: #94a3b8;
    }
    .meal-desc {
        font-size: 0.85rem;
        color: #334155;
        margin: 8px 0;
    }
    .meal-cal {
        font-weight: 600;
        color: #10b981;
        font-size: 0.8rem;
    }
    .meal-photo {
        margin-top: 8px;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Métricas Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Narrative Box */
    .narrative-box {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #fcd34d;
    }
    
    /* Progresso */
    .progress-bar {
        background: #e2e8f0;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-fill {
        background: linear-gradient(90deg, #f59e0b, #ea580c);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s;
    }
    
    #MainMenu, header, footer {display: none;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================================
# SUPABASE
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

supabase = get_supabase()

# ============================================================================
# CONSTANTES
# ============================================================================
class EventType(Enum):
    CHECKIN = "checkin"
    MEAL = "meal"
    WEIGHT = "weight"
    LEVEL_UP = "level_up"

EMOTIONS = {
    "motivado": {"icon": "✨", "label": "Motivado", "color": "#22c55e"},
    "neutro": {"icon": "😐", "label": "Neutro", "color": "#94a3b8"},
    "ansioso": {"icon": "😰", "label": "Ansioso", "color": "#f59e0b"},
    "cansado": {"icon": "😔", "label": "Cansado", "color": "#ef4444"},
    "confiante": {"icon": "💪", "label": "Confiante", "color": "#0d9488"},
}

MEAL_TYPES = {
    "cafe": {"name": "☀️ Café da manhã", "order": 1, "cal_hint": 350},
    "almoco": {"name": "🍽️ Almoço", "order": 2, "cal_hint": 600},
    "lanche": {"name": "🍎 Lanche", "order": 3, "cal_hint": 200},
    "jantar": {"name": "🌙 Jantar", "order": 4, "cal_hint": 550},
}

LEVELS = [
    {"name": "🌱 Iniciante", "min": 0, "desc": "Todo começo é válido."},
    {"name": "🔥 Explorador", "min": 15, "desc": "Descobrindo seu ritmo."},
    {"name": "💪 Persistente", "min": 35, "desc": "Construindo presença."},
    {"name": "🔄 Reconstrutor", "min": 55, "desc": "Recair faz parte. Voltar é força."},
    {"name": "⚓ Inabalável", "min": 75, "desc": "Sua consistência é sua âncora."},
    {"name": "🌟 Guia", "min": 90, "desc": "Você inspira pelo exemplo."},
]

GOAL_TYPES = {
    "emagrecer": {"label": "🎯 Emagrecer", "calorie_target": 1800, "weight_loss": 2.0},
    "ganhar_massa": {"label": "💪 Ganhar massa muscular", "calorie_target": 2500, "weight_gain": 1.0},
    "manter": {"label": "⚖️ Manter o peso", "calorie_target": 2100, "weight_maintain": 0},
}

# ============================================================================
# DATACLASSES
# ============================================================================
@dataclass
class MealEntry:
    type: str
    description: str
    calories: int
    photo_url: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(DEFAULT_TZ).isoformat())
    
    def to_dict(self) -> Dict:
        return {"type": self.type, "description": self.description, "calories": self.calories, 
                "photo_url": self.photo_url, "timestamp": self.timestamp}

@dataclass
class WeightEntry:
    weight: float
    timestamp: str = field(default_factory=lambda: datetime.now(DEFAULT_TZ).isoformat())
    
    def to_dict(self) -> Dict:
        return {"weight": self.weight, "timestamp": self.timestamp}

@dataclass
class BehavioralState:
    user_id: str = ""
    goal: str = "emagrecer"
    current_weight: float = 80.0
    target_weight: float = 70.0
    height: float = 1.70
    age: int = 30
    
    consistency_score: float = 0.0
    current_streak: int = 0
    longest_streak: int = 0
    total_checkins: int = 0
    last_checkin: Optional[str] = None
    current_level: int = 0
    
    meals_today: List[Dict] = field(default_factory=list)
    weight_history: List[Dict] = field(default_factory=list)
    emotion_history: List[Dict] = field(default_factory=list)
    
    def get_level_info(self) -> Dict:
        for i, level in enumerate(reversed(LEVELS)):
            if self.consistency_score >= level["min"]:
                return level
        return LEVELS[0]
    
    def get_progress_to_next_level(self) -> float:
        current = self.consistency_score
        for i, level in enumerate(LEVELS):
            if current < level["min"]:
                prev_min = LEVELS[i-1]["min"] if i > 0 else 0
                return (current - prev_min) / (level["min"] - prev_min) * 100 if level["min"] > prev_min else 0
        return 100
    
    def get_bmi(self) -> float:
        if self.height <= 0:
            return 0
        return self.current_weight / (self.height ** 2)
    
    def get_bmi_category(self) -> str:
        bmi = self.get_bmi()
        if bmi < 18.5: return "Abaixo do peso"
        if bmi < 25: return "Peso normal"
        if bmi < 30: return "Sobrepeso"
        return "Obesidade"
    
    def get_daily_calorie_target(self) -> int:
        return GOAL_TYPES.get(self.goal, GOAL_TYPES["emagrecer"])["calorie_target"]

# ============================================================================
# REPOSITORY
# ============================================================================
class StateRepository:
    def __init__(self, client: Optional[Client]):
        self.client = client
    
    @st.cache_data(ttl=120)
    def load_state(_self, user_id: str) -> Optional[BehavioralState]:
        if user_id == "demo-user" or not _self.client:
            return None
        try:
            result = _self.client.table("behavioral_state").select("*").eq("user_id", user_id).execute()
            if result.data:
                data = result.data[0]
                return BehavioralState(
                    user_id=data["user_id"],
                    goal=data.get("goal", "emagrecer"),
                    current_weight=data.get("current_weight", 80.0),
                    target_weight=data.get("target_weight", 70.0),
                    height=data.get("height", 1.70),
                    age=data.get("age", 30),
                    consistency_score=data.get("consistency_score", 0),
                    current_streak=data.get("current_streak", 0),
                    longest_streak=data.get("longest_streak", 0),
                    total_checkins=data.get("total_checkins", 0),
                    last_checkin=data.get("last_checkin"),
                    current_level=data.get("current_level", 0),
                    meals_today=data.get("meals_today", []),
                    weight_history=data.get("weight_history", []),
                    emotion_history=data.get("emotion_history", []),
                )
            return None
        except Exception as e:
            logger.error(f"load_state error: {e}")
            return None
    
    def save_state(self, state: BehavioralState) -> bool:
        if state.user_id == "demo-user" or not self.client:
            return False
        try:
            self.client.table("behavioral_state").upsert({
                "user_id": state.user_id,
                "goal": state.goal,
                "current_weight": state.current_weight,
                "target_weight": state.target_weight,
                "height": state.height,
                "age": state.age,
                "consistency_score": state.consistency_score,
                "current_streak": state.current_streak,
                "longest_streak": state.longest_streak,
                "total_checkins": state.total_checkins,
                "last_checkin": state.last_checkin,
                "current_level": state.current_level,
                "meals_today": state.meals_today,
                "weight_history": state.weight_history,
                "emotion_history": state.emotion_history,
                "updated_at": datetime.now(DEFAULT_TZ).isoformat(),
            }, on_conflict="user_id").execute()
            self.load_state.clear(state.user_id)
            return True
        except Exception as e:
            logger.error(f"save_state error: {e}")
            return False
    
    def log_event(self, user_id: str, event_type: str, metadata: Dict) -> bool:
        if user_id == "demo-user" or not self.client:
            return False
        try:
            self.client.table("behavioral_events").insert({
                "user_id": user_id,
                "event_type": event_type,
                "metadata": json.dumps(metadata),
                "created_at": datetime.now(DEFAULT_TZ).isoformat(),
            }).execute()
            return True
        except Exception as e:
            logger.error(f"log_event error: {e}")
            return False

repository = StateRepository(supabase)

# ============================================================================
# BEHAVIORAL ENGINE
# ============================================================================
class BehavioralEngine:
    @staticmethod
    def calculate_consistency(events: List[Dict]) -> float:
        """Score baseado em presença e ações"""
        if not events:
            return 0.0
        now = datetime.now(DEFAULT_TZ)
        score = 0.0
        for event in events[-60:]:
            weight = {"checkin": 2, "meal": 1, "weight": 1}.get(event.get("event_type"), 1)
            try:
                ts = datetime.fromisoformat(event.get("created_at", "").replace('Z', '+00:00'))
                days_ago = (now - ts).days
                decay = max(0.3, 1 - (days_ago * 0.02))
                score += weight * decay
            except:
                pass
        return round(min(100, score / 2.5), 1)
    
    @staticmethod
    def calculate_streak(last_checkin: Optional[str]) -> Tuple[int, bool]:
        if not last_checkin:
            return 1, False
        try:
            last = datetime.fromisoformat(last_checkin.replace('Z', '+00:00'))
            now = datetime.now(DEFAULT_TZ)
            delta = (now.date() - last.date()).days
            if delta == 0:
                return 0, False
            elif delta == 1:
                return 1, False
            else:
                return 1, True
        except:
            return 1, False
    
    @staticmethod
    def calculate_level(consistency: float) -> int:
        for i, level in enumerate(LEVELS):
            if consistency < level["min"]:
                return max(0, i - 1)
        return len(LEVELS) - 1

# ============================================================================
# NARRATIVE ENGINE
# ============================================================================
class NarrativeEngine:
    @staticmethod
    def get_greeting(state: BehavioralState) -> str:
        hour = datetime.now(DEFAULT_TZ).hour
        base = "Bom dia" if hour < 12 else "Boa tarde" if hour < 18 else "Boa noite"
        level_info = state.get_level_info()
        return f"{base}. Você está no nível {level_info['name']} — {level_info['desc']}"
    
    @staticmethod
    def get_message(state: BehavioralState) -> str:
        if state.current_streak >= 7:
            return f"🔥 {state.current_streak} dias seguidos! Isso é consistência real."
        if state.current_streak >= 3:
            return f"📈 Você já está há {state.current_streak} dias presente. Continue!"
        if state.consistency_score < 30:
            return "🌱 Todo recomeço é uma semente. Hoje é um novo começo."
        return "💪 Sua presença hoje importa mais do que qualquer número na balança."

# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================
def process_checkin(state: BehavioralState, emotion: str) -> BehavioralState:
    now_utc = datetime.now(DEFAULT_TZ).isoformat()
    new_streak, was_broken = BehavioralEngine.calculate_streak(state.last_checkin)
    
    state.current_streak = new_streak
    state.longest_streak = max(state.longest_streak, new_streak)
    state.total_checkins += 1
    state.last_checkin = now_utc
    
    state.emotion_history.append({"emotion": emotion, "timestamp": now_utc})
    state.emotion_history = state.emotion_history[-50:]
    
    # Atualizar consistência (precisa de eventos)
    events = [{"event_type": "checkin", "created_at": now_utc}]
    state.consistency_score = BehavioralEngine.calculate_consistency(events)
    state.current_level = BehavioralEngine.calculate_level(state.consistency_score)
    
    repository.save_state(state)
    repository.log_event(state.user_id, "checkin", {"emotion": emotion, "streak": new_streak})
    return state

def process_meal(state: BehavioralState, meal_type: str, description: str, calories: int, photo_url: str = None) -> BehavioralState:
    now_utc = datetime.now(DEFAULT_TZ).isoformat()
    today = datetime.now(DEFAULT_TZ).date().isoformat()
    
    # Limpar refeições de dias anteriores
    state.meals_today = [m for m in state.meals_today if m.get("date") == today]
    
    state.meals_today.append({
        "date": today,
        "type": meal_type,
        "description": description,
        "calories": calories,
        "photo_url": photo_url,
        "time": datetime.now(DEFAULT_TZ).strftime("%H:%M"),
    })
    
    repository.log_event(state.user_id, "meal", {"type": meal_type, "calories": calories})
    repository.save_state(state)
    return state

def process_weight(state: BehavioralState, weight: float) -> BehavioralState:
    now_utc = datetime.now(DEFAULT_TZ).isoformat()
    state.current_weight = weight
    state.weight_history.append({"weight": weight, "timestamp": now_utc})
    state.weight_history = state.weight_history[-90:]
    
    repository.log_event(state.user_id, "weight", {"weight": weight})
    repository.save_state(state)
    return state

# ============================================================================
# UI COMPONENTS
# ============================================================================
def render_narrative(state: BehavioralState):
    st.markdown(f"""
    <div class="narrative-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.8rem; color: #92400e;">{NarrativeEngine.get_greeting(state)}</div>
                <div style="font-weight: 500; margin-top: 4px;">{NarrativeEngine.get_message(state)}</div>
            </div>
            <div class="level-badge">{state.get_level_info()['name']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics(state: BehavioralState):
    today_meals = [m for m in state.meals_today if m.get("date") == datetime.now(DEFAULT_TZ).date().isoformat()]
    total_calories = sum(m.get("calories", 0) for m in today_meals)
    calorie_target = state.get_daily_calorie_target()
    
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-value">{state.current_streak}</div>
            <div class="metric-label">🔥 Sequência</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{state.consistency_score:.0f}%</div>
            <div class="metric-label">🎯 Consistência</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_calories}</div>
            <div class="metric-label">🍽️ Calorias</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de calorias
    percent = min(100, (total_calories / calorie_target) * 100)
    st.markdown(f"""
    <div style="font-size: 0.7rem; color: #64748b;">Meta diária: {calorie_target} kcal</div>
    <div class="progress-bar"><div class="progress-fill" style="width: {percent}%;"></div></div>
    """, unsafe_allow_html=True)
    
    # IMC (referência)
    bmi = state.get_bmi()
    st.caption(f"📊 IMC: {bmi:.1f} • {state.get_bmi_category()} (referência)")

def render_meals(state: BehavioralState):
    st.markdown("### 🍽️ Refeições de hoje")
    
    today = datetime.now(DEFAULT_TZ).date().isoformat()
    today_meals = [m for m in state.meals_today if m.get("date") == today]
    
    if today_meals:
        for meal in today_meals:
            meal_name = MEAL_TYPES.get(meal.get("type"), {}).get("name", meal.get("type"))
            st.markdown(f"""
            <div class="meal-card">
                <div class="meal-header">
                    <span class="meal-type">{meal_name}</span>
                    <span class="meal-time">{meal.get('time', '--:--')}</span>
                </div>
                <div class="meal-desc">{meal.get('description', '')}</div>
                <div class="meal-cal">🔥 {meal.get('calories', 0)} kcal</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma refeição registrada hoje.")
    
    # Formulário de nova refeição
    with st.expander("➕ Adicionar refeição", expanded=not today_meals):
        col1, col2 = st.columns(2)
        with col1:
            meal_type = st.selectbox("Tipo", options=list(MEAL_TYPES.keys()), format_func=lambda x: MEAL_TYPES[x]["name"])
        with col2:
            calories = st.number_input("Calorias (kcal)", min_value=0, max_value=1500, value=MEAL_TYPES[meal_type]["cal_hint"], step=50)
        
        description = st.text_area("O que você comeu?", placeholder="Ex: Arroz integral, frango grelhado, salada", height=68)
        photo = st.camera_input("Tirar foto do prato (opcional)", help="Fotografar ajuda na consciência alimentar")
        
        if st.button("✅ Salvar refeição", use_container_width=True):
            if description:
                photo_url = None
                if photo:
                    photo_url = "temp_photo_url"  # Implementar storage depois
                state = process_meal(state, meal_type, description, calories, photo_url)
                st.success(f"🍽️ Refeição registrada! +{calories} kcal")
                st.rerun()
            else:
                st.warning("Descreva o que você comeu")

def render_weight_section(state: BehavioralState):
    st.markdown("### ⚖️ Acompanhamento de peso")
    
    col1, col2 = st.columns(2)
    with col1:
        new_weight = st.number_input("Peso atual (kg)", min_value=30.0, max_value=250.0, value=state.current_weight, step=0.1)
    with col2:
        target_weight = st.number_input("Peso desejado (kg)", min_value=30.0, max_value=250.0, value=state.target_weight, step=0.5)
    
    if new_weight != state.current_weight:
        if st.button("💾 Registrar peso", use_container_width=True):
            state = process_weight(state, new_weight)
            st.success(f"⚖️ Peso registrado: {new_weight:.1f} kg")
            st.rerun()
    
    if target_weight != state.target_weight:
        state.target_weight = target_weight
        repository.save_state(state)
    
    # Gráfico de evolução
    if len(state.weight_history) >= 2:
        df = pd.DataFrame(state.weight_history[-30:])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        fig = px.line(df, x="timestamp", y="weight", title="Evolução do peso", markers=True)
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0))
        fig.update_traces(line=dict(color="#f59e0b", width=2))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def render_history(state: BehavioralState):
    st.markdown("### 📊 Sua jornada")
    
    # Gráfico de emoções
    if state.emotion_history:
        df = pd.DataFrame(state.emotion_history[-30:])
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        emotion_counts = df.groupby("emotion").size()
        if not emotion_counts.empty:
            fig = px.bar(x=emotion_counts.index, y=emotion_counts.values, labels={"x": "Emoção", "y": "Frequência"}, color=emotion_counts.index)
            fig.update_layout(height=200, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total check-ins", state.total_checkins)
    col2.metric("Maior sequência", f"{state.longest_streak} dias")
    col3.metric("Refeições registradas", len([m for m in state.meals_today]))
    
    # Progresso para próximo nível
    progress = state.get_progress_to_next_level()
    st.markdown(f"### 📈 Progresso para próximo nível")
    st.progress(progress / 100)
    st.caption(f"{state.consistency_score:.0f} pontos de consistência")

def render_profile(state: BehavioralState):
    st.markdown("### 👤 Meu perfil")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Idade", 18, 100, state.age)
            height = st.number_input("Altura (m)", 1.40, 2.20, state.height, 0.01)
        with col2:
            goal = st.selectbox("Objetivo", options=list(GOAL_TYPES.keys()), format_func=lambda x: GOAL_TYPES[x]["label"])
        
        if st.form_submit_button("Salvar perfil"):
            state.age = age
            state.height = height
            state.goal = goal
            repository.save_state(state)
            st.success("Perfil atualizado!")
            st.rerun()
    
    st.markdown(f"""
    <div class="card" style="margin-top: 16px;">
        <div style="font-size: 0.8rem; color: #64748b;">Sobre você</div>
        <div><strong>Idade:</strong> {state.age} anos</div>
        <div><strong>Altura:</strong> {state.height:.2f}m</div>
        <div><strong>Objetivo:</strong> {GOAL_TYPES.get(state.goal, {}).get('label', 'Emagrecer')}</div>
        <div><strong>IMC:</strong> {state.get_bmi():.1f} ({state.get_bmi_category()})</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN
# ============================================================================
def main():
    user_id = "demo-user"
    state = repository.load_state(user_id) or BehavioralState(user_id=user_id)
    
    render_narrative(state)
    render_metrics(state)
    
    tabs = st.tabs(["🍽️ Refeições", "⚖️ Peso", "📊 Histórico", "👤 Perfil"])
    
    with tabs[0]:
        render_meals(state)
    
    with tabs[1]:
        render_weight_section(state)
    
    with tabs[2]:
        render_history(state)
    
    with tabs[3]:
        render_profile(state)
    
    # Check-in rápido
    st.markdown("---")
    with st.expander("😊 Como você está se sentindo hoje?"):
        emotion_cols = st.columns(3)
        selected = None
        for idx, (key, data) in enumerate(EMOTIONS.items()):
            with emotion_cols[idx % 3]:
                if st.button(f"{data['icon']} {data['label']}", key=f"emotion_{key}", use_container_width=True):
                    selected = key
        if selected:
            state = process_checkin(state, selected)
            st.success(f"✅ Presença registrada! Você está se sentindo {EMOTIONS[selected]['label']}.")
            st.rerun()
    
    st.caption(f"EmagreSim • Nível {state.get_level_info()['name']} • {state.current_streak} dias de sequência")

if __name__ == "__main__":
    main()