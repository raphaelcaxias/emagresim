# -*- coding: utf-8 -*-
"""
EmagreSim v6.0 - Behavioral Health OS
Arquivo único refatorado com:
- Engines de domínio (Consistency, XP, Analytics)
- Camada de serviços
- Validação real de dados
- Event tracking (telemetria)
- Cache seletivo
- Splash screen corrigida
- Reset com confirmação dupla
- Requests com retry
- Fórmula de consistência realista
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import logging
import json
import os
from datetime import datetime, timedelta, date
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from scipy import stats
import plotly.express as px
import requests
from io import BytesIO
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES GLOBAIS
# -----------------------------------------------------------------------------
IS_DEV = os.environ.get("EMAGRESIM_ENV", "dev") == "dev"
CACHE_TTL = 5 if IS_DEV else 120
DB_PATH = "emagresim_v6.db"
USER_ID = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger("emagresim")

st.set_page_config(
    page_title="EmagreSim | Behavioral OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. DESIGN SYSTEM
# -----------------------------------------------------------------------------
@dataclass
class C:
    BG: str = "#070910"
    SURFACE: str = "#0d1117"
    CARD: str = "#111620"
    BORDER: str = "rgba(255,255,255,0.05)"
    BORDER_HL: str = "rgba(0,230,118,0.35)"
    PRIMARY: str = "#00E676"
    PRIMARY_DIM: str = "rgba(0,230,118,0.15)"
    ORANGE: str = "#FF6B35"
    BLUE: str = "#38BDF8"
    PURPLE: str = "#C084FC"
    AMBER: str = "#FBBF24"
    TEXT: str = "#E2E8F0"
    MUTED: str = "#64748B"
    DANGER: str = "#F87171"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

.stApp {{ background: {C.BG} !important; }}
section[data-testid="stSidebar"] {{
    background: {C.SURFACE} !important;
    border-right: 1px solid {C.BORDER};
}}

*, p, div, span, label, .stMarkdown {{
    font-family: 'Outfit', sans-serif !important;
}}
h1, h2, h3, h4 {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: {C.TEXT};
}}

.es-card {{
    background: {C.CARD};
    border: 1px solid {C.BORDER};
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s, transform 0.2s;
}}
.es-card:hover {{
    border-color: {C.BORDER_HL};
    transform: translateY(-2px);
}}

.kpi-wrap {{ display: flex; flex-direction: column; gap: 2px; }}
.kpi-label {{ font-size: .65rem; font-weight: 700; text-transform: uppercase;
               letter-spacing: .14em; color: {C.MUTED}; }}
.kpi-value {{ font-size: 2rem; font-weight: 900; line-height: 1.1; }}
.kpi-sub {{ font-size: .68rem; color: {C.MUTED}; margin-top: 4px; }}

.c-green {{ color: {C.PRIMARY}; }}
.c-orange {{ color: {C.ORANGE}; }}
.c-blue {{ color: {C.BLUE}; }}
.c-purple {{ color: {C.PURPLE}; }}

.prog-track {{
    background: rgba(255,255,255,0.05);
    border-radius: 99px; height: 5px;
    overflow: hidden; margin-top: 10px;
}}
.prog-fill {{ height: 100%; border-radius: 99px; transition: width .6s ease; }}
.fill-purple {{ background: linear-gradient(90deg, {C.PURPLE}, #818CF8); }}

.insight-box {{
    padding: 12px 16px; border-radius: 10px;
    margin: 8px 0; font-size: .85rem; line-height: 1.55;
}}
.ins-info {{ background: rgba(0,230,118,.05); border-left: 3px solid {C.PRIMARY}; }}

.pill {{
    display: inline-block; padding: 3px 10px; border-radius: 99px;
    font-size: .68rem; font-weight: 700; letter-spacing: .08em;
}}
.pill-green {{ background: {C.PRIMARY_DIM}; color: {C.PRIMARY}; }}

.stButton > button {{ border-radius: 10px !important; font-weight: 600 !important; }}
div[data-testid="stMetric"] label {{ color: {C.MUTED} !important; font-size: .7rem !important; }}

#MainMenu, header, footer, .stDeployButton {{ display: none !important; }}
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: {C.BG}; }}
::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 99px; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. IMAGENS E ASSETS (COM RETRY E FALLBACK)
# -----------------------------------------------------------------------------
def get_session_with_retries() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_fallback_image() -> Optional[Image.Image]:
    """Cria uma imagem simples de fallback (círculo com texto)"""
    try:
        img = Image.new('RGB', (200, 200), color=C.CARD)
        return img
    except:
        return None

def load_image_from_url(url: str) -> Optional[Image.Image]:
    """Carrega imagem com retry e fallback. SEM CACHE (evita pickle error)"""
    session = get_session_with_retries()
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception as e:
        logger.warning(f"Erro ao carregar {url}: {e}")
    return get_fallback_image()

# URLs raw
LOGO_URL = "https://raw.githubusercontent.com/raphaelcaxias/emagresim/main/logo.png"
ICON_URL = "https://raw.githubusercontent.com/raphaelcaxias/emagresim/main/icon.png"
SPLASH_URL = "https://raw.githubusercontent.com/raphaelcaxias/emagresim/main/splash.png"

logo_img = load_image_from_url(LOGO_URL)
icon_img = load_image_from_url(ICON_URL)
splash_img = load_image_from_url(SPLASH_URL)

# -----------------------------------------------------------------------------
# 4. SPLASH SCREEN CORRIGIDA (SEM RERUN INFINITO)
# -----------------------------------------------------------------------------
if splash_img and "splash_shown" not in st.session_state:
    with st.container():
        st.image(splash_img, use_container_width=True)
        st.session_state["splash_shown"] = True
        # Pequeno delay visual antes de limpar
        import time
        time.sleep(0.5)
        st.rerun()

# -----------------------------------------------------------------------------
# 5. DATABASE LAYER
# -----------------------------------------------------------------------------
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'Usuario',
    age INT NOT NULL DEFAULT 30,
    sex TEXT NOT NULL DEFAULT 'M',
    height REAL NOT NULL DEFAULT 1.75,
    current_weight REAL NOT NULL DEFAULT 80.0,
    target_weight REAL NOT NULL DEFAULT 70.0,
    activity_level TEXT NOT NULL DEFAULT 'moderado',
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
    UNIQUE(user_id, badge_key),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS xp_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    amount INT NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    event_name TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_checkins ON daily_checkins(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_weights ON weight_logs(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_events ON user_events(user_id, created_at DESC);
"""

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
        conn.executescript(SCHEMA_SQL)
    logger.info("DB initialized")

