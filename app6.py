# -*- coding: utf-8 -*-
"""
EmagreSim v9.0 - Modo Claro/Escuro | Português | Animado
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
from typing import List, Dict, Optional, Tuple
from scipy import stats

# -----------------------------------------------------------------------------
# 1. CONFIGURACOES
# -----------------------------------------------------------------------------
IS_DEV = os.environ.get("EMAGRESIM_ENV", "dev") == "dev"
DB_PATH = "emagresim_v9.db"
USER_ID = 1

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("emagresim")

st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. TEMAS (Claro / Escuro)
# -----------------------------------------------------------------------------
if "tema" not in st.session_state:
    st.session_state.tema = "escuro"

@dataclass
class TemaEscuro:
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
    BORDER: str = "rgba(255,255,255,0.06)"

@dataclass
class TemaClaro:
    BG: str = "#F5F5F0"
    SURFACE: str = "#FFFFFF"
    CARD: str = "#FFFFFF"
    PRIMARY: str = "#FF4D00"
    PRIMARY_DARK: str = "#E63E00"
    PRIMARY_LIGHT: str = "#FF8A4D"
    TEXT: str = "#1A1A1A"
    TEXT_MUTED: str = "#666666"
    TEXT_DIM: str = "#999999"
    SUCCESS: str = "#22C55E"
    WARNING: str = "#FBBF24"
    BORDER: str = "rgba(0,0,0,0.08)"

def get_tema():
    return TemaClaro() if st.session_state.tema == "claro" else TemaEscuro()

# -----------------------------------------------------------------------------
# 3. CSS DINÂMICO (muda com o tema)
# -----------------------------------------------------------------------------
def aplicar_css():
    C = get_tema()
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700;800&display=swap');
    
    .stApp, .stApp > header {{
        background: {C.BG} !important;
        transition: background 0.3s ease;
    }}
    
    section[data-testid="stSidebar"] {{
        background: {C.SURFACE} !important;
        border-right: 1px solid {C.BORDER} !important;
        transition: background 0.3s ease;
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
    
    /* Animações */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); opacity: 0.7; }}
        50% {{ transform: scale(1.05); opacity: 1; }}
        100% {{ transform: scale(1); opacity: 0.7; }}
    }}
    
    .es-card, .kpi-card, .chart-panel, .metrics-panel {{
        animation: fadeInUp 0.4s ease-out;
        transition: all 0.3s ease;
    }}
    
    .es-card:hover, .kpi-card:hover {{
        transform: translateY(-4px);
    }}
    
    .kpi-card {{
        background: {C.CARD};
        border-radius: 20px;
        padding: 20px;
        border: 1px solid {C.BORDER};
        transition: all 0.3s ease;
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
        color: {C.TEXT};
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
    
    .chart-panel, .metrics-panel {{
        background: {C.CARD};
        border-radius: 20px;
        padding: 20px;
        border: 1px solid {C.BORDER};
    }}
    
    .metric-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid {C.BORDER};
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
        background: rgba(0,0,0,0.1);
        border-radius: 3px;
        overflow: hidden;
    }}
    
    .metric-bar-fill {{
        height: 100%;
        border-radius: 3px;
        background: {C.PRIMARY};
        transition: width 0.5s ease;
    }}
    
    .metric-value {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {C.TEXT};
        min-width: 40px;
        text-align: right;
    }}
    
    .prog-track {{
        background: rgba(0,0,0,0.1);
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
    
    .botao-toggle {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: {C.SURFACE};
        border: 1px solid {C.BORDER};
        border-radius: 40px;
        padding: 8px 16px;
        margin: 16px 0;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .botao-toggle:hover {{
        border-color: {C.PRIMARY};
    }}
    
    /* Esconder elementos padrão */
    #MainMenu, header, footer, .stDeployButton {{
        display: none !important;
    }}
    
    @media (max-width: 768px) {{
        .kpi-card {{ padding: 12px; }}
        .kpi-value {{ font-size: 1.5rem; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. SPLASH
# -----------------------------------------------------------------------------
if "splash_shown" not in st.session_state:
    with st.container():
        st.markdown(f"""
        <div style="height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <div style="font-size:5rem; animation: pulse 1.5s infinite;">🔥</div>
            <h1 style="font-size:2.5rem; margin-top:1rem;">Emagre<span style="color:#FF4D00;">Sim</span></h1>
            <p style="color:{get_tema().TEXT_MUTED};">Sistema de Transformação Comportamental</p>
        </div>
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
    conn.execute("INSERT INTO users VALUES (1,'Usuário Demo',30,'M',1.78,88.0,72.0,'moderado',CURRENT_TIMESTAMP)")
    end_date = date.today() - timedelta(days=1)
    dates = [end_date - timedelta(days=x) for x in range(180)][::-1]
    rng = np.random.default_rng(42)
    for i, d in enumerate(dates):
        w = max(88.0 - 0.025 * i + rng.normal(0, 0.3), 55.0)
        bf = max(22 - 0.04 * i, 8)
        lm = 35 + 0.008 * i
        conn.execute("INSERT INTO weight_logs(user_id,date,weight,body_fat,lean_mass) VALUES(1,?,?,?,?)",
                     (d.isoformat(), round(w, 1), round(bf, 1), round(lm, 1)))
        cons = int(np.clip(70 - 0.1 * i + rng.normal(0, 8), 40, 98))
        disc = int(np.clip(cons + rng.integers(-5, 6), 40, 98))
        conn.execute("INSERT INTO daily_checkins(user_id,date,calories_consumed,water_ml,sleep_hours,workout_minutes,mood_score,consistency_score,emotional_state,discipline_score) VALUES(1,?,1800,2500,7.2,45,6,?,?,?)",
                     (d.isoformat(), cons, "Motivado", disc))
    conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(1,500,'seed')")

