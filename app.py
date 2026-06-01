import streamlit as st
import logging
import os
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    page_title="EmagreSim - Transforme sua jornada em um jogo!",
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

def init_session_state():
    """Inicializa TODAS as variáveis de sessão"""
    if "user" not in st.session_state:
        st.session_state.user = None
    
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

def main():
    if not IMPORTS_OK:
        st.stop()
    
    init_session_state()
    services = init_services()
    
    if not services:
        st.error("Não foi possível inicializar os serviços.")
        st.stop()
    
    # Verifica se usuário está logado
    if st.session_state.user is None:
        # Tela de Login
        if render_login(services["db"]):
            # Após login bem-sucedido, verifica se é primeiro acesso
            if st.session_state.user and not st.session_state.user.get("onboarded"):
                st.rerun()
            elif st.session_state.user:
                st.rerun()
    else:
        # Usuário logado
        user = st.session_state.user
        
        # Sidebar
        with st.sidebar:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="margin: 0;">💪 EmagreSim</h2>
                <p style="color: #9ca3af; font-size: 0.75rem;">v2.0</p>
                <div style="margin-top: 1rem; padding: 0.5rem; background: #374151; border-radius: 8px;">
                    <p style="margin: 0; font-size: 0.875rem;">👤 {user.get('name', 'Usuário')}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: #9ca3af;">{user.get('email', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            plan_badge = "👑 PRO" if user.get("plan") != "free" else "🎁 GRÁTIS"
            plan_color = "#f59e0b" if user.get("plan") != "free" else "#6b7280"
            st.markdown(f"""
            <div style="background: {plan_color}; color: white; padding: 0.5rem; border-radius: 12px; text-align: center; font-weight: 600;">
                {plan_badge}
            </div>
            """, unsafe_allow_html=True)
            
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
