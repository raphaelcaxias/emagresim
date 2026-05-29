import streamlit as st
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine
from views import render_dashboard, render_refeicoes, render_historico, render_perfil

# 1. Configuração Global
st.set_page_config(
    page_title="EmagreSim", 
    page_icon="🍽️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Profissional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); min-height: 100vh; }
    .stAlert, .stInfo, .stSuccess, .stWarning {
        background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
        border-radius: 16px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    [data-testid="stMetricValue"] { color: #11998e; font-weight: 700; font-size: 2rem; }
    [data-testid="stMetricLabel"] { color: #6c757d; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; }
    .stButton > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white;
        border: none; border-radius: 10px; font-weight: 600; width: 100%;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        border-radius: 10px; border: 2px solid #e0e0e0; padding: 12px;
    }
    h1 { color: white; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    h2, h3 { color: #2d3748; font-weight: 600; }
    .stProgress > div > div { background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 2. Inicialização de Serviços
@st.cache_resource
def init_services():
    db = SupabaseDB()
    return db, UserService(db), PsychologyEngine()

db, user_service, psychology = init_services()

# 3. Estado da Sessão
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = " Dashboard"

# 4. Tela de Autenticação
if not st.session_state.user:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🍽️ EmagreSim")
    st.subheader("Sua jornada fitness começa aqui")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 Entrar", " Criar Conta"])
        
        with tab1:
            st.markdown("### 👋 Bem-vindo de volta!")
            email = st.text_input("Email", placeholder="seu@email.com", label_visibility="collapsed")
            pwd = st.text_input("Senha", type="password", placeholder="Sua senha", label_visibility="collapsed")
            
            if st.button("Entrar", use_container_width=True):
                if email and pwd:
                    res = db.sign_in(email, pwd)
                    if res["success"]: st.rerun()
                    else: st.error(f"Erro: {res.get('error', 'Email ou senha incorretos')}")
                else: st.warning("Preencha todos os campos")

        with tab2:
            st.markdown("### 🚀 Nova Conta")
            new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com", label_visibility="collapsed")
            new_pwd = st.text_input("Senha", key="reg_pwd", type="password", placeholder="Mín. 6 caracteres", label_visibility="collapsed")
            new_user = st.text_input("Nome de Usuário", key="reg_user", placeholder="Seu apelido", label_visibility="collapsed")
            
            if st.button("Criar Conta", use_container_width=True):
                if new_email and new_pwd and new_user:
                    if len(new_pwd) >= 6:
                        res = db.sign_up(new_email, new_pwd, new_user)
                        if res["success"]: 
                            st.success("✅ Conta criada! Faça login."); st.balloons()
                        else: st.error(f"Erro: {res['error']}")
                    else: st.warning("Senha deve ter pelo menos 6 caracteres")
                else: st.warning("Preencha todos os campos")

# 5. App Principal (Logado)
else:
    with st.sidebar:
        st.title("🍽️ EmagreSim")
        st.markdown("---")
        
        profile = db.get_profile()
        if profile:
            st.metric(label="🏆 Nível", value=profile.get('level', 1))
            st.metric(label=" XP", value=profile.get('experience', 0))
            st.metric(label="⚖️ Peso", value=f"{profile.get('current_weight_kg', 0)} kg")
        
        st.markdown("---")
        page = st.radio(
            "Navegação",
            ["📊 Dashboard", "🍴 Refeições", "📈 Histórico", "👤 Perfil"],
            label_visibility="collapsed"
        )
        st.session_state.page = page
        
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            db.sign_out()
            st.rerun()

    # 6. Roteamento de Telas
    if profile:
        if st.session_state.page == "📊 Dashboard":
            render_dashboard(db, user_service, psychology, profile)
        elif st.session_state.page == "🍴 Refeições":
            render_refeicoes(db, user_service)
        elif st.session_state.page == "📈 Histórico":
            render_historico(db)
        elif st.session_state.page == "👤 Perfil":
            render_perfil(db, user_service, profile)
