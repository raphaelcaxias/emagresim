import streamlit as st
import logging
from core.database import AppDatabase
from core.nutrition import NutritionService
from core.analytics import AnalyticsService
from core.gamification import GamificationSystem
from core.payments import PaymentService
from pages.Dashboard import render_dashboard
from pages.Registro_Refeições import render_meals
from pages.Evolução_Peso import render_weight
from pages.Análise_Estátistica import render_stats
from pages.Perfil import render_profile

# Configuração global
st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do estado
def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

init_session_state()

# Carregamento dos serviços
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
        logger.error(f"Erro na inicialização dos serviços: {e}")
        return None

# Renderização da sidebar
def render_sidebar(user):
    with st.sidebar:
        st.markdown('<h2 style="text-align:center;color:#0891b2;margin-bottom:0.5rem;">💪 EmagreSim</h2>', unsafe_allow_html=True)
        plan_badge = "👑 PRO" if user.get("plan") != "free" else "🎁 GRATUITO"
        st.markdown(f'<div style="text-align:center;margin-bottom:1.5rem;"><span style="background:#0891b2;color:white;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.75rem;font-weight:bold;">{plan_badge}</span></div>', unsafe_allow_html=True)
        
        pages = [
            ("📊 Dashboard", "dashboard"), 
            ("🍴 Registro Alimentar", "meals"), 
            ("⚖️ Evolução de Peso", "weight"), 
            ("📈 Análise Estatística", "stats"), 
            ("👤 Perfil", "profile")
        ]
        
        for label, page_key in pages:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()
                
        st.markdown("---")
        st.button("🚪 Sair do Sistema", use_container_width=True, on_click=lambda: st.session_state.update({"user": None, "current_page": "dashboard"}))

# Main
def main():
    services = init_services()
    if not services:
        st.error("Falha ao inicializar o ecossistema interno.")
        st.stop()
        
    user = st.session_state.user
    if user is None:
        st.switch_page("pages/Dashboard.py")
        return
    
    if not user.get("current_weight") or not user.get("height"):
        st.switch_page("pages/Perfil.py")
        return

    render_sidebar(user)
    current_page = st.session_state.current_page
    
    if current_page == "dashboard": 
        render_dashboard(services["nutrition"], services["gamification"], user)
    elif current_page == "meals": 
        render_meals(services["nutrition"], user)
    elif current_page == "weight": 
        render_weight(services["nutrition"], user)
    elif current_page == "stats": 
        render_stats(services["nutrition"], services["analytics"])
    elif current_page == "profile": 
        render_profile(services["payment"], user)

if __name__ == "__main__":
    main()
