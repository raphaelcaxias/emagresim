# app.py — EmagreSim v36.0 "Core Evolution"
# Design: Dark Luxury (Esmeralda + Ouro) - IDENTITY PRESERVED
# Stack: Streamlit + Plotly
# Funcionalidades: TMB/TDEE dinâmico, pontos por tarefas, níveis,
#                 memória narrativa, protocolo de recaída, análise de correlação,
#                 micro-metas contextuais, detecção de risco de abandono,
#                 check-in com reflexão, foto do prato com bônus

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import json
import random
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="EmagreSim • Transformação Inteligente",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# DESIGN SYSTEM — Dark Luxury + Esmeralda + Ouro (IDENTIDADE PRESERVADA)
# ============================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,700;1,9..144,300&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:          #0d1117;
  --bg2:         #161b22;
  --bg3:         #1c2330;
  --surface:     #21262d;
  --border:      #30363d;
  --border-soft: #21262d;
  --emerald:     #2dce89;
  --emerald-dim: #1a7d52;
  --emerald-glow:rgba(45,206,137,0.12);
  --gold:        #f0b429;
  --gold-dim:    rgba(240,180,41,0.15);
  --text:        #e6edf3;
  --text-muted:  #7d8590;
  --text-dim:    #484f58;
  --danger:      #f85149;
  --info:        #58a6ff;
  --warning:     #f0b429;
  --radius:      16px;
  --radius-sm:   10px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main { 
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

.block-container {
  padding: 2rem 1rem 4rem !important;
  max-width: 700px !important;
}

/* Tipografia */
h1, h2, h3 { font-family: 'Fraunces', Georgia, serif; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* Hero Header */
.hero {
  position: relative;
  padding: 36px 28px 28px;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 24px;
  margin-bottom: 20px;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 60% 60% at 85% 20%, rgba(45,206,137,0.08) 0%, transparent 70%);
  pointer-events: none;
}
.hero-eyebrow {
  font-size: 0.68rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--emerald);
  font-weight: 600;
  margin-bottom: 8px;
}
.hero-name {
  font-family: 'Fraunces', serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
  margin-bottom: 6px;
}
.hero-sub {
  font-size: 0.82rem;
  color: var(--text-muted);
  font-weight: 300;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--emerald-glow);
  border: 1px solid var(--emerald-dim);
  color: var(--emerald);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  margin-top: 14px;
  letter-spacing: 0.04em;
}
.hero-streak {
  position: absolute;
  top: 28px; right: 28px;
  text-align: center;
}
.hero-streak-num {
  font-family: 'Fraunces', serif;
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--gold);
  line-height: 1;
}
.hero-streak-label {
  font-size: 0.62rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Companion Card - Memória Narrativa */
.companion-card {
  background: var(--bg2);
  border-left: 3px solid var(--emerald);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 20px;
}
.companion-name {
  font-size: 0.7rem;
  color: var(--emerald);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}
.companion-text {
  font-size: 0.9rem;
  line-height: 1.45;
  color: var(--text);
  font-style: italic;
}
.companion-memory {
  font-size: 0.7rem;
  color: var(--gold);
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}

/* Stat Cards */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.stat-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 14px;
  text-align: center;
  transition: border-color .2s;
}
.stat-card:hover { border-color: var(--emerald-dim); }
.stat-num {
  font-family: 'Fraunces', serif;
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1;
}
.stat-num.green { color: var(--emerald); }
.stat-num.gold  { color: var(--gold); }
.stat-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 4px;
}

