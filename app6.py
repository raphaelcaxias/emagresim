# -*- coding: utf-8 -*-
"""
EmagreSim v6.4 - Behavioral Health OS
Arquivo único - Funcional e estável
Correção: migrations segura, sem pydantic, cache granular, UI melhorada
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
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES GLOBAIS
# -----------------------------------------------------------------------------
IS_DEV = os.environ.get("EMAGRESIM_ENV", "dev") == "dev"
DB_PATH = "emagresim_v6.db"
USER_ID = 1

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("emagresim")

st.set_page_config(
    page_title="EmagreSim | Behavioral OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# URLs das imagens (raw do GitHub)
LOGO_URL = "https://raw.githubusercontent.com/raphaelcaxias/emagresim/main/logo.png"
SPLASH_URL = "https://raw.githubusercontent.com/raphaelcaxias/emagresim/main/splash.png"

# -----------------------------------------------------------------------------
# 2. CONSTANTS
# -----------------------------------------------------------------------------
@dataclass
class Constants:
    TARGET_CALORIES: int = 1800
    TARGET_WATER_ML: int = 2500
    TARGET_SLEEP_HOURS: float = 7.5
    TARGET_WORKOUT_MIN: int = 30
    WEIGHT_MIN: float = 30.0
    WEIGHT_MAX: float = 300.0
    BODY_FAT_MIN: float = 3.0
    BODY_FAT_MAX: float = 60.0
    LEAN_MASS_MIN: float = 20.0
    LEAN_MASS_MAX: float = 120.0
    VALIDATION_TOLERANCE: float = 0.08
    XP_COOLDOWN_HOURS: int = 12
    XP_BASE: int = 10
    XP_CONSISTENCY_BONUS: int = 20
    XP_SLEEP_BONUS: int = 40
    XP_WORKOUT_BONUS: int = 15
    XP_WEIGHT_BASE: int = 20

CONST = Constants()

# -----------------------------------------------------------------------------
# 3. DOMAIN ENGINES
# -----------------------------------------------------------------------------
class ConsistencyEngine:
    @staticmethod
    def calculate(calories: float, water_ml: int, sleep_hours: float, 
                  workout_minutes: int, mood_score: int) -> int:
        cal_score = max(0, 100 - abs(calories - CONST.TARGET_CALORIES) / 18)
        cal_score = min(cal_score, 100)
        water_score = min(water_ml / 35, 100)
        sleep_score = min(sleep_hours / 8.5 * 100, 100)
        workout_score = min(workout_minutes / 45 * 100, 100)
        mood_score_norm = mood_score * 10
        consistency = (
            cal_score * 0.30 + water_score * 0.15 +
            sleep_score * 0.20 + workout_score * 0.25 +
            mood_score_norm * 0.10
        )
        return int(np.clip(consistency, 0, 100))

class XPEngine:
    @staticmethod
    def calculate(consistency: int, sleep_hours: float, workout_minutes: int) -> int:
        xp = CONST.XP_BASE
        if consistency >= 80:
            xp += CONST.XP_CONSISTENCY_BONUS
        if sleep_hours >= 8:
            xp += CONST.XP_SLEEP_BONUS
        if workout_minutes >= 30:
            xp += CONST.XP_WORKOUT_BONUS
        return xp
    
    @staticmethod
    def can_earn(uid: int, source: str) -> bool:
        with db() as conn:
            row = conn.execute(
                "SELECT MAX(created_at) FROM xp_logs WHERE user_id=? AND source=?",
                (uid, source)
            ).fetchone()
            if row and row[0]:
                last = datetime.fromisoformat(row[0])
                hours_since = (datetime.now() - last).total_seconds() / 3600
                return hours_since >= CONST.XP_COOLDOWN_HOURS
        return True

class LevelEngine:
    LEVELS = [
        ("Iniciante", 0), ("Guerreiro", 500), ("Atleta", 1500),
        ("Elite", 3000), ("Lenda Fit", 6000)
    ]
    
    @classmethod
    def info(cls, xp: int) -> Tuple[str, float, float]:
        for i, (name, thr) in enumerate(cls.LEVELS):
            if xp >= thr:
                next_thr = cls.LEVELS[i+1][1] if i+1 < len(cls.LEVELS) else thr + 2000
                progress = (xp - thr) / max(next_thr - thr, 1) * 100
                return name, next_thr, min(progress, 100)
        return "Iniciante", 500, 0.0

class AnalyticsEngine:
    @staticmethod
    def scores(checkins: pd.DataFrame) -> Dict[str, float]:
        empty = {"adherence": 0.0, "discipline": 0.0, "recovery": 0.0, "momentum": 0.0, "stability": 0.0}
        if checkins.empty or len(checkins) < 7:
            return empty
        r30 = checkins.tail(30) if len(checkins) >= 30 else checkins
        r7 = checkins.tail(7)["consistency_score"].mean()
        p23 = checkins.tail(30).head(23)["consistency_score"].mean() if len(checkins) >= 30 else checkins["consistency_score"].mean()
        momentum = float(np.clip((r7 - p23 + 50), 0, 100))
        std = r30["consistency_score"].std()
        stability = 100.0 - min(float(std) if not np.isnan(std) else 50.0, 50.0)
        return {
            "adherence": round(r30["consistency_score"].mean(), 1),
            "discipline": round(r30["discipline_score"].mean(), 1),
            "recovery": round(min(r30["sleep_hours"].mean() / 8 * 100, 100), 1),
            "momentum": round(momentum, 1),
            "stability": round(stability, 1),
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

# -----------------------------------------------------------------------------
# 4. DATABASE LAYER (com migrations segura)
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
CREATE INDEX IF NOT EXISTS idx_events ON user_events(user_id, created_at DESC);
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
    """Inicializa o banco de dados com verificacao segura de tabelas"""
    with db() as conn:
        # Verifica se a tabela users existe
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Primeira execucao: cria todas as tabelas
            conn.executescript(SCHEMA_SQL)
            logger.info("Database schema created")
        else:
            logger.info("Database already exists")
    
    # Seed apenas se nao houver dados
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count == 0:
            _generate_seed(conn)

def _generate_seed(conn):
    """Gera dados demo apenas quando o banco está vazio"""
    conn.execute("""
        INSERT INTO users (id, name, age, sex, height, current_weight, target_weight, activity_level)
        VALUES (1, 'Usuario Demo', 30, 'M', 1.78, 88.0, 72.0, 'moderado')
    """)
    
    end_date = date.today() - timedelta(days=1)
    dates = [end_date - timedelta(days=x) for x in range(180)][::-1]
    rng = np.random.default_rng(42)
    weights = []
    checkins = []
    
    for i, d in enumerate(dates):
        w = max(88.0 - 0.025 * i + rng.normal(0, 0.3), 55.0)
        bf = max(22 - 0.04 * i, 8)
        lm = 35 + 0.008 * i
        weights.append((1, d.isoformat(), round(w, 1), round(bf, 1), round(lm, 1)))
        
        cons = int(np.clip(70 - 0.1 * i + rng.normal(0, 8), 40, 98))
        disc = int(np.clip(cons + rng.integers(-5, 6), 40, 98))
        checkins.append((1, d.isoformat(), 1800, 2500, 7.2, 45, 6, cons, "Motivado", disc))
    
    conn.executemany("INSERT INTO weight_logs(user_id,date,weight,body_fat,lean_mass) VALUES(?,?,?,?,?)", weights)
    conn.executemany("INSERT INTO daily_checkins(user_id,date,calories_consumed,water_ml,sleep_hours,workout_minutes,mood_score,consistency_score,emotional_state,discipline_score) VALUES(?,?,?,?,?,?,?,?,?,?)", checkins)
    conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(1,500,'seed')")
    logger.info("Seed data generated")

# -----------------------------------------------------------------------------
# 5. REPOSITORY (cache granular)
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
    """Limpa apenas o cache relacionado aos dados do usuario"""
    load_user.clear()
    load_weights.clear()
    load_checkins.clear()
    load_xp_total.clear()

# -----------------------------------------------------------------------------
# 6. SERVICES
# -----------------------------------------------------------------------------
def track_event(uid: int, event_name: str, metadata: dict = None):
    with db() as conn:
        conn.execute(
            "INSERT INTO user_events(user_id, event_name, metadata) VALUES(?,?,?)",
            (uid, event_name, json.dumps(metadata or {}))
        )

def save_checkin(uid: int, data: dict) -> int:
    is_new = False
    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM daily_checkins WHERE user_id=? AND date=?", (uid, data["date"])
        ).fetchone()
        
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(
                f"UPDATE daily_checkins SET {set_clause} WHERE user_id=? AND date=?",
                list(data.values()) + [uid, data["date"]]
            )
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            conn.execute(
                f"INSERT INTO daily_checkins(user_id,{cols}) VALUES(?,{placeholders})",
                [uid] + list(data.values())
            )
            is_new = True
    
    xp = 0
    if is_new and XPEngine.can_earn(uid, "checkin"):
        xp = XPEngine.calculate(
            data.get("consistency_score", 0),
            data.get("sleep_hours", 0),
            data.get("workout_minutes", 0)
        )
        with db() as conn:
            conn.execute(
                "INSERT INTO xp_logs(user_id, amount, source) VALUES(?,?,?)",
                (uid, xp, "checkin")
            )
    
    track_event(uid, "checkin_saved", {"xp": xp, "date": data["date"]})
    invalidate_cache()
    return xp

def save_weight(uid: int, data: dict) -> int:
    is_new = False
    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM weight_logs WHERE user_id=? AND date=?", (uid, data["date"])
        ).fetchone()
        
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(
                f"UPDATE weight_logs SET {set_clause} WHERE user_id=? AND date=?",
                list(data.values()) + [uid, data["date"]]
            )
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            conn.execute(
                f"INSERT INTO weight_logs(user_id,{cols}) VALUES(?,{placeholders})",
                [uid] + list(data.values())
            )
            is_new = True
        conn.execute("UPDATE users SET current_weight=? WHERE id=?", (data["weight"], uid))
    
    xp = 0
    if is_new and XPEngine.can_earn(uid, "weight"):
        xp = CONST.XP_WEIGHT_BASE
        with db() as conn:
            conn.execute("INSERT INTO xp_logs(user_id, amount, source) VALUES(?,?,?)", (uid, xp, "weight"))
    
    track_event(uid, "weight_saved", {"weight": data["weight"], "date": data["date"]})
    invalidate_cache()
    return xp

def update_profile(uid: int, updates: dict):
    with db() as conn:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", list(updates.values()) + [uid])
    track_event(uid, "profile_updated", updates)
    invalidate_cache()

def reset_all(uid: int = USER_ID):
    with db() as conn:
        for tbl in ("xp_logs", "user_badges", "user_events", "daily_checkins", "weight_logs"):
            conn.execute(f"DELETE FROM {tbl} WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
    # Recria os dados
    with db() as conn:
        _generate_seed(conn)
    track_event(uid, "reset_data", {})
    invalidate_cache()

def export_data(uid: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    return load_checkins(uid), load_weights(uid)

def get_events_df(uid: int) -> pd.DataFrame:
    with db() as conn:
        return pd.read_sql("SELECT * FROM user_events WHERE user_id=? ORDER BY created_at DESC", conn, params=(uid,))

# -----------------------------------------------------------------------------
# 7. UI COMPONENTS
# -----------------------------------------------------------------------------
class UI:
    @staticmethod
    def card(html: str, flat: bool = False) -> str:
        cls = "es-card-flat" if flat else "es-card"
        return f'<div class="{cls}">{html}</div>'
    
    @staticmethod
    def kpi(label: str, value: str, color: str = "c-green", sub: str = "") -> str:
        sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
        return f'<div class="kpi-wrap"><div class="kpi-label">{label}</div><div class="kpi-value {color}">{value}</div>{sub_html}</div>'
    
    @staticmethod
    def progress_bar(pct: float, color: str = "fill-purple") -> str:
        return f'<div class="prog-track"><div class="prog-fill {color}" style="width:{pct:.1f}%"></div></div>'
    
    @staticmethod
    def insight(text: str) -> str:
        return f'<div class="insight-box ins-info">💡 {text}</div>'
    
    @staticmethod
    def section_header(title: str, subtitle: str = ""):
        sub = f'<p style="color:#64748B;font-size:.85rem;">{subtitle}</p>' if subtitle else ""
        st.markdown(f"<h2>{title}</h2>{sub}<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:12px 0 20px 0;'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. CSS (otimizado)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
.stApp, .stApp > header { background: #070910 !important; }
section[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid rgba(255,255,255,0.05); }
*, p, div, span, label, .stMarkdown { font-family: 'Outfit', sans-serif !important; }
h1, h2, h3, h4 { font-family: 'Outfit', sans-serif !important; font-weight: 800; letter-spacing: -0.03em; color: #E2E8F0; }
.es-card, .es-card-flat { background: #111620; border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px 24px; margin-bottom: 16px; transition: all 0.2s; }
.es-card:hover { border-color: rgba(0,230,118,0.35); transform: translateY(-2px); }
.kpi-wrap { display: flex; flex-direction: column; gap: 2px; }
.kpi-label { font-size: .65rem; font-weight: 700; text-transform: uppercase; letter-spacing: .14em; color: #64748B; }
.kpi-value { font-size: 2rem; font-weight: 900; line-height: 1.1; }
.kpi-sub { font-size: .68rem; color: #64748B; margin-top: 4px; }
.c-green { color: #00E676; }
.c-orange { color: #FF6B35; }
.c-blue { color: #38BDF8; }
.c-purple { color: #C084FC; }
.prog-track { background: rgba(255,255,255,0.05); border-radius: 99px; height: 5px; overflow: hidden; margin-top: 10px; }
.prog-fill { height: 100%; border-radius: 99px; transition: width .6s ease; }
.fill-purple { background: linear-gradient(90deg, #C084FC, #818CF8); }
.insight-box { padding: 12px 16px; border-radius: 10px; margin: 8px 0; font-size: .85rem; background: rgba(0,230,118,.05); border-left: 3px solid #00E676; }
.pill { display: inline-block; padding: 3px 10px; border-radius: 99px; font-size: .68rem; font-weight: 700; }
.pill-green { background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,.25); }
.stButton > button { border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s; }
.stButton > button:hover { transform: translateY(-1px); }
div[data-testid="stMetric"] label { color: #64748B !important; font-size: .7rem !important; }
#MainMenu, header, footer, .stDeployButton { display: none; }
@media (max-width: 768px) { .es-card, .es-card-flat { padding: 16px; } .kpi-value { font-size: 1.5rem; } }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. SPLASH CORRIGIDO
# -----------------------------------------------------------------------------
if "app_initialized" not in st.session_state:
    with st.container():
        st.image(SPLASH_URL, use_container_width=True)
        st.session_state["app_initialized"] = True
        time.sleep(0.5)
        st.rerun()

# -----------------------------------------------------------------------------
# 10. PAGES
# -----------------------------------------------------------------------------
def page_dashboard(user, weights, checkins, scores, xp):
    UI.section_header("Dashboard Estratégico", "Visão geral do seu comportamento e progresso")
    
    streak = AnalyticsEngine.streak(checkins["consistency_score"].tolist()) if not checkins.empty else 0
    cur_w = weights["weight"].iloc[-1] if not weights.empty else user["current_weight"]
    lvl_name, _, lvl_pct = LevelEngine.info(xp)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(UI.card(UI.kpi("ADHERENCE", f"{scores['adherence']:.0f}", "c-green", f"Streak {streak}d")), unsafe_allow_html=True)
    with col2: st.markdown(UI.card(UI.kpi("PESO ATUAL", f"{cur_w:.1f}kg", "c-blue")), unsafe_allow_html=True)
    with col3: st.markdown(UI.card(UI.kpi("DISCIPLINA", f"{scores['discipline']:.0f}", "c-purple")), unsafe_allow_html=True)
    with col4: st.markdown(UI.card(UI.kpi("RECUPERACAO", f"{scores['recovery']:.0f}", "c-orange")), unsafe_allow_html=True)
    
    st.markdown(UI.card(UI.kpi("NIVEL", lvl_name, "c-purple", f"{xp} XP") + UI.progress_bar(lvl_pct)), unsafe_allow_html=True)
    
    if checkins.empty:
        st.info("📝 Nenhum registro ainda. Vá em 'Registrar' para começar sua jornada.")

def page_register(uid: int, user: Dict):
    UI.section_header("Registrar Hoje", f"Entrada do dia {date.today().strftime('%d/%m/%Y')}")
    tab1, tab2 = st.tabs(["Check-in Diario", "Peso e Medidas"])
    
    with tab1:
        with st.form("form_checkin"):
            col1, col2 = st.columns(2)
            with col1:
                cal = st.number_input("Calorias", 0, 8000, 1800, 50)
                water = st.number_input("Agua (ml)", 0, 6000, 2500, 100)
                sleep = st.slider("Sono (h)", 0.0, 12.0, 7.0, 0.5)
            with col2:
                workout = st.number_input("Treino (min)", 0, 300, 0, 5)
                mood = st.slider("Humor (1-10)", 1, 10, 7)
                emotion = st.selectbox("Estado emocional", ["Focado", "Motivado", "Determinado", "Cansado", "Ansioso"])
            
            if st.form_submit_button("Salvar Check-in"):
                with st.spinner("Salvando..."):
                    cons = ConsistencyEngine.calculate(cal, water, sleep, workout, mood)
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
                        st.toast(f"Check-in salvo! +{xp} XP", icon="✅")
                        if cons >= 90:
                            st.balloons()
                    else:
                        st.toast("Check-in atualizado!", icon="✏️")
                    st.rerun()
    
    with tab2:
        with st.form("form_weight"):
            col1, col2, col3 = st.columns(3)
            with col1:
                w = st.number_input("Peso (kg)", CONST.WEIGHT_MIN, CONST.WEIGHT_MAX, float(user["current_weight"]), 0.1)
            with col2:
                bf = st.number_input("Gordura (%)", CONST.BODY_FAT_MIN, CONST.BODY_FAT_MAX, 20.0, 0.1)
            with col3:
                lm = st.number_input("Massa magra (kg)", CONST.LEAN_MASS_MIN, CONST.LEAN_MASS_MAX, 35.0, 0.1)
            
            if st.form_submit_button("Salvar Peso"):
                with st.spinner("Salvando..."):
                    data = {"date": date.today().isoformat(), "weight": w, "body_fat": bf, "lean_mass": lm}
                    xp = save_weight(uid, data)
                    if xp:
                        st.toast(f"Peso salvo! +{xp} XP", icon="⚖️")
                    else:
                        st.toast("Peso atualizado!", icon="✏️")
                    st.rerun()

def page_profile(uid: int, user: Dict):
    UI.section_header("Perfil", "Editar dados pessoais e metas")
    with st.form("form_profile"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome", user["name"])
            age = st.number_input("Idade", 18, 100, int(user["age"]))
            sex = st.selectbox("Sexo", ["M", "F"], index=0 if user["sex"] == "M" else 1)
        with col2:
            height = st.number_input("Altura (m)", 1.40, 2.20, float(user["height"]), 0.01)
            target = st.number_input("Meta de peso (kg)", CONST.WEIGHT_MIN, CONST.WEIGHT_MAX, float(user["target_weight"]), 0.5)
            acts = ["sedentario", "leve", "moderado", "intenso", "extremo"]
            act = st.selectbox("Nivel de atividade", acts, index=acts.index(user["activity_level"]) if user["activity_level"] in acts else 2)
        if st.form_submit_button("Salvar Alteracoes"):
            update_profile(uid, {"name": name, "age": age, "sex": sex, "height": height, "target_weight": target, "activity_level": act})
            st.toast("Perfil atualizado!", icon="👤")
            st.rerun()

def page_config(uid: int):
    UI.section_header("Configuracoes", "Exportar dados e opcoes do sistema")
    
    st.markdown("#### 📥 Exportar dados")
    if st.button("Gerar CSVs"):
        with st.spinner("Preparando..."):
            ch, wt = export_data(uid)
            st.download_button("Check-ins CSV", ch.to_csv(index=False), "checkins.csv", "text/csv")
            st.download_button("Pesos CSV", wt.to_csv(index=False), "weights.csv", "text/csv")
    
    st.markdown("---")
    st.markdown("#### ⚠️ Resetar dados")
    
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
            if st.button("✅ Sim, resetar tudo"):
                with st.spinner("Resetando..."):
                    reset_all(uid)
                    st.session_state.confirm_reset = False
                    st.toast("Dados resetados!", icon="🔄")
                    st.rerun()
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirm_reset = False
                st.rerun()

def page_telemetry(uid: int):
    UI.section_header("Telemetria", "Eventos e comportamento")
    df = get_events_df(uid)
    if df.empty:
        st.info("Nenhum evento registrado ainda.")
        return
    st.dataframe(df.head(50), use_container_width=True)

# -----------------------------------------------------------------------------
# 11. SIDEBAR
# -----------------------------------------------------------------------------
def render_sidebar(user: Dict, xp: int) -> str:
    lvl_name, _, lvl_pct = LevelEngine.info(xp)
    with st.sidebar:
        st.image(LOGO_URL, width=120)
        st.markdown(UI.card(UI.kpi("NIVEL", lvl_name, "c-purple", f"{xp} XP") + UI.progress_bar(lvl_pct)), unsafe_allow_html=True)
        page = st.radio("Navegacao", ["Dashboard", "Registrar", "Perfil", "Config", "Telemetria"], label_visibility="collapsed")
        st.markdown(f"<div style='margin-top:20px;font-size:.75rem;color:#64748B;'>Ola, {user.get('name', 'Usuario')}</div>", unsafe_allow_html=True)
    return page

# -----------------------------------------------------------------------------
# 12. MAIN
# -----------------------------------------------------------------------------
def main():
    init_db()
    
    user = load_user(USER_ID)
    if user is None:
        st.error("Erro ao carregar dados. Recarregue a pagina.")
        return
    
    weights = load_weights(USER_ID)
    checkins = load_checkins(USER_ID)
    xp = load_xp_total(USER_ID)
    scores = AnalyticsEngine.scores(checkins)
    
    page = render_sidebar(user, xp)
    
    if page == "Dashboard":
        page_dashboard(user, weights, checkins, scores, xp)
    elif page == "Registrar":
        page_register(USER_ID, user)
    elif page == "Perfil":
        page_profile(USER_ID, user)
    elif page == "Config":
        page_config(USER_ID)
    elif page == "Telemetria":
        page_telemetry(USER_ID)

if __name__ == "__main__":
    main()