# -----------------------------------------------------------------------------
# 6. ENGINES
# -----------------------------------------------------------------------------
class AnaliseEngine:
    @staticmethod
    def calcular_metricas(checkins: pd.DataFrame) -> Dict[str, float]:
        vazio = {"consistencia": 0.0, "disciplina": 0.0, "recuperacao": 0.0, "momento": 0.0, "estabilidade": 0.0}
        if checkins.empty or len(checkins) < 7:
            return vazio
        ult30 = checkins.tail(30) if len(checkins) >= 30 else checkins
        momento = float(np.clip((checkins.tail(7)["consistency_score"].mean() - ult30["consistency_score"].mean() + 50), 0, 100))
        return {
            "consistencia": round(ult30["consistency_score"].mean(), 1),
            "disciplina": round(ult30["discipline_score"].mean(), 1),
            "recuperacao": round(min(ult30["sleep_hours"].mean() / 8 * 100, 100), 1),
            "momento": round(momento, 1),
            "estabilidade": round(100 - min(ult30["consistency_score"].std(), 50), 1),
        }
    
    @staticmethod
    def sequencia(notas: List[float], limite: int = 70) -> int:
        s = 0
        for n in reversed(notas):
            if n >= limite: s += 1
            else: break
        return s
    
    @staticmethod
    def ultimos_14_dias(checkins: pd.DataFrame) -> List[int]:
        if checkins.empty:
            return []
        return checkins.tail(14)["consistency_score"].tolist()

class NivelEngine:
    NIVEL = [("Iniciante", 0), ("Guerreiro", 500), ("Atleta", 1500), ("Elite", 3000), ("Lenda", 6000)]
    
    @classmethod
    def info(cls, xp: int) -> Tuple[str, float, float]:
        for i, (nome, limiar) in enumerate(cls.NIVEL):
            if xp >= limiar:
                prox = cls.NIVEL[i+1][1] if i+1 < len(cls.NIVEL) else limiar + 2000
                return nome, prox, min((xp - limiar) / max(prox - limiar, 1) * 100, 100)
        return "Iniciante", 500, 0

# -----------------------------------------------------------------------------
# 7. REPOSITORY
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def carregar_usuario(uid: int = USER_ID) -> Optional[Dict]:
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None

