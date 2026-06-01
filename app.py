import streamlit as st
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Garante que session_state existe ANTES de qualquer import
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

try:
    from core.database import AppDatabase
    from core.nutrition import NutritionService
    from core.behavior import BehaviorEngine
    from core.payments import PaymentService
    from views import (
        render_login, render_onboarding, render_dashboard, 
        render_meals, render_weight, render_behavior, render_subscription
    )
    IMPORTS_OK = True
except Exception as e:
    st.error(f"❌ Erro na inicialização: {e}")
    IMPORTS_OK = False

st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪", 
    layout="wide", 
    initial_sidebar_state="expanded"
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
        st.error(f"Erro ao carregar serviços: {e}")
        return None

def main():
    if not IMPORTS_OK:
        st.stop()
    
    services = init_services()
    if not services:
        st.stop()
    
    # Verifica se usuário está logado
    if st.session_state.user is None:
        # Tela de Login
        render_login(services["db"])
    else:
        # Usuário logado
        user = st.session_state.user
        
        # Sidebar
        with st.sidebar:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="margin: 0;">💪 EmagreSim</h2>
                <p style="color: #9ca3af; font-size: 0.75rem;">v2.0</p>
            </div>
            """, unsafe_allow_html=True)
            
            plan_badge = "👑 PRO" if user.get("plan") != "free" else "🎁 GRÁTIS"
            plan_color = "#f59e0b" if user.get("plan") != "free" else "#6b7280"
            st.markdown(f"""
            <div style="background: {plan_color}; color: white; padding: 0.5rem; border-radius: 12px; text-align: center; font-weight: 600; margin-bottom: 1rem;">
                {plan_badge}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"👤 {user.get('name', 'Usuário')}")
            st.markdown(f"📧 {user.get('email', '')}")
            st.markdown("---")
            
            if user.get("onboarded"):
                page = st.radio(
                    "📱 Navegação", 
                    ["📊 Dashboard", "🍴 Refeições", "⚖️ Peso", "🧠 Perfil", "💳 Upgrade"],
                    index=0
                )
                
                st.markdown("---")
                
                if st.button("🚪 Sair", use_container_width=True):
                    st.session_state.user = None
                    st.rerun()
            else:
                page = "onboarding"
        
        # Renderização das páginas
        try:
            if not user.get("onboarded"):
                if render_onboarding(services["nutrition"], user):
                    st.rerun()
            else:
                if page == "📊 Dashboard":
                    render_dashboard(services["nutrition"], services["behavior"], user)
                elif page == "🍴 Refeições":
                    render_meals(services["nutrition"], services["behavior"], user)
                elif page == "⚖️ Peso":
                    render_weight(services["nutrition"], user)
                elif page == "🧠 Perfil":
                    render_behavior(services["behavior"], user)
                elif page == "💳 Upgrade":
                    render_subscription(services["payment"], user)
        except Exception as e:
            logger.error(f"Erro ao renderizar página: {e}")
            st.error(f"Ocorreu um erro: {str(e)}")
            if st.button("🔄 Recarregar"):
                st.rerun()

if __name__ == "__main__":
    main()
