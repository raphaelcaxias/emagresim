# -*- coding: utf-8 -*-
"""
EmagreSim v7.0 - Behavioral Health OS (Modern Edition)
Sem imagens externas | Cores quentes | Glassmorphism | Animações
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import logging
import json
import os
import time
from datetime import datetime, timedelta, date
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CONFIGURACOES
# -----------------------------------------------------------------------------
IS_DEV = os.environ.get("EMAGRESIM_ENV", "dev") == "dev"
DB_PATH = "emagresim_v7.db"
USER_ID = 1

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("emagresim")

st.set_page_config(
    page_title="EmagreSim | Modern OS",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. CORES (Paleta quente)
# -----------------------------------------------------------------------------
@dataclass
class C:
    BG: str = "#1a0f0a"
    SURFACE: str = "#2d1f18"
    CARD_BG: str = "rgba(255,245,235,0.06)"
    CARD_BORDER: str = "rgba(255,245,235,0.12)"
    CARD_BORDER_HOVER: str = "rgba(255,140,66,0.4)"
    PRIMARY: str = "#FF8C42"
    SECONDARY: str = "#E67E22"
    ACCENT: str = "#FF6B6B"
    TEXT: str = "#FFF5EE"
    MUTED: str = "#D4A574"
    DANGER: str = "#FF6B6B"

# -----------------------------------------------------------------------------
# 3. CSS MODERNO
# -----------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700;800&display=swap');

.stApp, .stApp > header {{
    background: linear-gradient(135deg, {C.BG} 0%, {C.SURFACE} 100%) !important;
}}

section[data-testid="stSidebar"] {{
    background: rgba(45,31,24,0.7) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid {C.CARD_BORDER};
}}

* {{
    font-family: 'Inter', sans-serif !important;
}}

h1, h2, h3, h4 {{
    font-weight: 800 !important;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, {C.PRIMARY}, {C.ACCENT});
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.es-card, .es-card-flat {{
    background: {C.CARD_BG};
    backdrop-filter: blur(10px);
    border: 1px solid {C.CARD_BORDER};
    border-radius: 24px;
    padding: 20px 24px;
    margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
}}

.es-card:hover {{
    border-color: {C.CARD_BORDER_HOVER};
    transform: translateY(-4px) scale(1.01);
}}

.kpi-wrap {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

.kpi-label {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {C.MUTED};
}}

.kpi-value {{
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.1;
}}

.kpi-sub {{
    font-size: 0.7rem;
    color: {C.MUTED};
    margin-top: 4px;
}}

.c-primary {{ color: {C.PRIMARY}; }}
.c-secondary {{ color: {C.SECONDARY}; }}
.c-accent {{ color: {C.ACCENT}; }}

.prog-track {{
    background: rgba(255,255,255,0.08);
    border-radius: 99px;
    height: 6px;
    overflow: hidden;
    margin-top: 12px;
}}

.prog-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
    background: linear-gradient(90deg, {C.PRIMARY}, {C.ACCENT});
}}

.insight-box {{
    padding: 12px 16px;
    border-radius: 16px;
    margin: 8px 0;
    font-size: 0.85rem;
    background: rgba(255,140,66,0.08);
    border-left: 3px solid {C.PRIMARY};
}}

.stButton > button {{
    border-radius: 40px !important;
    font-weight: 600 !important;
    background: {C.PRIMARY} !important;
    color: {C.BG} !important;
    border: none !important;
    transition: all 0.2s !important;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    filter: brightness(1.05);
}}

div[data-testid="stMetric"] label {{
    color: {C.MUTED} !important;
    font-size: 0.7rem !important;
}}

#MainMenu, header, footer, .stDeployButton {{ display: none; }}

@media (max-width: 768px) {{
    .es-card, .es-card-flat {{ padding: 16px; }}
    .kpi-value {{ font-size: 1.5rem; }}
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. SPLASH (sem imagem externa)
# -----------------------------------------------------------------------------
if "splash_shown" not in st.session_state:
    with st.container():
        st.markdown("""
        <div style="height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <div style="font-size:5rem; animation: pulse 1.5s infinite;">🔥</div>
            <h1 style="font-size:2.5rem; margin-top:1rem;">Emagre<span style="color:#FF8C42;">Sim</span></h1>
            <p style="color:#D4A574; margin-top:0.5rem;">Behavioral Health OS</p>
        </div>
        <style>
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.7; }
            50% { transform: scale(1.05); opacity: 1; }
            100% { transform: scale(1); opacity: 0.7; }
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state["splash_shown"] = True
        time.sleep(1)
        st.rerun()

