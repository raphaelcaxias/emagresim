import streamlit as st
from core.database import SupabaseDB
from views import render_onboarding, render_dashboard, render_daily_log, render_profile

# ==========================================
# CONFIGURAÇÃO & CSS PREMIUM
# ==========================================
st.set_page_config(page_title="EmagreSim Analytics", page_icon="📊", layout="wide")

st.markdown("""
<style>
    /* FONTE E CORES GLOBAIS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    body { background-color: #f0f2f6; }
    
    /* CARDS DE VIDRO */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* MÉTRICAS ESTILIZADAS */
    [data-testid="stMetric"] {
        background: white; padding: 15px; border-radius: 12px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.03); text-align: center;
    }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #2d3436; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; text-transform: uppercase; color: #636e72; font-weight: 600; }
    
    /* BOTÕES MODERNOS */
    .stButton > button {
        background: linear-gradient(90deg, #00b894 0%, #00cec9 100%);
        color: white; border: none; border-radius: 8px; font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,184,148,0.2); transition: all 0.3s;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,184,148,0.3); }
    
    /* INPUTS */
    input, select, textarea { border-radius: 8px !important; border: 1px solid #dfe6e9 !important; padding: 10px !important; }
    input:focus { border-color: #00b894 !important; box-shadow: 0 0 0 3px rgba(0,184,148,0.1) !important; }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background: white; border-right: 1px solid #e0e0e0; }
    
    /* TÍTULOS */
    h1 { color: #2d3436; font-weight: 800; letter-spacing: -1px; }
    h2 { color: #2d3436; font-weight: 600; }
    h3 { color: #636e72; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZAÇÃO
# ==========================================
@st.cache_resource
def init_db(): return SupabaseDB()

db = init_db()

if "user" not in st.session_state: st.session_state.user = None

# ==========================================
# TELA DE LOGIN
# ==========================================
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🍽️ EmagreSim")
        st.subheader("Plataforma de Analytics Corporal")
        
        tab1, tab2 = st.tabs([" Entrar", "🚀 Criar Conta"])
        
        with tab1:
            email = st.text_input("Email", placeholder="seu@email.com")
            pwd = st.text_input("Senha", type="password", placeholder="••••••••")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Entrar", use_container_width=True):
                    res = db.sign_in(email, pwd)
                    if res["success"]: st.rerun()
                    else: st.error("Falha no login. Verifique os dados.")
            with c2:
                if st.button(" Esqueci Senha", use_container_width=True):
                    try:
                        db.client.auth.reset_password_for_email(email)
                        st.success("Link de recuperação enviado!")
                    except: st.warning("Verifique o email digitado.")
            
            st.divider()
            if st.button("👁️ Entrar como DEMO", use_container_width=True):
                # Login Mock para Demo
                st.session_state.user = {"id": "demo-user", "email": "demo@emagresim.com", "user_metadata": {"username": "Visitante"}}
                st.rerun()

        with tab2:
            email = st.text_input("Email", key="reg_email")
            pwd = st.text_input("Senha", type="password", key="reg_pwd")
            user = st.text_input("Nome de Usuário", key="reg_user")
            if st.button("Cadastrar", use_container_width=True):
                res = db.sign_up(email, pwd, user)
                if res["success"]: st.success("Conta criada! Faça login.")
                else: st.error(res["error"])

# ==========================================
# APLICAÇÃO PRINCIPAL
# ==========================================
else:
    # Verifica se é demo
    is_demo = st.session_state.user["id"] == "demo-user"
    
    # Sidebar
    with st.sidebar:
        st.title("🍽️ EmagreSim")
        if is_demo:
            st.info("🎭 **Modo Demonstração**\nVeja como funciona!")
        
        st.divider()
        
        # Menu de Navegação
        page = st.radio("Menu", ["📊 Dashboard", "📝 Registro do Dia", "👤 Meu Perfil"])
        
        st.divider()
        if st.button("🚪 Sair"): db.sign_out(); st.rerun()

    # Roteamento
    if is_demo:
        # Se for demo, simula dados
        profile = {"level": 5, "experience": 320, "streak_days": 12, "goal_weight_kg": 72.0, 
                   "current_weight_kg": 78.5, "is_onboarding_complete": True, "gender": "M", "date_of_birth": "1995-01-01", "height_cm": 175, "age": 29}
    else:
        profile = db.get_profile()
    
    if not profile and not is_demo: st.warning("Erro ao carregar perfil."); db.sign_out()
    
    # 1. ONBOARDING (Se o usuário ainda não completou o cadastro)
    elif not profile.get("is_onboarding_complete") and not is_demo:
        if render_onboarding(db, profile):
            st.rerun() # Recarrega para atualizar o perfil
            
    # 2. APP PRINCIPAL
    else:
        if page == "📊 Dashboard":
            render_dashboard(db, profile, is_demo)
        elif page == "📝 Registro do Dia":
            render_daily_log(db)
        elif page == "👤 Meu Perfil":
            render_profile(db, profile)
