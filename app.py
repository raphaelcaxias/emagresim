import streamlit as st
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from core.database import AppDatabase
    from core.nutrition import NutritionService
    from core.behavior import BehaviorEngine
    from core.payments import PaymentService
    from views import (
        render_onboarding, render_dashboard, render_meals, 
        render_weight, render_behavior, render_subscription, load_css
    )
    IMPORTS_OK = True
    logger.info("✅ Todos os módulos importados com sucesso")
except Exception as e:
    st.error(f"❌ Erro na inicialização: {str(e)}")
    logger.error(f"Erro de importação: {e}")
    IMPORTS_OK = False

st.set_page_config(
    page_title="EmagreSim - Sua Jornada Fitness Gamificada",
    page_icon="💪", layout="wide", initial_sidebar_state="expanded"
)

@st.cache_resource
def init_services():
    try:
        db = AppDatabase()
        nutrition = NutritionService(db)
        behavior = BehaviorEngine(db)
        payment = PaymentService()
        logger.info("✅ Serviços inicializados")
        return {"db": db, "nutrition": nutrition, "behavior": behavior, "payment": payment}
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {e}")
        st.error(f"Erro ao carregar serviços: {e}")
        return None

def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = {
            "id": "demo_user_" + str(hash(os.urandom(8))),
            "name": "Visitante", "plan": "free", "onboarded": False,
            "weight": None, "height": None, "age": None, "goal_weight": None,
            "app_url": os.getenv("STREAMLIT_APP_URL", "https://emagresim.streamlit.app")  # ✅ FIX
        }
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

def main():
    if not IMPORTS_OK:
        st.stop()
    init_session_state()
    services = init_services()
    if not services:  # ✅ FIX: Tratamento de None
        st.error("Não foi possível inicializar os serviços. Verifique os logs.")
        st.stop()
    db = services["db"]
    nutrition = services["nutrition"]
    behavior = services["behavior"]
    payment = services["payment"]
    user = st.session_state.user
    with st.sidebar:
        st.markdown("""<div style="text-align: center; margin-bottom: 2rem;"><h2 style="margin: 0;">💪 EmagreSim</h2><p style="color: #9ca3af; font-size: 0.75rem;">v2.0</p></div>""", unsafe_allow_html=True)
        plan_badge = "👑 PRO" if user.get("plan") != "free" else "🎁 GRÁTIS"
        plan_color = "#f59e0b" if user.get("plan") != "free" else "#6b7280"
        st.markdown(f"""<div style="background: {plan_color}20; border-radius: 12px; padding: 0.5rem; text-align: center; margin-bottom: 1.5rem;"><span style="color: {plan_color}; font-weight: 600;">{plan_badge}</span></div>""", unsafe_allow_html=True)
        if user.get("onboarded"):
            page = st.radio("📱 Navegação", ["📊 Dashboard", "🍴 Refeições", "⚖️ Peso", "🧠 Perfil", "💳 Upgrade"], index=0, key="nav_menu")
            st.markdown("---")
            if st.button("🗑️ Resetar Demo", use_container_width=True):
                st.session_state.clear()
                st.rerun()
            if user.get("weight"):
                st.caption(f"⚡ Peso atual: {user['weight']} kg")
            if user.get("streak", 0) > 0:
                st.caption(f"🔥 Sequência: {user.get('streak', 0)} dias")
        else:
            page = "onboarding"
    try:
        if not user.get("onboarded"):
            if render_onboarding(nutrition, user):
                st.rerun()
        else:
            if page == "📊 Dashboard": render_dashboard(nutrition, behavior, user)
            elif page == "🍴 Refeições": render_meals(nutrition, behavior, user)
            elif page == "⚖️ Peso": render_weight(nutrition, user)
            elif page == "🧠 Perfil": render_behavior(behavior, user)
            elif page == "💳 Upgrade": render_subscription(payment, user)
    except Exception as e:
        logger.error(f"Erro ao renderizar página: {e}")
        st.error(f"Ocorreu um erro: {str(e)}")
        st.info("Tente recarregar a página ou entrar em contato com o suporte.")

if __name__ == "__main__":
    main()
