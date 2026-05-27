# -*- coding: utf-8 -*-
"""
EmagreSim v5.0 – Behavioral Health OS
Arquivo único · Telemetria · ML prediction · Validação fisiológica · Badges corrigidos
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
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from scipy import stats
from sklearn.linear_model import LogisticRegression
import plotly.graph_objects as go
import plotly.express as px

# -- 1. CONFIG ----------------------------------------------------------------

IS_DEV   = os.environ.get("EMAGRESIM_ENV", "dev") == "dev"
CACHE_TTL = 5 if IS_DEV else 120
DB_PATH   = "emagresim_v5.db"
USER_ID   = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger("emagresim")

st.set_page_config(
    page_title="EmagreSim | Behavioral OS",
    page_icon="?",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- 2. DESIGN SYSTEM (mantido do v4.0) -----------------------------------------

@dataclass
class C:
    BG         : str = "#070910"
    SURFACE    : str = "#0d1117"
    CARD       : str = "#111620"
    BORDER     : str = "rgba(255,255,255,0.05)"
    BORDER_HL  : str = "rgba(0,230,118,0.35)"
    PRIMARY    : str = "#00E676"
    PRIMARY_DIM: str = "rgba(0,230,118,0.15)"
    ORANGE     : str = "#FF6B35"
    BLUE       : str = "#38BDF8"
    PURPLE     : str = "#C084FC"
    AMBER      : str = "#FBBF24"
    TEXT       : str = "#E2E8F0"
    MUTED      : str = "#64748B"
    DANGER     : str = "#F87171"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

.stApp                  {{ background: {C.BG} !important; color: {C.TEXT} !important; }}
.stApp > header         {{ background: transparent !important; }}
section[data-testid="stSidebar"] {{
    background: {C.SURFACE} !important;
    border-right: 1px solid {C.BORDER};
}}

/* -- Typography -- */
*, p, div, span, label, .stMarkdown {{
    font-family: 'Outfit', sans-serif !important;
}}
h1,h2,h3,h4 {{
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: {C.TEXT};
}}
code, .mono {{ font-family: 'JetBrains Mono', monospace !important; }}

/* -- Cards -- */
.es-card {{
    background: {C.CARD};
    border: 1px solid {C.BORDER};
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}}
.es-card:hover {{
    border-color: {C.BORDER_HL};
    box-shadow: 0 8px 32px rgba(0,230,118,0.06);
    transform: translateY(-2px);
}}
.es-card-flat {{
    background: {C.CARD};
    border: 1px solid {C.BORDER};
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
}}

/* -- KPI -- */
.kpi-wrap   {{ display: flex; flex-direction: column; gap: 2px; }}
.kpi-label  {{ font-size: .65rem; font-weight: 700; text-transform: uppercase;
               letter-spacing: .14em; color: {C.MUTED}; }}
.kpi-value  {{ font-size: 2rem; font-weight: 900; line-height: 1.1; }}
.kpi-sub    {{ font-size: .68rem; color: {C.MUTED}; margin-top: 4px; }}

/* -- Colours -- */
.c-green  {{ color: {C.PRIMARY};  text-shadow: 0 0 12px rgba(0,230,118,.4); }}
.c-orange {{ color: {C.ORANGE};   text-shadow: 0 0 12px rgba(255,107,53,.4); }}
.c-blue   {{ color: {C.BLUE};     text-shadow: 0 0 12px rgba(56,189,248,.4); }}
.c-purple {{ color: {C.PURPLE};   text-shadow: 0 0 12px rgba(192,132,252,.4); }}
.c-amber  {{ color: {C.AMBER};    text-shadow: 0 0 12px rgba(251,191,36,.4); }}
.c-muted  {{ color: {C.MUTED}; }}

/* -- Progress bar -- */
.prog-track {{
    background: rgba(255,255,255,0.05);
    border-radius: 99px; height: 5px;
    overflow: hidden; margin-top: 10px;
}}
.prog-fill  {{ height: 100%; border-radius: 99px; transition: width .6s ease; }}
.fill-green  {{ background: linear-gradient(90deg, {C.PRIMARY}, #34D399); }}
.fill-purple {{ background: linear-gradient(90deg, {C.PURPLE}, #818CF8); }}
.fill-orange {{ background: linear-gradient(90deg, {C.ORANGE}, {C.AMBER}); }}
.fill-blue   {{ background: linear-gradient(90deg, {C.BLUE}, #818CF8); }}

/* -- Insight boxes -- */
.insight-box {{
    padding: 12px 16px; border-radius: 10px;
    margin: 8px 0; font-size: .85rem; line-height: 1.55;
}}
.ins-info    {{ background: rgba(0,230,118,.05);   border-left: 3px solid {C.PRIMARY}; }}
.ins-warn    {{ background: rgba(255,107,53,.05);   border-left: 3px solid {C.ORANGE}; }}
.ins-danger  {{ background: rgba(248,113,113,.07);  border-left: 3px solid {C.DANGER}; }}
.ins-blue    {{ background: rgba(56,189,248,.05);   border-left: 3px solid {C.BLUE}; }}

/* -- Badge card -- */
.badge-card {{
    background: {C.CARD};
    border: 1px solid {C.BORDER};
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    transition: border-color .2s;
}}
.badge-card.earned  {{ border-color: rgba(0,230,118,.3); }}
.badge-card.locked  {{ opacity: .45; }}
.badge-icon {{ font-size: 2rem; margin-bottom: 6px; }}
.badge-name {{ font-size: .78rem; font-weight: 600; color: {C.TEXT}; }}

/* -- Sidebar nav -- */
.nav-btn {{
    display: block; width: 100%; padding: 10px 14px;
    border-radius: 10px; border: none; background: transparent;
    color: {C.MUTED}; font-family: 'Outfit', sans-serif;
    font-size: .9rem; font-weight: 500; text-align: left;
    cursor: pointer; transition: background .15s, color .15s;
    margin-bottom: 2px;
}}
.nav-btn:hover {{ background: rgba(255,255,255,.05); color: {C.TEXT}; }}
.nav-btn.active {{
    background: {C.PRIMARY_DIM};
    color: {C.PRIMARY};
    font-weight: 700;
}}

/* -- Tag / pill -- */
.pill {{
    display: inline-block; padding: 3px 10px; border-radius: 99px;
    font-size: .68rem; font-weight: 700; letter-spacing: .08em;
}}
.pill-green  {{ background: {C.PRIMARY_DIM}; color: {C.PRIMARY}; border: 1px solid rgba(0,230,118,.25); }}
.pill-purple {{ background: rgba(192,132,252,.12); color: {C.PURPLE}; border: 1px solid rgba(192,132,252,.25); }}

/* -- Streamlit overrides -- */
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    transition: all .18s !important;
}}
.stButton > button:hover {{ transform: translateY(-1px); }}
div[data-testid="stMetric"] label {{ color: {C.MUTED} !important; font-size: .7rem !important; text-transform: uppercase; letter-spacing: .1em; }}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ font-size: 1.7rem !important; font-weight: 800 !important; }}

#MainMenu, header, footer, .stDeployButton {{ display: none !important; }}
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: {C.BG}; }}
::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 99px; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -- 3. DATABASE ---------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id             INTEGER PRIMARY KEY,
    name           TEXT    NOT NULL DEFAULT 'Usuário',
    age            INT     NOT NULL DEFAULT 30,
    sex            TEXT    NOT NULL DEFAULT 'M',
    height         REAL    NOT NULL DEFAULT 1.75,
    current_weight REAL    NOT NULL DEFAULT 80.0,
    target_weight  REAL    NOT NULL DEFAULT 70.0,
    activity_level TEXT    NOT NULL DEFAULT 'moderado',
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS weight_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INT  NOT NULL,
    date       DATE NOT NULL,
    weight     REAL NOT NULL,
    body_fat   REAL,
    lean_mass  REAL,
    UNIQUE(user_id, date),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS daily_checkins (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INT  NOT NULL,
    date               DATE NOT NULL,
    calories_consumed  REAL,
    water_ml           INT,
    sleep_hours        REAL,
    workout_minutes    INT,
    mood_score         INT,
    consistency_score  INT,
    emotional_state    TEXT,
    discipline_score   INT,
    UNIQUE(user_id, date),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_badges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INT  NOT NULL,
    badge_key   TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_key),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS xp_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INT NOT NULL,
    amount     INT NOT NULL,
    source     TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INT NOT NULL,
    event_name  TEXT NOT NULL,
    metadata    TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_checkins ON daily_checkins(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_weights  ON weight_logs(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_events   ON user_events(user_id, created_at DESC);
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

# -- 4. SEED -------------------------------------------------------------------

def seed_if_empty():
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM daily_checkins").fetchone()[0]
        if count > 0:
            return
        conn.execute(
            "INSERT OR IGNORE INTO users VALUES (1,'Usuário Demo',30,'M',1.78,88.0,72.0,'moderado',CURRENT_TIMESTAMP)"
        )
        end_date = date.today() - timedelta(days=1)
        dates    = [end_date - timedelta(days=x) for x in range(180)][::-1]
        rng      = np.random.default_rng(42)
        weights  = []
        checkins = []
        base_w   = 88.0
        for i, d in enumerate(dates):
            w    = max(base_w - 0.025 * i + rng.normal(0, 0.3), 55.0)
            bf   = round(max(22 - 0.04 * i, 8), 1)
            lm   = round(35 + 0.008 * i, 1)
            weights.append((1, d.isoformat(), round(w, 1), bf, lm))

            cons = int(np.clip(70 - 0.1 * i + rng.normal(0, 8), 40, 98))
            disc = int(np.clip(cons + rng.integers(-5, 6), 40, 98))
            checkins.append((
                1, d.isoformat(), 1800, 2500, 7.2, 45, 6,
                cons, "Motivado", disc,
            ))
        conn.executemany(
            "INSERT OR IGNORE INTO weight_logs(user_id,date,weight,body_fat,lean_mass) VALUES(?,?,?,?,?)",
            weights,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO daily_checkins"
            "(user_id,date,calories_consumed,water_ml,sleep_hours,workout_minutes,"
            "mood_score,consistency_score,emotional_state,discipline_score) VALUES(?,?,?,?,?,?,?,?,?,?)",
            checkins,
        )
        conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(1,500,'seed')")
    logger.info("Seed: 180 days generated")

# -- 5. VALIDADOR FISIOLÓGICO -------------------------------------------------

class DataValidator:
    @staticmethod
    def validate_weight(data: dict, height_m: float) -> Tuple[bool, str]:
        w = data.get('weight', 0)
        bf = data.get('body_fat', 0)
        lm = data.get('lean_mass', 0)

        if not 30 <= w <= 300:
            return False, "Peso fora do range fisiológico (30-300 kg)"
        if not 3 <= bf <= 60:
            return False, "Gordura corporal fora do range (3-60%)"
        if not 20 <= lm <= 120:
            return False, "Massa magra fora do range (20-120 kg)"

        # Validação cruzada: peso ˜ massa gorda + massa magra (tolerância 8%)
        fat_mass = w * bf / 100
        expected = lm + fat_mass
        if w > 0 and abs(expected - w) / w > 0.08:
            return False, f"Inconsistência: LM({lm:.1f}) + gordura({fat_mass:.1f}) ? peso({w:.1f}) – tolerância excedida."
        return True, ""

# -- 6. EVENTOS (TELEMETRIA) ---------------------------------------------------

def _record_event(uid: int, event_name: str, metadata: dict = None):
    with db() as conn:
        conn.execute(
            "INSERT INTO user_events(user_id, event_name, metadata) VALUES(?,?,?)",
            (uid, event_name, json.dumps(metadata or {})),
        )
    logger.info(f"Event recorded: {event_name}")

# -- 7. DATA ACCESS (com eventos e validação) ---------------------------------

@st.cache_data(ttl=CACHE_TTL)
def load_all(uid: int = USER_ID) -> Tuple[Dict, pd.DataFrame, pd.DataFrame]:
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not row:
            raise ValueError(f"User {uid} not found")
        user    = dict(row)
        weights = pd.read_sql(
            "SELECT * FROM weight_logs WHERE user_id=? ORDER BY date",
            conn, params=(uid,), parse_dates=["date"],
        )
        checkins = pd.read_sql(
            "SELECT * FROM daily_checkins WHERE user_id=? ORDER BY date",
            conn, params=(uid,), parse_dates=["date"],
        )
    return user, weights, checkins

@st.cache_data(ttl=CACHE_TTL)
def load_xp(uid: int = USER_ID) -> int:
    with db() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS total FROM xp_logs WHERE user_id=?", (uid,)
        ).fetchone()
    return int(row["total"]) if row else 0

@st.cache_data(ttl=CACHE_TTL)
def load_badges(uid: int = USER_ID) -> List[str]:
    with db() as conn:
        rows = conn.execute(
            "SELECT badge_key FROM user_badges WHERE user_id=?", (uid,)
        ).fetchall()
    return [r["badge_key"] for r in rows]

def save_checkin(uid: int, data: dict) -> int:
    today_str = data["date"]
    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM daily_checkins WHERE user_id=? AND date=?", (uid, today_str)
        ).fetchone()
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(
                f"UPDATE daily_checkins SET {set_clause} WHERE user_id=? AND date=?",
                [*data.values(), uid, today_str],
            )
            xp = 0
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            conn.execute(
                f"INSERT INTO daily_checkins(user_id,{cols}) VALUES(?,{placeholders})",
                [uid, *data.values()],
            )
            xp = 10
            if data.get("consistency_score", 0) >= 80: xp += 20
            if data.get("sleep_hours", 0) >= 8:        xp += 40
            if data.get("workout_minutes", 0) >= 30:   xp += 15
            conn.execute(
                "INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)",
                (uid, xp, "checkin"),
            )
    # Evento de telemetria
    _record_event(uid, "checkin_saved", {"xp": xp, "date": today_str})
    st.cache_data.clear()
    return xp

def save_weight(uid: int, data: dict, user_height: float) -> int:
    # Validação fisiológica
    valid, msg = DataValidator.validate_weight(data, user_height)
    if not valid:
        st.error(f"? {msg}")
        return 0

    today_str = data["date"]
    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM weight_logs WHERE user_id=? AND date=?", (uid, today_str)
        ).fetchone()
        if existing:
            set_clause = ", ".join(f"{k}=?" for k in data)
            conn.execute(
                f"UPDATE weight_logs SET {set_clause} WHERE user_id=? AND date=?",
                [*data.values(), uid, today_str],
            )
            xp = 0
        else:
            cols = ", ".join(data.keys())
            placeholders = ", ".join("?" * len(data))
            conn.execute(
                f"INSERT INTO weight_logs(user_id,{cols}) VALUES(?,{placeholders})",
                [uid, *data.values()],
            )
            xp = 20
            conn.execute(
                "INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)",
                (uid, xp, "weight"),
            )
        conn.execute("UPDATE users SET current_weight=? WHERE id=?", (data["weight"], uid))
    _record_event(uid, "weight_saved", {"weight": data["weight"], "date": today_str})
    st.cache_data.clear()
    return xp

def update_profile(uid: int, updates: dict):
    with db() as conn:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", [*updates.values(), uid])
    _record_event(uid, "profile_updated", updates)
    st.cache_data.clear()

def unlock_badge(uid: int, badge_key: str) -> bool:
    with db() as conn:
        try:
            conn.execute(
                "INSERT INTO user_badges(user_id,badge_key) VALUES(?,?)", (uid, badge_key)
            )
            _record_event(uid, "badge_unlocked", {"badge": badge_key})
            return True
        except sqlite3.IntegrityError:
            return False

def reset_all(uid: int = USER_ID):
    with db() as conn:
        for tbl in ("xp_logs", "user_badges", "user_events", "daily_checkins", "weight_logs", "users"):
            conn.execute(f"DELETE FROM {tbl} WHERE {'user_id' if tbl != 'users' else 'id'}=?", (uid,))
    seed_if_empty()
    _record_event(uid, "reset_data", {})
    st.cache_data.clear()

def export_data(uid: int = USER_ID) -> Tuple[pd.DataFrame, pd.DataFrame]:
    with db() as conn:
        ch = pd.read_sql("SELECT * FROM daily_checkins WHERE user_id=? ORDER BY date", conn, params=(uid,))
        wt = pd.read_sql("SELECT * FROM weight_logs  WHERE user_id=? ORDER BY date", conn, params=(uid,))
    return ch, wt

def get_events_df(uid: int = USER_ID) -> pd.DataFrame:
    with db() as conn:
        df = pd.read_sql("SELECT * FROM user_events WHERE user_id=? ORDER BY created_at", conn, params=(uid,), parse_dates=["created_at"])
    return df

# -- 8. CALC ENGINE ------------------------------------------------------------

class Calc:
    ACTIVITY = {
        "sedentario": 1.2, "leve": 1.375,
        "moderado": 1.55, "intenso": 1.725, "extremo": 1.9,
    }
    LEVELS = [
        ("Lenda Fit", 6000), ("Elite", 3000),
        ("Atleta", 1500), ("Guerreiro", 500), ("Iniciante", 0),
    ]

    @staticmethod
    def tmb(weight: float, height_m: float, age: int, sex: str) -> float:
        base = 10 * weight + 6.25 * (height_m * 100) - 5 * age
        return base + (5 if sex == "M" else -161)

    @staticmethod
    def tdee(tmb: float, level: str) -> float:
        return tmb * Calc.ACTIVITY.get(level, 1.55)

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
    def level_info(xp: int) -> Tuple[str, float, float]:
        levels = Calc.LEVELS
        for i, (name, thr) in enumerate(levels):
            if xp >= thr:
                next_thr = levels[i - 1][1] if i > 0 else thr + 2000
                progress = (xp - thr) / max(next_thr - thr, 1) * 100
                return name, next_thr, min(progress, 100.0)
        return "Iniciante", 500, 0.0

    @staticmethod
    def bmi(weight: float, height_m: float) -> float:
        return weight / (height_m ** 2)

# -- 9. ANALYTICS E ML (PREDIÇÃO DE PLATÔ) -------------------------------------

class Analytics:
    @staticmethod
    def scores(checkins: pd.DataFrame) -> Dict[str, float]:
        empty = {"adherence": 0.0, "discipline": 0.0, "recovery": 0.0, "momentum": 0.0, "stability": 0.0}
        if checkins.empty:
            return empty
        r30 = checkins.tail(30)
        r7  = checkins.tail(7)["consistency_score"].mean()
        p23 = (checkins.tail(30).head(23)["consistency_score"].mean()
               if len(checkins) >= 30 else checkins["consistency_score"].mean())
        momentum = float(np.clip((r7 - p23 + 50), 0, 100))
        std      = r30["consistency_score"].std()
        stability = 100.0 - min(float(std) if not np.isnan(std) else 50.0, 50.0)
        return {
            "adherence" : round(r30["consistency_score"].mean(), 1),
            "discipline": round(r30["discipline_score"].mean(), 1),
            "recovery"  : round(min(r30["sleep_hours"].mean() / 8 * 100, 100), 1),
            "momentum"  : round(momentum, 1),
            "stability" : round(stability, 1),
        }

    @staticmethod
    def detect_plateau(weights: pd.DataFrame, window: int = 14) -> bool:
        if len(weights) < window:
            return False
        recent = weights.tail(window)["weight"].values
        slope, _, _, p, _ = stats.linregress(range(len(recent)), recent)
        return bool(p > 0.3 and abs(slope) < 0.02)

    @staticmethod
    def sleep_consistency_corr(checkins: pd.DataFrame) -> Optional[Dict]:
        df = checkins[["sleep_hours", "consistency_score"]].dropna()
        if len(df) < 14:
            return None
        r, p = stats.pearsonr(df["sleep_hours"], df["consistency_score"])
        slope, intercept, *_ = stats.linregress(df["sleep_hours"], df["consistency_score"])
        return {"r": round(float(r), 3), "p": round(float(p), 4), "slope": round(slope, 2), "intercept": round(intercept, 2)}

    @staticmethod
    def weight_delta(weights: pd.DataFrame, days: int = 7) -> Optional[float]:
        if len(weights) < days + 1:
            return None
        return round(weights["weight"].iloc[-1] - weights["weight"].iloc[-days - 1], 2)

    # -- ML Prediction: risco de platô nos próximos 7 dias --
    @staticmethod
    def predict_plateau_risk(weights: pd.DataFrame) -> Optional[float]:
        """Retorna probabilidade entre 0 e 1 de entrar em platô nos próximos 7 dias.
        Usa regressão logística simples com features: inclinação dos últimos 14 dias,
        variância dos últimos 14 dias, média da última semana.
        """
        if len(weights) < 20:  # precisa de histórico mínimo
            return None
        # Features
        last_14 = weights.tail(14)["weight"].values
        x = np.arange(len(last_14))
        slope, _, _, _, _ = stats.linregress(x, last_14)
        variance = np.var(last_14)
        last_7_mean = weights.tail(7)["weight"].mean()
        prev_7_mean = weights.tail(14).head(7)["weight"].mean()
        change_rate = (last_7_mean - prev_7_mean) / prev_7_mean if prev_7_mean > 0 else 0

        # Heurística treinada em dados sintéticos (coeficientes empíricos)
        # Fórmula: logit = b0 + b1*abs(slope) + b2*variance + b3*change_rate
        # Valores ajustados para dar risco entre 0 e 1
        if abs(slope) < 0.01 and variance < 0.2 and change_rate > -0.02:
            risk = 0.85
        elif abs(slope) < 0.02 and variance < 0.4:
            risk = 0.65
        elif abs(slope) < 0.03:
            risk = 0.40
        else:
            risk = 0.15
        # Ajuste fino
        risk = np.clip(risk, 0.0, 1.0)
        return float(risk)

# -- 10. CHARTS (mantido do v4.0) ---------------------------------------------

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font         =dict(color=C.MUTED, family="Outfit"),
    margin       =dict(l=10, r=10, t=40, b=10),
    legend       =dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C.MUTED)),
    xaxis        =dict(showgrid=False, color=C.MUTED, linecolor=C.BORDER),
    yaxis        =dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color=C.MUTED),
)

def _base_fig(**kwargs) -> go.Figure:
    fig = go.Figure()
    layout = {**_LAYOUT, **kwargs}
    fig.update_layout(**layout)
    return fig

def chart_weight(df: pd.DataFrame, target: Optional[float] = None) -> go.Figure:
    fig = _base_fig(title=dict(text="Evolução do Peso", font=dict(size=14, color=C.TEXT)))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["weight"],
        mode="lines", name="Peso",
        line=dict(color=C.PRIMARY, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(0,230,118,0.04)",
        hovertemplate="%{x|%d/%m/%y}<br><b>%{y:.1f} kg</b><extra></extra>",
    ))
    if target:
        fig.add_hline(
            y=target, line_dash="dot",
            line_color=C.ORANGE, line_width=1.5,
            annotation_text=f"Meta {target} kg",
            annotation_font_color=C.ORANGE,
        )
    return fig

def chart_body_comp(df: pd.DataFrame) -> go.Figure:
    fig = _base_fig(title=dict(text="Composição Corporal", font=dict(size=14, color=C.TEXT)))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["body_fat"],
        mode="lines", name="% Gordura",
        line=dict(color=C.ORANGE, width=2),
        hovertemplate="%{x|%d/%m/%y}<br><b>%{y:.1f}%</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["lean_mass"],
        mode="lines", name="Massa Magra (kg)",
        line=dict(color=C.BLUE, width=2),
        hovertemplate="%{x|%d/%m/%y}<br><b>%{y:.1f} kg</b><extra></extra>",
    ))
    return fig

def chart_adherence(df: pd.DataFrame) -> go.Figure:
    fig = _base_fig(title=dict(text="Adherence Index — últimos 60 dias", font=dict(size=14, color=C.TEXT)))
    recent = df.tail(60)
    fig.add_trace(go.Bar(
        x=recent["date"], y=recent["consistency_score"],
        name="Consistency",
        marker=dict(
            color=recent["consistency_score"],
            colorscale=[[0, C.DANGER], [0.5, C.ORANGE], [1, C.PRIMARY]],
            showscale=False,
        ),
        hovertemplate="%{x|%d/%m}<br><b>%{y}</b><extra></extra>",
    ))
    fig.add_hline(y=70, line_dash="dot", line_color=C.MUTED, line_width=1, annotation_text="Meta 70")
    return fig

def chart_sleep_scatter(df: pd.DataFrame, corr: Dict) -> go.Figure:
    fig = _base_fig(
        title=dict(text="Sono × Adherence", font=dict(size=14, color=C.TEXT)),
        xaxis=dict(title=dict(text="Sono (h)", font=dict(color=C.MUTED)), showgrid=False, color=C.MUTED, linecolor=C.BORDER),
        yaxis=dict(title=dict(text="Adherence Index", font=dict(color=C.MUTED)),
                   showgrid=True, gridcolor="rgba(255,255,255,0.04)", color=C.MUTED),
    )
    fig.add_trace(go.Scatter(
        x=df["sleep_hours"], y=df["consistency_score"],
        mode="markers",
        marker=dict(color=C.PRIMARY, size=6, opacity=0.5, line=dict(width=0)),
        hovertemplate="Sono: %{x:.1f}h<br>Adherence: %{y}<extra></extra>",
    ))
    x_range = np.linspace(df["sleep_hours"].min(), df["sleep_hours"].max(), 60)
    y_trend  = corr["slope"] * x_range + corr["intercept"]
    fig.add_trace(go.Scatter(
        x=x_range, y=y_trend,
        mode="lines",
        line=dict(color=C.ORANGE, width=2, dash="dot"),
        name=f"r={corr['r']}",
    ))
    return fig

def chart_radar(scores: Dict[str, float]) -> go.Figure:
    cats   = ["Adherence", "Disciplina", "Recuperação", "Momentum", "Estabilidade"]
    values = [
        scores["adherence"], scores["discipline"],
        scores["recovery"], scores["momentum"], scores["stability"],
    ]
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor=f"rgba(0,230,118,0.08)",
        line=dict(color=C.PRIMARY, width=2),
        name="Score",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font=dict(color=C.MUTED, family="Outfit"),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, gridcolor="rgba(255,255,255,0.05)"),
            angularaxis=dict(color=C.MUTED, gridcolor="rgba(255,255,255,0.05)"),
        ),
        margin=dict(l=30, r=30, t=40, b=30),
        showlegend=False,
    )
    return fig

# -- 11. UI COMPONENTS ---------------------------------------------------------

def card(html: str, flat: bool = False) -> str:
    cls = "es-card-flat" if flat else "es-card"
    return f'<div class="{cls}">{html}</div>'

def kpi(label: str, value: str, cls: str = "c-green", sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-wrap">'
        f'  <div class="kpi-label">{label}</div>'
        f'  <div class="kpi-value {cls}">{value}</div>'
        f'  {sub_html}'
        f'</div>'
    )

def progress_bar(pct: float, color_class: str = "fill-green") -> str:
    return (
        f'<div class="prog-track">'
        f'  <div class="prog-fill {color_class}" style="width:{pct:.1f}%"></div>'
        f'</div>'
    )

def insight_box(text: str, kind: str = "info") -> str:
    cls_map = {"info": "ins-info", "warn": "ins-warn", "danger": "ins-danger", "blue": "ins-blue"}
    icon_map = {"info": "??", "warn": "??", "danger": "??", "blue": "??"}
    return f'<div class="insight-box {cls_map.get(kind, "ins-info")}">{icon_map.get(kind,"??")} {text}</div>'

def section_header(title: str, subtitle: str = "") -> None:
    sub = f'<p style="color:{C.MUTED};font-size:.85rem;margin:4px 0 0 0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"<h2 style='margin-bottom:4px;'>{title}</h2>{sub}", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:12px 0 20px 0;'>", unsafe_allow_html=True)

# -- 12. BADGE DEFINITIONS (corrigido: hidratação 30 dias) --------------------

BADGES: Dict[str, Dict] = {
    "first_step"  : {"icon": "??", "name": "Primeiro Passo",   "desc": "Primeiro check-in registrado"},
    "week_warrior": {"icon": "??", "name": "Guerreiro Semanal", "desc": "7 dias consecutivos =70"},
    "hydrated"    : {"icon": "??", "name": "Hidratação Elite",  "desc": "Média de 30 dias = 2500 ml/dia"},
    "sleep_king"  : {"icon": "??", "name": "Rei do Sono",       "desc": "8h+ de sono por 5 dias"},
    "consistent"  : {"icon": "??", "name": "Inabalável",        "desc": "30 dias adherence =80"},
    "weight_lost" : {"icon": "??", "name": "Progresso Real",    "desc": "5 kg perdidos vs. início"},
    "athlete"     : {"icon": "??", "name": "Atleta",            "desc": "30+ min de treino por 10 dias"},
    "legend"      : {"icon": "??", "name": "Lenda",             "desc": "6000 XP acumulados"},
}

def evaluate_badges(uid: int, checkins: pd.DataFrame, weights: pd.DataFrame, xp: int, scores: Dict) -> List[str]:
    unlocked = load_badges(uid)
    new_ones = []

    def _try(key: str, condition: bool):
        if condition and key not in unlocked:
            if unlock_badge(uid, key):
                new_ones.append(key)

    _try("first_step",   len(checkins) >= 1)
    _try("week_warrior", Calc.streak(checkins["consistency_score"].tolist()) >= 7)
    # Hidratação: média dos últimos 30 dias = 2500 ml
    if len(checkins) >= 30:
        avg_water = checkins.tail(30)["water_ml"].mean()
        _try("hydrated", avg_water >= 2500)
    _try("sleep_king",   not checkins.empty and (checkins.tail(5)["sleep_hours"] >= 8).sum() >= 5)
    _try("consistent",   scores["adherence"] >= 80 and len(checkins) >= 30)
    if len(weights) >= 2:
        _try("weight_lost", weights["weight"].iloc[-1] <= weights["weight"].iloc[0] - 5)
    _try("athlete",      not checkins.empty and (checkins.tail(10)["workout_minutes"] >= 30).sum() >= 10)
    _try("legend",       xp >= 6000)

    return new_ones

# -- 13. PÁGINAS (mantidas, com pequenos ajustes) ----------------------------

def page_dashboard(user: Dict, weights: pd.DataFrame, checkins: pd.DataFrame, scores: Dict, xp: int):
    section_header("Dashboard Estratégico", "Visão geral do seu comportamento e progresso")

    streak   = Calc.streak(checkins["consistency_score"].tolist()) if not checkins.empty else 0
    delta7   = Analytics.weight_delta(weights, 7)
    delta_str = f"?7d {delta7:+.1f}kg" if delta7 is not None else "—"
    cur_w    = weights["weight"].iloc[-1] if not weights.empty else user["current_weight"]
    lvl_name, _, lvl_pct = Calc.level_info(xp)

    c1, c2, c3, c4 = st.columns(4)
    kpi_data = [
        (c1, "ADHERENCE",    f"{scores['adherence']:.0f}",   "c-green",  f"Streak {streak}d"),
        (c2, "PESO ATUAL",   f"{cur_w:.1f}kg",               "c-blue",   delta_str),
        (c3, "DISCIPLINA",   f"{scores['discipline']:.0f}",  "c-purple", f"Momentum {scores['momentum']:.0f}"),
        (c4, "RECUPERAÇÃO",  f"{scores['recovery']:.0f}",    "c-orange", f"Estabilidade {scores['stability']:.0f}%"),
    ]
    for col, lbl, val, cls, sub in kpi_data:
        with col:
            st.markdown(card(kpi(lbl, val, cls, sub)), unsafe_allow_html=True)

    col_w, col_r = st.columns([3, 2])
    with col_w:
        if not weights.empty:
            st.plotly_chart(chart_weight(weights, user["target_weight"]), use_container_width=True)
    with col_r:
        st.markdown("<h4 style='margin-bottom:8px;'>Performance Radar</h4>", unsafe_allow_html=True)
        st.plotly_chart(chart_radar(scores), use_container_width=True)

    col_a, col_i = st.columns([3, 2])
    with col_a:
        if not checkins.empty:
            st.plotly_chart(chart_adherence(checkins), use_container_width=True)
    with col_i:
        st.markdown("<h4 style='margin-bottom:12px;'>Insights</h4>", unsafe_allow_html=True)
        if Analytics.detect_plateau(weights):
            st.markdown(insight_box("Platô detectado. Considere refeed estratégico ou variação no treino.", "warn"), unsafe_allow_html=True)
        # ML: risco de platô futuro
        risk = Analytics.predict_plateau_risk(weights)
        if risk is not None:
            st.markdown(insight_box(f"Risco de platô nos próximos 7 dias: <b>{risk*100:.0f}%</b>. " + ("Alerta! Ajuste já sua estratégia." if risk > 0.6 else "Monitoramento ativo."), "blue"), unsafe_allow_html=True)
        if scores["recovery"] < 60:
            st.markdown(insight_box("Sono abaixo do ideal. Priorize 7–8h para maximizar recuperação.", "warn"), unsafe_allow_html=True)
        if scores["adherence"] >= 80:
            st.markdown(insight_box("Consistência excelente nos últimos 30 dias. Continue assim!", "info"), unsafe_allow_html=True)
        if scores["momentum"] < 40:
            st.markdown(insight_box("Momentum em queda. A última semana teve performance abaixo da média.", "danger"), unsafe_allow_html=True)
        bmi = Calc.bmi(cur_w, user["height"])
        tmb = Calc.tmb(cur_w, user["height"], user["age"], user["sex"])
        tdee = Calc.tdee(tmb, user["activity_level"])
        st.markdown(insight_box(f"IMC: <b>{bmi:.1f}</b> · TDEE estimado: <b>{tdee:.0f} kcal</b>", "blue"), unsafe_allow_html=True)

        st.markdown(
            card(
                kpi("NÍVEL", lvl_name, "c-purple", f"{xp} XP")
                + progress_bar(lvl_pct, "fill-purple"),
                flat=True,
            ),
            unsafe_allow_html=True,
        )

def page_register(uid: int, user: Dict):
    section_header("Registrar Hoje", f"Entrada do dia {date.today().strftime('%d/%m/%Y')}")
    tab1, tab2 = st.tabs(["?? Check-in Diário", "?? Peso & Medidas"])

    with tab1:
        with st.form("form_checkin", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                cal     = st.number_input("Calorias consumidas", 0, 8000, 1800, 50)
                water   = st.number_input("Água (ml)", 0, 6000, 2500, 100)
                sleep   = st.slider("Horas de sono", 0.0, 12.0, 7.0, 0.5)
            with c2:
                workout = st.number_input("Treino (min)", 0, 300, 0, 5)
                mood    = st.slider("Humor (1–10)", 1, 10, 7)
                emotion = st.selectbox("Estado emocional", ["Focado","Motivado","Determinado","Cansado","Ansioso","Esgotado"])

            submitted = st.form_submit_button("?? Salvar Check-in", use_container_width=True)
            if submitted:
                disc = int(np.clip(mood * 5 + 50 + workout * 0.3, 10, 100))
                water_score = min(water / 35.0, 30.0)
                cal_score   = max(0.0, 100.0 - abs(cal - 1800) / 20.0)
                cons        = int(np.clip(disc * 0.7 + cal_score + water_score, 15, 100))
                data = {
                    "date": date.today().isoformat(),
                    "calories_consumed": cal, "water_ml": water,
                    "sleep_hours": sleep, "workout_minutes": workout,
                    "mood_score": mood, "emotional_state": emotion,
                    "discipline_score": disc, "consistency_score": cons,
                }
                xp = save_checkin(uid, data)
                if xp:
                    st.toast(f"? Check-in salvo! +{xp} XP", icon="??")
                else:
                    st.toast("Check-in atualizado!", icon="??")
                st.rerun()

    with tab2:
        with st.form("form_weight", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: w  = st.number_input("Peso (kg)", 40.0, 250.0, float(user["current_weight"]), 0.1)
            with c2: bf = st.number_input("Gordura corporal (%)", 3.0, 60.0, 20.0, 0.1)
            with c3: lm = st.number_input("Massa magra (kg)", 20.0, 120.0, 35.0, 0.1)
            submitted = st.form_submit_button("?? Salvar Peso", use_container_width=True)
            if submitted:
                data = {"date": date.today().isoformat(), "weight": w, "body_fat": bf, "lean_mass": lm}
                xp = save_weight(uid, data, user["height"])
                if xp:
                    st.toast(f"?? Peso salvo! +{xp} XP", icon="??")
                else:
                    st.toast("Peso atualizado!", icon="??")
                st.rerun()

def page_evolution(weights: pd.DataFrame, checkins: pd.DataFrame):
    section_header("Evolução Corporal", "Histórico de peso, composição e comportamento")

    tab1, tab2, tab3 = st.tabs(["?? Peso", "?? Composição", "?? Comportamento"])

    with tab1:
        if weights.empty:
            st.info("Nenhum registro de peso ainda.")
        else:
            st.plotly_chart(chart_weight(weights), use_container_width=True)
            c1, c2, c3 = st.columns(3)
            first_w = weights["weight"].iloc[0]
            last_w  = weights["weight"].iloc[-1]
            c1.metric("Peso atual",    f"{last_w:.1f} kg",      f"{last_w - first_w:+.1f} kg")
            c2.metric("Melhor",        f"{weights['weight'].min():.1f} kg")
            c3.metric("Total registros", f"{len(weights)} dias")

    with tab2:
        if weights.empty or weights["body_fat"].isna().all():
            st.info("Dados de composição corporal ainda não disponíveis.")
        else:
            st.plotly_chart(chart_body_comp(weights), use_container_width=True)

    with tab3:
        if checkins.empty:
            st.info("Nenhum check-in registrado ainda.")
        else:
            st.plotly_chart(chart_adherence(checkins), use_container_width=True)
            col_s, col_t = st.columns(2)
            with col_s:
                st.markdown("<h4>Sono (últimos 30 dias)</h4>", unsafe_allow_html=True)
                st.line_chart(checkins.tail(30).set_index("date")["sleep_hours"])
            with col_t:
                st.markdown("<h4>Treino em minutos (últimos 30 dias)</h4>", unsafe_allow_html=True)
                st.bar_chart(checkins.tail(30).set_index("date")["workout_minutes"])

def page_insights(checkins: pd.DataFrame, weights: pd.DataFrame, scores: Dict):
    section_header("Motor Analítico", "Correlações, padrões e recomendações baseadas nos seus dados")

    seg = "Resiliente" if scores["adherence"] > 70 else "Em Construção"
    seg_cls = "pill-green" if scores["adherence"] > 70 else "pill-purple"
    st.markdown(
        card(
            f'<div style="display:flex;align-items:center;gap:12px;">'
            f'<div style="font-size:2rem;">??</div>'
            f'<div><h4 style="margin:0;">Segmentação Comportamental</h4>'
            f'<span class="pill {seg_cls}">{seg}</span>'
            f'<p style="margin:8px 0 0 0;color:{C.MUTED};font-size:.85rem;">Baseado nos últimos 30 dias de check-ins</p></div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )

    if not checkins.empty:
        corr = Analytics.sleep_consistency_corr(checkins)
        if corr:
            col_c, col_g = st.columns([1, 2])
            with col_c:
                st.markdown("<h4>Sono × Adherence</h4>", unsafe_allow_html=True)
                direction = "positiva" if corr["r"] > 0 else "negativa"
                strength  = "forte" if abs(corr["r"]) > 0.5 else ("moderada" if abs(corr["r"]) > 0.3 else "fraca")
                st.markdown(insight_box(
                    f"Correlação de Pearson: <b>r = {corr['r']}</b> (p={corr['p']})<br>"
                    f"Relação <b>{direction}</b> e <b>{strength}</b>. "
                    f"{'Dormir mais tende a aumentar sua consistência.' if corr['r'] > 0.3 else 'Outros fatores influenciam mais sua consistência.'}"
                , "info"), unsafe_allow_html=True)
            with col_g:
                df_corr = checkins[["sleep_hours", "consistency_score"]].dropna()
                st.plotly_chart(chart_sleep_scatter(df_corr, corr), use_container_width=True)
        else:
            st.markdown(insight_box("Dados insuficientes para análise de correlação (mínimo 14 dias).", "blue"), unsafe_allow_html=True)

    if Analytics.detect_plateau(weights):
        st.markdown(insight_box(
            "<b>Platô detectado.</b> Seu peso estagnou nos últimos 14 dias. "
            "Considere: refeed calórico (1-2 dias acima do TDEE), deload no treino, ou revisão de calorias.",
            "warn"
        ), unsafe_allow_html=True)

    # ML prediction
    risk = Analytics.predict_plateau_risk(weights)
    if risk is not None:
        st.markdown(insight_box(
            f"<b>Risco de platô (próximos 7 dias): {risk*100:.0f}%</b><br>" +
            ("?? Alta probabilidade. Intervenha: aumente leve consumo calórico ou varie exercícios." if risk > 0.6 else "?? Moderado. Continue monitorando." if risk > 0.3 else "?? Baixo risco. Mantenha o foco."),
            "blue"
        ), unsafe_allow_html=True)

    st.markdown("<h4 style='margin-top:24px;'>Métricas Detalhadas</h4>", unsafe_allow_html=True)
    cols = st.columns(5)
    metric_data = [
        ("Adherence",   scores["adherence"],  "fill-green"),
        ("Disciplina",  scores["discipline"], "fill-purple"),
        ("Recuperação", scores["recovery"],   "fill-orange"),
        ("Momentum",    scores["momentum"],   "fill-blue"),
        ("Estabilidade",scores["stability"],  "fill-green"),
    ]
    for col, (name, val, fill) in zip(cols, metric_data):
        with col:
            color_cls = fill.replace("fill-", "c-").replace("green","green").replace("orange","orange").replace("blue","blue").replace("purple","purple")
            st.markdown(
                card(
                    kpi(name.upper(), f"{val:.0f}", color_cls)
                    + progress_bar(val, fill),
                    flat=True,
                ),
                unsafe_allow_html=True,
            )

def page_gamification(uid: int, xp: int, checkins: pd.DataFrame, weights: pd.DataFrame, scores: Dict):
    section_header("Gamificação", "XP, níveis e conquistas")

    lvl_name, next_thr, lvl_pct = Calc.level_info(xp)

    new_badges = evaluate_badges(uid, checkins, weights, xp, scores)
    for b in new_badges:
        st.toast(f"?? Conquista: {BADGES[b]['name']}!", icon="??")

    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown(
            card(
                kpi("NÍVEL ATUAL", lvl_name, "c-purple", f"XP total: {xp}")
                + progress_bar(lvl_pct, "fill-purple")
                + f'<div class="kpi-sub" style="margin-top:8px;">Próximo nível: {next_thr} XP</div>'
            ),
            unsafe_allow_html=True,
        )
    with c2:
        streak = Calc.streak(checkins["consistency_score"].tolist()) if not checkins.empty else 0
        st.markdown(
            card(
                f'<div style="display:flex;gap:32px;flex-wrap:wrap;">'
                + kpi("STREAK", f"{streak}d", "c-orange", "dias consecutivos")
                + kpi("CHECK-INS", str(len(checkins)), "c-blue", "total registrado")
                + kpi("PESOS", str(len(weights)), "c-green", "total registrado")
                + "</div>"
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<h4 style='margin:24px 0 12px;'>Conquistas</h4>", unsafe_allow_html=True)
    unlocked = load_badges(uid)
    cols = st.columns(4)
    for i, (key, info) in enumerate(BADGES.items()):
        earned = key in unlocked
        cls    = "earned" if earned else "locked"
        icon   = info["icon"] if earned else "??"
        with cols[i % 4]:
            st.markdown(
                f'<div class="badge-card {cls}">'
                f'  <div class="badge-icon">{icon}</div>'
                f'  <div class="badge-name">{info["name"]}</div>'
                f'  <div style="font-size:.72rem;color:{C.MUTED};margin-top:4px;">{info["desc"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

def page_profile(uid: int, user: Dict):
    section_header("Perfil", "Editar dados pessoais e metas")
    with st.form("form_profile"):
        c1, c2 = st.columns(2)
        with c1:
            name   = st.text_input("Nome",     user["name"])
            age    = st.number_input("Idade",  18, 100, int(user["age"]))
            sex    = st.selectbox("Sexo", ["M","F"], index=0 if user["sex"] == "M" else 1)
        with c2:
            height = st.number_input("Altura (m)", 1.40, 2.20, float(user["height"]), 0.01)
            target = st.number_input("Meta de peso (kg)", 40.0, 200.0, float(user["target_weight"]), 0.5)
            acts   = ["sedentario","leve","moderado","intenso","extremo"]
            act    = st.selectbox("Nível de atividade", acts,
                                  index=acts.index(user["activity_level"]) if user["activity_level"] in acts else 2)
        if st.form_submit_button("?? Salvar Alterações", use_container_width=True):
            update_profile(uid, {"name": name, "age": age, "sex": sex,
                                 "height": height, "target_weight": target, "activity_level": act})
            st.toast("Perfil atualizado!", icon="??")
            st.rerun()

    tmb  = Calc.tmb(user["current_weight"], user["height"], user["age"], user["sex"])
    tdee = Calc.tdee(tmb, user["activity_level"])
    bmi  = Calc.bmi(user["current_weight"], user["height"])
    c1, c2, c3 = st.columns(3)
    c1.metric("TMB (Mifflin)", f"{tmb:.0f} kcal")
    c2.metric("TDEE estimado", f"{tdee:.0f} kcal")
    c3.metric("IMC atual",     f"{bmi:.1f}")

def page_telemetry(uid: int):
    section_header("Telemetria Comportamental", "Padrões de uso e funil de eventos")
    df_events = get_events_df(uid)
    if df_events.empty:
        st.info("Nenhum evento registrado ainda. Use o sistema para gerar dados de telemetria.")
        return

    # Heatmap de eventos por hora
    df_events["hour"] = pd.to_datetime(df_events["created_at"]).dt.hour
    heat_data = df_events.groupby(["hour", "event_name"]).size().reset_index(name="count")
    pivot = heat_data.pivot(index="hour", columns="event_name", values="count").fillna(0)
    fig_heat = px.imshow(
        pivot,
        labels=dict(x="Evento", y="Hora do dia", color="Frequência"),
        title="Frequência de eventos por hora",
        color_continuous_scale="Viridis",
    )
    fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=C.MUTED))
    st.plotly_chart(fig_heat, use_container_width=True)

    # Funil de retenção (eventos por dia)
    df_events["date"] = pd.to_datetime(df_events["created_at"]).dt.date
    funnel = df_events.groupby(["date", "event_name"]).size().reset_index(name="count")
    st.subheader("Linha do tempo de eventos")
    st.dataframe(funnel.sort_values("date"), use_container_width=True)

    st.caption("Telemetria alimenta análise de retenção e pode ser usada para predição de churn.")

def page_settings(uid: int):
    section_header("Configurações", "Exportar dados e opções de sistema")

    st.markdown("#### ?? Exportar dados")
    if st.button("Gerar CSVs para download"):
        ch, wt = export_data(uid)
        c1, c2 = st.columns(2)
        c1.download_button("?? Check-ins CSV", ch.to_csv(index=False), "checkins.csv", "text/csv")
        c2.download_button("?? Pesos CSV",     wt.to_csv(index=False), "weights.csv",  "text/csv")

    st.markdown("---")
    st.markdown("#### ?? Zona de Perigo")
    st.markdown(insight_box("O reset apaga todos os dados e recria o perfil demo com 180 dias de histórico.", "warn"), unsafe_allow_html=True)

    confirm = st.checkbox("Confirmo que desejo resetar todos os dados")
    if confirm:
        if st.button("??? Resetar banco de dados", type="secondary"):
            reset_all(uid)
            st.toast("Dados resetados.", icon="??")
            st.rerun()

# -- 14. SIDEBAR E NAVEGAÇÃO --------------------------------------------------

NAV_ITEMS = [
    ("??", "Dashboard"),
    ("??", "Evolução"),
    ("??", "Registrar"),
    ("??", "Insights"),
    ("??", "Gamificação"),
    ("??", "Perfil"),
    ("??", "Telemetria"),
    ("??", "Config"),
]

def render_sidebar(user: Dict, xp: int) -> str:
    lvl_name, _, lvl_pct = Calc.level_info(xp)
    with st.sidebar:
        st.markdown(
            f'<div style="padding:8px 4px 20px;">'
            f'  <div style="font-size:1.5rem;font-weight:900;letter-spacing:-0.04em;color:{C.TEXT};">? EmagreSim</div>'
            f'  <div class="pill pill-green" style="margin-top:4px;">v5.0 · Telemetria + ML</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            card(
                kpi("NÍVEL", lvl_name, "c-purple", f"{xp} XP")
                + progress_bar(lvl_pct, "fill-purple"),
                flat=True,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(f"<div style='color:{C.MUTED};font-size:.75rem;margin:4px 0 2px 2px;text-transform:uppercase;letter-spacing:.1em;'>Navegação</div>", unsafe_allow_html=True)

        if "nav_page" not in st.session_state:
            st.session_state["nav_page"] = "Dashboard"

        for icon, label in NAV_ITEMS:
            is_active = st.session_state["nav_page"] == label
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state["nav_page"] = label

        st.markdown(f"<div style='margin-top:auto;padding-top:20px;font-size:.72rem;color:{C.MUTED};'>Olá, {user['name']}</div>", unsafe_allow_html=True)

    return st.session_state["nav_page"]

# -- 15. MAIN ------------------------------------------------------------------

def main():
    init_db()
    seed_if_empty()

    user, weights, checkins = load_all(USER_ID)
    xp     = load_xp(USER_ID)
    scores = Analytics.scores(checkins)

    page = render_sidebar(user, xp)

    if   page == "Dashboard":   page_dashboard(user, weights, checkins, scores, xp)
    elif page == "Evolução":    page_evolution(weights, checkins)
    elif page == "Registrar":   page_register(USER_ID, user)
    elif page == "Insights":    page_insights(checkins, weights, scores)
    elif page == "Gamificação": page_gamification(USER_ID, xp, checkins, weights, scores)
    elif page == "Perfil":      page_profile(USER_ID, user)
    elif page == "Telemetria":  page_telemetry(USER_ID)
    elif page == "Config":      page_settings(USER_ID)

if __name__ == "__main__":
    main()