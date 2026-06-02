import streamlit as st
import logging
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO E LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EmagreSim")

st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "EmagreSim v2.0 - Monitoramento nutricional baseado em dados"
    }
)

# ============================================================
# ESTADO GLOBAL
# ============================================================
def init_session_state():
    """Inicializa variáveis de sessão necessárias."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "mock_db" not in st.session_state:
        st.session_state.mock_db = {
            "users": {
                "demo@emagresim.com": {
                    "password": "demo",
                    "name": "Usuário Demo",
                    "email": "demo@emagresim.com",
                    "plan": "free",
                    "current_weight": 75.0,
                    "goal_weight": 70.0,
                    "height": 170,
                    "age": 30,
                    "activity_level": "moderate",
                    "goal": "lose"
                }
            },
            "meals": [],
            "weights": [],
            "achievements": []
        }

init_session_state()

# ============================================================
# CARREGAMENTO DE CSS
# ============================================================
def load_css():
    """Carrega estilos customizados."""
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"CSS não carregado: {e}")

# ============================================================
# INICIALIZAÇÃO DE SERVIÇOS (com cache)
# ============================================================
@st.cache_resource(show_spinner=False)
def init_services():
    """Inicializa todos os serviços da aplicação."""
    try:
        from core.database import AppDatabase
        from core.nutrition import NutritionService
        from core.analytics import AnalyticsService
        from core.gamification import GamificationSystem
        from core.payment import PaymentService
        
        logger.info("🚀 Inicializando serviços...")
        db = AppDatabase()
        
        services = {
            "db": db,
            "nutrition": NutritionService(db),
            "analytics": AnalyticsService(db),
            "gamification": GamificationSystem(db),
            "payment": PaymentService()
        }
        
        logger.info("✅ Serviços inicializados com sucesso")
        return services
        
    except Exception as e:
        logger.critical(f" Falha fatal na inicialização: {e}")
        return None

# ============================================================
# FUNÇÕES DE SEGURANÇA (wrappers para evitar KeyError)
# ============================================================
def get_daily_summary_safe(nutrition_service):
    """Wrapper seguro para resumos diários."""
    default = {"calories": 0, "count": 0, "meals": [], "proteins": 0, "carbs": 0, "fats": 0}
    try:
        summary = nutrition_service.get_daily_summary()
        if not summary:
            return default
        return {
            "calories": int(summary.get("calories", summary.get("cal", 0))),
            "count": int(summary.get("count", 0)),
            "meals": summary.get("meals", []),
            "proteins": float(summary.get("proteins", summary.get("protein", 0))),
            "carbs": float(summary.get("carbs", 0)),
            "fats": float(summary.get("fats", 0)),
        }
    except Exception as e:
        logger.error(f"Erro get_daily_summary_safe: {e}")
        return default

def get_streak_safe(gamification_service):
    """Wrapper seguro para cálculo de streak."""
    try:
        streak = gamification_service.calculate_streak()
        return int(streak) if streak else 0
    except Exception as e:
        logger.error(f"Erro get_streak_safe: {e}")
        return 0

# ============================================================
# ROTEAMENTO DE PÁGINAS
# ============================================================
def render_page(services, page_name):
    """Renderiza a página solicitada."""
    try:
        if page_name == "home":
            from views.home import render_home
            render_home(services, st.session_state.user)
            
        elif page_name == "dashboard":
            from views.dashboard import render_dashboard
            render_dashboard(services, st.session_state.user)
            
        elif page_name == "meals":
            from views.meals import render_meals
            render_meals(services, st.session_state.user)
            
        elif page_name == "weight":
            from views.weight import render_weight
            render_weight(services, st.session_state.user)
            
        elif page_name == "analysis":
            from views.analysis import render_analysis
            render_analysis(services, st.session_state.user)
            
        elif page_name == "profile":
            from views.profile import render_profile
            render_profile(services, st.session_state.user)
            
        else:
            st.warning(f"Página '{page_name}' não encontrada.")
            
    except ImportError as e:
        logger.error(f"ImportError na página '{page_name}': {e}")
        st.error(f"📦 Módulo '{page_name}' não encontrado. Verifique se o arquivo views/{page_name}.py existe.")
    except Exception as e:
        logger.error(f"Erro ao renderizar '{page_name}': {e}")
        st.error(f"Ocorreu um erro ao carregar a página.")

# ============================================================
# MAIN
# ============================================================
def main():
    """Função principal da aplicação."""
    load_css()
    
    # Inicializa serviços
    services = init_services()
    if not services:
        st.error("❌ Falha ao inicializar o sistema. Verifique os logs.")
        st.stop()
    
    # Roteamento principal
    user = st.session_state.user
    
    if user is None:
        # Tela de Login
        try:
            from views.login import render_login
            render_login(services["db"])
        except Exception as e:
            logger.error(f"Erro ao carregar login: {e}")
            st.error("Erro ao carregar tela de login.")
        return
    
    # Sidebar (para usuários logados)
    try:
        from views.sidebar import render_sidebar
        render_sidebar(services)
    except Exception as e:
        logger.error(f"Erro ao carregar sidebar: {e}")
    
    # Renderiza a página atual
    page = st.session_state.page
    logger.debug(f"Navegando para: {page}")
    render_page(services, page)

if __name__ == "__main__":
    main()
