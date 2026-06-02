import streamlit as st
import logging
from core.database import AppDatabase
from core.nutrition import NutritionService
from core.analytics import AnalyticsService
from core.gamification import GamificationSystem
from core.payments import PaymentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None

init_session_state()

@st.cache_resource
def init_services():
    try:
        db = AppDatabase()
        return {
            "db": db,
            "nutrition": NutritionService(db),
            "analytics": AnalyticsService(db),
            "gamification": GamificationSystem(db),
            "payment": PaymentService()
        }
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        return None

def main():
    load_css()
    services = init_services()
    if not services:
        st.error("Falha ao inicializar serviços.")
        st.stop()
    
    user = st.session_state.user
    
    # Tela de Login (se não logado)
    if user is None:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;margin-top:2rem;"><h1 style="font-size:2.5rem;color:#0891b2;">💪 EmagreSim</h1><p style="color:#64748b;">Monitoramento de saúde baseado em dados</p></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Acessar Conta", "Criar Conta"])
        
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Senha", type="password", key="login_pass")
            if st.button("Entrar", use_container_width=True, type="primary"):
                user_data = services["db"].get_user(email, password)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Credenciais incorretas.")
            
            st.markdown('<div style="text-align:center;margin:1rem 0;color:#64748b;">ou</div>', unsafe_allow_html=True)
            if st.button("Modo Demonstração", use_container_width=True):
                st.session_state.user = services["db"].get_user("demo@emagresim.com", "demo")
                st.rerun()
        
        with tab2:
            new_email = st.text_input("Email", key="reg_email")
            new_name = st.text_input("Nome", key="reg_name")
            new_password = st.text_input("Senha", type="password", key="reg_pass")
            if st.button("Cadastrar", use_container_width=True, type="primary"):
                if services["db"].create_user(new_email, new_password, new_name):
                    st.success("Conta criada! Faça login.")
                else:
                    st.error("Email já cadastrado.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Usuário logado - mostra dashboard básico e navegação
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown(f'<h1 style="color:#0891b2;">Bem-vindo(a), {user.get("name", "Usuário")}!</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b;">Use o menu lateral para navegar entre as funcionalidades.</p>', unsafe_allow_html=True)
    
    # Cards de resumo rápido
    today_summary = services["nutrition"].get_daily_summary()
    streak = services["gamification"].calculate_streak()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="data-card"><div class="data-value">{today_summary["calories"]}</div><div class="data-label">Calorias Hoje</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="data-card"><div class="data-value">{streak}</div><div class="data-label">Dias Seguidos</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="data-card"><div class="data-value">{user.get("current_weight", "--")}</div><div class="data-label">Peso Atual</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("👈 Use o menu lateral para acessar todas as funcionalidades!")
    
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
