# -*- coding: utf-8 -*-
"""
EmagreSim v9.0 - MVP (Sem Supabase)
- Multi-usuário via SQLite + session_state
- Modo demonstração (Adriano)
- Planos: Grátis / Premium (simulado)
- Registro: peso, refeições (8/dia grátis), humor
- Tema claro/escuro/automático
- Tudo em português
"""

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
import time
from datetime import datetime, timedelta, date
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES
# -----------------------------------------------------------------------------
DB_PATH = "emagresim_v9.db"

st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. CORES E TEMAS
# -----------------------------------------------------------------------------
if "tema" not in st.session_state:
    st.session_state.tema = "auto"

@dataclass
class TemaEscuro:
    BG: str = "#0D0D0D"
    SURFACE: str = "#1A1A1A"
    CARD: str = "#1E1E1E"
    PRIMARY: str = "#FF4D00"
    TEXT: str = "#FFFFFF"
    TEXT_MUTED: str = "#A0A0A0"
    BORDER: str = "rgba(255,255,255,0.06)"

@dataclass
class TemaClaro:
    BG: str = "#F5F5F0"
    SURFACE: str = "#FFFFFF"
    CARD: str = "#FFFFFF"
    PRIMARY: str = "#FF4D00"
    TEXT: str = "#1A1A1A"
    TEXT_MUTED: str = "#666666"
    BORDER: str = "rgba(0,0,0,0.08)"

def get_tema():
    if st.session_state.tema == "claro":
        return TemaClaro()
    elif st.session_state.tema == "escuro":
        return TemaEscuro()
    else:
        # Auto: detecta preferência do sistema (simulado com horário)
        hora = datetime.now().hour
        return TemaEscuro() if hora < 6 or hora > 18 else TemaClaro()

