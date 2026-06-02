import streamlit as st
import logging
from datetime import datetime

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EmagreSim.App")

st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização de estado
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# Inicialização de serviços com cache
@st.cache_resource(show_spinner=False)
def init_services():
    from core.database import AppDatabase
    from core.nutrition import NutritionService
    from core.analytics import AnalyticsService
    from core.gamification import GamificationSystem
    from core.payment import PaymentService
    
    try:
        db = AppDatabase()
        logger.info("Serviços inicializados com sucesso.")
        return {
            "db": db,
            "nutrition": NutritionService(db),
            "analytics": AnalyticsService(db),
            "gamification": GamificationSystem(db),
            "payment": PaymentService()
        }
    except Exception as e:
        logger.critical(f"Falha fatal na inicialização dos serviços: {e}")
        return None

def main():
    # Carregamento de CSS
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"Não foi possível carregar style.css: {e}")

    services = init_services()
    if not services:
        st.error("❌ Falha ao inicializar o sistema. Verifique os logs.")
        st.stop()

    # Roteamento
    if st.session_state.user is None:
        logger.debug("Usuário não autenticado. Renderizando login.")
        from views.login import render_login
        render_login(services["db"])
        return

    # Sidebar (Fase 3)
    from views.sidebar import render_sidebar
    render_sidebar(services)

    page = st.session_state.page
    logger.debug(f"Navegando para: {page}")

    try:
        if page == "home":
            from views.home import render_home
            render_home(services, st.session_state.user)
        elif page == "dashboard":
            from views.dashboard import render_dashboard
            render_dashboard(services, st.session_state.user)
        elif page == "meals":
            from views.meals import render_meals
            render_meals(services, st.session_state.user)
        elif page == "weight":
            from views.weight import render_weight
            render_weight(services, st.session_state.user)
        elif page == "analysis":
            from views.analysis import render_analysis
            render_analysis(services, st.session_state.user)
        elif page == "profile":
            from views.profile import render_profile
            render_profile(services, st.session_state.user)
    except Exception as e:
        logger.error(f"Erro ao renderizar a página '{page}': {e}")
        st.error(f"Ocorreu um erro ao carregar a página. Verifique os logs.")

if __name__ == "__main__":
    main()