# -----------------------------------------------------------------------------
# 5. DATABASE
# -----------------------------------------------------------------------------
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT DEFAULT 'Usuario',
    age INT DEFAULT 30,
    sex TEXT DEFAULT 'M',
    height REAL DEFAULT 1.75,
    current_weight REAL DEFAULT 80.0,
    target_weight REAL DEFAULT 70.0,
    activity_level TEXT DEFAULT 'moderado',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    weight REAL NOT NULL,
    body_fat REAL,
    lean_mass REAL,
    UNIQUE(user_id, date),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS daily_checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    calories_consumed REAL,
    water_ml INT,
    sleep_hours REAL,
    workout_minutes INT,
    mood_score INT,
    consistency_score INT,
    emotional_state TEXT,
    discipline_score INT,
    UNIQUE(user_id, date),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    badge_key TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_key)
);
CREATE TABLE IF NOT EXISTS xp_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    amount INT NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS user_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    event_name TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_checkins ON daily_checkins(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_weights ON weight_logs(user_id, date DESC);
"""

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db() as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cur.fetchone() is None:
            conn.executescript(SCHEMA_SQL)
            _generate_seed(conn)
            logger.info("Database created with seed")
        else:
            logger.info("Database already exists")

def _generate_seed(conn):
    conn.execute("""
        INSERT INTO users (id, name, age, sex, height, current_weight, target_weight, activity_level)
        VALUES (1, 'Usuario Demo', 30, 'M', 1.78, 88.0, 72.0, 'moderado')
    """)
    end_date = date.today() - timedelta(days=1)
    dates = [end_date - timedelta(days=x) for x in range(180)][::-1]
    rng = np.random.default_rng(42)
    for i, d in enumerate(dates):
        w = max(88.0 - 0.025 * i + rng.normal(0, 0.3), 55.0)
        bf = max(22 - 0.04 * i, 8)
        lm = 35 + 0.008 * i
        conn.execute(
            "INSERT INTO weight_logs(user_id,date,weight,body_fat,lean_mass) VALUES(1,?,?,?,?)",
            (d.isoformat(), round(w, 1), round(bf, 1), round(lm, 1))
        )
        cons = int(np.clip(70 - 0.1 * i + rng.normal(0, 8), 40, 98))
        disc = int(np.clip(cons + rng.integers(-5, 6), 40, 98))
        conn.execute(
            "INSERT INTO daily_checkins(user_id,date,calories_consumed,water_ml,sleep_hours,workout_minutes,mood_score,consistency_score,emotional_state,discipline_score) VALUES(1,?,1800,2500,7.2,45,6,?,?,?)",
            (d.isoformat(), cons, "Motivado", disc)
        )
    conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(1,500,'seed')")

# -----------------------------------------------------------------------------
# 6. ENGINES
# -----------------------------------------------------------------------------
class AnalyticsEngine:
    @staticmethod
    def scores(checkins: pd.DataFrame) -> Dict[str, float]:
        empty = {"adherence": 0.0, "discipline": 0.0, "recovery": 0.0, "momentum": 0.0, "stability": 0.0}
        if checkins.empty or len(checkins) < 7:
            return empty
        r30 = checkins.tail(30) if len(checkins) >= 30 else checkins
        momentum = float(np.clip((checkins.tail(7)["consistency_score"].mean() - r30["consistency_score"].mean() + 50), 0, 100))
        return {
            "adherence": round(r30["consistency_score"].mean(), 1),
            "discipline": round(r30["discipline_score"].mean(), 1),
            "recovery": round(min(r30["sleep_hours"].mean() / 8 * 100, 100), 1),
            "momentum": round(momentum, 1),
            "stability": round(100 - min(r30["consistency_score"].std(), 50), 1),
        }
    
    @staticmethod
    def streak(scores: List[float], threshold: int = 70) -> int:
        s = 0
        for sc in reversed(scores):
            if sc >= threshold: s += 1
            else: break
        return s

class LevelEngine:
    LEVELS = [("Iniciante", 0), ("Guerreiro", 500), ("Atleta", 1500), ("Elite", 3000), ("Lenda Fit", 6000)]
    
    @classmethod
    def info(cls, xp: int) -> Tuple[str, float, float]:
        for i, (name, thr) in enumerate(cls.LEVELS):
            if xp >= thr:
                next_thr = cls.LEVELS[i+1][1] if i+1 < len(cls.LEVELS) else thr + 2000
                return name, next_thr, min((xp - thr) / max(next_thr - thr, 1) * 100, 100)
        return "Iniciante", 500, 0

# -----------------------------------------------------------------------------
# 7. REPOSITORY
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_user(uid: int = USER_ID) -> Optional[Dict]:
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None

@st.cache_data(ttl=300, show_spinner=False)
def load_weights(uid: int = USER_ID) -> pd.DataFrame:
    with db() as conn:
        return pd.read_sql("SELECT * FROM weight_logs WHERE user_id=? ORDER BY date", conn, params=(uid,), parse_dates=["date"])

@st.cache_data(ttl=300, show_spinner=False)
def load_checkins(uid: int = USER_ID) -> pd.DataFrame:
    with db() as conn:
        return pd.read_sql("SELECT * FROM daily_checkins WHERE user_id=? ORDER BY date", conn, params=(uid,), parse_dates=["date"])

@st.cache_data(ttl=300, show_spinner=False)
def load_xp_total(uid: int = USER_ID) -> int:
    with db() as conn:
        row = conn.execute("SELECT COALESCE(SUM(amount),0) FROM xp_logs WHERE user_id=?", (uid,)).fetchone()
        return row[0] if row else 0

def invalidate_cache():
    load_user.clear()
    load_weights.clear()
    load_checkins.clear()
    load_xp_total.clear()

def save_checkin(uid: int, data: dict) -> int:
    with db() as conn:
        existing = conn.execute("SELECT id FROM daily_checkins WHERE user_id=? AND date=?", (uid, data["date"])).fetchone()
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(f"UPDATE daily_checkins SET {set_clause} WHERE user_id=? AND date=?", list(data.values()) + [uid, data["date"]])
            xp = 0
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            conn.execute(f"INSERT INTO daily_checkins(user_id,{cols}) VALUES(?,{placeholders})", [uid] + list(data.values()))
            xp = 10
            if data.get("consistency_score", 0) >= 80: xp += 20
            if data.get("sleep_hours", 0) >= 8: xp += 40
            if data.get("workout_minutes", 0) >= 30: xp += 15
            conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)", (uid, xp, "checkin"))
    invalidate_cache()
    return xp

def save_weight(uid: int, data: dict) -> int:
    with db() as conn:
        existing = conn.execute("SELECT id FROM weight_logs WHERE user_id=? AND date=?", (uid, data["date"])).fetchone()
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(f"UPDATE weight_logs SET {set_clause} WHERE user_id=? AND date=?", list(data.values()) + [uid, data["date"]])
            xp = 0
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            conn.execute(f"INSERT INTO weight_logs(user_id,{cols}) VALUES(?,{placeholders})", [uid] + list(data.values()))
            xp = 20
            conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)", (uid, xp, "weight"))
        conn.execute("UPDATE users SET current_weight=? WHERE id=?", (data["weight"], uid))
    invalidate_cache()
    return xp

def update_profile(uid: int, updates: dict):
    with db() as conn:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", list(updates.values()) + [uid])
    invalidate_cache()

def reset_all(uid: int = USER_ID):
    with db() as conn:
        for tbl in ("xp_logs", "user_badges", "user_events", "daily_checkins", "weight_logs", "users"):
            conn.execute(f"DELETE FROM {tbl} WHERE {'user_id' if tbl != 'users' else 'id'}=?", (uid,))
        _generate_seed(conn)
    invalidate_cache()

def get_events_df(uid: int) -> pd.DataFrame:
    with db() as conn:
        return pd.read_sql("SELECT * FROM user_events WHERE user_id=? ORDER BY created_at DESC", conn, params=(uid,))

# -----------------------------------------------------------------------------
# 8. UI COMPONENTS
# -----------------------------------------------------------------------------
def card(html: str, flat: bool = False) -> str:
    cls = "es-card-flat" if flat else "es-card"
    return f'<div class="{cls}">{html}</div>'

def kpi(label: str, value: str, color: str = "c-primary", sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi-wrap"><div class="kpi-label">{label}</div><div class="kpi-value {color}">{value}</div>{sub_html}</div>'

def progress_bar(pct: float) -> str:
    return f'<div class="prog-track"><div class="prog-fill" style="width:{pct:.1f}%"></div></div>'

def insight(text: str) -> str:
    return f'<div class="insight-box">💡 {text}</div>'

def section_header(title: str, subtitle: str = ""):
    sub = f'<p style="color:{C.MUTED};font-size:0.85rem;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"<h2>{title}</h2>{sub}<hr style='border:none;border-top:1px solid {C.CARD_BORDER};margin:12px 0 20px 0;'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. PAGES
# -----------------------------------------------------------------------------
def page_dashboard(user, weights, checkins, scores, xp):
    section_header("Dashboard Estratégico", "Visão geral do seu comportamento")
    
    streak = AnalyticsEngine.streak(checkins["consistency_score"].tolist()) if not checkins.empty else 0
    cur_w = weights["weight"].iloc[-1] if not weights.empty else user["current_weight"]
    lvl_name, _, lvl_pct = LevelEngine.info(xp)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(card(kpi("ADHERENCE", f"{scores['adherence']:.0f}", "c-primary", f"Streak {streak}d")), unsafe_allow_html=True)
    with col2: st.markdown(card(kpi("PESO", f"{cur_w:.1f}kg", "c-secondary")), unsafe_allow_html=True)
    with col3: st.markdown(card(kpi("DISCIPLINA", f"{scores['discipline']:.0f}", "c-accent")), unsafe_allow_html=True)
    with col4: st.markdown(card(kpi("RECUPERAÇÃO", f"{scores['recovery']:.0f}", "c-primary")), unsafe_allow_html=True)
    
    st.markdown(card(kpi("NÍVEL", lvl_name, "c-primary", f"{xp} XP") + progress_bar(lvl_pct)), unsafe_allow_html=True)
    
    if checkins.empty:
        st.info("📝 Nenhum registro ainda. Comece na aba 'Registrar'.")

def page_register(uid: int, user: Dict):
    section_header("Registrar Hoje", f"Entrada do dia {date.today().strftime('%d/%m/%Y')}")
    tab1, tab2 = st.tabs(["📝 Check-in Diário", "⚖️ Peso e Medidas"])
    
    with tab1:
        with st.form("form_checkin"):
            col1, col2 = st.columns(2)
            with col1:
                cal = st.number_input("Calorias", 0, 8000, 1800, 50, help="Meta: 1800 kcal")
                water = st.number_input("Água (ml)", 0, 6000, 2500, 100, help="Meta: 2500 ml")
                sleep = st.slider("Sono (h)", 0.0, 12.0, 7.0, 0.5, help="Recomendado: 7-8h")
            with col2:
                workout = st.number_input("Treino (min)", 0, 300, 0, 5, help="Meta: 30 min")
                mood = st.slider("Humor (1-10)", 1, 10, 7)
                emotion = st.selectbox("Estado emocional", ["Focado", "Motivado", "Determinado", "Cansado", "Ansioso"])
            if st.form_submit_button("🔥 Salvar Check-in"):
                with st.spinner("Salvando..."):
                    cal_score = max(0, 100 - abs(cal - 1800) / 18)
                    water_score = min(water / 35, 100)
                    sleep_score = min(sleep / 8.5 * 100, 100)
                    workout_score = min(workout / 45 * 100, 100)
                    mood_score_norm = mood * 10
                    cons = int(cal_score * 0.3 + water_score * 0.15 + sleep_score * 0.2 + workout_score * 0.25 + mood_score_norm * 0.1)
                    disc = int(np.clip(mood * 10 + workout / 5, 10, 100))
                    data = {
                        "date": date.today().isoformat(),
                        "calories_consumed": cal,
                        "water_ml": water,
                        "sleep_hours": sleep,
                        "workout_minutes": workout,
                        "mood_score": mood,
                        "emotional_state": emotion,
                        "discipline_score": disc,
                        "consistency_score": cons,
                    }
                    xp = save_checkin(uid, data)
                    if xp:
                        st.toast(f"✅ Check-in salvo! +{xp} XP", icon="🔥")
                    else:
                        st.toast("✏️ Check-in atualizado!", icon="📝")
                    st.rerun()
    
    with tab2:
        with st.form("form_weight"):
            col1, col2, col3 = st.columns(3)
            with col1: w = st.number_input("Peso (kg)", 30, 300, float(user["current_weight"]), 0.1)
            with col2: bf = st.number_input("Gordura (%)", 3, 60, 20, 0.1)
            with col3: lm = st.number_input("Massa magra (kg)", 20, 120, 35, 0.1)
            if st.form_submit_button("🔥 Salvar Peso"):
                data = {"date": date.today().isoformat(), "weight": w, "body_fat": bf, "lean_mass": lm}
                xp = save_weight(uid, data)
                if xp:
                    st.toast(f"⚖️ Peso salvo! +{xp} XP", icon="🔥")
                else:
                    st.toast("✏️ Peso atualizado!", icon="⚖️")
                st.rerun()

def page_profile(uid: int, user: Dict):
    section_header("Perfil", "Edite seus dados pessoais")
    with st.form("form_profile"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome", user["name"])
            age = st.number_input("Idade", 18, 100, int(user["age"]))
            sex = st.selectbox("Sexo", ["M", "F"], index=0 if user["sex"] == "M" else 1)
        with col2:
            height = st.number_input("Altura (m)", 1.40, 2.20, float(user["height"]), 0.01)
            target = st.number_input("Meta de peso (kg)", 30, 200, float(user["target_weight"]), 0.5)
            acts = ["sedentario", "leve", "moderado", "intenso", "extremo"]
            act = st.selectbox("Nível de atividade", acts, index=acts.index(user["activity_level"]) if user["activity_level"] in acts else 2)
        if st.form_submit_button("💾 Salvar Alterações"):
            update_profile(uid, {"name": name, "age": age, "sex": sex, "height": height, "target_weight": target, "activity_level": act})
            st.toast("Perfil atualizado!", icon="👤")
            st.rerun()

def page_config(uid: int):
    section_header("Configurações", "Exportar dados e opções do sistema")
    if st.button("📥 Gerar CSVs"):
        with st.spinner("Preparando..."):
            ch = load_checkins(uid)
            wt = load_weights(uid)
            st.download_button("Check-ins.csv", ch.to_csv(index=False), "checkins.csv", "text/csv")
            st.download_button("Pesos.csv", wt.to_csv(index=False), "weights.csv", "text/csv")
    st.markdown("---")
    st.markdown("### ⚠️ Zona de Perigo")
    if "confirm_reset" not in st.session_state:
        st.session_state.confirm_reset = False
    if not st.session_state.confirm_reset:
        if st.button("🗑️ Resetar todos os dados", type="secondary"):
            st.session_state.confirm_reset = True
            st.rerun()
    else:
        st.warning("⚠️ Isso apagará TODOS os seus dados permanentemente.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, resetar"):
                reset_all(uid)
                st.session_state.confirm_reset = False
                st.toast("Dados resetados!", icon="🔄")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirm_reset = False
                st.rerun()

def page_telemetry(uid: int):
    section_header("Telemetria", "Eventos registrados")
    df = get_events_df(uid)
    if df.empty:
        st.info("Nenhum evento registrado ainda.")
        return
    st.dataframe(df.head(50), use_container_width=True)

# -----------------------------------------------------------------------------
# 10. SIDEBAR
# -----------------------------------------------------------------------------
def render_sidebar(user: Dict, xp: int) -> str:
    lvl_name, _, lvl_pct = LevelEngine.info(xp)
    with st.sidebar:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
            <div style="font-size:2rem;">🔥</div>
            <div style="font-size:1.2rem; font-weight:800;">
                Emagre<span style="color:#FF8C42;">Sim</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(card(kpi("NÍVEL", lvl_name, "c-primary", f"{xp} XP") + progress_bar(lvl_pct)), unsafe_allow_html=True)
        page = st.radio("Navegação", ["Dashboard", "Registrar", "Perfil", "Config", "Telemetria"], label_visibility="collapsed")
        st.markdown(f"<div style='margin-top:20px;font-size:0.75rem;color:{C.MUTED};'>Olá, {user.get('name', 'Usuário')}</div>", unsafe_allow_html=True)
    return page

# -----------------------------------------------------------------------------
# 11. MAIN
# -----------------------------------------------------------------------------
def main():
    init_db()
    user = load_user(USER_ID)
    if user is None:
        st.error("Erro ao carregar dados. Recarregue a página.")
        return
    weights = load_weights(USER_ID)
    checkins = load_checkins(USER_ID)
    xp = load_xp_total(USER_ID)
    scores = AnalyticsEngine.scores(checkins)
    page = render_sidebar(user, xp)
    
    if page == "Dashboard": page_dashboard(user, weights, checkins, scores, xp)
    elif page == "Registrar": page_register(USER_ID, user)
    elif page == "Perfil": page_profile(USER_ID, user)
    elif page == "Config": page_config(USER_ID)
    elif page == "Telemetria": page_telemetry(USER_ID)

if __name__ == "__main__":
    main()