def seed_if_empty():
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM daily_checkins").fetchone()[0]
        if count > 0:
            return
        conn.execute(
            "INSERT INTO users VALUES (1,'Usuario Demo',30,'M',1.78,88.0,72.0,'moderado',CURRENT_TIMESTAMP)"
        )
        end_date = date.today() - timedelta(days=1)
        dates = [end_date - timedelta(days=x) for x in range(180)][::-1]
        rng = np.random.default_rng(42)
        weights = []
        checkins = []
        base_w = 88.0
        for i, d in enumerate(dates):
            w = max(base_w - 0.025 * i + rng.normal(0, 0.3), 55.0)
            bf = round(max(22 - 0.04 * i, 8), 1)
            lm = round(35 + 0.008 * i, 1)
            weights.append((1, d.isoformat(), round(w, 1), bf, lm))
            cons = int(np.clip(70 - 0.1 * i + rng.normal(0, 8), 40, 98))
            disc = int(np.clip(cons + rng.integers(-5, 6), 40, 98))
            checkins.append((1, d.isoformat(), 1800, 2500, 7.2, 45, 6, cons, "Motivado", disc))
        conn.executemany("INSERT INTO weight_logs(user_id,date,weight,body_fat,lean_mass) VALUES(?,?,?,?,?)", weights)
        conn.executemany("INSERT INTO daily_checkins(user_id,date,calories_consumed,water_ml,sleep_hours,workout_minutes,mood_score,consistency_score,emotional_state,discipline_score) VALUES(?,?,?,?,?,?,?,?,?,?)", checkins)
        conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(1,500,'seed')")
    logger.info("Seed: 180 days generated")