/* Progress Bar */
.pbar-wrap { margin: 6px 0 2px; }
.pbar-header { display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-muted); margin-bottom: 6px; }
.pbar-track { background: var(--surface); border-radius: 6px; height: 6px; overflow: hidden; }
.pbar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width .6s cubic-bezier(.4,0,.2,1);
}
.pbar-fill.green { background: linear-gradient(90deg, #2dce89, #20a870); }
.pbar-fill.gold  { background: linear-gradient(90deg, #f0b429, #e07b00); }

/* Meal Cards */
.meal-item {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: border-color .2s;
}
.meal-item:hover { border-color: var(--emerald-dim); }
.meal-type-tag {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--emerald);
  margin-bottom: 4px;
}
.meal-desc { font-size: 0.85rem; color: var(--text); line-height: 1.4; }
.meal-time { font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; }
.meal-kcal {
  font-family: 'Fraunces', serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--emerald);
  white-space: nowrap;
  margin-left: 16px;
}
.meal-photo-badge {
  font-size: 0.6rem;
  background: var(--gold-dim);
  color: var(--gold);
  border-radius: 6px;
  padding: 2px 6px;
  margin-left: 6px;
}

/* Section Headers */
.section-title {
  font-family: 'Fraunces', serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin: 24px 0 12px;
}
.section-title span { color: var(--emerald); }

/* Alert Cards */
.alert-card {
  background: rgba(248,81,73,0.08);
  border: 1px solid rgba(248,81,73,0.3);
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 16px;
}
.alert-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--danger);
  text-transform: uppercase;
  margin-bottom: 6px;
}
.alert-text {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 32px 20px;
  color: var(--text-dim);
}
.empty-state .icon { font-size: 2rem; margin-bottom: 8px; }
.empty-state .msg { font-size: 0.82rem; }

/* Level Card */
.level-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px;
  margin-bottom: 16px;
}
.level-name {
  font-family: 'Fraunces', serif;
  font-size: 1rem;
  color: var(--gold);
  margin-bottom: 4px;
}
.level-desc { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 12px; }

/* Premium Card */
.premium-card {
  background: linear-gradient(135deg, #1a2a1e, #0d1a12);
  border: 1px solid var(--emerald-dim);
  border-radius: 20px;
  padding: 24px;
  margin-top: 20px;
  position: relative;
  overflow: hidden;
}
.premium-card::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 160px; height: 160px;
  background: radial-gradient(circle, rgba(45,206,137,0.12) 0%, transparent 70%);
}
.premium-title {
  font-family: 'Fraunces', serif;
  font-size: 1.2rem;
  color: var(--emerald);
  margin-bottom: 8px;
}
.premium-feature {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin: 6px 0;
}
.premium-feature::before {
  content: '✓';
  color: var(--emerald);
  font-weight: 700;
  font-size: 0.75rem;
}

/* Logo */
.wordmark {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.wordmark-icon {
  width: 36px; height: 36px;
  background: var(--emerald);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}
.wordmark-text {
  font-family: 'Fraunces', serif;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
}
.wordmark-tagline {
  font-size: 0.62rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Footer */
.app-footer {
  text-align: center;
  padding: 24px 0 8px;
  font-size: 0.65rem;
  color: var(--text-dim);
}

/* Overrides Streamlit */
div[data-testid="stTabs"] [role="tablist"] {
  background: var(--bg2) !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  padding: 4px !important;
}
div[data-testid="stTabs"] [role="tab"] {
  background: transparent !important;
  color: var(--text-muted) !important;
  border-radius: 8px !important;
  font-size: 0.78rem !important;
  padding: 6px 12px !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--emerald) !important;
  font-weight: 600 !important;
}
.stButton > button {
  background: var(--emerald) !important;
  color: #0d1117 !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  padding: 10px 18px !important;
  transition: opacity .2s !important;
}
.stButton > button:hover { opacity: 0.9 !important; }
div[data-testid="stNumberInput"] > div,
div[data-testid="stTextInput"] > div,
div[data-testid="stTextArea"] > div {
  background: var(--surface) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius-sm) !important;
}
input, textarea, select {
  background: var(--surface) !important;
  color: var(--text) !important;
}
div[data-testid="stForm"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 20px !important;
}
#MainMenu, header, footer { display: none !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================================
# CONSTANTES
# ============================================================================
EMOTIONS = {
    "motivado":   {"icon": "✨", "label": "Motivado",  "color": "#2dce89", "risk_decay": -0.1},
    "confiante":  {"icon": "💪", "label": "Confiante", "color": "#58a6ff", "risk_decay": -0.05},
    "neutro":     {"icon": "😐", "label": "Neutro",    "color": "#7d8590", "risk_decay": 0},
    "ansioso":    {"icon": "😰", "label": "Ansioso",   "color": "#f0b429", "risk_decay": 0.1},
    "cansado":    {"icon": "😔", "label": "Cansado",   "color": "#f85149", "risk_decay": 0.15},
    "frustrado":  {"icon": "😞", "label": "Frustrado", "color": "#b3413a", "risk_decay": 0.2},
}

