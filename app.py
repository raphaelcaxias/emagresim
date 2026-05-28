# app.py
import streamlit as st
from utils.constants import CORES
from utils.helpers import mensagem_bom_dia

st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS GLOBAL
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', sans-serif;
    background-color: {CORES["background"]};
    color: {CORES["text"]};
}}

.topbar {{
    background: linear-gradient(135deg, {CORES["secondary"]} 0%, #005A5A 100%);
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 0 0 16px 16px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0, 128, 128, 0.15);
}}
.topbar-logo {{
    color: #FFFFFF;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}}
.topbar-logo span {{ color: {CORES["primary"]}; }}
.topbar-user {{ color: #E2E8F0; font-size: 0.9rem; font-weight: 500; }}

.hero-card {{
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 25px;
    border-left: 6px solid {CORES["primary"]};
}}
.avatar-container {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: white;
    padding: 4px;
    border: 4px solid {CORES["secondary"]};
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 2.2rem;
    box-shadow: 0 4px 10px rgba(0, 128, 128, 0.2);
}}
.hero-text h2 {{ margin: 0; color: #1A202C; font-size: 1.8rem; font-weight: 700; }}
.hero-text p {{ margin: 4px 0 0 0; color: #718096; font-size: 1rem; }}

.section-card {{
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    margin-bottom: 20px;
}}
.section-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: {CORES["text"]};
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.apoio-card {{
    background: #FFF5F5;
    border: 1px solid #FED7D7;
    border-radius: 12px;
    padding: 16px;
    height: 100%;
}}
.dica-card {{
    background: #EBF8FA;
    border: 1px solid #E2F8FA;
    border-radius: 12px;
    padding: 16px;
    height: 100%;
}}

.metric-coral div[data-testid="stMetric"] {{ border-top: 4px solid {CORES["primary"]}; }}
.metric-teal div[data-testid="stMetric"] {{ border-top: 4px solid {CORES["secondary"]}; }}
.metric-blue div[data-testid="stMetric"] {{ border-top: 4px solid #3182CE; }}
.metric-orange div[data-testid="stMetric"] {{ border-top: 4px solid #DD6B20; }}

#MainMenu, header, footer, .stDeployButton {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "dashboard"
if "peso_atual" not in st.session_state:
    st.session_state["peso_atual"] = 105.8
if "refeicoes" not in st.session_state:
    st.session_state["refeicoes"] = []
if "historico_pesos" not in st.session_state:
    from datetime import datetime, timedelta
    import random
    datas = [datetime.now() - timedelta(days=i) for i in range(30, -1, -1)]
    pesos = [108.0 - (i * 0.08) + random.uniform(-0.3, 0.3) for i in range(31)]
    st.session_state.historico_pesos = list(zip(datas, pesos))

# Topbar
st.markdown(f"""
<div class="topbar">
    <div class="topbar-logo">🌱 Emagre<span>Sim</span></div>
    <div class="topbar-user">👤 Adriano | Modo Demo</div>
</div>
""", unsafe_allow_html=True)

# Navegação
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state["pagina"] = "dashboard"
        st.rerun()
with col2:
    if st.button("🍽️ Refeições", use_container_width=True):
        st.session_state["pagina"] = "refeicoes"
        st.rerun()
with col3:
    if st.button("📈 Histórico", use_container_width=True):
        st.session_state["pagina"] = "historico"
        st.rerun()
with col4:
    if st.button("👤 Perfil", use_container_width=True):
        st.session_state["pagina"] = "perfil"
        st.rerun()

# Roteamento
pagina = st.session_state["pagina"]

if pagina == "dashboard":
    from pages.dashboard import mostrar_dashboard
    mostrar_dashboard()
elif pagina == "refeicoes":
    from pages.refeicoes import mostrar_refeicoes
    mostrar_refeicoes()
elif pagina == "historico":
    from pages.historico import mostrar_historico
    mostrar_historico()
elif pagina == "perfil":
    from pages.perfil import mostrar_perfil
    mostrar_perfil()