# -----------------------------------------------------------------------------
# 6. DOMAIN ENGINES
# -----------------------------------------------------------------------------
class DataValidator:
    @staticmethod
    def validate_weight(weight: float, body_fat: float, lean_mass: float) -> Tuple[bool, str]:
        if weight < 30 or weight > 300:
            return False, "Peso fora do range fisiológico (30-300 kg)"
        if body_fat < 3 or body_fat > 60:
            return False, "Gordura corporal fora do range (3-60%)"
        if lean_mass < 20 or lean_mass > 120:
            return False, "Massa magra fora do range (20-120 kg)"
        
        fat_mass = weight * body_fat / 100
        expected = lean_mass + fat_mass
        if weight > 0 and abs(expected - weight) / weight > 0.08:
            return False, f"Inconsistência: massa magra({lean_mass}) + gordura({fat_mass:.1f}) ≠ peso({weight:.1f})"
        return True, ""

class ConsistencyEngine:
    @staticmethod
    def calculate(calories: float, water_ml: int, sleep_hours: float, 
                  workout_minutes: int, mood_score: int) -> int:
        """Fórmula realista de consistência (0-100)"""
        # Calorias: 1800 é ideal, desvio máximo 800kcal
        cal_score = max(0, 100 - abs(calories - 1800) / 18)
        cal_score = min(cal_score, 100)
        
        # Água: 2000ml baseline, 3000ml excelente
        water_score = min(water_ml / 35, 100)
        
        # Sono: 7h baseline, 8h+ excelente
        sleep_score = min(sleep_hours / 8.5 * 100, 100)
        
        # Treino: 30min baseline, 60min excelente
        workout_score = min(workout_minutes / 45 * 100, 100)
        
        # Humor: influência moderada (10-100)
        mood_score_norm = mood_score * 10
        
        # Ponderadores realistas
        consistency = (
            cal_score * 0.30 +
            water_score * 0.15 +
            sleep_score * 0.20 +
            workout_score * 0.25 +
            mood_score_norm * 0.10
        )
        return int(np.clip(consistency, 0, 100))

class XPEngine:
    @staticmethod
    def calculate(consistency: int, sleep_hours: float, workout_minutes: int) -> int:
        xp = 10  # base
        if consistency >= 80:
            xp += 20
        if sleep_hours >= 8:
            xp += 40
        if workout_minutes >= 30:
            xp += 15
        return xp
    
    @staticmethod
    def can_earn(uid: int, source: str) -> bool:
        """Anti-fraude: cooldown de 12h para mesma fonte"""
        with db() as conn:
            row = conn.execute(
                "SELECT MAX(created_at) FROM xp_logs WHERE user_id=? AND source=?",
                (uid, source)
            ).fetchone()
            if row and row[0]:
                last = datetime.fromisoformat(row[0])
                hours_since = (datetime.now() - last).total_seconds() / 3600
                return hours_since >= 12
        return True

class AnalyticsEngine:
    @staticmethod
    def scores(checkins: pd.DataFrame) -> Dict[str, float]:
        empty = {"adherence": 0.0, "discipline": 0.0, "recovery": 0.0, "momentum": 0.0, "stability": 0.0}
        if checkins.empty:
            return empty
        r30 = checkins.tail(30)
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

class LevelEngine:
    LEVELS = [("Lenda Fit", 6000), ("Elite", 3000), ("Atleta", 1500), ("Guerreiro", 500), ("Iniciante", 0)]
    
    @staticmethod
    def info(xp: int) -> Tuple[str, float, float]:
        for i, (name, thr) in enumerate(LevelEngine.LEVELS):
            if xp >= thr:
                next_thr = LevelEngine.LEVELS[i-1][1] if i > 0 else thr + 2000
                progress = (xp - thr) / max(next_thr - thr, 1) * 100
                return name, next_thr, min(progress, 100)
        return "Iniciante", 500, 0.0

