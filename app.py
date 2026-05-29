# app.py — EmagreSim v34.0 "Complete Core"
# Funcionalidades: Calculadora calórica dinâmica, sistema de pontos, análise de dados, monetização
# Foco: Emagrecimento/Ganho de Massa + Consciência Alimentar + Foto do Prato + Gamificação Real

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import random
import json
import hashlib
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from supabase import create_client, Client

# ============================================================================
# CONFIGURAÇÃO GLOBAL
# ============================================================================
DEFAULT_TZ = datetime.now().astimezone().tzinfo

st.set_page_config(
    page_title="EmagreSim • Transformação",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# CSS Moderno
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
    
    .card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .level-badge {
        background: linear-gradient(135deg, #f59e0b, #ea580c);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
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
    
    .narrative-box {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #fcd34d;
    }
    
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
    
    .points-badge {
        background: #fef3c7;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #92400e;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    #MainMenu, header, footer {display: none;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================================
# SUPABASE (opcional)
# ============================================================================
def get_supabase() -> Optional[Client]:
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("CHAVE_SUPABASE")
        if not url or not key:
            return None
        return create_client(url, key)
    except:
        return None

supabase = get_supabase()

# ============================================================================
# CONSTANTES
# ============================================================================
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
    {"name": "🌱 Iniciante", "min_points": 0, "desc": "Todo começo é válido."},
    {"name": "🔥 Explorador", "min_points": 500, "desc": "Descobrindo seu ritmo."},
    {"name": "💪 Persistente", "min_points": 1500, "desc": "Construindo presença."},
    {"name": "🔄 Reconstrutor", "min_points": 3000, "desc": "Recair faz parte. Voltar é força."},
    {"name": "⚓ Inabalável", "min_points": 6000, "desc": "Sua consistência é sua âncora."},
    {"name": "🌟 Guia", "min_points": 10000, "desc": "Você inspira pelo exemplo."},
]

GOAL_TYPES = {
    "emagrecer": {"label": "🎯 Emagrecer", "activity_level": 1.55},
    "ganhar_massa": {"label": "💪 Ganhar massa muscular", "activity_level": 1.725},
    "manter": {"label": "⚖️ Manter o peso", "activity_level": 1.55},
}

ACTIVITY_LEVELS = {
    "sedentario": 1.2,
    "leve": 1.375,
    "moderado": 1.55,
    "intenso": 1.725,
    "extremo": 1.9,
}

# ============================================================================
# CÁLCULOS
# ============================================================================
def calcular_tmb(peso: float, altura: float, idade: int, sexo: str = "M") -> float:
    altura_cm = altura * 100
    if sexo == "M":
        return (10 * peso) + (6.25 * altura_cm) - (5 * idade) + 5
    else:
        return (10 * peso) + (6.25 * altura_cm) - (5 * idade) - 161

def calcular_meta_calorica(tmb: float, objetivo: str, nivel_atividade: str = "moderado") -> int:
    fator_atividade = ACTIVITY_LEVELS.get(nivel_atividade, 1.55)
    tdee = tmb * fator_atividade
    
    if objetivo == "emagrecer":
        return int(tdee - 500)
    elif objetivo == "ganhar_massa":
        return int(tdee + 300)
    else:
        return int(tdee)

def calcular_imc(peso: float, altura: float) -> float:
    if altura <= 0:
        return 0
    return peso / (altura ** 2)

def calcular_progresso_peso(peso_atual: float, peso_inicio: float, meta_mensal: float = 2.0) -> Dict:
    perdido = max(0, peso_inicio - peso_atual)
    percentual = min(100, (perdido / meta_mensal) * 100) if meta_mensal > 0 else 0
    return {"perdido": perdido, "percentual": percentual, "restante": max(0, meta_mensal - perdido)}

# ============================================================================
# DATACLASSES
# ============================================================================
@dataclass
class MealEntry:
    type: str
    description: str
    calories: int
    photo_url: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {"type": self.type, "description": self.description, "calories": self.calories, 
                "photo_url": self.photo_url, "timestamp": self.timestamp}

@dataclass
class WeightEntry:
    weight: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class BehavioralState:
    user_id: str = "demo-user"
    nome: str = "Usuário"
    sexo: str = "M"
    idade: int = 30
    altura: float = 1.70
    objetivo: str = "emagrecer"
    nivel_atividade: str = "moderado"
    
    current_weight: float = 80.0
    target_weight: float = 70.0
    peso_inicio_mes: float = 80.0
    meta_mensal_kg: float = 2.0
    
    # Pontuação e níveis
    total_points: int = 0
    current_level: int = 0
    
    # Consistência
    current_streak: int = 0
    longest_streak: int = 0
    total_checkins: int = 0
    last_checkin: Optional[str] = None
    
    # Registros
    meals_today: List[Dict] = field(default_factory=list)
    weight_history: List[Dict] = field(default_factory=list)
    emotion_history: List[Dict] = field(default_factory=list)
    points_history: List[Dict] = field(default_factory=list)
    
    # Para análises
    is_premium: bool = False
    
    def get_level_info(self) -> Dict:
        for i, level in enumerate(reversed(LEVELS)):
            if self.total_points >= level["min_points"]:
                return level
        return LEVELS[0]
    
    def get_next_level_info(self) -> Dict:
        for level in LEVELS:
            if self.total_points < level["min_points"]:
                return level
        return LEVELS[-1]
    
    def get_progress_to_next_level(self) -> float:
        current = self.total_points
        next_level = self.get_next_level_info()
        prev_min = LEVELS[LEVELS.index(next_level) - 1]["min_points"] if LEVELS.index(next_level) > 0 else 0
        if next_level["min_points"] <= prev_min:
            return 0
        return min(100, (current - prev_min) / (next_level["min_points"] - prev_min) * 100)
    
    def get_daily_calorie_target(self) -> int:
        tmb = calcular_tmb(self.current_weight, self.altura, self.idade, self.sexo)
        return calcular_meta_calorica(tmb, self.objetivo, self.nivel_atividade)
    
    def get_tmb(self) -> float:
        return calcular_tmb(self.current_weight, self.altura, self.idade, self.sexo)
    
    def get_tdee(self) -> float:
        tmb = self.get_tmb()
        return tmb * ACTIVITY_LEVELS.get(self.nivel_atividade, 1.55)

# ============================================================================
# SISTEMA DE PONTOS
# ============================================================================
class PointsSystem:
    REWARDS = {
        "checkin": 10,
        "meal": 15,
        "meal_with_photo": 5,
        "weight_log": 10,
        "calorie_goal_achieved": 30,
        "streak_7_days": 100,
        "streak_30_days": 500,
    }
    
    @classmethod
    def calculate_daily_points(cls, has_checkin: bool, meals_count: int, meals_with_photo: int, 
                                has_weight: bool, calorie_goal_achieved: bool, current_streak: int) -> int:
        points = 0
        if has_checkin:
            points += cls.REWARDS["checkin"]
        points += meals_count * cls.REWARDS["meal"]
        points += meals_with_photo * cls.REWARDS["meal_with_photo"]
        if has_weight:
            points += cls.REWARDS["weight_log"]
        if calorie_goal_achieved:
            points += cls.REWARDS["calorie_goal_achieved"]
        if current_streak >= 7 and current_streak % 7 == 0:
            points += cls.REWARDS["streak_7_days"]
        if current_streak >= 30 and current_streak % 30 == 0:
            points += cls.REWARDS["streak_30_days"]
        return points

# ============================================================================
# PROCESSAMENTO
# ============================================================================
def process_checkin(state: BehavioralState, emotion: str) -> Tuple[BehavioralState, int]:
    now_utc = datetime.now().isoformat()
    
    # Calcular streak
    if state.last_checkin:
        try:
            last = datetime.fromisoformat(state.last_checkin.replace('Z', '+00:00'))
            delta = (datetime.now() - last).days
            if delta == 1:
                state.current_streak += 1
            elif delta > 1:
                state.current_streak = 1
            else:
                state.current_streak = state.current_streak
        except:
            state.current_streak = 1
    else:
        state.current_streak = 1
    
    state.longest_streak = max(state.longest_streak, state.current_streak)
    state.total_checkins += 1
    state.last_checkin = now_utc
    
    state.emotion_history.append({"emotion": emotion, "timestamp": now_utc})
    state.emotion_history = state.emotion_history[-50:]
    
    # Calcular pontos do dia (parcial)
    today = datetime.now().date().isoformat()
    today_meals = [m for m in state.meals_today if m.get("date") == today]
    meals_with_photo = sum(1 for m in today_meals if m.get("photo_url"))
    total_calories = sum(m.get("calories", 0) for m in today_meals)
    calorie_goal = state.get_daily_calorie_target()
    
    daily_points = PointsSystem.calculate_daily_points(
        has_checkin=True,
        meals_count=len(today_meals),
        meals_with_photo=meals_with_photo,
        has_weight=False,
        calorie_goal_achieved=total_calories <= calorie_goal,
        current_streak=state.current_streak
    )
    
    state.total_points += daily_points
    state.points_history.append({"points": daily_points, "date": now_utc, "source": "checkin"})
    
    # Atualizar nível
    new_level = 0
    for i, level in enumerate(LEVELS):
        if state.total_points >= level["min_points"]:
            new_level = i
    state.current_level = new_level
    
    return state, daily_points

def process_meal(state: BehavioralState, meal_type: str, description: str, calories: int, photo_url: str = None) -> Tuple[BehavioralState, int]:
    now_utc = datetime.now().isoformat()
    today = datetime.now().date().isoformat()
    
    # Limpar refeições antigas
    state.meals_today = [m for m in state.meals_today if m.get("date") == today]
    
    has_photo = photo_url is not None
    state.meals_today.append({
        "date": today,
        "type": meal_type,
        "description": description,
        "calories": calories,
        "photo_url": photo_url,
        "time": datetime.now().strftime("%H:%M"),
        "has_photo": has_photo,
    })
    
    # Calcular pontos do dia (parcial)
    today_meals = state.meals_today
    meals_with_photo = sum(1 for m in today_meals if m.get("photo_url"))
    total_calories = sum(m.get("calories", 0) for m in today_meals)
    calorie_goal = state.get_daily_calorie_target()
    has_checkin_today = state.last_checkin and datetime.fromisoformat(state.last_checkin.replace('Z', '+00:00')).date() == datetime.now().date()
    
    daily_points = PointsSystem.calculate_daily_points(
        has_checkin=has_checkin_today,
        meals_count=len(today_meals),
        meals_with_photo=meals_with_photo,
        has_weight=False,
        calorie_goal_achieved=total_calories <= calorie_goal,
        current_streak=state.current_streak
    )
    
    # Atualizar pontos totais (substituindo os anteriores do dia)
    # Remover pontos antigos do dia
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    state.points_history = [p for p in state.points_history if p.get("date", "") < today_start]
    state.points_history.append({"points": daily_points, "date": now_utc, "source": "meals"})
    
    # Recalcular total
    state.total_points = sum(p["points"] for p in state.points_history)
    
    # Atualizar nível
    new_level = 0
    for i, level in enumerate(LEVELS):
        if state.total_points >= level["min_points"]:
            new_level = i
    state.current_level = new_level
    
    return state, daily_points

def process_weight(state: BehavioralState, weight: float) -> BehavioralState:
    now_utc = datetime.now().isoformat()
    state.current_weight = weight
    state.weight_history.append({"weight": weight, "timestamp": now_utc})
    state.weight_history = state.weight_history[-90:]
    
    # Verificar se bateu meta mensal
    progress = calcular_progresso_peso(weight, state.peso_inicio_mes, state.meta_mensal_kg)
    if progress["percentual"] >= 100 and not state.is_premium:
        # Sugerir upgrade para premium
        pass
    
    return state

# ============================================================================
# REPOSITORY (mock)
# ============================================================================
class StateRepository:
    def __init__(self):
        self._state = None
    
    def load_state(self, user_id: str) -> Optional[BehavioralState]:
        if self._state:
            return self._state
        return None
    
    def save_state(self, state: BehavioralState) -> bool:
        self._state = state
        return True

repository = StateRepository()

# ============================================================================
# UI COMPONENTS
# ============================================================================
def render_narrative(state: BehavioralState):
    level_info = state.get_level_info()
    next_level = state.get_next_level_info()
    
    st.markdown(f"""
    <div class="narrative-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.8rem; color: #92400e;">Bom dia! Você está evoluindo.</div>
                <div style="font-weight: 500; margin-top: 4px;">{level_info['desc']}</div>
            </div>
            <div class="level-badge">{level_info['name']}</div>
        </div>
        <div style="margin-top: 12px;">
            <div class="points-badge">⭐ {state.total_points} pontos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics(state: BehavioralState):
    today = datetime.now().date().isoformat()
    today_meals = [m for m in state.meals_today if m.get("date") == today]
    total_calories = sum(m.get("calories", 0) for m in today_meals)
    calorie_target = state.get_daily_calorie_target()
    tmb = state.get_tmb()
    tdee = state.get_tdee()
    
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-value">{state.current_streak}</div>
            <div class="metric-label">🔥 Sequência</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(today_meals)}</div>
            <div class="metric-label">🍽️ Refeições</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_calories}</div>
            <div class="metric-label">🔥 Calorias</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de calorias
    percent = min(100, (total_calories / calorie_target) * 100)
    st.markdown(f"""
    <div style="font-size: 0.7rem; color: #64748b;">Meta diária: {calorie_target} kcal | TMB: {tmb:.0f} | TDEE: {tdee:.0f}</div>
    <div class="progress-bar"><div class="progress-fill" style="width: {percent}%;"></div></div>
    """, unsafe_allow_html=True)
    
    # Progresso para próximo nível
    next_level = state.get_next_level_info()
    progress = state.get_progress_to_next_level()
    st.markdown(f"""
    <div style="margin-top: 16px;">
        <div style="font-size: 0.7rem; color: #64748b;">Próximo nível: {next_level['name']}</div>
        <div class="progress-bar"><div class="progress-fill" style="width: {progress}%; background: linear-gradient(90deg, #8b5cf6, #6d28d9);"></div></div>
        <div style="font-size: 0.7rem; color: #64748b; text-align: right;">{state.total_points} / {next_level['min_points']} pontos</div>
    </div>
    """, unsafe_allow_html=True)

def render_meals(state: BehavioralState) -> Tuple[BehavioralState, bool]:
    today = datetime.now().date().isoformat()
    today_meals = [m for m in state.meals_today if m.get("date") == today]
    
    st.markdown("### 🍽️ Refeições de hoje")
    
    if today_meals:
        for meal in today_meals:
            meal_name = MEAL_TYPES.get(meal.get("type"), {}).get("name", meal.get("type"))
            photo_badge = " 📸" if meal.get("photo_url") else ""
            st.markdown(f"""
            <div class="meal-card">
                <div class="meal-header">
                    <span class="meal-type">{meal_name}{photo_badge}</span>
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
        photo = st.camera_input("Tirar foto do prato (opcional)", help="Fotografar ajuda na consciência alimentar + ganha +5 pontos!")
        
        if st.button("✅ Salvar refeição", use_container_width=True):
            if description:
                photo_url = None
                has_photo = False
                if photo:
                    photo_url = "temp_photo_url"
                    has_photo = True
                state, points_earned = process_meal(state, meal_type, description, calories, photo_url)
                if has_photo:
                    st.success(f"🍽️ Refeição registrada! +{points_earned} pontos (📸 bônus por foto!)")
                else:
                    st.success(f"🍽️ Refeição registrada! +{points_earned} pontos")
                return state, True
            else:
                st.warning("Descreva o que você comeu")
    return state, False

def render_weight_section(state: BehavioralState) -> Tuple[BehavioralState, bool]:
    st.markdown("### ⚖️ Acompanhamento de peso")
    
    col1, col2 = st.columns(2)
    with col1:
        new_weight = st.number_input("Peso atual (kg)", min_value=30.0, max_value=250.0, value=state.current_weight, step=0.1)
    with col2:
        target_weight = st.number_input("Peso desejado (kg)", min_value=30.0, max_value=250.0, value=state.target_weight, step=0.5)
    
    if new_weight != state.current_weight:
        if st.button("💾 Registrar peso (+10 pontos)", use_container_width=True):
            state = process_weight(state, new_weight)
            # Adicionar pontos por registrar peso
            daily_points = PointsSystem.calculate_daily_points(
                has_checkin=False, meals_count=0, meals_with_photo=0,
                has_weight=True, calorie_goal_achieved=False, current_streak=state.current_streak
            )
            state.total_points += daily_points
            state.points_history.append({"points": daily_points, "date": datetime.now().isoformat(), "source": "weight"})
            st.success(f"⚖️ Peso registrado! +{daily_points} pontos")
            return state, True
    
    if target_weight != state.target_weight:
        state.target_weight = target_weight
        st.success("Meta de peso atualizada!")
        return state, True
    
    # Gráfico de evolução
    if len(state.weight_history) >= 2:
        df = pd.DataFrame(state.weight_history[-30:])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        fig = px.line(df, x="timestamp", y="weight", title="Evolução do peso", markers=True)
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0))
        fig.update_traces(line=dict(color="#f59e0b", width=2))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    return state, False

def render_checkin_section(state: BehavioralState) -> Tuple[BehavioralState, bool]:
    st.markdown("---")
    st.markdown("### 😊 Check-in diário")
    
    emotion_cols = st.columns(3)
    selected = None
    for idx, (key, data) in enumerate(EMOTIONS.items()):
        with emotion_cols[idx % 3]:
            if st.button(f"{data['icon']} {data['label']}", key=f"emotion_{key}", use_container_width=True):
                selected = key
    
    if selected:
        state, points_earned = process_checkin(state, selected)
        st.success(f"✅ Presença registrada! Você está se sentindo {EMOTIONS[selected]['label']}. +{points_earned} pontos")
        return state, True
    
    return state, False

def render_history(state: BehavioralState):
    st.markdown("### 📊 Análises e histórico")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolução", "😊 Emoções", "⭐ Pontos", "🔬 Correlações"])
    
    with tab1:
        if len(state.weight_history) >= 2:
            df = pd.DataFrame(state.weight_history[-30:])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            fig = px.line(df, x="timestamp", y="weight", title="Evolução do peso", markers=True)
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Registre peso para ver sua evolução")
    
    with tab2:
        if state.emotion_history:
            df = pd.DataFrame(state.emotion_history[-30:])
            df["date"] = pd.to_datetime(df["timestamp"]).dt.date
            emotion_counts = df.groupby("emotion").size()
            if not emotion_counts.empty:
                fig = px.bar(x=emotion_counts.index, y=emotion_counts.values, 
                            labels={"x": "Emoção", "y": "Frequência"}, color=emotion_counts.index)
                fig.update_layout(height=250, margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
            
            # Correlação humor × refeição
            st.markdown("#### 🔍 Correlação humor × alimentação")
            st.caption("Em breve: análise de como seu humor afeta suas escolhas alimentares")
        else:
            st.info("Registre seu estado emocional para ver análises")
    
    with tab3:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total check-ins", state.total_checkins)
        col2.metric("Maior sequência", f"{state.longest_streak} dias")
        col3.metric("Pontos totais", state.total_points)
        
        if state.points_history:
            df_points = pd.DataFrame(state.points_history[-30:])
            df_points["date"] = pd.to_datetime(df_points["date"]).dt.date
            points_by_day = df_points.groupby("date")["points"].sum().reset_index()
            fig = px.bar(points_by_day, x="date", y="points", title="Pontos por dia")
            fig.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("#### 📊 Análise comportamental")
        
        # Correlação humor × horário
        if state.emotion_history:
            df_emo = pd.DataFrame(state.emotion_history)
            df_emo["hour"] = pd.to_datetime(df_emo["timestamp"]).dt.hour
            emo_by_hour = df_emo.groupby(["hour", "emotion"]).size().unstack(fill_value=0)
            if not emo_by_hour.empty:
                fig = px.imshow(emo_by_hour.T, labels=dict(x="Hora", y="Emoção", color="Frequência"),
                                title="Mapa de calor: Emoções por horário")
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Correlação calorias × humor (se tiver dados)
        st.caption("💡 Análises avançadas disponíveis no plano Premium")

def render_profile(state: BehavioralState) -> Tuple[BehavioralState, bool]:
    st.markdown("### 👤 Meu perfil")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", state.nome)
            idade = st.number_input("Idade", 18, 100, state.idade)
            sexo = st.selectbox("Sexo", ["M", "F"], index=0 if state.sexo == "M" else 1)
        with col2:
            altura = st.number_input("Altura (m)", 1.40, 2.20, state.altura, 0.01)
            objetivo = st.selectbox("Objetivo", options=list(GOAL_TYPES.keys()), format_func=lambda x: GOAL_TYPES[x]["label"])
            atividade = st.selectbox("Nível de atividade", options=list(ACTIVITY_LEVELS.keys()), 
                                     format_func=lambda x: x.capitalize())
        
        if st.form_submit_button("Salvar perfil"):
            state.nome = nome
            state.idade = idade
            state.sexo = sexo
            state.altura = altura
            state.objetivo = objetivo
            state.nivel_atividade = atividade
            st.success("Perfil atualizado!")
            return state, True
    
    # Card de upgrade para premium
    if not state.is_premium:
        st.markdown("---")
        st.markdown("### 💎 Upgrade para Premium")
        st.markdown("""
        - 📊 Análises avançadas (correlações completas)
        - 📥 Exportar dados (CSV/PDF)
        - 📈 Histórico ilimitado
        - 🏆 Desafios exclusivos
        """)
        if st.button("🔥 Assinar Premium (R$ 19,90/mês)", use_container_width=True):
            st.success("🎉 Premium ativado! (modo demonstração)")
            state.is_premium = True
            return state, True
    
    return state, False

def render_premium_banner(state: BehavioralState):
    if not state.is_premium:
        st.info("💎 **Desbloqueie análises avançadas e exportação de dados com o plano Premium!**")
        if st.button("Ver planos", use_container_width=True):
            st.session_state["show_premium"] = True

# ============================================================================
# MAIN
# ============================================================================
def main():
    # Inicializar estado
    user_id = "demo-user"
    state = repository.load_state(user_id)
    if not state:
        state = BehavioralState(user_id=user_id)
    
    # Renderizar UI
    render_narrative(state)
    render_metrics(state)
    
    tabs = st.tabs(["🍽️ Refeições", "⚖️ Peso", "📊 Análises", "👤 Perfil"])
    
    needs_refresh = False
    
    with tabs[0]:
        state, refreshed = render_meals(state)
        if refreshed: needs_refresh = True
    
    with tabs[1]:
        state, refreshed = render_weight_section(state)
        if refreshed: needs_refresh = True
    
    with tabs[2]:
        render_history(state)
        render_premium_banner(state)
    
    with tabs[3]:
        state, refreshed = render_profile(state)
        if refreshed: needs_refresh = True
    
    # Check-in rápido
    state, refreshed = render_checkin_section(state)
    if refreshed: needs_refresh = True
    
    # Salvar estado
    repository.save_state(state)
    
    if needs_refresh:
        st.rerun()
    
    st.caption(f"EmagreSim • Nível {state.get_level_info()['name']} • {state.total_points} pontos • {state.current_streak} dias de sequência")

if __name__ == "__main__":
    main()