MEAL_TYPES = {
    "cafe":   {"name": "Café da manhã",  "icon": "☀️", "order": 1, "cal_hint": 350},
    "almoco": {"name": "Almoço",         "icon": "🥗", "order": 2, "cal_hint": 600},
    "lanche": {"name": "Lanche",         "icon": "🍎", "order": 3, "cal_hint": 200},
    "jantar": {"name": "Jantar",         "icon": "🌙", "order": 4, "cal_hint": 500},
}

LEVELS = [
    {"name": "Iniciante",     "icon": "🌱", "min": 0,     "desc": "Todo começo é válido."},
    {"name": "Explorador",    "icon": "🔥", "min": 500,   "desc": "Descobrindo seu ritmo."},
    {"name": "Persistente",   "icon": "💪", "min": 1500,  "desc": "Construindo consistência."},
    {"name": "Reconstrutor",  "icon": "🔄", "min": 3000,  "desc": "Recair faz parte. Voltar é força."},
    {"name": "Inabalável",    "icon": "⚓", "min": 6000,  "desc": "Sua consistência é sua âncora."},
    {"name": "Guia",          "icon": "🌟", "min": 10000, "desc": "Você inspira pelo exemplo."},
]

GOAL_TYPES = {
    "emagrecer":     {"label": "Emagrecer",          "tdee_adj": -500},
    "ganhar_massa":  {"label": "Ganhar massa",       "tdee_adj": +300},
    "manter":        {"label": "Manter o peso",      "tdee_adj": 0},
}

ACTIVITY_LEVELS = {
    "sedentario": {"label": "Sedentário",     "factor": 1.2},
    "leve":       {"label": "Levemente ativo","factor": 1.375},
    "moderado":   {"label": "Moderadamente",  "factor": 1.55},
    "intenso":    {"label": "Muito ativo",    "factor": 1.725},
    "extremo":    {"label": "Extremamente",   "factor": 1.9},
}

POINTS = {
    "checkin":     10,
    "meal":        15,
    "meal_photo":   5,
    "weight":      10,
    "goal_hit":    30,
    "streak_7":   100,
    "streak_30":  500,
}

# ============================================================================
# CÁLCULOS
# ============================================================================
def calc_tmb(peso, altura, idade, sexo="M"):
    h = altura * 100
    return (10*peso + 6.25*h - 5*idade + 5) if sexo == "M" else (10*peso + 6.25*h - 5*idade - 161)

def calc_tdee(tmb, nivel):
    return tmb * ACTIVITY_LEVELS.get(nivel, ACTIVITY_LEVELS["moderado"])["factor"]

def calc_meta(tdee, objetivo):
    return int(tdee + GOAL_TYPES.get(objetivo, GOAL_TYPES["emagrecer"])["tdee_adj"])

def get_level(pts):
    lvl = LEVELS[0]
    for l in LEVELS:
        if pts >= l["min"]:
            lvl = l
    return lvl

def get_next_level(pts):
    for l in LEVELS:
        if pts < l["min"]:
            return l
    return LEVELS[-1]

def level_progress(pts):
    nl = get_next_level(pts)
    idx = LEVELS.index(nl)
    prev_min = LEVELS[idx-1]["min"] if idx > 0 else 0
    span = nl["min"] - prev_min
    return min(100, (pts - prev_min) / span * 100) if span > 0 else 0

def calculate_risk_score(state) -> float:
    risk = 0.0
    if state.last_checkin:
        try:
            last = datetime.fromisoformat(state.last_checkin)
            days_gap = (datetime.now() - last).days
            if days_gap >= 3:
                risk += 20 * min(3, days_gap / 3)
            elif days_gap >= 1:
                risk += 5 * days_gap
        except:
            pass
    recent_emotions = state.emotion_history[-14:]
    negative_emotions = ["ansioso", "cansado", "frustrado"]
    for e in recent_emotions:
        if e.get("emotion") in negative_emotions:
            risk += 10
    if len(state.today_meals()) < 2:
        risk += 10
    if state.streak == 0 and state.total_checkins > 5:
        risk += 15
    return min(100, risk)