@st.cache_data(ttl=300, show_spinner=False)
def carregar_pesos(uid: int = USER_ID) -> pd.DataFrame:
    with db() as conn:
        return pd.read_sql("SELECT * FROM weight_logs WHERE user_id=? ORDER BY date", conn, params=(uid,), parse_dates=["date"])

@st.cache_data(ttl=300, show_spinner=False)
def carregar_checkins(uid: int = USER_ID) -> pd.DataFrame:
    with db() as conn:
        return pd.read_sql("SELECT * FROM daily_checkins WHERE user_id=? ORDER BY date", conn, params=(uid,), parse_dates=["date"])

@st.cache_data(ttl=300, show_spinner=False)
def carregar_xp(uid: int = USER_ID) -> int:
    with db() as conn:
        row = conn.execute("SELECT COALESCE(SUM(amount),0) FROM xp_logs WHERE user_id=?", (uid,)).fetchone()
        return row[0] if row else 0

def limpar_cache():
    carregar_usuario.clear()
    carregar_pesos.clear()
    carregar_checkins.clear()
    carregar_xp.clear()

def salvar_checkin(uid: int, dados: dict) -> int:
    with db() as conn:
        existe = conn.execute("SELECT id FROM daily_checkins WHERE user_id=? AND date=?", (uid, dados["date"])).fetchone()
        if existe:
            set_clause = ", ".join(f"{k}=?" for k in dados)
            conn.execute(f"UPDATE daily_checkins SET {set_clause} WHERE user_id=? AND date=?", list(dados.values()) + [uid, dados["date"]])
            return 0
        else:
            cols = ", ".join(dados.keys())
            placeholders = ", ".join(["?"] * len(dados))
            conn.execute(f"INSERT INTO daily_checkins(user_id,{cols}) VALUES(?,{placeholders})", [uid] + list(dados.values()))
            xp = 10
            if dados.get("consistency_score", 0) >= 80: xp += 20
            if dados.get("sleep_hours", 0) >= 8: xp += 40
            if dados.get("workout_minutes", 0) >= 30: xp += 15
            conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)", (uid, xp, "checkin"))
            limpar_cache()
            return xp

def salvar_peso(uid: int, dados: dict) -> int:
    with db() as conn:
        existe = conn.execute("SELECT id FROM weight_logs WHERE user_id=? AND date=?", (uid, dados["date"])).fetchone()
        if existe:
            set_clause = ", ".join(f"{k}=?" for k in dados)
            conn.execute(f"UPDATE weight_logs SET {set_clause} WHERE user_id=? AND date=?", list(dados.values()) + [uid, dados["date"]])
            return 0
        else:
            cols = ", ".join(dados.keys())
            placeholders = ", ".join(["?"] * len(dados))
            conn.execute(f"INSERT INTO weight_logs(user_id,{cols}) VALUES(?,{placeholders})", [uid] + list(dados.values()))
            xp = 20
            conn.execute("INSERT INTO xp_logs(user_id,amount,source) VALUES(?,?,?)", (uid, xp, "peso"))
            conn.execute("UPDATE users SET current_weight=? WHERE id=?", (dados["weight"], uid))
            limpar_cache()
            return xp

def atualizar_perfil(uid: int, atualizacoes: dict):
    with db() as conn:
        set_clause = ", ".join(f"{k}=?" for k in atualizacoes)
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", list(atualizacoes.values()) + [uid])
    limpar_cache()

def resetar_tudo(uid: int = USER_ID):
    with db() as conn:
        for tabela in ("xp_logs", "user_badges", "user_events", "daily_checkins", "weight_logs", "users"):
            conn.execute(f"DELETE FROM {tabela} WHERE {'user_id' if tabela != 'users' else 'id'}=?", (uid,))
        _generate_seed(conn)
    limpar_cache()

# -----------------------------------------------------------------------------
# 8. COMPONENTES DE UI
# -----------------------------------------------------------------------------
def toggle_tema():
    C = get_tema()
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🌙 Escuro", use_container_width=True):
                st.session_state.tema = "escuro"
                st.rerun()
        with col2:
            if st.button("☀️ Claro", use_container_width=True):
                st.session_state.tema = "claro"
                st.rerun()

