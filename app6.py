# -*- coding: utf-8 -*-
"""
EmagreSim v12.1 - Responsivo + Layout Premium
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from supabase import create_client, Client
from streamlit_confetti import confetti

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Conectar ao Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["CHAVE_SUPABASE"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("Erro de conexão com Supabase")

# -----------------------------------------------------------------------------
# 2. CORES E TEMAS
# -----------------------------------------------------------------------------
if "tema" not in st.session_state:
    st.session_state.tema = "claro"

def get_tema():
    if st.session_state.tema == "claro":
        return {
            "bg": "#F8F9FA", "surface": "#FFFFFF", "card": "#FFFFFF",
            "primary": "#FF4D00", "text": "#1A1A1A", "text_muted": "#6B7280",
            "border": "rgba(0,0,0,0.08)", "shadow": "0 4px 12px rgba(0,0,0,0.05)"
        }
    else:
        return {
            "bg": "#0F172A", "surface": "#1E293B", "card": "#1E293B",
            "primary": "#FF4D00", "text": "#F8FAFC", "text_muted": "#94A3B8",
            "border": "rgba(255,255,255,0.08)", "shadow": "0 4px 12px rgba(0,0,0,0.2)"
        }

def aplicar_css():
    C = get_tema()
    css = f"""
    <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    
    .stApp, .stApp > header {{ background: {C['bg']} !important; }}
    section[data-testid="stSidebar"] {{ background: {C['surface']} !important; border-right: none !important; }}
    
    /* Cards responsivos */
    .card, .kpi-card {{
        background: {C['card']};
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid {C['border']};
        box-shadow: {C['shadow']};
        transition: all 0.3s ease;
    }}
    
    .card:hover, .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }}
    
    /* KPIs responsivos */
    .kpi-label {{ font-size: 0.7rem; color: {C['text_muted']}; text-transform: uppercase; letter-spacing: 0.05em; }}
    .kpi-value {{ font-size: 1.8rem; font-weight: 800; color: {C['primary']}; line-height: 1.2; }}
    .kpi-sub {{ font-size: 0.7rem; color: {C['text_muted']}; margin-top: 0.25rem; }}
    
    /* Grid responsivo */
    .grid-2, .grid-3, .grid-4 {{ display: grid; gap: 1rem; margin-bottom: 1rem; }}
    .grid-2 {{ grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }}
    .grid-3 {{ grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }}
    .grid-4 {{ grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
    
    /* Botões */
    .btn-primary {{
        background: {C['primary']};
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        transition: all 0.2s;
    }}
    .btn-primary:hover {{ opacity: 0.9; transform: translateY(-2px); }}
    
    .btn-secondary {{
        background: transparent;
        border: 1px solid {C['primary']};
        color: {C['primary']};
        border-radius: 40px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        width: 100%;
        cursor: pointer;
    }}
    
    /* Comparação */
    .comparison-card {{
        background: {C['surface']};
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid {C['border']};
    }}
    
    .comparison-value {{ font-size: 1.3rem; font-weight: 800; color: {C['primary']}; }}
    .comparison-label {{ font-size: 0.65rem; color: {C['text_muted']}; text-transform: uppercase; }}
    
    /* Insight box */
    .insight-box {{
        background: rgba(255,77,0,0.08);
        border-left: 3px solid {C['primary']};
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }}
    
    /* Progress bar */
    .progress-track {{ background: rgba(0,0,0,0.1); border-radius: 99px; height: 6px; overflow: hidden; }}
    .progress-fill {{ height: 100%; border-radius: 99px; background: {C['primary']}; transition: width 0.5s; }}
    
    /* Títulos */
    h1 {{ font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; color: {C['text']}; }}
    h2 {{ font-size: 1.3rem; font-weight: 700; margin: 1rem 0 0.5rem; color: {C['text']}; }}
    h3 {{ font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0; color: {C['text']}; }}
    
    /* Esconder elementos padrão */
    #MainMenu, header, footer, .stDeployButton {{ display: none; }}
    
    /* Responsivo mobile */
    @media (max-width: 768px) {{
        .card, .kpi-card {{ padding: 1rem; }}
        .kpi-value {{ font-size: 1.4rem; }}
        .grid-2, .grid-3, .grid-4 {{ gap: 0.75rem; }}
        h1 {{ font-size: 1.5rem; }}
    }}
    
    @media (max-width: 480px) {{
        .kpi-value {{ font-size: 1.2rem; }}
        .btn-primary, .btn-secondary {{ padding: 0.5rem 1rem; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------------
def card(content, kpi=False):
    cls = "kpi-card" if kpi else "card"
    return f'<div class="{cls}">{content}</div>'

def kpi(label, value, sub=None):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{sub_html}</div>'

def insight(text):
    return f'<div class="insight-box">💡 {text}</div>'

def progress_bar(pct):
    return f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>'

# -----------------------------------------------------------------------------
# 4. PÁGINA DEMONSTRAÇÃO (ADRIANO)
# -----------------------------------------------------------------------------
def pagina_demo():
    C = get_tema()
    st.markdown("<h1>🧪 Modo Demonstração - Adriano</h1>", unsafe_allow_html=True)
    
    if st.button("← Voltar para o início", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    
    adriano = {"name": "Adriano", "age": 39, "height": 1.75, "current_weight": 144.0, "target_weight": 90.0}
    
    # Grid 3 colunas responsivo
    col1, col2, col3 = st.columns(3)
    with col1:
        imc = adriano["current_weight"] / (adriano["height"] ** 2)
        st.metric("Peso Atual", f"{adriano['current_weight']:.1f} kg", f"Meta: {adriano['target_weight']:.0f} kg")
        st.metric("IMC", f"{imc:.1f}", "Obesidade Grave (Grau III)")
    with col2:
        tmb = (10 * adriano["current_weight"]) + (6.25 * adriano["height"] * 100) - (5 * adriano["age"]) + 5
        st.metric("TMB", f"{int(tmb)} kcal/dia")
        st.metric("Meta calórica", f"{int(tmb - 500)} kcal/dia")
    with col3:
        st.metric("Idade", f"{adriano['age']} anos")
        st.metric("Altura", f"{adriano['height']:.2f} m")
    
    # Projeção
    ritmo = 0.8
    kg_restantes = adriano["current_weight"] - adriano["target_weight"]
    semanas = kg_restantes / ritmo
    data_estimada = date.today() + timedelta(days=int(semanas * 7))
    st.info(f"📅 **Previsão:** No ritmo de -{ritmo}kg/semana, você chega em {adriano['target_weight']:.0f} kg em **{data_estimada.strftime('%d/%m/%Y')}**")
    
    # Recomendações
    with st.expander("💡 Recomendações Personalizadas", expanded=True):
        st.markdown("""
        - 🥩 **Proteína:** Priorize 2g/kg (≈288g/dia)
        - 💧 **Hidratação:** Beba 3L de água por dia
        - 🚶 **Movimento:** Caminhada leve 30min, 5x por semana
        - ⚠️ **Aviso:** Consulte um médico antes de começar
        """)
    
    # Metas intermediárias
    st.markdown("### 📊 Metas Intermediárias")
    metas = [
        ("Obesidade Grau I (IMC 35)", 35 * (adriano["height"] ** 2)),
        ("Sobrepeso (IMC 30)", 30 * (adriano["height"] ** 2)),
        ("Saudável (IMC 25)", 25 * (adriano["height"] ** 2)),
    ]
    for nome, peso_meta in metas:
        kg_faltam = adriano["current_weight"] - peso_meta
        if kg_faltam > 0:
            st.write(f"- **{nome}:** perder {kg_faltam:.0f} kg (chegar a {peso_meta:.0f} kg)")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔥 Criar minha conta", use_container_width=True):
            st.query_params["pagina"] = "criar_conta"
            st.rerun()
    with col_b2:
        if st.button("📊 Ver Ranking", use_container_width=True):
            st.query_params["pagina"] = "ranking"
            st.rerun()

# -----------------------------------------------------------------------------
# 5. PÁGINA LOGIN
# -----------------------------------------------------------------------------
def pagina_login():
    st.markdown("<h1 style='text-align:center;'>🔥 EmagreSim</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            if st.form_submit_button("Entrar", use_container_width=True):
                st.info("Login simulado - modo demo disponível")
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Criar conta", use_container_width=True):
                st.query_params["pagina"] = "criar_conta"
                st.rerun()
        with col_b:
            if st.button("🧪 Modo demonstração", use_container_width=True):
                st.query_params["pagina"] = "demo"
                st.rerun()

# -----------------------------------------------------------------------------
# 6. MAIN
# -----------------------------------------------------------------------------
def main():
    aplicar_css()
    
    pagina = st.query_params.get("pagina", "login")
    
    if pagina == "demo":
        pagina_demo()
    elif pagina == "criar_conta":
        st.info("Tela de criação de conta em desenvolvimento")
        if st.button("← Voltar"):
            st.query_params.clear()
            st.rerun()
    else:
        pagina_login()

if __name__ == "__main__":
    main()
