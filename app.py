import streamlit as st
import logging
from config import APP_TITLE, APP_ICON, DEMO_USER_EMAIL, DEMO_USER_PASS
from core.infrastructure.database_repo import DatabaseRepository
from core.services.nutrition_service import NutritionService
from core.services.analytics_service import AnalyticsService
from core.services.gamification_service import GamificationService
from core.services.auth_service import AuthService
from views.auth_views import render_login
from views.dashboard_views import render_dashboard
from views.meals_views import render_meals
from views.weight_views import render_weight
from views.stats_views import render_stats
from views.profile_views import render_profile
from views.subscription_views import render_subscription

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")

def load_css():
    try:
        with open("assets/style.css") as f: st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except: pass

def init_session_state():
    if "user" not in st.session_state: st.session_state.user = None
    if "current_page" not in st.session_state: st.session_state.current_page = "dashboard"

def init_services():
    try:
        db = DatabaseRepository()
        return {
            "db": db,
            "nutrition": NutritionService(db),
            "analytics": AnalyticsService(db),
            "gamification": GamificationService(db),
            "auth": AuthService(db)
        }
    except Exception as e:
        logger.error(f"Erro fatal na instanciação dos serviços: {e}")
        return None

def render_sidebar(user):
    with st.sidebar:
        st.markdown(f'<h2 style="text-align:center;color:#0891b2;margin-bottom:0.5rem;">{APP_ICON} {APP_TITLE}</h2>', unsafe_allow_html=True)
        plan_badge = " PRO" if user.get("plan") != "free" else "🎁 GRATUITO"
        st.markdown(f'<div style="text-align:center;margin-bottom:1.5rem;"><span style="background:#0891b2;color:white;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.75rem;font-weight:bold;">{plan_badge}</span></div>', unsafe_allow_html=True)
                pages = [
            ("📊 Dashboard", "dashboard"), 
            ("🍴 Registro Alimentar", "meals"), 
            ("⚖️ Evolução de Peso", "weight"), 
            (" Inteligência Analítica", "stats"), 
            ("👤 Perfil de Metas", "profile"), 
            ("👑 Tornar-se Pro", "subscription")
        ]
        
        for label, page_key in pages:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()
                
        st.markdown("---")
        st.button("🚪 Sair do Sistema", use_container_width=True, on_click=lambda: st.session_state.update({"user": None, "current_page": "dashboard"}))

def main():
    load_css()
    init_session_state()
    
    services = init_services()
    if not services:
        st.error("Falha ao inicializar o ecossistema interno.")
        st.stop()
        
    user = st.session_state.user
    if user is None:
        _, col_central, _ = st.columns([1, 2, 1])
        with col_central: render_login(services["auth"])
        return

    if not user.get("current_weight") or not user.get("height"):
        _, col_central, _ = st.columns([1, 2, 1])
        with col_central:
            st.markdown('<div class="fade-in">', unsafe_allow_html=True)
            st.header("Configuração Inicial de Saúde")
            st.caption("Insira seus dados reais básicos para o cálculo do gasto calórico diário.")
            
            weight = st.number_input("Peso Atual (kg)", min_value=30.0, max_value=250.0, value=75.0)
            height = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170)
            age = st.number_input("Idade", min_value=12, max_value=100, value=25)
            goal_w = st.number_input("Meta de Peso Alvo (kg)", min_value=30.0, max_value=250.0, value=70.0)
            
            if st.button("Gravar Configurações e Acessar", use_container_width=True, type="primary"):
                init_data = {"current_weight": weight, "height": height, "age": age, "goal_weight": goal_w}
                services["auth"].update_profile(init_data)
                user.update(init_data)
                st.session_state.user = user
                st.rerun()            st.markdown('</div>', unsafe_allow_html=True)
        return

    render_sidebar(user)
    current_page = st.session_state.current_page
    
    if current_page == "dashboard": render_dashboard(services["nutrition"], services["gamification"], user)
    elif current_page == "meals": render_meals(services["nutrition"], user)
    elif current_page == "weight": render_weight(services["nutrition"], user)
    elif current_page == "stats": render_stats(services["nutrition"], services["analytics"])
    elif current_page == "profile": render_profile(services["auth"], user)
    elif current_page == "subscription": render_subscription(services["auth"], user)

if __name__ == "__main__": main()