def mostrar_barras_consistencia(valores: List[int]):
    if not valores:
        st.info("Dados insuficientes")
        return
    
    max_val = max(valores) if max(valores) > 0 else 100
    cols = st.columns(len(valores))
    
    for i, (col, val) in enumerate(zip(cols, valores)):
        altura = (val / max_val) * 100 if max_val > 0 else 0
        with col:
            st.markdown(f"""
            <div style="display:flex; flex-direction:column; align-items:center; gap:6px;">
                <div style="width:100%; height:{altura}px; background:{get_tema().PRIMARY}; border-radius:4px 4px 0 0;"></div>
                <div style="font-size:0.55rem; color:{get_tema().TEXT_DIM};">{i+1}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.caption("Consistência — últimos 14 dias")

def mostrar_tabela_metricas(metricas: Dict[str, float]):
    itens = [
        ("Consistência", metricas.get("consistencia", 0)),
        ("Disciplina", metricas.get("disciplina", 0)),
        ("Recuperação", metricas.get("recuperacao", 0)),
        ("Momento", metricas.get("momento", 0)),
        ("Estabilidade", metricas.get("estabilidade", 0)),
    ]
    
    for nome, valor in itens:
        st.markdown(f"""
        <div class="metric-item">
            <span class="metric-name">{nome}</span>
            <div class="metric-bar-wrapper">
                <div class="metric-bar-fill" style="width:{valor}%"></div>
            </div>
            <span class="metric-value">{valor:.0f}</span>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. PÁGINAS
# -----------------------------------------------------------------------------
def pagina_inicio(usuario, pesos, checkins, metricas, xp, dados_consistencia):
    C = get_tema()
    sequencia_atual = AnaliseEngine.sequencia(checkins["consistency_score"].tolist()) if not checkins.empty else 0
    peso_atual = pesos["weight"].iloc[-1] if not pesos.empty else usuario["current_weight"]
    meta = usuario["target_weight"]
    diferenca = peso_atual - meta
    texto_diferenca = f"{diferenca:+.1f} kg"
    tipo_diferenca = "positive" if diferenca < 0 else "warning"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">CONSISTÊNCIA</div>
            <div class="kpi-value">{metricas['consistencia']:.0f}</div>
            <span class="kpi-badge positive">Sequência {sequencia_atual}d</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        badge_class = "positive" if diferenca < 0 else "warning"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">PESO</div>
            <div class="kpi-value">{peso_atual:.1f} kg</div>
            <span class="kpi-badge {badge_class}">{texto_diferenca}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">DISCIPLINA</div>
            <div class="kpi-value">{metricas['disciplina']:.0f}</div>
            <span class="kpi-badge positive">+3 esta semana</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">RECUPERAÇÃO</div>
            <div class="kpi-value">{metricas['recuperacao']:.0f}</div>
            <span class="kpi-badge positive">+3 esta semana</span>
        </div>
        """, unsafe_allow_html=True)
    
    col_grafico, col_tabela = st.columns([2, 1])
    
    with col_grafico:
        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        mostrar_barras_consistencia(dados_consistencia)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_tabela:
        st.markdown('<div class="metrics-panel">', unsafe_allow_html=True)
        mostrar_tabela_metricas(metricas)
        st.markdown('</div>', unsafe_allow_html=True)
    
    nivel, _, progresso = NivelEngine.info(xp)
    st.markdown(f"""
    <div class="es-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div><span style="color:{C.TEXT_DIM};">NÍVEL</span><br><span style="font-size:1.2rem; font-weight:700;">{nivel}</span></div>
            <div style="text-align:right;"><span style="color:{C.TEXT_DIM};">XP TOTAL</span><br><span style="font-size:1.2rem; font-weight:700;">{xp}</span></div>
        </div>
        <div class="prog-track"><div class="prog-fill" style="width:{progresso:.1f}%"></div></div>
    </div>
    """, unsafe_allow_html=True)

def pagina_registrar(uid: int, usuario: Dict):
    st.markdown("<h2>Registrar Hoje</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{get_tema().TEXT_MUTED}; margin-bottom:20px;'>Entrada do dia {date.today().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
    
    aba1, aba2 = st.tabs(["📝 Check-in Diário", "⚖️ Peso e Medidas"])
    
    with aba1:
        with st.form("form_checkin"):
            col1, col2 = st.columns(2)
            with col1:
                calorias = st.number_input("Calorias", 0, 8000, 1800, 50, help="Meta: 1800 kcal")
                agua = st.number_input("Água (ml)", 0, 6000, 2500, 100, help="Meta: 2500 ml")
                sono = st.slider("Sono (h)", 0.0, 12.0, 7.0, 0.5, help="Recomendado: 7-8h")
            with col2:
                treino = st.number_input("Treino (min)", 0, 300, 0, 5, help="Meta: 30 min")
                humor = st.slider("Humor (1-10)", 1, 10, 7)
                estado = st.selectbox("Estado emocional", ["Focado", "Motivado", "Determinado", "Cansado", "Ansioso"])
            
            if st.form_submit_button("🔥 Salvar Check-in", use_container_width=True):
                with st.spinner("Salvando..."):
                    nota_cal = max(0, 100 - abs(calorias - 1800) / 18)
                    nota_agua = min(agua / 35, 100)
                    nota_sono = min(sono / 8.5 * 100, 100)
                    nota_treino = min(treino / 45 * 100, 100)
                    nota_humor = humor * 10
                    cons = int(nota_cal * 0.3 + nota_agua * 0.15 + nota_sono * 0.2 + nota_treino * 0.25 + nota_humor * 0.1)
                    disc = int(np.clip(humor * 10 + treino / 5, 10, 100))
                    dados = {
                        "date": date.today().isoformat(),
                        "calories_consumed": calorias,
                        "water_ml": agua,
                        "sleep_hours": sono,
                        "workout_minutes": treino,
                        "mood_score": humor,
                        "emotional_state": estado,
                        "discipline_score": disc,
                        "consistency_score": cons,
                    }
                    xp = salvar_checkin(uid, dados)
                    if xp:
                        st.toast(f"✅ Check-in salvo! +{xp} XP", icon="🔥")
                    else:
                        st.toast("✏️ Check-in atualizado!", icon="📝")
                    st.rerun()
    
    with aba2:
        with st.form("form_peso"):
            col1, col2, col3 = st.columns(3)
            with col1:
                peso = st.number_input("Peso (kg)", 30.0, 300.0, usuario["current_weight"], 0.1)
            with col2:
                gordura = st.number_input("Gordura (%)", 3.0, 60.0, 20.0, 0.1)
            with col3:
                massa_magra = st.number_input("Massa magra (kg)", 20.0, 120.0, 35.0, 0.1)
            
            if st.form_submit_button("🔥 Salvar Peso", use_container_width=True):
                dados = {"date": date.today().isoformat(), "weight": peso, "body_fat": gordura, "lean_mass": massa_magra}
                xp = salvar_peso(uid, dados)
                if xp:
                    st.toast(f"⚖️ Peso salvo! +{xp} XP", icon="🔥")
                else:
                    st.toast("✏️ Peso atualizado!", icon="⚖️")
                st.rerun()

def pagina_perfil(uid: int, usuario: Dict):
    st.markdown("<h2>Perfil</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{get_tema().TEXT_MUTED}; margin-bottom:20px;'>Edite seus dados pessoais</p>", unsafe_allow_html=True)
    
    with st.form("form_perfil"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", usuario["name"])
            idade = st.number_input("Idade", 18, 100, int(usuario["age"]))
            sexo = st.selectbox("Sexo", ["M", "F"], index=0 if usuario["sex"] == "M" else 1)
        with col2:
            altura = st.number_input("Altura (m)", 1.40, 2.20, usuario["height"], 0.01)
            meta_peso = st.number_input("Meta de peso (kg)", 30.0, 200.0, usuario["target_weight"], 0.5)
            niveis = ["sedentário", "leve", "moderado", "intenso", "extremo"]
            nivel_atual = st.selectbox("Nível de atividade", niveis, index=niveis.index(usuario["activity_level"]) if usuario["activity_level"] in niveis else 2)
        
        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
            atualizar_perfil(uid, {"name": nome, "age": idade, "sex": sexo, "height": altura, "target_weight": meta_peso, "activity_level": nivel_atual})
            st.toast("Perfil atualizado!", icon="👤")
            st.rerun()

def pagina_config(uid: int):
    st.markdown("<h2>Configurações</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{get_tema().TEXT_MUTED}; margin-bottom:20px;'>Exportar dados e opções do sistema</p>", unsafe_allow_html=True)
    
    if st.button("📥 Gerar arquivos CSV"):
        checkins = carregar_checkins(uid)
        pesos = carregar_pesos(uid)
        st.download_button("Check-ins.csv", checkins.to_csv(index=False), "checkins.csv", "text/csv")
        st.download_button("Pesos.csv", pesos.to_csv(index=False), "weights.csv", "text/csv")
    
    st.markdown("---")
    st.markdown("### ⚠️ Zona de Perigo")
    
    if "confirmar_reset" not in st.session_state:
        st.session_state.confirmar_reset = False
    
    if not st.session_state.confirmar_reset:
        if st.button("🗑️ Resetar todos os dados", type="secondary"):
            st.session_state.confirmar_reset = True
            st.rerun()
    else:
        st.warning("⚠️ Isso apagará TODOS os seus dados permanentemente.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, resetar"):
                with st.spinner("Resetando..."):
                    resetar_tudo(uid)
                    st.session_state.confirmar_reset = False
                    st.toast("Dados resetados!", icon="🔄")
                    st.rerun()
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_reset = False
                st.rerun()

# -----------------------------------------------------------------------------
# 10. SIDEBAR
# -----------------------------------------------------------------------------
def mostrar_sidebar(usuario: Dict, xp: int) -> str:
    C = get_tema()
    nivel, _, progresso = NivelEngine.info(xp)
    
    with st.sidebar:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:24px;">
            <div style="font-size:2rem;">🔥</div>
            <div style="font-size:1.2rem; font-weight:800;">Emagre<span style="color:{C.PRIMARY};">Sim</span></div>
        </div>
        <div style="background:{C.CARD}; border-radius:16px; padding:16px; margin-bottom:24px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:{C.TEXT_DIM};">NÍVEL</span>
                <span style="color:{C.PRIMARY};">{nivel}</span>
            </div>
            <div class="prog-track"><div class="prog-fill" style="width:{progresso:.1f}%"></div></div>
            <div style="margin-top:8px; font-size:0.7rem; color:{C.TEXT_DIM};">{xp} XP</div>
        </div>
        """, unsafe_allow_html=True)
        
        pagina = st.radio("", ["Início", "Registrar", "Perfil", "Configurações"], label_visibility="collapsed")
        
        toggle_tema()
        
        st.markdown(f"<div style='margin-top:32px; font-size:0.7rem; color:{C.TEXT_DIM}; text-align:center;'>Olá, {usuario.get('name', 'Usuário')}</div>", unsafe_allow_html=True)
    
    return pagina

# -----------------------------------------------------------------------------
# 11. MAIN
# -----------------------------------------------------------------------------
def main():
    init_db()
    usuario = carregar_usuario(USER_ID)
    if usuario is None:
        st.error("Erro ao carregar dados.")
        return
    
    aplicar_css()
    
    pesos = carregar_pesos(USER_ID)
    checkins = carregar_checkins(USER_ID)
    xp = carregar_xp(USER_ID)
    metricas = AnaliseEngine.calcular_metricas(checkins)
    dados_consistencia = AnaliseEngine.ultimos_14_dias(checkins)
    
    pagina = mostrar_sidebar(usuario, xp)
    
    if pagina == "Início":
        pagina_inicio(usuario, pesos, checkins, metricas, xp, dados_consistencia)
    elif pagina == "Registrar":
        pagina_registrar(USER_ID, usuario)
    elif pagina == "Perfil":
        pagina_perfil(USER_ID, usuario)
    elif pagina == "Configurações":
        pagina_config(USER_ID)

if __name__ == "__main__":
    main()
