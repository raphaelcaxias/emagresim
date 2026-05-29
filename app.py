import streamlit as st
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine
from views import render_dashboard, render_refeicoes, render_historico, render_perfil

# Configuração Global
st.set_page_config(
    page_title="EmagreSim", 
    page_icon="🍽️", 
    layout="wide", # Mudamos para wide para dar mais respiro
    initial_sidebar_state="expanded"
)

# CSS PROFISSIONAL AVANÇADO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    /* Fundo com gradiente suave e moderno */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Remover padding padrão do Streamlit para layout fluido */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Sidebar Estilizada */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0f2f6 100%);
        border-right: 1px solid #e0e0e0;
    }
    section[data-testid="stSidebar"] .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Cards Glassmorphism */
    .css-1r6slb0, .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
        padding: 1.5rem !important;
    }
    
    /* Métricas em Cards */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #f0f0f0;
        text-align: center;
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricValue"] {
        color: #2d3436;
        font-weight: 700;
        font-size: 2.2rem;
    }
    [data-testid="stMetricLabel"] {
        color: #636e72;
        font-weight: 500;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Botões Premium */
    .stButton > button {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00cec9 0%, #00b894 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 184, 148, 0.4);
    }
    
    /* Inputs Elegantes */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #dfe6e9;
        padding: 10px;
        color: #2d3436;
    }
    
    /* Títulos */
    h1 {
        color: #2d3436;
        font-weight: 700;
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
    }
    h2 {
        color: #2d3436;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    h3 {
        color: #636e72;
        font-weight: 500;
    }
    
    /* Barra de Progresso Customizada */
    .stProgress > div > div {
        background-color: #00b894;
        border-radius: 10px;
    }
    
    /* Login Container */
    .login-box {
        background: white;
        padding: 3rem;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        max-width: 450px;
        margin: 2rem auto;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização de Serviços
@st.cache_resource
def init_services():
    db = SupabaseDB()
    return db, UserService(db), PsychologyEngine()

db, user_service, psychology = init_services()

# Estado
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "📊 Painel"

# TELA DE AUTENTICAÇÃO
if not st.session_state.user:
    st.markdown("<br>", unsafe_allow_html=True)
    # Centralizar login
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        st.title("🍽️ EmagreSim")
        st.caption("Sua jornada fitness começa aqui")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        with tab1:
            email = st.text_input("Email", placeholder="seu@email.com", label_visibility="collapsed")
            pwd = st.text_input("Senha", type="password", placeholder="Sua senha", label_visibility="collapsed")
            
            if st.button("Entrar"):
                if email and pwd:
                    res = db.sign_in(email, pwd)
                    if res["success"]: st.rerun()
                    else: st.error(f"Erro: {res.get('error', 'Credenciais inválidas')}")
                else: st.warning("Preencha todos os campos")

        with tab2:
            new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com", label_visibility="collapsed")
            new_pwd = st.text_input("Senha", key="reg_pwd", type="password", placeholder="Mín. 6 caracteres", label_visibility="collapsed")
            new_user = st.text_input("Nome de Usuário", key="reg_user", placeholder="Seu apelido", label_visibility="collapsed")
            
            if st.button("Criar Conta"):
                if new_email and new_pwd and new_user:
                    if len(new_pwd) >= 6:
                        res = db.sign_up(new_email, new_pwd, new_user)
                        if res["success"]: 
                            st.success("✅ Conta criada! Faça login."); st.balloons()
                        else: st.error(f"Erro: {res['error']}")
                    else: st.warning("Senha muito curta")
                else: st.warning("Preencha todos os campos")
        
        st.markdown('</div>', unsafe_allow_html=True)

# APP PRINCIPAL
else:
    with st.sidebar:
        st.markdown("### 🍽️ EmagreSim")
        st.markdown("---")
        
        profile = db.get_profile()
        if profile:
            st.metric(label="🏆 Nível", value=profile.get('level', 1))
            st.metric(label="⚡ XP", value=profile.get('experience', 0))
        
        st.markdown("---")
        page = st.radio(
            "Menu",
            ["📊 Painel", "🍴 Refeições", "📈 Histórico", "👤 Perfil"],
            label_visibility="collapsed",
            key="nav_radio"
        )
        st.session_state.page = page
        
        st.markdown("---")
        if st.button("🚪 Sair"):
            db.sign_out()
            st.rerun()

    # ROTEAMENTO
    if profile:
        if st.session_state.page == "📊 Painel":
            render_dashboard(db, user_service, psychology, profile)
        elif st.session_state.page == "🍴 Refeições":
            render_refeicoes(db, user_service)
        elif st.session_state.page == "📈 Histórico":
            render_historico(db)
        elif st.session_state.page == "👤 Perfil":
            render_perfil(db, user_service, profile)
    else:
        st.warning("Perfil não carregado. Tente logar novamente.")
