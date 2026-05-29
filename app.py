# app.py — EmagreSim v36.0 "Core Evolution"
# Design: Dark Luxury (Esmeralda + Ouro) - IDENTITY PRESERVED
# Stack: Streamlit + Plotly

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, date
from typing import Optional, Dict, List
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
# DESIGN SYSTEM — Dark Luxury + Esmeralda + Ouro
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
  --emerald:     #2dce89;
  --emerald-dim: #1a7d52;
  --emerald-glow: rgba(45,206,137,0.08);
  --gold:        #f0b429;
  --gold-dim:    rgba(240,180,41,0.15);
  --text:        #e6edf3;
  --text-muted:  #7d8590;
  --text-dim:    #484f58;
  --danger:      #f85149;
  --radius:      16px;
  --radius-sm:   10px;
}

/* Base App Reset */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main { 
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

.block-container {
  padding: 2rem 1rem 4rem !important;
  max-width: 680px !important;
}

h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

/* Hero Header */
.hero {
  position: relative;
  padding: 32px 28px;
  background: linear-gradient(145deg, var(--bg2), #12161f);
  border: 1px solid var(--border);
  border-radius: 24px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(circle at 90% 10%, rgba(45,206,137,0.1) 0%, transparent 60%);
  pointer-events: none;
}
.hero-eyebrow {
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--emerald);
  font-weight: 600;
  margin-bottom: 8px;
}
.hero-name {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.15;
  margin-bottom: 8px;
}
.hero-sub {
  font-size: 0.85rem;
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
  font-size: 0.75rem;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 30px;
  margin-top: 16px;
}
.hero-streak {
  position: absolute;
  top: 32px; right: 32px;
  text-align: center;
  background: rgba(0, 0, 0, 0.15);
  padding: 8px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.03);
}
.hero-streak-num {
  font-family: 'Fraunces', serif;
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--gold);
  line-height: 1;
}
.hero-streak-label {
  font-size: 0.6rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* Companion Card */
.companion-card {
  background: var(--bg2);
  border-left: 4px solid var(--emerald);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.companion-name {
  font-size: 0.7rem;
  color: var(--emerald);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
  font-weight: 600;
}
.companion-text {
  font-size: 0.92rem;
  line-height: 1.5;
  color: var(--text);
  font-style: italic;
}
.companion-memory {
  font-size: 0.75rem;
  color: var(--gold);
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}

/* Stat Cards */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 12px;
  text-align: center;
  transition: all .2s ease;
}
.stat-card:hover { border-color: var(--emerald-dim); transform: translateY(-2px); }
.stat-num {
  font-family: 'Fraunces', serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.1;
}
.stat-num.green { color: var(--emerald); }
.stat-num.gold  { color: var(--gold); }
.stat-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 6px;
}