def get_psychological_mode(state) -> str:
    risk = calculate_risk_score(state)
    if risk >= 60:
        return "survival"
    if risk >= 30:
        return "returning"
    if state.streak >= 7 and state.total_points >= 500:
        return "stable"
    return "normal"

def get_micro_goal(mode: str) -> str:
    goals = {
        "survival": [
            "Hoje só abra o app. Nada além disso importa.",
            "Beba um copo d'água agora.",
            "Registre como você está se sentindo — só isso já conta.",
        ],
        "returning": [
            "Registre uma refeição hoje. Apenas uma.",
            "Não tente compensar o tempo perdido. Um passo de cada vez.",
            "Olhe para o que você já conquistou. Isso não desapareceu.",
        ],
        "stable": [
            "Mantenha o ritmo. Você está no caminho certo.",
            "Que tal adicionar uma cor nova no seu prato hoje?",
            "Continue com a consistência. Ela é sua maior aliada.",
        ],
        "normal": [
            "Registre seu estado emocional agora.",
            "Faça uma refeição consciente, sem pressa.",
            "Anote uma coisa que você fez bem hoje.",
        ],
    }
    return random.choice(goals.get(mode, goals["normal"]))

def get_companion_message(state) -> str:
    risk = calculate_risk_score(state)
    mode = get_psychological_mode(state)
    if mode == "survival":
        return "Hoje o único objetivo é se manter presente. Nada além disso importa. Você está seguro aqui."
    if mode == "returning":
        return "Você voltou. Isso é o que realmente importa. O tempo fora não apaga o que você já construiu."
    if risk > 50:
        return f"Você está há {state.streak} dias presente. Cuidado com o cansaço emocional. Vá com calma hoje."
    if state.streak >= 7:
        return f"{state.streak} dias seguidos. Isso não é sorte — é consistência real. Você está construindo algo sólido."
    if len(state.emotion_history) >= 10:
        return "Você já registrou suas emoções várias vezes. Isso é autocuidado. Continue."
    return "Sua presença hoje já é um ato de cuidado. Um dia de cada vez."

def get_memory_line(state) -> str:
    memories = []
    if state.longest_streak >= 14:
        memories.append(f"✨ Você já alcançou {state.longest_streak} dias seguidos. Essa força ainda está em você.")
    if len(state.emotion_history) >= 30:
        positive = sum(1 for e in state.emotion_history if e.get("emotion") in ["motivado", "confiante"])
        if positive > 15:
            memories.append(f"💚 Em {len(state.emotion_history)} registros, você teve {positive} momentos de confiança. Isso é resiliência.")
    if state.total_points >= 1000:
        memories.append(f"⭐ Você já acumulou {state.total_points} pontos. Cada um deles representa um passo que você não desistiu de dar.")
    return random.choice(memories) if memories else ""

# ============================================================================
# STATE
# ============================================================================
@dataclass
class AppState:
    nome: str = "Atleta"
    sexo: str = "M"
    idade: int = 28
    altura: float = 1.72
    objetivo: str = "emagrecer"
    nivel_atividade: str = "moderado"
    peso_atual: float = 82.0
    peso_meta: float = 72.0
    peso_inicio: float = 82.0
    total_points: int = 0
    streak: int = 0
    longest_streak: int = 0
    total_checkins: int = 0
    last_checkin: Optional[str] = None
    meals_today: List[Dict] = field(default_factory=list)
    weight_history: List[Dict] = field(default_factory=list)
    emotion_history: List[Dict] = field(default_factory=list)
    points_log: List[Dict] = field(default_factory=list)
    is_premium: bool = False

    def meta_calorica(self):
        tmb = calc_tmb(self.peso_atual, self.altura, self.idade, self.sexo)
        tdee = calc_tdee(tmb, self.nivel_atividade)
        return calc_meta(tdee, self.objetivo)

    def tmb(self):
        return calc_tmb(self.peso_atual, self.altura, self.idade, self.sexo)

    def tdee(self):
        return calc_tdee(self.tmb(), self.nivel_atividade)

    def today_str(self):
        return date.today().isoformat()

    def today_meals(self):
        return [m for m in self.meals_today if m.get("date") == self.today_str()]

    def today_calories(self):
        return sum(m.get("calories", 0) for m in self.today_meals())

    def add_points(self, pts, source=""):
        self.total_points += pts
        self.points_log.append({"pts": pts, "source": source, "date": datetime.now().isoformat()})

