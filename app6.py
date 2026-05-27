# -*- coding: utf-8 -*-
"""
EmagreSim v8.1 - Premium Dark Edition (Corrigido)
Gráfico de consistência com st.columns + st.progress (nativo)
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

# -----------------------------------------------------------------------------
# 1. CONFIGURACOES
# -----------------------------------------------------------------------------
IS_DEV = os.environ.get("EMAGRESIM_ENV", "dev") == "dev"
DB_PATH = "emagresim_v8.db"
USER_ID = 1

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("emagresim")

st.set_page_config(
    page_title="EmagreSim | Premium",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. CORES
# -----------------------------------------------------------------------------
@dataclass
class C:
    BG: str = "#0D0D0D"
    SURFACE: str = "#1A1A1A"
    CARD: str = "#1E1E1E"
    PRIMARY: str = "#FF4D00"
    PRIMARY_DARK: str = "#E63E00"
    PRIMARY_LIGHT: str = "#FF8A4D"
    TEXT: str = "#FFFFFF"
    TEXT_MUTED: str = "#A0A0A0"
    TEXT_DIM: str = "#6B6B6B"
    SUCCESS: str = "#22C55E"
    WARNING: str = "#FBBF24"

# -----------------------------------------------------------------------------
# 3. CSS PREMIUM
# -----------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700;800&display=swap');

.stApp, .stApp > header {{
    background: {C.BG} !important;
}}

section[data-testid="stSidebar"] {{
    background: {C.SURFACE} !important;
    border-right: none !important;
}}

hr, .stMarkdown hr {{
    display: none !important;
}}

* {{
    font-family: 'Inter', sans-serif !important;
}}

h1, h2, h3, h4 {{
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    color: {C.TEXT} !important;
    margin-bottom: 0.5rem !important;
}}

.es-card {{
    background: {C.CARD};
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
}}

.kpi-row {{
    display: flex;
    gap: 20px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}}

.kpi-card {{
    flex: 1;
    background: {C.CARD};
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.06);
}}

.kpi-label {{
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {C.TEXT_DIM};
    margin-bottom: 4px;
}}

.kpi-value {{
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 8px;
}}

.kpi-badge {{
    display: inline-flex;
    align-items: center;
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 0.7rem;
    font-weight: 500;
    color: {C.TEXT_MUTED};
    gap: 4px;
}}

.kpi-badge.positive {{
    background: rgba(34,197,94,0.12);
    color: {C.SUCCESS};
}}

.kpi-badge.warning {{
    background: rgba(251,191,36,0.12);
    color: {C.WARNING};
}}

.scores-row {{
    display: flex;
    gap: 24px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}}

.chart-panel {{
    flex: 2;
    background: {C.CARD};
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.06);
}}

.metrics-panel {{
    flex: 1;
    background: {C.CARD};
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.06);
}}

.metric-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}

.metric-item:last-child {{
    border-bottom: none;
}}

.metric-name {{
    font-size: 0.85rem;
    color: {C.TEXT_MUTED};
}}

.metric-bar-wrapper {{
    flex: 1;
    margin: 0 12px;
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
}}

.metric-bar-fill {{
    height: 100%;
    border-radius: 3px;
    background: {C.PRIMARY};
}}

.metric-value {{
    font-size: 0.85rem;
    font-weight: 600;
    color: {C.TEXT};
    min-width: 40px;
    text-align: right;
}}

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
    background: linear-gradient(90deg, {C.PRIMARY}, {C.PRIMARY_LIGHT});
}}

.bar-chart {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 6px;
    height: 140px;
    margin-top: 10px;
}}

.bar-item {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}}

.bar {{
    width: 100%;
    background: {C.PRIMARY};
    border-radius: 4px 4px 0 0;
    transition: height 0.3s ease;
}}

.bar-label {{
    font-size: 0.55rem;
    color: {C.TEXT_DIM};
}}

/* Navegação sidebar */
.nav-btn {{
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 10px 14px;
    margin: 4px 0;
    background: transparent;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 500;
    color: {C.TEXT_MUTED};
    transition: all 0.2s;
}}

.nav-btn.active {{
    background: rgba(255,77,0,0.12);
    color: {C.PRIMARY};
}}

/* Esconder elementos padrão */
#MainMenu, header, footer, .stDeployButton {{
    display: none !important;
}}

@media (max-width: 768px) {{
    .kpi-row {{ flex-direction: column; }}
    .scores-row {{ flex-direction: column; }}
    .bar-chart {{ gap: 3px; }}
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. SPLASH
# -----------------------------------------------------------------------------
if "splash_shown" not in st.session_state:
    with st.container():
        st.markdown(f"""
        <div style="height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <div style="font-size:5rem; animation: pulse 1.5s infinite;">🔥</div>
            <h1 style="font-size:2.5rem; margin-top:1rem;">Emagre<span style="color:{C.PRIMARY};">Sim</span></h1>
            <p style="color:{C.TEXT_MUTED};">Behavioral Health OS</p>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(1); opacity: 0.7; }}
            50% {{ transform: scale(1.05); opacity: 1; }}
            100% {{ transform: scale(1); opacity: 0.7; }}
        }}
        </style>
        """, unsafe_allow_html=True)
        st.session_state["splash_shown"] = True
        time.sleep(1)
        st.rerun()

# -----------------------------------------------------------------------------
# 5. DATABASE (mantido igual)
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
    except Exception:
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

def _generate_seed(conn):
    conn.execute("INSERT INTO users VALUES (1,'Usuario Demo',30,'M',1.78,88.0,72.0,'moderado',CURRENT_TIMESTAMP)")
    end_date = date.today() - timedelta(days=1)
    dates = [end_date - timedelta(days=x) for x in range(180)][::-1]
    rng = np.random.default_rng(42)
    for i, d in enumerate(dates):
        w = max(88.0 - 0.025 * i + rng.normal(0, 0.3), 55.0)
        bf = max(22 - 0.04 * i, 8)
        lm = 35 + 0.008 * i
        conn.execute("INSERT INTO weight_logs VALUES (?,?,?,?,?)",
                     (i+1, 1, d.isoformat(), round(w, 1), round(bf, 1), round(lm, 1)))
        cons = int(np.clip(70 - 0.1 * i + rng.normal(0, 8), 40, 98))
        disc = int(np.clip(cons + rng.integers(-5, 6), 40, 98))
        conn.execute("INSERT INTO daily_checkins(user_id,date,calories_consumed,water_ml,sleep_hours,workout_minutes,mood_score,consistency_score,emotional_state,discipline_score) VALUES(1,?,1800,2500,7.2,45,6,?,?,?)",
                     (d.isoformat(), cons, "Motivado", disc))
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
            if sc >= threshold:
                s += 1
            else:
                break
        return s
    
    @staticmethod
    def last_n_consistency(checkins: pd.DataFrame, n: int = 14) -> List[int]:
        if checkins.empty:
            return []
        return checkins.tail(n)["consistency_score"].tolist()

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
            return 0
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
            return 0
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

# -----------------------------------------------------------------------------
# 8. UI COMPONENTS CORRIGIDOS
# -----------------------------------------------------------------------------
def render_consistency_bars(values: List[int]):
    """Renderiza o gráfico de barras usando columns nativas do Streamlit"""
    if not values:
        st.info("Sem dados suficientes")
        return
    
    max_val = max(values) if max(values) > 0 else 100
    cols = st.columns(len(values))
    
    for i, (col, val) in enumerate(zip(cols, values)):
        height_pct = (val / max_val) * 100 if max_val > 0 else 0
        with col:
            st.markdown(f"""
            <div style="display:flex; flex-direction:column; align-items:center; gap:6px;">
                <div style="width:100%; height:{height_pct}px; background:{C.PRIMARY}; border-radius:4px 4px 0 0;"></div>
                <div style="font-size:0.55rem; color:{C.TEXT_DIM};">{i+1}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.caption("Consistência — últimos 14 dias")