/* Progress Bar */
.pbar-wrap { margin: 12px 0; }
.pbar-header { display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 6px; }
.pbar-track { background: var(--surface); border-radius: 20px; height: 8px; overflow: hidden; }
.pbar-fill { height: 100%; border-radius: 20px; transition: width .6s ease; }
.pbar-fill.green { background: linear-gradient(90deg, #2dce89, #20a870); }
.pbar-fill.gold  { background: linear-gradient(90deg, #f0b429, #e07b00); }

/* Meal Cards */
.meal-item {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.meal-type-tag {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--emerald);
  margin-bottom: 4px;
}
.meal-desc { font-size: 0.9rem; color: var(--text); line-height: 1.4; }
.meal-time { font-size: 0.7rem; color: var(--text-muted); margin-top: 4px; }
.meal-kcal {
  font-family: 'Fraunces', serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--emerald);
  text-align: right;
  line-height: 1;
}
.meal-photo-badge {
  font-size: 0.6rem;
  background: var(--gold-dim);
  color: var(--gold);
  border-radius: 4px;
  padding: 1px 6px;
  margin-left: 6px;
  border: 1px solid rgba(240,180,41,0.2);
}

/* Section Headers */
.section-title {
  font-family: 'Fraunces', serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  margin: 28px 0 14px;
}

/* Alert Cards */
.alert-card {
  background: rgba(248,81,73,0.06);
  border: 1px solid rgba(248,81,73,0.25);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 20px;
}
.alert-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--danger);
  text-transform: uppercase;
  margin-bottom: 4px;
}
.alert-text { font-size: 0.85rem; color: var(--text-muted); }

/* Empty State */
.empty-state { text-align: center; padding: 40px 20px; color: var(--text-dim); }
.empty-state .icon { font-size: 2.5rem; margin-bottom: 8px; }
.empty-state .msg { font-size: 0.88rem; color: var(--text-muted); }

/* Premium Card */
.premium-card {
  background: linear-gradient(135deg, #132219, #0d1117);
  border: 1px solid rgba(45,206,137,0.2);
  border-radius: 20px;
  padding: 24px;
  margin-top: 24px;
}
.premium-title {
  font-family: 'Fraunces', serif;
  font-size: 1.3rem;
  color: var(--emerald);
  margin-bottom: 12px;
}
.premium-feature {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 8px 0;
}
.premium-feature::before { content: '✓'; color: var(--emerald); font-weight: 700; }

/* Footers & Tabs Custom */
.app-footer { text-align: center; padding: 40px 0 10px; font-size: 0.7rem; color: var(--text-dim); line-height: 1.6; }

div[data-testid="stTabs"] [role="tablist"] {
  background: var(--bg2) !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  padding: 4px !important;
  gap: 4px;
}
div[data-testid="stTabs"] [role="tab"] {
  background: transparent !important;
  color: var(--text-muted) !important;
  border-radius: 6px !important;
  font-size: 0.85rem !important;
  padding: 8px 16px !important;
  border: none !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--emerald) !important;
  font-weight: 600 !important;
}
.stButton > button {
  background: linear-gradient(135deg, var(--emerald), #24b274) !important;
  color: #0d1117 !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 12px 24px !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 12px rgba(45,206,137,0.2) !important;
}
.stButton > button:hover { opacity: 0.95 !important; transform: translateY(-1px); }
div[data-testid="stForm"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 24px !important;
}
header, footer { display: none !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================================
# CONSTANTS & CONFIGURATIONS
# ============================================================================
EMOTIONS = {
    "motivado":   {"icon": "✨", "label": "Motivado",  "color": "#2dce89"},
    "confiante":  {"icon": "💪", "label": "Confiante", "color": "#58a6ff"},
    "neutro":     {"icon": "😐", "label": "Neutro",    "color": "#7d8590"},
    "ansioso":    {"icon": "😰", "label": "Ansioso",   "color": "#f0b429"},
    "cansado":    {"icon": "😔", "label": "Cansado",   "color": "#f85149"},
    "frustrado":  {"icon": "😞", "label": "Frustrado", "color": "#b3413a"},
}

MEAL_TYPES = {
    "cafe":   {"name": "Café da manhã",  "icon": "☀️", "cal_hint": 350},
    "almoco": {"name": "Almoço",         "icon": "🥗", "cal_hint": 600},
    "lanche": {"name": "Lanche",         "icon": "🍎", "cal_hint": 200},
    "jantar": {"name": "Jantar",         "icon": "🌙", "cal_hint": 500},
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
    "checkin": 10, "meal": 15, "meal_photo": 5, "weight": 10, "streak_7": 100
}

# ============================================================================
# DATA ENGINE & MATH
# ============================================================================
def calc_tmb(peso: float, altura: float, idade: int, sexo: str) -> float:
    h = altura * 100
    return (10 * peso + 6.25 * h - 5 * idade + 5) if sexo == "M" else (10 * peso + 6.25 * h - 5 * idade - 161)

def calc_tdee(tmb: float, nivel: str) -> float:
    return tmb * ACTIVITY_LEVELS.get(nivel, ACTIVITY_LEVELS["moderado"])["factor"]

def get_level(pts: int) -> Dict:
    for l in reversed(LEVELS):
        if pts >= l["min"]: return l
    return LEVELS[0]

def get_next_level(pts: int) -> Dict:
    for l in LEVELS:
        if pts < l["min"]: return l
    return LEVELS[-1]

def level_progress(pts: int) -> float:
    nl = get_next_level(pts)
    idx = LEVELS.index(nl)
    prev_min = LEVELS[idx-1]["min"] if idx > 0 else 0
    span = nl["min"] - prev_min
    return min(100.0, float((pts - prev_min) / span * 100)) if span > 0 else 100.0

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
    meals_history: List[Dict] = field(default_factory=list)
    weight_history: List[Dict] = field(default_factory=list)
    emotion_history: List[Dict] = field(default_factory=list)
    points_log: List[Dict] = field(default_factory=list)
    is_premium: bool = False

    def meta_calorica(self) -> int:
        tmb = calc_tmb(self.peso_atual, self.altura, self.idade, self.sexo)
        tdee = calc_tdee(tmb, self.nivel_atividade)
        return int(tdee + GOAL_TYPES.get(self.objetivo, GOAL_TYPES["emagrecer"])["tdee_adj"])

    def today_str(self) -> str:
        return date.today().isoformat()

    def today_meals(self) -> List[Dict]:
        return [m for m in self.meals_history if m.get("date") == self.today_str()]

    def today_calories(self) -> int:
        return sum(m.get("calories", 0) for m in self.today_meals())

    def add_points(self, pts: int, source: str):
        self.total_points += pts
        self.points_log.append({"pts": pts, "source": source, "date": self.today_str()})

# Initialize Session State
if "state" not in st.session_state:
    st.session_state.state = AppState()
if "selected_emotion" not in st.session_state:
    st.session_state.selected_emotion = None

S: AppState = st.session_state.state

# ============================================================================
# PSYCHOLOGICAL & RISK INTELLIGENCE
# ============================================================================
def calculate_risk_score() -> float:
    risk = 0.0
    if S.last_checkin:
        days_gap = (date.today() - date.fromisoformat(S.last_checkin)).days
        if days_gap >= 3: risk += 30
        elif days_gap >= 1: risk += 10
    
    negatives = sum(1 for e in S.emotion_history[-7:] if e.get("emotion") in ["ansioso", "cansado", "frustrado"])
    risk += negatives * 12
    if len(S.today_meals()) == 0: risk += 10
    return min(100.0, risk)

def get_psychological_mode() -> str:
    risk = calculate_risk_score()
    if risk >= 55: return "survival"
    if risk >= 30: return "returning"
    if S.streak >= 7: return "stable"
    return "normal"

def get_micro_goal(mode: str) -> str:
    goals = {
        "survival": ["Apenas mantenha o app aberto hoje. Estar aqui já é vencer.", "Beba um copo de água agora.", "Escreva uma única palavra sobre seu sentimento."],
        "returning": ["Registre apenas uma refeição hoje. Sem cobranças por perfeição.", "Dê um passo pequeno. O passado está no passado.", "Escreva o motivo número 1 de você ter começado."],
        "stable": ["Adicione uma cor nova e natural no seu próximo prato.", "Tente fazer 5 minutos de respiração consciente hoje.", "Mantenha o ritmo básico. A consistência vive no tédio positivo."],
        "normal": ["Registre uma refeição em tempo real.", "Faça uma refeição longe de telas hoje.", "Beba 500ml de água na próxima hora."]
    }
    return random.choice(goals[mode])

def get_companion_message(mode: str) -> str:
    messages = {
        "survival": "Hoje o foco é reduzir o peso mental. Sem metas complexas. Só fique aqui com a gente.",
        "returning": "Você escolheu voltar, e voltar é o comportamento dos fortes. O placar recomeça agora.",
        "stable": f"Sua sequência de {S.streak} dias está gerando novos caminhos neurais. Excelente consistência.",
        "normal": "Sua saúde é um ativo construído em silêncio. Um dia comum bem feito é um dia ganho."
    }
    return messages[mode]

# ============================================================================
# RENDERING UTILITIES
# ============================================================================
def render_pbar(label_left: str, label_right: str, pct: float, cls: str = "green"):
    st.markdown(f"""
    <div class="pbar-wrap">
      <div class="pbar-header"><span>{label_left}</span><span>{label_right}</span></div>
      <div class="pbar-track"><div class="pbar-fill {cls}" style="width:{max(0.0, min(100.0, pct))}%"></div></div>
    </div>""", unsafe_allow_html=True)

# ============================================================================
# UI HEADER
# ============================================================================
st.markdown("""
<div class="wordmark">
  <div class="wordmark-icon">🌱</div>
  <div><div class="wordmark-text">EmagreSim</div><div class="wordmark-tagline">v36.0 • Core Evolution</div></div>
</div>""", unsafe_allow_html=True)

# Context Calculus
current_mode = get_psychological_mode()
lvl = get_level(S.total_points)
saudacao = "Bom dia" if datetime.now().hour < 12 else ("Boa tarde" if datetime.now().hour < 18 else "Boa noite")

st.markdown(f"""
<div class="hero">
  <div class="hero-streak"><div class="hero-streak-num">{S.streak}</div><div class="hero-streak-label">Dias Seguidos</div></div>
  <div class="hero-eyebrow">{saudacao}, {S.nome.split()[0]}</div>
  <div class="hero-name">Sua jornada<br/><em style="font-style:italic;font-weight:300">continua hoje.</em></div>
  <div class="hero-sub">{lvl['desc']}</div>
  <div class="hero-badge">{lvl['icon']} {lvl['name']} · ⭐ {S.total_points} pts</div>
</div>""", unsafe_allow_html=True)

# Companion
st.markdown(f"""
<div class="companion-card">
  <div class="companion-name">🌿 Companion Co-Piloto</div>
  <div class="companion-text">“{get_companion_message(current_mode)}”</div>
  {f'<div class="companion-memory">🧠 Memória Dinâmica: Você já acumulou {S.total_points} pontos nesta jornada. Continue firme.</div>' if S.total_points > 100 else ''}
</div>""", unsafe_allow_html=True)

if current_mode == "survival":
    st.markdown("""
    <div class="alert-card">
      <div class="alert-title">🛡️ Protocolo de Resiliência Ativado</div>
      <div class="alert-text">Detectamos alta carga emocional recente. Sua única obrigação hoje é não sumir. Ajustamos suas expectativas para zero.</div>
    </div>""", unsafe_allow_html=True)

# Micro Meta
st.markdown(f"""
<div style="background: var(--bg2); border-radius: 14px; padding: 14px 18px; margin-bottom: 24px; border-left: 3px solid var(--gold); box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
  <div style="font-size: 0.68rem; color: var(--gold); text-transform: uppercase; letter-spacing: 0.05em; font-weight:600;">🎯 Micro-Meta de Contexto</div>
  <div style="font-size: 0.9rem; margin-top: 4px; color: var(--text);">{get_micro_goal(current_mode)}</div>
</div>""", unsafe_allow_html=True)

# Metric Matrix
cal_today = S.today_calories()
meta_cal = S.meta_calorica()
diff_p = round(S.peso_inicio - S.peso_atual, 1)
diff_str = f"-{diff_p} kg" if diff_p >= 0 else f"+{abs(diff_p)} kg"

st.markdown(f"""
<div class="stats-row">
  <div class="stat-card"><div class="stat-num green">{cal_today}</div><div class="stat-label">Kcal Consumidas</div></div>
  <div class="stat-card"><div class="stat-num">{meta_cal}</div><div class="stat-label">Meta Diária</div></div>
  <div class="stat-card"><div class="stat-num gold">{diff_str}</div><div class="stat-label">Evolução Total</div></div>
</div>""", unsafe_allow_html=True)

render_pbar(f"🔥 {cal_today} / {meta_cal} kcal", f"{int(cal_today/meta_cal*100) if meta_cal > 0 else 0}%", cal_today/meta_cal*100 if meta_cal > 0 else 0, "green")
render_pbar(f"{lvl['icon']} {lvl['name']}", f"{get_next_level(S.total_points)['name']} ({get_next_level(S.total_points)['min']} pts)", level_progress(S.total_points), "gold")

# ============================================================================
# APP TABS CONTROL SYSTEM
# ============================================================================
tabs = st.tabs(["🥗 Nutrição", "⚖️ Peso & Antropometria", "📊 Inteligência Analítica", "👤 Perfil Prêmio"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB: NUTRITION
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="section-title">Refeições Estruturadas de Hoje</div>', unsafe_allow_html=True)
    t_meals = S.today_meals()
    
    if t_meals:
        for m in t_meals:
            m_cfg = MEAL_TYPES.get(m["type"], MEAL_TYPES["cafe"])
            photo_badge = '<span class="meal-photo-badge">📸 Foto Validada</span>' if m.get("has_photo") else ""
            st.markdown(f"""
            <div class="meal-item">
              <div>
                <div class="meal-type-tag">{m_cfg['icon']} {m_cfg['name']}{photo_badge}</div>
                <div class="meal-desc">{m['description']}</div>
                <div class="meal-time">⏱ Registrado às {m['time']}</div>
              </div>
              <div class="meal-kcal">{m['calories']}<br/><span style="font-size:.65rem; color:var(--text-muted);">kcal</span></div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
          <div class="icon">🥗</div>
          <div class="msg">Nenhum bloco nutricional inserido hoje.</div>
        </div>""", unsafe_allow_html=True)

    with st.expander("➕ Inserir Novo Bloco Nutricional", expanded=not t_meals):
        with st.form("add_meal_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                m_type = st.selectbox("Momento", options=list(MEAL_TYPES.keys()), format_func=lambda x: f"{MEAL_TYPES[x]['icon']} {MEAL_TYPES[x]['name']}")
            with c2:
                m_cal = st.number_input("Calorias Estimadas (kcal)", min_value=0, max_value=3000, value=MEAL_TYPES[m_type]["cal_hint"], step=25)
            m_desc = st.text_area("Composição Analítica", placeholder="Ex: 150g de patinho grelhado, 200g de arroz integral, brócolis cozido vapor...")
            m_photo = st.camera_input("Foto Real do Prato (Bônus +5 pts)")
            
            if st.form_submit_button("Gravar Registro Nutricional", use_container_width=True):
                if m_desc.strip():
                    photo_check = m_photo is not None
                    S.meals_history.append({
                        "date": S.today_str(),
                        "type": m_type,
                        "description": m_desc.strip(),
                        "calories": m_cal,
                        "has_photo": photo_check,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    earned = POINTS["meal"] + (POINTS["meal_photo"] if photo_check else 0)
                    S.add_points(earned, "nutrition")
                    st.success(f"Bloco gravado com sucesso! +{earned} pontos.")
                    st.rerun()
                else:
                    st.error("Por favor, descreva os alimentos do prato para prosseguir.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB: WEIGHT
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="section-title">Registro Biométrico</div>', unsafe_allow_html=True)
    
    with st.form("weight_form"):
        c1, c2 = st.columns(2)
        with c1: w_now = st.number_input("Peso Balança Atual (kg)", 30.0, 250.0, float(S.peso_atual), 0.1)
        with c2: w_meta = st.number_input("Peso Alvo Estratégico (kg)", 30.0, 250.0, float(S.peso_meta), 0.1)
        
        if st.form_submit_button("Atualizar Métricas Corporais (+10 pts)", use_container_width=True):
            S.peso_atual = w_now
            S.peso_meta = w_meta
            S.weight_history.append({"weight": w_now, "date": S.today_str()})
            S.add_points(POINTS["weight"], "weight")
            st.success("Métricas atualizadas no núcleo.")
            st.rerun()

    imc = S.peso_atual / (S.altura ** 2)
    c1, c2, c3 = st.columns(3)
    c1.metric("IMC Atual", f"{imc:.1f}")
    c2.metric("Eliminado", f"{max(0.0, S.peso_inicio - S.peso_atual):.1f} kg")
    c3.metric("Falta para Alvo", f"{max(0.0, S.peso_atual - S.peso_meta):.1f} kg")

    if len(S.weight_history) >= 2:
        df_w = pd.DataFrame(S.weight_history)
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(x=df_w["date"], y=df_w["weight"], mode="lines+markers", line=dict(color="#2dce89", width=3), marker=dict(color="#f0b429", size=6), fill="tozeroy", fillcolor="rgba(45,206,137,0.03)"))
        fig_w.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#7d8590", size=10), xaxis=dict(gridcolor="#21262d", showgrid=True), yaxis=dict(gridcolor="#21262d", showgrid=True))
        st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────────────────────────────────────
# TAB: ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="section-title">Módulos de Correlação Mental e Física</div>', unsafe_allow_html=True)
    sub_analitycs = st.tabs(["😊 Vetores de Humor", "🔬 Correlações Avançadas"])
    
    with sub_analitycs[0]:
        if S.emotion_history:
            df_e = pd.DataFrame(S.emotion_history)
            counts = df_e["emotion"].value_counts().reset_index()
            counts.columns = ["Fator Emocional", "Ocorrências"]
            fig_e = go.Figure(go.Bar(x=counts["Fator Emocional"], y=counts["Ocorrências"], marker_color="#2dce89"))
            fig_e.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#7d8590"), xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"))
            st.plotly_chart(fig_e, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Alimente o Check-in Emocional na base do app para liberar gráficos de humor.")

    with sub_analitycs[1]:
        st.markdown("#### Correlação Comportamental: Emoções × Ingestão Calórica")
        if S.emotion_history and S.meals_history:
            # Simple link matching emotion date to meal date
            cal_pos, cal_neg, c_pos, c_neg = 0, 0, 0, 0
            for m in S.meals_history:
                match = [e for e in S.emotion_history if e["timestamp"][:10] == m["date"]]
                if match:
                    emo = match[0]["emotion"]
                    if emo in ["motivado", "confiante"]: cal_pos += m["calories"]; c_pos += 1
                    elif emo in ["ansioso", "cansado", "frustrado"]: cal_neg += m["calories"]; c_neg += 1
            
            col1, col2 = st.columns(2)
            with col1: st.metric("Média em Dias Positivos", f"{int(cal_pos/c_pos) if c_pos > 0 else 0} kcal")
            with col2: st.metric("Média em Dias Complexos", f"{int(cal_neg/c_neg) if c_neg > 0 else 0} kcal")
            st.caption("💡 Dias categorizados como 'Complexos' costumam sinalizar maior propensão à fome emocional ou compensação tardia.")
        else:
            st.info("Gere dados combinados de refeições e emoções para cruzar os relatórios.")

    if not S.is_premium:
        st.markdown("""
        <div class="premium-card">
          <div class="premium-title">👑 Upgrade de Nível: Versão Black Luxury</div>
          <div class="premium-feature">Cruzamento analítico completo macro/micro nutrientes</div>
          <div class="premium-feature">Exportação pontual em PDF para envio ao nutricionista</div>
          <div class="premium-feature">Histórico estendido sem compressão de dados (365 dias)</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Ativar Acesso Premium — R$ 19,90/mês", use_container_width=True):
            S.is_premium = True
            st.success("Plano Prêmio Ativado! Recursos liberados.")
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB: PROFILE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-title">Parâmetros Antropométricos de Base</div>', unsafe_allow_html=True)
    with st.form("profile_form_new"):
        c1, c2 = st.columns(2)
        with c1:
            u_name = st.text_input("Designação/Nome", S.nome)
            u_age = st.number_input("Idade Cronológica", 16, 110, S.idade)
            u_sex = st.selectbox("Gênero Biológico", ["M", "F"], index=0 if S.sexo == "M" else 1, format_func=lambda x: "Masculino" if x == "M" else "Feminino")
        with c2:
            u_height = st.number_input("Altura Métrica (m)", 1.20, 2.40, S.altura, step=0.01)
            u_goal = st.selectbox("Alvo Estratégico", list(GOAL_TYPES.keys()), format_func=lambda x: GOAL_TYPES[x]["label"])
            u_act = st.selectbox("Taxa de Atividade Diária", list(ACTIVITY_LEVELS.keys()), format_func=lambda x: ACTIVITY_LEVELS[x]["label"])
        
        if st.form_submit_button("Sincronizar Dados Globais", use_container_width=True):
            S.nome, S.idade, S.sexo, S.altura, S.objetivo, S.nivel_atividade = u_name, u_age, u_sex, u_height, u_goal, u_act
            st.success("Dados globais atualizados.")
            st.rerun()

# ============================================================================
# FIXED SYSTEM: EMOTIONAL CHECK-IN (ANTI-LOOP FORM CONTROL)
# ============================================================================
st.markdown("<hr style='border:0; border-top: 1px solid var(--border); margin: 24px 0;'>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Check-in Psicológico</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:14px;">Selecione abaixo seu estado de espírito dominante para calibração do algoritmo:</div>', unsafe_allow_html=True)

# Grid for visual action
cols = st.columns(6)
for i, (k, v) in enumerate(EMOTIONS.items()):
    with cols[i]:
        # Visual hint for selection state
        btn_label = f"{v['icon']}\n{v['label']}"
        if st.session_state.selected_emotion == k:
            btn_label = f"🟢\n{v['label']}"
        if st.button(btn_label, key=f"btn_emo_{k}", use_container_width=True):
            st.session_state.selected_emotion = k

# Reflection Form opens dynamically after emotion check to prevent loops
if st.session_state.selected_emotion:
    active_emo = st.session_state.selected_emotion
    st.markdown(f"""<div style='padding: 10px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom:10px; font-size:0.85rem;'>
        Fator ativo selecionado: <b>{EMOTIONS[active_emo]['icon']} {EMOTIONS[active_emo]['label']}</b>
    </div>""", unsafe_allow_html=True)
    
    with st.form("reflection_form"):
        user_refl = st.text_area("Notas Mentais / Reflexão Espontânea (Opcional)", placeholder="O que engatilhou esse sentimento hoje? Deixe registrado aqui...")
        
        if st.form_submit_button("Confirmar Check-In Diário (+10 pts)", use_container_width=True):
            # Evaluate Streak Sequence
            if S.last_checkin:
                gap = (date.today() - date.fromisoformat(S.last_checkin)).days
                if gap == 1: S.streak += 1
                elif gap > 1: S.streak = 1
            else:
                S.streak = 1
            
            S.longest_streak = max(S.longest_streak, S.streak)
            S.total_checkins += 1
            S.last_checkin = S.today_str()
            
            S.emotion_history.append({
                "emotion": active_emo,
                "timestamp": datetime.now().isoformat(),
                "reflection": user_refl.strip()
            })
            
            final_pts = POINTS["checkin"]
            if S.streak % 7 == 0:
                final_pts += POINTS["streak_7"]
                st.balloons()
                
            S.add_points(final_pts, "checkin")
            
            # Clean State
            st.session_state.selected_emotion = None
            st.success("Check-in efetuado e integrado com sucesso!")
            st.rerun()

# ============================================================================
# APP FOOTER SYSTEM
# ============================================================================
st.markdown(f"""
<div class="app-footer">
  EMAGRESIM · v36.0 "Core Evolution"<br/>
  ⭐ {S.total_points} PONTOS TOTAIS · 🔥 SEGUIDOS: {S.streak} DIAS<br/>
  <span style="color: var(--text-dim);">Tecnologia Pessoal Orientada à Mudança de Comportamento</span>
</div>""", unsafe_allow_html=True)
