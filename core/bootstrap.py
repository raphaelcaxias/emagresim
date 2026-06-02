import streamlit as st
import logging

logger = logging.getLogger(__name__)

def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "home"

@st.cache_resource(show_spinner=False)
def init_services():
    from core.database import AppDatabase
    from core.nutrition import NutritionService
    from core.analytics import AnalyticsService
    from core.gamification import GamificationSystem
    from core.payment import PaymentService
    
    try:
        db = AppDatabase()
        logger.info("Serviços inicializados via Bootstrap.")
        return {
            "db": db,
            "nutrition": NutritionService(db),
            "analytics": AnalyticsService(db),
            "gamification": GamificationSystem(db),
            "payment": PaymentService()
        }
    except Exception as e:
        logger.critical(f"Falha fatal na inicialização: {e}")
        return None