def render_metrics_table(scores: Dict[str, float]):
    """Renderiza a tabela de métricas com barras horizontais"""
    metrics = [
        ("Adherence", scores.get("adherence", 0)),
        ("Disciplina", scores.get("discipline", 0)),
        ("Recuperação", scores.get("recovery", 0)),
        ("Momentum", scores.get("momentum", 0)),
        ("Estabilidade", scores.get("stability", 0)),
    ]
    
    for name, value in metrics:
        st.markdown(f"""
        <div class="metric-item">
            <span class="metric-name">{name}</span>
            <div class="metric-bar-wrapper">
                <div class="metric-bar-fill" style="width:{value}%"></div>
            </div>
            <span class="metric-value">{value:.0f}</span>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. PAGES
# -----------------------------------------------------------------------------
def page_dashboard(user, weights, checkins, scores, xp, consistency_data):
    streak = AnalyticsEngine.streak(checkins["consistency_score"].tolist()) if not checkins.empty else 0
    cur_w = weights["weight"].iloc[-1] if not weights.empty else user["current_weight"]
    target = user["target_weight"]
    delta = cur_w - target
    delta_text = f"{delta:+.1f} kg"
    delta_type = "positive" if delta < 0 else "warning"
    
    # KPIs com badges (usando st.columns + st.markdown)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">ADHERENCE</div>
            <div class="kpi-value">{scores['adherence']:.0f}</div>
            <span class="kpi-badge positive">Streak {streak}d</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        badge_class = "positive" if delta < 0 else "warning"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">PESO</div>
            <div class="kpi-value">{cur_w:.1f} kg</div>
            <span class="kpi-badge {badge_class}">{delta_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">DISCIPLINA</div>
            <div class="kpi-value">{scores['discipline']:.0f}</div>
            <span class="kpi-badge positive">+3 esta semana</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">RECUPERAÇÃO</div>
            <div class="kpi-value">{scores['recovery']:.0f}</div>
            <span class="kpi-badge positive">+3 esta semana</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de consistência + tabela de métricas
    col_chart, col_metrics = st.columns([2, 1])
    
    with col_chart:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        render_consistency_bars(consistency_data)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_metrics:
        st.markdown('<div class="metrics-panel">', unsafe_allow_html=True)
        render_metrics_table(scores)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Level e XP
    lvl_name, _, lvl_pct = LevelEngine.info(xp)
    st.markdown(f"""
    <div class="es-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div><span style="color:{C.TEXT_DIM};">NÍVEL</span><br><span style="font-size:1.2rem; font-weight:700;">{lvl_name}</span></div>
            <div style="text-align:right;"><span style="color:{C.TEXT_DIM};">XP TOTAL</span><br><span style="font-size:1.2rem; font-weight:700;">{xp}</span></div>
        </div>
        <div class="prog-track"><div class="prog-fill" style="width:{lvl_pct:.1f}%"></div></div>
    </div>
    """, unsafe_allow_html=True)

def page_register(uid: int, user: Dict):
    st.markdown("<h2>Registrar Hoje</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C.TEXT_MUTED}; margin-bottom:20px;'>Entrada do dia {date.today().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Check-in Diário", "⚖️ Peso e Medidas"])
    
    with tab1:
        with st.form("form_checkin"):
            col1, col2 = st.columns(2)
            with col1:
                cal = st.number_input("Calorias", 0, 8000, 1800, 50)
                water = st.number_input("Água (ml)", 0, 6000, 2500, 100)
                sleep = st.slider("Sono (h)", 0.0, 12.0, 7.0, 0.5)
            with col2:
                workout = st.number_input("Treino (min)", 0, 300, 0, 5)
                mood = st.slider("Humor (1-10)", 1, 10, 7)
                emotion = st.selectbox("Estado emocional", ["Focado", "Motivado", "Determinado", "Cansado", "Ansioso"])
            
            if st.form_submit_button("🔥 Salvar Check-in", use_container_width=True):
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
            with col1:
                w = st.number_input("Peso (kg)", 30.0, 300.0, user["current_weight"], 0.1)
            with col2:
                bf = st.number_input("Gordura (%)", 3.0, 60.0, 20.0, 0.1)
            with col3:
                lm = st.number_input("Massa magra (kg)", 20.0, 120.0, 35.0, 0.1)
            
            if st.form_submit_button("🔥 Salvar Peso", use_container_width=True):
                data = {"date": date.today().isoformat(), "weight": w, "body_fat": bf, "lean_mass": lm}
                xp = save_weight(uid, data)
                if xp:
                    st.toast(f"⚖️ Peso salvo! +{xp} XP", icon="🔥")
                else:
                    st.toast("✏️ Peso atualizado!", icon="⚖️")
                st.rerun()

def page_profile(uid: int, user: Dict):
    st.markdown("<h2>Perfil</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C.TEXT_MUTED}; margin-bottom:20px;'>Edite seus dados pessoais</p>", unsafe_allow_html=True)
    
    with st.form("form_profile"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome", user["name"])
            age = st.number_input("Idade", 18, 100, int(user["age"]))
            sex = st.selectbox("Sexo", ["M", "F"], index=0 if user["sex"] == "M" else 1)
        with col2:
            height = st.number_input("Altura (m)", 1.40, 2.20, user["height"], 0.01)
            target = st.number_input("Meta de peso (kg)", 30.0, 200.0, user["target_weight"], 0.5)
            acts = ["sedentario", "leve", "moderado", "intenso", "extremo"]
            act = st.selectbox("Nível de atividade", acts, index=acts.index(user["activity_level"]) if user["activity_level"] in acts else 2)
        
        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
            update_profile(uid, {"name": name, "age": age, "sex": sex, "height": height, "target_weight": target, "activity_level": act})
            st.toast("Perfil atualizado!", icon="👤")
            st.rerun()

def page_config(uid: int):
    st.markdown("<h2>Configurações</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C.TEXT_MUTED}; margin-bottom:20px;'>Exportar dados e opções do sistema</p>", unsafe_allow_html=True)
    
    if st.button("📥 Gerar CSVs"):
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

# -----------------------------------------------------------------------------
# 10. SIDEBAR
# -----------------------------------------------------------------------------
def render_sidebar(user: Dict, xp: int) -> str:
    lvl_name, _, lvl_pct = LevelEngine.info(xp)
    
    with st.sidebar:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:24px;">
            <div style="font-size:2rem;">🔥</div>
            <div style="font-size:1.2rem; font-weight:800;">Emagre<span style="color:{C.PRIMARY};">Sim</span></div>
        </div>
        <div style="background:{C.CARD}; border-radius:16px; padding:16px; margin-bottom:24px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:{C.TEXT_DIM};">NÍVEL</span>
                <span style="color:{C.PRIMARY};">{lvl_name}</span>
            </div>
            <div class="prog-track"><div class="prog-fill" style="width:{lvl_pct:.1f}%"></div></div>
            <div style="margin-top:8px; font-size:0.7rem; color:{C.TEXT_DIM};">{xp} XP</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navegação com radio estilizado via CSS
        page = st.radio("", ["Dashboard", "Registrar", "Perfil", "Config"], label_visibility="collapsed")
        
        st.markdown(f"<div style='margin-top:32px; font-size:0.7rem; color:{C.TEXT_DIM}; text-align:center;'>Olá, {user.get('name', 'Usuário')}</div>", unsafe_allow_html=True)
    
    return page

# -----------------------------------------------------------------------------
# 11. MAIN
# -----------------------------------------------------------------------------
def main():
    init_db()
    user = load_user(USER_ID)
    if user is None:
        st.error("Erro ao carregar dados.")
        return
    
    weights = load_weights(USER_ID)
    checkins = load_checkins(USER_ID)
    xp = load_xp_total(USER_ID)
    scores = AnalyticsEngine.scores(checkins)
    consistency_data = AnalyticsEngine.last_n_consistency(checkins, 14)
    
    page = render_sidebar(user, xp)
    
    if page == "Dashboard":
        page_dashboard(user, weights, checkins, scores, xp, consistency_data)
    elif page == "Registrar":
        page_register(USER_ID, user)
    elif page == "Perfil":
        page_profile(USER_ID, user)
    elif page == "Config":
        page_config(USER_ID)

if __name__ == "__main__":
    main()
