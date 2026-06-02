import streamlit as st
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== INICIALIZAÇÃO GLOBAL ====================
def init_session_state():
    """Garante que o estado inicial exista antes de qualquer renderização"""
    if "mock_db" not in st.session_state:
        st.session_state.mock_db = {
            "meals": [], 
            "weights": [], 
            "achievements": [], 
            "users": {
                # Usuário Demo pré-configurado para garantir que o botão funcione sempre
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

# Executa a inicialização imediatamente
init_session_state()

# ==================== IMPORTS ====================
try:
    from core.database import AppDatabase
    from core.nutrition import NutritionService
    from core.behavior import BehaviorEngine
    from core.payments import PaymentService
    from views import (
        render_login, render_onboarding, render_dashboard,
        render_meals, render_weight, render_behavior, render_subscription,
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
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# ==================== CACHE DE SERVIÇOS ====================
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

# ==================== SIDEBAR OTIMIZADA ====================
def render_sidebar(user):
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="margin: 0; font-size: 1.5rem;">💪 EmagreSim</h1>
        </div>
        """, unsafe_allow_html=True)
        
        plan_badge = "👑 PRO" if user.get("plan") != "free" else "🎁 GRÁTIS"
        plan_color = "#f59e0b" if user.get("plan") != "free" else "#6b7280"
        st.markdown(f"""
        <div style="background: {plan_color}15; border-radius: 12px; padding: 0.5rem; text-align: center; margin-bottom: 1.5rem;">
            <span style="color: {plan_color}; font-weight: 600;">{plan_badge}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if user.get("onboarded"):
            pages = [
                ("📊 Dash", "dashboard"),
                ("🍴 Meals", "meals"),
                ("⚖️ Peso", "weight"),
                ("🧠 Perfil", "profile"),
                ("💳 Upgrade", "upgrade")
            ]
                        for label, page_key in pages:
                is_active = st.session_state.current_page == page_key
                if st.button(label, use_container_width=True, type="primary" if is_active else "secondary"):
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
        
        return "onboarding"

# ==================== MAIN ====================
def main():
    if not IMPORTS_OK:
        st.stop()
    
    load_css()
    services = init_services()
    if not services:
        st.error("Erro crítico ao carregar os serviços do app.")
        st.stop()
    
    user = st.session_state.user
    
    # ========== TELA DE LOGIN (Centralizada) ==========
    if user is None:
        _, col_central, _ = st.columns([1, 2, 1])
        with col_central:
            render_login(services["db"])
        return
    
    # ========== SIDEBAR & NAVEGAÇÃO ==========
    current_page = render_sidebar(user)
    
    # ========== ONBOARDING (Centralizado) ==========
    if not user.get("onboarded"):
        _, col_central, _ = st.columns([1, 2, 1])
        with col_central:
            if render_onboarding(services["nutrition"], user):
                st.rerun()
        return    
    # ========== ROTEAMENTO DE PÁGINAS ==========
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