# -----------------------------------------------------------------------------
# 7. SERVICES (COM EVENT TRACKING)
# -----------------------------------------------------------------------------
def track_event(uid: int, event_name: str, metadata: dict = None):
    with db() as conn:
        conn.execute(
            "INSERT INTO user_events(user_id, event_name, metadata) VALUES(?,?,?)",
            (uid, event_name, json.dumps(metadata or {}))
        )
    logger.info(f"Event: {event_name}")

@st.cache_data(ttl=CACHE_TTL)
def load_all(uid: int = USER_ID) -> Tuple[Dict, pd.DataFrame, pd.DataFrame]:
    with db() as conn:
        user_row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not user_row:
            raise ValueError(f"User {uid} not found")
        user = dict(user_row)
        weights = pd.read_sql("SELECT * FROM weight_logs WHERE user_id=? ORDER BY date", conn, params=(uid,), parse_dates=["date"])
        checkins = pd.read_sql("SELECT * FROM daily_checkins WHERE user_id=? ORDER BY date", conn, params=(uid,), parse_dates=["date"])
    return user, weights, checkins

@st.cache_data(ttl=CACHE_TTL)
def load_xp(uid: int = USER_ID) -> int:
    with db() as conn:
        row = conn.execute("SELECT COALESCE(SUM(amount),0) AS total FROM xp_logs WHERE user_id=?", (uid,)).fetchone()
    return int(row["total"]) if row else 0

def save_checkin(uid: int, data: dict) -> int:
    valid, msg = DataValidator.validate_weight(
        data.get("weight", 80), 
        data.get("body_fat", 20), 
        data.get("lean_mass", 35)
    ) if "weight" in data else (True, "")
    if not valid:
        st.error(f"❌ {msg}")
        return 0
    
    with db() as conn:
        existing = conn.execute("SELECT id FROM daily_checkins WHERE user_id=? AND date=?", (uid, data["date"])).fetchone()
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(f"UPDATE daily_checkins SET {set_clause} WHERE user_id=? AND date=?", list(data.values()) + [uid, data["date"]])
            xp = 0
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            conn.execute(f"INSERT INTO daily_checkins(user_id,{cols}) VALUES(?,{placeholders})", [uid] + list(data.values()))
            xp = XPEngine.calculate(data.get("consistency_score", 0), data.get("sleep_hours", 0), data.get("workout_minutes", 0))
            if XPEngine.can_earn(uid, "checkin"):
                conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)", (uid, xp, "checkin"))
            else:
                xp = 0
        track_event(uid, "checkin_saved", {"xp": xp, "date": data["date"]})
    
    st.cache_data.clear()
    return xp

def save_weight(uid: int, data: dict) -> int:
    valid, msg = DataValidator.validate_weight(data["weight"], data.get("body_fat", 20), data.get("lean_mass", 35))
    if not valid:
        st.error(f"❌ {msg}")
        return 0
    
    with db() as conn:
        existing = conn.execute("SELECT id FROM weight_logs WHERE user_id=? AND date=?", (uid, data["date"])).fetchone()
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(f"UPDATE weight_logs SET {set_clause} WHERE user_id=? AND date=?", list(data.values()) + [uid, data["date"]])
            xp = 0
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            conn.execute(f"INSERT INTO weight_logs(user_id,{cols}) VALUES(?,{placeholders})", [uid] + list(data.values()))
            xp = 20
            if XPEngine.can_earn(uid, "weight"):
                conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)", (uid, xp, "weight"))
            else:
                xp = 0
        conn.execute("UPDATE users SET current_weight=? WHERE id=?", (data["weight"], uid))
        track_event(uid, "weight_saved", {"weight": data["weight"], "date": data["date"]})
    
    st.cache_data.clear()
    return xp