# -----------------------------------------------------------------------------
# 3. CSS DINÂMICO
# -----------------------------------------------------------------------------
def aplicar_css():
    C = get_tema()
    css = f"""
    <style>
    .stApp, .stApp > header {{ background: {C.BG} !important; }}
    section[data-testid="stSidebar"] {{ background: {C.SURFACE} !important; border-right: 1px solid {C.BORDER} !important; }}
    .es-card, .kpi-card {{ background: {C.CARD}; border-radius: 20px; padding: 20px; margin-bottom: 20px; border: 1px solid {C.BORDER}; }}
    .kpi-label {{ font-size: 0.7rem; color: {C.TEXT_MUTED}; text-transform: uppercase; }}
    .kpi-value {{ font-size: 2rem; font-weight: 800; color: {C.TEXT}; }}
    .kpi-badge {{ background: rgba(255,77,0,0.15); color: {C.PRIMARY}; border-radius: 20px; padding: 4px 10px; font-size: 0.7rem; }}
    .prog-track {{ background: rgba(0,0,0,0.1); border-radius: 99px; height: 6px; }}
    .prog-fill {{ height: 100%; border-radius: 99px; background: {C.PRIMARY}; transition: width 0.5s; }}
    .insight-box {{ background: rgba(255,77,0,0.08); border-left: 3px solid {C.PRIMARY}; padding: 12px; border-radius: 12px; margin: 8px 0; }}
    .divider {{ border-top: 1px solid {C.BORDER}; margin: 16px 0; }}
    #MainMenu, header, footer, .stDeployButton {{ display: none; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. BANCO DE DADOS (SQLite)
# -----------------------------------------------------------------------------
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    age INT,
    height REAL,
    current_weight REAL,
    target_weight REAL,
    sex TEXT,
    is_premium BOOLEAN DEFAULT 0,
    premium_expires DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    weight REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checkin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    humor TEXT,
    consistency_score INT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    meal_type TEXT,
    food_name TEXT,
    calories INT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    habit_name TEXT,
    target_daily INT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    habit_id INT,
    completed INT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    target_weight REAL,
    target_date DATE,
    monthly_goal_kg REAL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
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
        # Criar usuário demo (Adriano) se não existir
        demo = conn.execute("SELECT id FROM users WHERE email='demo@emagresim.com'").fetchone()
        if not demo:
            conn.execute("""
                INSERT INTO users (name, email, password, age, height, current_weight, target_weight, sex, is_premium)
                VALUES ('Adriano', 'demo@emagresim.com', 'demo', 39, 1.75, 144.0, 90.0, 'M', 1)
            """)
            user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            # Dados simulados para Adriano (últimos 30 dias)
            for i in range(30):
                d = date.today() - timedelta(days=i)
                peso = max(144 - i * 0.15, 90)
                conn.execute("INSERT INTO weight_logs(user_id,date,weight) VALUES(?,?,?)", (user_id, d.isoformat(), round(peso, 1)))
                humor = ["Motivado", "Cansado", "Determinado", "Focado"][i % 4]
                cons = int(max(100 - i * 0.5, 50))
                conn.execute("INSERT INTO checkin_logs(user_id,date,humor,consistency_score) VALUES(?,?,?,?)", (user_id, d.isoformat(), humor, cons))
    print("Banco de dados inicializado")

# -----------------------------------------------------------------------------
# 5. FUNÇÕES DE AUTENTICAÇÃO (simples, sem Supabase)
# -----------------------------------------------------------------------------
def criar_usuario(name, email, password, age, height, weight, target, sex):
    with db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            return False, "E-mail já cadastrado"
        hashed = hashlib.sha256(password.encode()).hexdigest()
        conn.execute("""
            INSERT INTO users (name, email, password, age, height, current_weight, target_weight, sex)
            VALUES (?,?,?,?,?,?,?,?)
        """, (name, email, hashed, age, height, weight, target, sex))
        return True, "Conta criada com sucesso"

def fazer_login(email, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed)).fetchone()
        if user:
            return dict(user)
        return None

def get_user_by_id(user_id):
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(user) if user else None

# -----------------------------------------------------------------------------
# 6. FUNÇÕES DE REGISTRO
# -----------------------------------------------------------------------------
def registrar_peso(user_id, peso, data):
    with db() as conn:
        existing = conn.execute("SELECT id FROM weight_logs WHERE user_id=? AND date=?", (user_id, data)).fetchone()
        if existing:
            conn.execute("UPDATE weight_logs SET weight=? WHERE user_id=? AND date=?", (peso, user_id, data))
        else:
            conn.execute("INSERT INTO weight_logs(user_id,date,weight) VALUES(?,?,?)", (user_id, data, peso))
        conn.execute("UPDATE users SET current_weight=? WHERE id=?", (peso, user_id))

def registrar_refeicao(user_id, data, meal_type, food_name, calories):
    with db() as conn:
        conn.execute("INSERT INTO food_logs(user_id,date,meal_type,food_name,calories) VALUES(?,?,?,?,?)",
                     (user_id, data, meal_type, food_name, calories))

def registrar_humor(user_id, data, humor, consistency):
    with db() as conn:
        existing = conn.execute("SELECT id FROM checkin_logs WHERE user_id=? AND date=?", (user_id, data)).fetchone()
        if existing:
            conn.execute("UPDATE checkin_logs SET humor=?, consistency_score=? WHERE user_id=? AND date=?",
                         (humor, consistency, user_id, data))
        else:
            conn.execute("INSERT INTO checkin_logs(user_id,date,humor,consistency_score) VALUES(?,?,?,?)",
                         (user_id, data, humor, consistency))

def get_refeicoes_hoje(user_id, data):
    with db() as conn:
        rows = conn.execute("SELECT * FROM food_logs WHERE user_id=? AND date=?", (user_id, data)).fetchall()
        return [dict(r) for r in rows]

def get_calorias_hoje(user_id, data):
    refeicoes = get_refeicoes_hoje(user_id, data)
    return sum(r["calories"] for r in refeicoes)

def get_ultimos_pesos(user_id, dias=30):
    with db() as conn:
        rows = conn.execute("SELECT date, weight FROM weight_logs WHERE user_id=? ORDER BY date DESC LIMIT ?", (user_id, dias)).fetchall()
        return [dict(r) for r in rows][::-1]

def get_consistencia_ultimos_dias(user_id, dias=14):
    with db() as conn:
        rows = conn.execute("SELECT date, consistency_score FROM checkin_logs WHERE user_id=? ORDER BY date DESC LIMIT ?", (user_id, dias)).fetchall()
        return [dict(r) for r in rows][::-1]

# -----------------------------------------------------------------------------
# 7. UI COMPONENTS
# -----------------------------------------------------------------------------
def card(content):
    return f'<div class="es-card">{content}</div>'

def kpi(label, value, badge=None):
    badge_html = f'<span class="kpi-badge">{badge}</span>' if badge else ""
    return f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{badge_html}</div>'

def progress_bar(percent):
    return f'<div class="prog-track"><div class="prog-fill" style="width:{percent}%"></div></div>'

def insight(text):
    return f'<div class="insight-box">💡 {text}</div>'

# -----------------------------------------------------------------------------
# 8. PÁGINAS
# -----------------------------------------------------------------------------
def pagina_dashboard(user):
    C = get_tema()
    st.markdown("<h1>🔥 Dashboard</h1>", unsafe_allow_html=True)
    
    # KPIs
    peso_atual = user["current_weight"]
    meta_peso = user["target_weight"]
    diferenca = peso_atual - meta_peso
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(kpi("PESO ATUAL", f"{peso_atual:.1f} kg", f"{diferenca:+.1f} kg da meta"), unsafe_allow_html=True)
    with col2:
        imc = peso_atual / (user["height"] ** 2)
        st.markdown(kpi("IMC", f"{imc:.1f}", "Obesidade" if imc > 30 else "Sobrepeso" if imc > 25 else "Normal"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi("PLANO", "PREMIUM" if user["is_premium"] else "GRÁTIS", "14 dias grátis"), unsafe_allow_html=True)
    
    # Gráfico de peso (simples)
    pesos = get_ultimos_pesos(user["id"], 30)
    if pesos:
        df = pd.DataFrame(pesos)
        st.line_chart(df.set_index("date")["weight"])
    
    # Frase do dia
    frases = [
        "Consistência é mais importante que intensidade.",
        "Um dia de cada vez. Você consegue.",
        "O progresso não é linear. Continue.",
        "Você está mais perto do que ontem."
    ]
    st.markdown(insight(frases[datetime.now().day % len(frases)]), unsafe_allow_html=True)
    
    # Limites do plano gratuito
    if not user["is_premium"]:
        st.info("💡 Plano gratuito: até 8 refeições/dia, histórico 30 dias. Assine premium para recursos ilimitados!")

def pagina_registrar(user):
    st.markdown("<h1>✏️ Registrar Hoje</h1>", unsafe_allow_html=True)
    hoje = date.today().isoformat()
    
    tab1, tab2, tab3 = st.tabs(["⚖️ Peso", "🍽️ Refeição", "😊 Humor"])
    
    with tab1:
        with st.form("form_peso"):
            peso = st.number_input("Peso (kg)", 30.0, 250.0, user["current_weight"], 0.1)
            if st.form_submit_button("Salvar Peso"):
                registrar_peso(user["id"], peso, hoje)
                st.toast("✅ Peso registrado!", icon="⚖️")
                st.rerun()
    
    with tab2:
        refeicoes_hoje = get_refeicoes_hoje(user["id"], hoje)
        calorias_hoje = sum(r["calories"] for r in refeicoes_hoje)
        limite_refeicoes = 8 if not user["is_premium"] else 999
        st.caption(f"📊 Calorias hoje: {calorias_hoje} kcal | Refeições: {len(refeicoes_hoje)}/{limite_refeicoes}")
        
        if len(refeicoes_hoje) >= limite_refeicoes and not user["is_premium"]:
            st.warning("🔒 Você atingiu o limite de refeições do plano gratuito. Assine premium para registrar mais.")
        else:
            with st.form("form_refeicao"):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Refeição", ["Café da manhã", "Almoço", "Jantar", "Lanche"])
                    alimento = st.text_input("O que comeu?")
                with col2:
                    calorias = st.number_input("Calorias (kcal)", 0, 2000, 300, 50)
                if st.form_submit_button("Salvar Refeição"):
                    if alimento:
                        registrar_refeicao(user["id"], hoje, tipo, alimento, calorias)
                        st.toast(f"✅ {tipo} registrado! +{calorias} kcal", icon="🍽️")
                        st.rerun()
                    else:
                        st.error("Digite o alimento")
        
        # Listar refeições do dia
        if refeicoes_hoje:
            st.markdown("---")
            for r in refeicoes_hoje:
                st.caption(f"🍴 {r['meal_type']}: {r['food_name']} - {r['calories']} kcal")
    
    with tab3:
        with st.form("form_humor"):
            humor = st.selectbox("Como você está se sentindo?", ["Motivado", "Cansado", "Determinado", "Focado", "Ansioso", "Frustrado", "Orgulhoso"])
            consistencia = st.slider("Consistência hoje (0-100)", 0, 100, 70)
            if st.form_submit_button("Salvar Humor"):
                registrar_humor(user["id"], hoje, humor, consistencia)
                st.toast("✅ Humor registrado!", icon="😊")
                st.rerun()

def pagina_perfil(user):
    st.markdown("<h1>👤 Meu Perfil</h1>", unsafe_allow_html=True)
    with st.form("form_perfil"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", user["name"])
            idade = st.number_input("Idade", 18, 100, user["age"] or 30)
            sexo = st.selectbox("Sexo", ["M", "F"], index=0 if user["sex"] == "M" else 1)
        with col2:
            altura = st.number_input("Altura (m)", 1.40, 2.20, user["height"] or 1.75, 0.01)
            meta_peso = st.number_input("Meta de peso (kg)", 40.0, 200.0, user["target_weight"], 0.5)
        if st.form_submit_button("Salvar"):
            st.toast("Perfil atualizado!", icon="👤")
            st.rerun()

def pagina_planos(user):
    st.markdown("<h1>💎 Planos</h1>", unsafe_allow_html=True)
    
    if user["is_premium"]:
        st.success("✅ Você já é assinante premium!")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(card("""
        <h3>🔥 GRÁTIS</h3>
        <p>R$ 0</p>
        <ul>
        <li>✅ Peso ilimitado</li>
        <li>✅ Até 8 refeições/dia</li>
        <li>✅ Histórico 30 dias</li>
        <li>✅ 1 dieta disponível</li>
        <li>📢 Anúncios leves</li>
        </ul>
        """), unsafe_allow_html=True)
    with col2:
        st.markdown(card("""
        <h3>💎 PREMIUM</h3>
        <p>R$ 19,90/mês</p>
        <ul>
        <li>✅ Tudo do grátis</li>
        <li>✅ Refeições ilimitadas</li>
        <li>✅ Histórico completo</li>
        <li>✅ 10 dietas</li>
        <li>✅ IA e toques inteligentes</li>
        <li>✅ Ranking completo</li>
        <li>✅ Exportar CSV</li>
        <li>🚫 Sem anúncios</li>
        </ul>
        """), unsafe_allow_html=True)
    
    if st.button("🔥 Testar 14 dias grátis", use_container_width=True):
        st.toast("✅ Teste grátis ativado! (simulação)", icon="🎉")
        st.rerun()

# -----------------------------------------------------------------------------
# 9. SIDEBAR
# -----------------------------------------------------------------------------
def sidebar(user):
    with st.sidebar:
        st.markdown("## 🔥 EmagreSim")
        
        # Temas
        tema_opts = ["auto", "claro", "escuro"]
        tema_idx = tema_opts.index(st.session_state.tema)
        tema = st.radio("🎨 Tema", tema_opts, index=tema_idx, horizontal=True, label_visibility="collapsed")
        if tema != st.session_state.tema:
            st.session_state.tema = tema
            st.rerun()
        
        st.markdown("---")
        st.page_link("app.py", label="📊 Dashboard", icon="📊")
        st.page_link("app.py", label="✏️ Registrar", icon="✏️")
        st.page_link("app.py", label="👤 Perfil", icon="👤")
        st.page_link("app.py", label="💎 Planos", icon="💎")
        
        st.markdown("---")
        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.rerun()
        
        st.caption(f"Olá, {user['name']} | {user['email']}")

# -----------------------------------------------------------------------------
# 10. MAIN
# -----------------------------------------------------------------------------
def main():
    init_db()
    aplicar_css()
    
    # Estado de autenticação
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    # Tela de login / demo
    if st.session_state.user_id is None:
        st.markdown("<h1 style='text-align:center;'>🔥 EmagreSim</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔐 Login")
            email = st.text_input("E-mail")
            password = st.text_input("Senha", type="password")
            if st.button("Entrar", use_container_width=True):
                user = fazer_login(email, password)
                if user:
                    st.session_state.user_id = user["id"]
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos")
        
        with col2:
            st.markdown("### 🧪 Modo demonstração")
            st.caption("Teste o EmagreSim com dados de exemplo (Adriano)")
            if st.button("🔥 Carregar demonstração", use_container_width=True):
                demo = fazer_login("demo@emagresim.com", "demo")
                if demo:
                    st.session_state.user_id = demo["id"]
                    st.rerun()
                else:
                    st.error("Erro ao carregar demonstração")
        
        st.markdown("---")
        st.markdown("### ✨ Criar conta")
        with st.form("form_criar_conta"):
            nome = st.text_input("Nome completo")
            email_criar = st.text_input("E-mail")
            senha_criar = st.text_input("Senha", type="password")
            idade_criar = st.number_input("Idade", 18, 100, 30)
            altura_criar = st.number_input("Altura (m)", 1.40, 2.20, 1.75, 0.01)
            peso_criar = st.number_input("Peso atual (kg)", 30.0, 250.0, 80.0, 0.1)
            meta_criar = st.number_input("Meta de peso (kg)", 40.0, 200.0, 70.0, 0.5)
            sexo_criar = st.selectbox("Sexo", ["M", "F"])
            if st.form_submit_button("Criar conta", use_container_width=True):
                ok, msg = criar_usuario(nome, email_criar, senha_criar, idade_criar, altura_criar, peso_criar, meta_criar, sexo_criar)
                if ok:
                    st.success(msg)
                    user = fazer_login(email_criar, senha_criar)
                    if user:
                        st.session_state.user_id = user["id"]
                        st.rerun()
                else:
                    st.error(msg)
        return
    
    # Usuário logado
    user = get_user_by_id(st.session_state.user_id)
    if not user:
        st.session_state.clear()
        st.rerun()
        return
    
    sidebar(user)
    
    # Router simples
    import sys
    if "page" not in st.query_params:
        st.query_params["page"] = "Dashboard"
    
    page = st.query_params.get("page", "Dashboard")
    
    if page == "Dashboard":
        pagina_dashboard(user)
    elif page == "Registrar":
        pagina_registrar(user)
    elif page == "Perfil":
        pagina_perfil(user)
    elif page == "Planos":
        pagina_planos(user)
    
    # Navegação por links na sidebar
    if st.sidebar.button("📊 Dashboard", key="nav_dash"):
        st.query_params["page"] = "Dashboard"
        st.rerun()
    if st.sidebar.button("✏️ Registrar", key="nav_reg"):
        st.query_params["page"] = "Registrar"
        st.rerun()
    if st.sidebar.button("👤 Perfil", key="nav_profile"):
        st.query_params["page"] = "Perfil"
        st.rerun()
    if st.sidebar.button("💎 Planos", key="nav_plans"):
        st.query_params["page"] = "Planos"
        st.rerun()

if __name__ == "__main__":
    main()
