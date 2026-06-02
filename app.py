import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_session_state():
    if "mock_db" not in st.session_state:
        st.session_state.mock_db = {
            "meals": [],
            "weights": [],
            "achievements": [],
            "users": {
                "demo@emagresim.com": {
                    "password": "demo123",
                    "name": "Usuário Demo",
                    "email": "demo@emagresim.com",
                    "is_demo": True
                }
            }
        }
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"


init_session_state()

try:
    from core.database import AppDatabase
    from core.nutrition import NutritionService
    from core.behavior import BehaviorEngine
    from core.payments import PaymentService
    from views import (
        render_login,
        render_onboarding,
        render_dashboard,
        render_meals,
        render_weight,
        render_behavior,
        render_subscription,
        load_css
    )
    IMPORTS_OK = True
except Exception as e:
    st.error(f"❌ Erro de Importação: {e}")
    IMPORTS_OK = False
st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)


@st.cache_resource
def init_services():
    try:
        db = AppDatabase()
        return {
            "db": db,
            "nutrition": NutritionService(db),
            "behavior": BehaviorEngine(db),
            "payment": PaymentService()
        }
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {e}")
        return None


def render_sidebar(user):
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;margin-bottom:1.5rem;">'
            '<h1 style="margin:0;font-size:1.5rem;">💪 EmagreSim</h1>'
            '</div>',
            unsafe_allow_html=True
        )

        is_pro = user.get("plan") != "free"
        plan_badge = "👑 PRO" if is_pro else "🎁 GRÁTIS"
        plan_color = "#f59e0b" if is_pro else "#6b7280"

        st.markdown(
            f'<div style="background:{plan_color}15;border-radius:12px;'
            f'padding:0.5rem;text-align:center;margin-bottom:1.5rem;">'
            f'<span style="color:{plan_color};font-weight:600;">{plan_badge}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        if not user.get("onboarded"):            return "onboarding"

        pages = [
            ("📊 Dash", "dashboard"),
            ("🍴 Meals", "meals"),
            ("⚖️ Peso", "weight"),
            ("🧠 Perfil", "profile"),
            ("💳 Upgrade", "upgrade"),
        ]

        for label, page_key in pages:
            is_active = st.session_state.current_page == page_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, use_container_width=True, type=btn_type):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        if user.get("weight"):
            st.caption(f"⚡ Peso: {user['weight']} kg")

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.user = None
            st.session_state.current_page = "dashboard"
            st.rerun()

        return st.session_state.current_page


def main():
    if not IMPORTS_OK:
        st.stop()

    load_css()

    services = init_services()
    if not services:
        st.error("Erro crítico ao carregar os serviços do app.")
        st.stop()

    user = st.session_state.user

    if user is None:
        _, col_central, _ = st.columns([1, 2, 1])
        with col_central:
            render_login(services["db"])
        return

    current_page = render_sidebar(user)
    if not user.get("onboarded"):
        _, col_central, _ = st.columns([1, 2, 1])
        with col_central:
            if render_onboarding(services["nutrition"], user):
                st.rerun()
        return

    if current_page == "dashboard":
        render_dashboard(services["nutrition"], services["behavior"], user)
    elif current_page == "meals":
        render_meals(services["nutrition"], services["behavior"], user)
    elif current_page == "weight":
        render_weight(services["nutrition"], user)
    elif current_page == "profile":
        render_behavior(services["behavior"], user)
    elif current_page == "upgrade":
        render_subscription(services["payment"], user)


if __name__ == "__main__":
    main()