def update_profile(uid: int, updates: dict):
    with db() as conn:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", list(updates.values()) + [uid])
        track_event(uid, "profile_updated", updates)
    st.cache_data.clear()

def unlock_badge(uid: int, badge_key: str) -> bool:
    with db() as conn:
        try:
            conn.execute("INSERT INTO user_badges(user_id,badge_key) VALUES(?,?)", (uid, badge_key))
            track_event(uid, "badge_unlocked", {"badge": badge_key})
            return True
        except sqlite3.IntegrityError:
            return False

def get_badges(uid: int) -> List[str]:
    with db() as conn:
        rows = conn.execute("SELECT badge_key FROM user_badges WHERE user_id=?", (uid,)).fetchall()
        return [r["badge_key"] for r in rows]

def reset_all(uid: int = USER_ID):
    with db() as conn:
        for tbl in ("xp_logs", "user_badges", "user_events", "daily_checkins", "weight_logs", "users"):
            conn.execute(f"DELETE FROM {tbl} WHERE {'user_id' if tbl != 'users' else 'id'}=?", (uid,))
    seed_if_empty()
    track_event(uid, "reset_data", {})
    st.cache_data.clear()

def export_data(uid: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    with db() as conn:
        checkins = pd.read_sql("SELECT * FROM daily_checkins WHERE user_id=? ORDER BY date", conn, params=(uid,))
        weights = pd.read_sql("SELECT * FROM weight_logs WHERE user_id=? ORDER BY date", conn, params=(uid,))
    return checkins, weights

def get_events_df(uid: int) -> pd.DataFrame:
    with db() as conn:
        return pd.read_sql("SELECT * FROM user_events WHERE user_id=? ORDER BY created_at DESC", conn, params=(uid,), parse_dates=["created_at"])

# -----------------------------------------------------------------------------
# 8. UI COMPONENTS
# -----------------------------------------------------------------------------
def card(html: str, flat: bool = False) -> str:
    cls = "es-card-flat" if flat else "es-card"
    return f'<div class="{cls}">{html}</div>'

def kpi(label: str, value: str, cls: str = "c-green", sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi-wrap"><div class="kpi-label">{label}</div><div class="kpi-value {cls}">{value}</div>{sub_html}</div>'

def progress_bar(pct: float, color_class: str = "fill-purple") -> str:
    return f'<div class="prog-track"><div class="prog-fill {color_class}" style="width:{pct:.1f}%"></div></div>'

def insight_box(text: str) -> str:
    return f'<div class="insight-box ins-info">💡 {text}</div>'

def section_header(title: str, subtitle: str = "") -> None:
    sub = f'<p style="color:{C.MUTED};font-size:.85rem;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"<h2>{title}</h2>{sub}<hr style='border:none;border-top:1px solid {C.BORDER};margin:12px 0 20px 0;'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. PAGES
# -----------------------------------------------------------------------------
def page_dashboard(user, weights, checkins, scores, xp):
    section_header("Dashboard Estratégico", "Visão geral do seu comportamento e progresso")
    
    streak = AnalyticsEngine.streak(checkins["consistency_score"].tolist()) if not checkins.empty else 0
    cur_w = weights["weight"].iloc[-1] if not weights.empty else user["current_weight"]
    lvl_name, _, lvl_pct = LevelEngine.info(xp)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(card(kpi("ADHERENCE", f"{scores['adherence']:.0f}", "c-green", f"Streak {streak}d")), unsafe_allow_html=True)
    with col2:
        st.markdown(card(kpi("PESO ATUAL", f"{cur_w:.1f}kg", "c-blue")), unsafe_allow_html=True)
    with col3:
        st.markdown(card(kpi("DISCIPLINA", f"{scores['discipline']:.0f}", "c-purple")), unsafe_allow_html=True)
    with col4:
        st.markdown(card(kpi("RECUPERACAO", f"{scores['recovery']:.0f}", "c-orange")), unsafe_allow_html=True)
    
    st.markdown(card(kpi("NIVEL", lvl_name, "c-purple", f"{xp} XP") + progress_bar(lvl_pct)), unsafe_allow_html=True)
    
    if checkins.empty:
        st.info("📝 Nenhum registro ainda. Vá em 'Registrar' para começar sua jornada.")

def page_register(uid: int, user: Dict):
    section_header("Registrar Hoje", f"Entrada do dia {date.today().strftime('%d/%m/%Y')}")
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
                else:
                    st.toast("Check-in atualizado!", icon="✏️")
                st.rerun()
    
    with tab2:
        with st.form("form_weight"):
            col1, col2, col3 = st.columns(3)
            with col1:
                w = st.number_input("Peso (kg)", 40.0, 250.0, float(user["current_weight"]), 0.1)
            with col2:
                bf = st.number_input("Gordura (%)", 3.0, 60.0, 20.0, 0.1)
            with col3:
                lm = st.number_input("Massa magra (kg)", 20.0, 120.0, 35.0, 0.1)
            if st.form_submit_button("Salvar Peso"):
                data = {"date": date.today().isoformat(), "weight": w, "body_fat": bf, "lean_mass": lm}
                xp = save_weight(uid, data)
                if xp:
                    st.toast(f"Peso salvo! +{xp} XP", icon="⚖️")
                else:
                    st.toast("Peso atualizado!", icon="✏️")
                st.rerun()

def page_profile(uid: int, user: Dict):
    section_header("Perfil", "Editar dados pessoais e metas")
    with st.form("form_profile"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome", user["name"])
            age = st.number_input("Idade", 18, 100, int(user["age"]))
            sex = st.selectbox("Sexo", ["M", "F"], index=0 if user["sex"] == "M" else 1)
        with col2:
            height = st.number_input("Altura (m)", 1.40, 2.20, float(user["height"]), 0.01)
            target = st.number_input("Meta de peso (kg)", 40.0, 200.0, float(user["target_weight"]), 0.5)
            acts = ["sedentario", "leve", "moderado", "intenso", "extremo"]
            act = st.selectbox("Nivel de atividade", acts, index=acts.index(user["activity_level"]) if user["activity_level"] in acts else 2)
        if st.form_submit_button("Salvar Alteracoes"):
            update_profile(uid, {"name": name, "age": age, "sex": sex, "height": height, "target_weight": target, "activity_level": act})
            st.toast("Perfil atualizado!", icon="👤")
            st.rerun()

def page_config(uid: int):
    section_header("Configuracoes", "Exportar dados e opcoes do sistema")
    
    st.markdown("#### 📥 Exportar dados")
    if st.button("Gerar CSVs"):
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
                reset_all(uid)
                st.session_state.confirm_reset = False
                st.toast("Dados resetados!", icon="🔄")
                st.rerun()
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirm_reset = False
                st.rerun()

def page_telemetry(uid: int):
    section_header("Telemetria", "Eventos e comportamento")
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
        if logo_img:
            st.image(logo_img, width=120)
        else:
            st.markdown("<h2>⚡ EmagreSim</h2>", unsafe_allow_html=True)
        st.markdown(card(kpi("NIVEL", lvl_name, "c-purple", f"{xp} XP") + progress_bar(lvl_pct)), unsafe_allow_html=True)
        page = st.radio("Navegacao", ["Dashboard", "Registrar", "Perfil", "Config", "Telemetria"], label_visibility="collapsed")
        st.markdown(f"<div style='margin-top:20px;font-size:.75rem;color:{C.MUTED};'>Ola, {user.get('name', 'Usuario')}</div>", unsafe_allow_html=True)
    return page

# -----------------------------------------------------------------------------
# 11. MAIN
# -----------------------------------------------------------------------------
def main():
    init_db()
    seed_if_empty()
    user, weights, checkins = load_all(USER_ID)
    xp = load_xp(USER_ID)
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