# ============================================================================
# SESSION STATE
# ============================================================================
if "state" not in st.session_state:
    st.session_state.state = AppState()

S: AppState = st.session_state.state

# ============================================================================
# HELPERS
# ============================================================================
def save():
    st.session_state.state = S

def pbar(label_left, label_right, pct, cls="green"):
    pct = max(0, min(100, pct))
    st.markdown(f"""
    <div class="pbar-wrap">
      <div class="pbar-header"><span>{label_left}</span><span>{label_right}</span></div>
      <div class="pbar-track"><div class="pbar-fill {cls}" style="width:{pct}%"></div></div>
    </div>""", unsafe_allow_html=True)

def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

# ============================================================================
# LOGO
# ============================================================================
st.markdown("""
<div class="wordmark">
  <div class="wordmark-icon">🌱</div>
  <div>
    <div class="wordmark-text">EmagreSim</div>
    <div class="wordmark-tagline">Transformação Inteligente</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# HERO + COMPANION
# ============================================================================
level = get_level(S.total_points)
hora = datetime.now().hour
saudacao = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")

st.markdown(f"""
<div class="hero">
  <div class="hero-streak">
    <div class="hero-streak-num">{S.streak}</div>
    <div class="hero-streak-label">dias seguidos</div>
  </div>
  <div class="hero-eyebrow">{saudacao}, {S.nome.split()[0]}</div>
  <div class="hero-name">Sua jornada<br/><em style="font-style:italic;font-weight:300">continua hoje.</em></div>
  <div class="hero-sub">{level['desc']}</div>
  <div class="hero-badge">{level['icon']} {level['name']} · ⭐ {S.total_points} pts</div>
</div>
""", unsafe_allow_html=True)

companion_msg = get_companion_message(S)
memory_line = get_memory_line(S)

st.markdown(f"""
<div class="companion-card">
  <div class="companion-name">🌿 seu companion</div>
  <div class="companion-text">“{companion_msg}”</div>
  {f'<div class="companion-memory">🧠 {memory_line}</div>' if memory_line else ''}
</div>
""", unsafe_allow_html=True)

# Modo Sobrevivência / Alerta
risk = calculate_risk_score(S)
mode = get_psychological_mode(S)

if mode == "survival":
    st.markdown(f"""
    <div class="alert-card">
      <div class="alert-title">🛡️ Modo Sobrevivência</div>
      <div class="alert-text">O momento é de acolhimento, não de pressão. Hoje foque apenas em presença.</div>
    </div>
    """, unsafe_allow_html=True)

micro_goal = get_micro_goal(mode)
st.markdown(f"""
<div style="background: var(--bg2); border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; border-left: 3px solid var(--gold);">
  <div style="font-size: 0.7rem; color: var(--gold); text-transform: uppercase;">🎯 micro-meta do dia</div>
  <div style="font-size: 0.85rem; margin-top: 4px;">{micro_goal}</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# STAT CARDS
# ============================================================================
meta = S.meta_calorica()
cal_today = S.today_calories()
diff_peso = round(S.peso_inicio - S.peso_atual, 1)
diff_str = f"-{diff_peso} kg" if diff_peso >= 0 else f"+{abs(diff_peso)} kg"

st.markdown(f"""
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-num green">{cal_today}</div>
    <div class="stat-label">kcal hoje</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{meta}</div>
    <div class="stat-label">meta diária</div>
  </div>
  <div class="stat-card">
    <div class="stat-num gold">{diff_str}</div>
    <div class="stat-label">progresso</div>
  </div>
</div>
""", unsafe_allow_html=True)

pct_cal = (cal_today / meta * 100) if meta > 0 else 0
pbar(f"🔥 {cal_today} kcal consumidas", f"Meta: {meta} kcal", pct_cal, "green")

lp = level_progress(S.total_points)
nl = get_next_level(S.total_points)
pbar(f"{level['icon']} {level['name']}", f"→ {nl['icon']} {nl['name']} ({nl['min']} pts)", lp, "gold")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ============================================================================
# ABAS
# ============================================================================
tabs = st.tabs(["🥗 Refeições", "⚖️ Peso", "📊 Análises", "👤 Perfil"])

# ─────────────────────────────────────────────────────────────────────────────
# ABA: REFEIÇÕES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    section("Refeições de hoje")

    today_m = S.today_meals()
    if today_m:
        for m in today_m:
            mt = MEAL_TYPES.get(m.get("type", "cafe"), MEAL_TYPES["cafe"])
            photo_badge = '<span class="meal-photo-badge">📸 foto</span>' if m.get("has_photo") else ""
            st.markdown(f"""
            <div class="meal-item">
              <div>
                <div class="meal-type-tag">{mt['icon']} {mt['name']}{photo_badge}</div>
                <div class="meal-desc">{m.get('description','')}</div>
                <div class="meal-time">⏱ {m.get('time','--:--')}</div>
              </div>
              <div class="meal-kcal">{m.get('calories',0)}<br/><span style="font-size:.6rem;color:#7d8590;">kcal</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">🥗</div>
          <div class="msg">Nenhuma refeição registrada hoje.<br/>Adicione sua primeira refeição abaixo.</div>
        </div>""", unsafe_allow_html=True)

    with st.expander("➕ Registrar refeição", expanded=not today_m):
        c1, c2 = st.columns(2)
        with c1:
            meal_type = st.selectbox("Tipo", options=list(MEAL_TYPES.keys()),
                                     format_func=lambda x: f"{MEAL_TYPES[x]['icon']} {MEAL_TYPES[x]['name']}")
        with c2:
            calories = st.number_input("Calorias (kcal)", 0, 2000, MEAL_TYPES[meal_type]["cal_hint"], 25)
        desc = st.text_area("Descreva sua refeição", placeholder="Ex: Arroz integral, frango grelhado, brócolis...", height=72)
        photo = st.camera_input("📸 Foto do prato (bônus +5 pts)")

        if st.button("✅ Salvar refeição", use_container_width=True):
            if desc.strip():
                has_photo = photo is not None
                S.meals_today.append({
                    "date": S.today_str(),
                    "type": meal_type,
                    "description": desc.strip(),
                    "calories": calories,
                    "has_photo": has_photo,
                    "time": datetime.now().strftime("%H:%M"),
                })
                pts = POINTS["meal"] + (POINTS["meal_photo"] if has_photo else 0)
                S.add_points(pts, "meal")
                save()
                bonus = " + bônus de foto 📸" if has_photo else ""
                st.success(f"Refeição salva! +{pts} pontos{bonus}")
                st.rerun()
            else:
                st.warning("Descreva o que você comeu.")

# ─────────────────────────────────────────────────────────────────────────────
# ABA: PESO
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    section("Registrar peso")

    c1, c2 = st.columns(2)
    with c1:
        novo_peso = st.number_input("Peso atual (kg)", 30.0, 300.0, S.peso_atual, 0.1)
    with c2:
        nova_meta = st.number_input("Peso desejado (kg)", 30.0, 300.0, S.peso_meta, 0.5)

    if st.button("💾 Registrar peso (+10 pts)", use_container_width=True):
        S.peso_atual = novo_peso
        S.peso_meta = nova_meta
        S.weight_history.append({"weight": novo_peso, "date": S.today_str()})
        S.add_points(POINTS["weight"], "weight")
        save()
        st.success(f"Peso registrado: {novo_peso} kg · +10 pontos")
        st.rerun()

    imc = S.peso_atual / (S.altura ** 2)
    faltam = max(0, S.peso_atual - S.peso_meta)
    perdidos = max(0, S.peso_inicio - S.peso_atual)

    c1, c2, c3 = st.columns(3)
    c1.metric("IMC", f"{imc:.1f}")
    c2.metric("Perdidos", f"{perdidos:.1f} kg")
    c3.metric("Faltam", f"{faltam:.1f} kg")

    if len(S.weight_history) >= 2:
        df = pd.DataFrame(S.weight_history[-60:])
        df["date"] = pd.to_datetime(df["date"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["weight"],
            mode="lines+markers",
            line=dict(color="#2dce89", width=2.5),
            marker=dict(color="#2dce89", size=6),
            fill="tozeroy",
            fillcolor="rgba(45,206,137,0.07)"
        ))
        fig.add_hline(y=S.peso_meta, line=dict(color="#f0b429", width=1, dash="dot"),
                      annotation_text=f"Meta: {S.peso_meta} kg",
                      annotation_font_color="#f0b429", annotation_font_size=10)
        fig.update_layout(
            height=240, margin=dict(l=0, r=0, t=16, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#7d8590", size=10, family="DM Sans"),
            xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown("""
        <div class="empty-state" style="padding:20px">
          <div class="icon">📉</div>
          <div class="msg">Registre ao menos 2 pesos para ver seu gráfico.</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ABA: ANÁLISES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    section("Dashboard analítico")

    sub_tabs = st.tabs(["📈 Evolução", "😊 Emoções", "⭐ Pontos", "🔬 Correlações"])

    with sub_tabs[0]:
        if len(S.weight_history) >= 2:
            df = pd.DataFrame(S.weight_history[-60:])
            df["date"] = pd.to_datetime(df["date"])
            fig = go.Figure(go.Scatter(
                x=df["date"], y=df["weight"],
                mode="lines+markers",
                line=dict(color="#2dce89", width=2),
                marker=dict(color="#2dce89", size=5),
            ))
            fig.update_layout(height=220, margin=dict(l=0, r=0, t=8, b=0),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#7d8590", size=10), showlegend=False,
                              xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Registre peso para ver sua evolução.")

    with sub_tabs[1]:
        if S.emotion_history:
            df_emo = pd.DataFrame(S.emotion_history)
            counts = df_emo["emotion"].value_counts().reset_index()
            counts.columns = ["emotion","count"]
            colors_map = {k: v["color"] for k,v in EMOTIONS.items()}
            counts["color"] = counts["emotion"].map(colors_map).fillna("#7d8590")
            fig = go.Figure(go.Bar(x=counts["emotion"], y=counts["count"], marker_color=counts["color"]))
            fig.update_layout(height=220, margin=dict(l=0, r=0, t=8, b=0),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#7d8590", size=10), showlegend=False,
                              xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Faça check-ins emocionais para ver análises de humor.")

    with sub_tabs[2]:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de pontos", S.total_points)
        c2.metric("Maior sequência", f"{S.longest_streak}d")
        c3.metric("Check-ins", S.total_checkins)

        if S.points_log:
            df_pts = pd.DataFrame(S.points_log)
            df_pts["date"] = pd.to_datetime(df_pts["date"]).dt.date
            by_day = df_pts.groupby("date")["pts"].sum().reset_index()
            fig = go.Figure(go.Bar(x=by_day["date"], y=by_day["pts"], marker_color="#f0b429"))
            fig.update_layout(height=220, margin=dict(l=0, r=0, t=8, b=0),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with sub_tabs[3]:
        st.markdown("#### 🧠 Correlação humor × alimentação")
        if S.emotion_history and S.meals_today:
            avg_cal_positive = 0
            avg_cal_negative = 0
            count_pos = 0
            count_neg = 0
            for meal in S.meals_today[-14:]:
                meal_date = meal.get("date")
                for emo in S.emotion_history[-30:]:
                    if emo.get("timestamp", "")[:10] == meal_date:
                        if emo.get("emotion") in ["motivado", "confiante"]:
                            avg_cal_positive += meal.get("calories", 0)
                            count_pos += 1
                        elif emo.get("emotion") in ["ansioso", "cansado", "frustrado"]:
                            avg_cal_negative += meal.get("calories", 0)
                            count_neg += 1
                        break
            if count_pos > 0:
                st.metric("Média calorias (dias positivos)", f"{avg_cal_positive/count_pos:.0f} kcal")
            if count_neg > 0:
                st.metric("Média calorias (dias difíceis)", f"{avg_cal_negative/count_neg:.0f} kcal")
            st.caption("💡 Quando você está motivado, suas escolhas alimentares tendem a ser mais equilibradas.")
        else:
            st.info("Registre emoções e refeições para ver correlações.")

    if not S.is_premium:
        st.markdown("""
        <div class="premium-card">
          <div class="premium-title">EmagreSim Premium</div>
          <div class="premium-feature">Correlação humor × alimentação completa</div>
          <div class="premium-feature">Exportação de relatórios (PDF / CSV)</div>
          <div class="premium-feature">Histórico ilimitado de 365 dias</div>
          <div class="premium-feature">Desafios exclusivos e conquistas</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Assinar Premium — R$ 19,90/mês", use_container_width=True):
            S.is_premium = True
            save()
            st.success("🎉 Bem-vindo ao Premium!")
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ABA: PERFIL
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    section("Meu perfil")

    st.markdown(f"""
    <div class="level-card">
      <div class="level-name">{level['icon']} {level['name']}</div>
      <div class="level-desc">{level['desc']}</div>
    </div>
    """, unsafe_allow_html=True)
    pbar(f"⭐ {S.total_points} pts", f"→ {nl['icon']} {nl['name']} ({nl['min']} pts)", lp, "gold")

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome   = st.text_input("Nome", S.nome)
            idade  = st.number_input("Idade", 16, 100, S.idade)
            sexo   = st.selectbox("Sexo biológico", ["M","F"],
                                  index=0 if S.sexo == "M" else 1,
                                  format_func=lambda x: "Masculino" if x == "M" else "Feminino")
        with c2:
            altura = st.number_input("Altura (m)", 1.40, 2.20, S.altura, 0.01)
            obj    = st.selectbox("Objetivo", list(GOAL_TYPES.keys()),
                                  format_func=lambda x: GOAL_TYPES[x]["label"])
            ativ   = st.selectbox("Nível de atividade", list(ACTIVITY_LEVELS.keys()),
                                  format_func=lambda x: ACTIVITY_LEVELS[x]["label"])
        if st.form_submit_button("💾 Salvar perfil", use_container_width=True):
            S.nome = nome; S.idade = idade; S.sexo = sexo
            S.altura = altura; S.objetivo = obj; S.nivel_atividade = ativ
            save()
            st.success("Perfil atualizado!")

    tmb_v = S.tmb()
    tdee_v = S.tdee()
    c1, c2, c3 = st.columns(3)
    c1.metric("TMB", f"{tmb_v:.0f} kcal")
    c2.metric("TDEE", f"{tdee_v:.0f} kcal")
    c3.metric("Meta", f"{S.meta_calorica()} kcal")

# ============================================================================
# CHECK-IN EMOCIONAL COM REFLEXÃO
# ============================================================================
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
section("Check-in emocional")
st.markdown('<div style="font-size:.78rem;color:#7d8590;margin-bottom:12px;">Como você está se sentindo agora?</div>', unsafe_allow_html=True)

cols = st.columns(len(EMOTIONS))
selected_emotion = None
for i, (key, data) in enumerate(EMOTIONS.items()):
    with cols[i]:
        if st.button(f"{data['icon']}\n{data['label']}", key=f"emo_{key}", use_container_width=True):
            selected_emotion = key

if selected_emotion:
    reflection = st.text_area("O que aconteceu hoje? (opcional)", 
                               placeholder="Compartilhe como foi seu dia...", 
                               height=60, key="reflection_input")

    if S.last_checkin:
        try:
            last = datetime.fromisoformat(S.last_checkin).date()
            delta = (date.today() - last).days
            if delta == 1:
                S.streak += 1
            elif delta > 1:
                S.streak = 1
        except:
            S.streak = 1
    else:
        S.streak = 1

    S.longest_streak = max(S.longest_streak, S.streak)
    S.total_checkins += 1
    S.last_checkin = datetime.now().isoformat()
    S.emotion_history.append({"emotion": selected_emotion, "timestamp": datetime.now().isoformat(), "reflection": reflection})
    S.emotion_history = S.emotion_history[-90:]

    pts = POINTS["checkin"]
    if S.streak > 0 and S.streak % 7 == 0:
        pts += POINTS["streak_7"]
        st.balloons()
    S.add_points(pts, "checkin")
    save()

    st.success(f"{EMOTIONS[selected_emotion]['icon']} Check-in registrado! Você está se sentindo **{EMOTIONS[selected_emotion]['label']}**. +{pts} pontos")
    if reflection:
        st.info("💬 Sua reflexão foi salva. Isso ajuda a identificar padrões.")
    st.rerun()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown(f"""
<div class="app-footer">
  EMAGRESIM · {level['icon']} {level['name']} · ⭐ {S.total_points} pts · 🔥 {S.streak} dias<br/>
  Transformação Inteligente • Feito com 💚 para quem não desiste
</div>
""", unsafe_allow_html=True)