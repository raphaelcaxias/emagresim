import streamlit as st
import logging
from datetime import datetime
from core.database import AppDatabase
from core.nutrition import NutritionService
from core.analytics import AnalyticsService
from core.gamification import GamificationSystem
from core.payments import PaymentService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="EmagreSim - Sua Jornada Fitness",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/seu-usuario/emagresim',
        'Report a bug': 'https://github.com/seu-usuario/emagresim/issues',
        'About': "# EmagreSim v2.0\nApp de monitoramento fitness baseado em dados."
    }
)

st.markdown("""
<style>
    .fade-in { animation: fadeIn 0.3s ease-in; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    
    .main-header { 
        background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .data-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .data-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    .data-value { font-size: 2rem; font-weight: 700; color: #0891b2; line-height: 1.2; }
    .data-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.25rem; }
    
    .stButton > button { 
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    .progress-container { 
        background: #e2e8f0; 
        border-radius: 9999px; 
        height: 0.75rem; 
        overflow: hidden; 
        margin: 0.5rem 0;
    }
    .progress-bar { 
        background: linear-gradient(90deg, #0891b2, #06b6d4); 
        height: 100%; 
        transition: width 0.5s ease;
    }
    
    [data-testid="stSidebar"] { background: #1e293b; }
    [data-testid="stSidebar"] * { color: #f1f5f9; }
</style>
""", unsafe_allow_html=True)


def load_css_file():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass


def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "home"


@st.cache_resource(show_spinner="Inicializando serviços...")
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
        logger.error(f"❌ Erro fatal na inicialização: {e}")
        return None


def get_daily_summary_safe(nutrition_service):
    """Retorna summary diário de forma segura (compatível com várias estruturas)"""
    try:
        summary = nutrition_service.get_daily_summary()
        if not summary:
            return {"calories": 0, "count": 0, "meals": [], "proteins": 0, "carbs": 0, "fats": 0}
        
        # Normaliza chaves possíveis (calories ou cal)
        calories = summary.get("calories", summary.get("cal", 0))
        count = summary.get("count", 0)
        meals = summary.get("meals", [])
        proteins = summary.get("proteins", summary.get("p", 0))
        carbs = summary.get("carbs", summary.get("c", 0))
        fats = summary.get("fats", summary.get("g", 0))
        
        return {
            "calories": int(calories) if calories else 0,
            "count": int(count) if count else 0,
            "meals": meals or [],
            "proteins": float(proteins) if proteins else 0,
            "carbs": float(carbs) if carbs else 0,
            "fats": float(fats) if fats else 0,
        }
    except Exception as e:
        logger.error(f"Erro em get_daily_summary_safe: {e}")
        return {"calories": 0, "count": 0, "meals": [], "proteins": 0, "carbs": 0, "fats": 0}


def get_streak_safe(gamification_service):
    """Retorna streak de forma segura"""
    try:
        streak = gamification_service.calculate_streak()
        return int(streak) if streak else 0
    except Exception as e:
        logger.error(f"Erro em get_streak_safe: {e}")
        return 0


def get_welcome_message() -> str:
    hour = datetime.now().hour
    if hour < 6:
        return "🌙 Boa madrugada! Descanso é importante."
    elif hour < 12:
        return "☀️ Bom dia! Energia para começar!"
    elif hour < 18:
        return "🌤️ Boa tarde! Mantenha o foco!"
    else:
        return "🌙 Boa noite! Revise suas conquistas!"


def check_onboarding_complete(user: dict) -> bool:
    required_fields = ["current_weight", "height", "age", "goal_weight"]
    return all(user.get(field) is not None for field in required_fields)


def render_login_page(services: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header" style="text-align: center;">
        <h1 style="margin: 0; font-size: 3rem;">💪 EmagreSim</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            Transforme dados em resultados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Acessar Conta", "📝 Criar Conta"])
    
    with tab1:
        st.markdown("### Login")
        email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", key="login_pass", placeholder="••••••••")
        
        if st.button("Entrar", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Preencha email e senha.")
            else:
                try:
                    user_data = services["db"].get_user(email, password)
                    if user_data:
                        st.session_state.user = user_data
                        st.success(f"Bem-vindo, {user_data.get('name', 'Usuário')}!")
                        st.rerun()
                    else:
                        st.error("Email ou senha incorretos.")
                except Exception as e:
                    logger.error(f"Erro no login: {e}")
                    st.error(f"Erro ao fazer login: {str(e)}")
        
        st.markdown("---")
        
        if st.button("🎮 Entrar no Modo Demonstração", use_container_width=True):
            try:
                demo_user = {
                    "email": "demo@emagresim.com",
                    "password": "demo",
                    "name": "Usuário Demo",
                    "plan": "free",
                    "current_weight": 75.0,
                    "goal_weight": 70.0,
                    "height": 170,
                    "age": 30,
                    "activity_level": "moderate",
                    "goal": "lose"
                }
                
                if "mock_db" not in st.session_state:
                    st.session_state.mock_db = {"users": {}, "meals": [], "weights": [], "achievements": []}
                if "users" not in st.session_state.mock_db:
                    st.session_state.mock_db["users"] = {}
                
                st.session_state.mock_db["users"]["demo@emagresim.com"] = demo_user
                st.session_state.user = demo_user
                
                st.success("✅ Modo demonstração ativado!")
                st.rerun()
            except Exception as e:
                logger.error(f"Erro no modo demo: {e}")
                st.error(f"Erro ao ativar modo demo: {str(e)}")
    
    with tab2:
        st.markdown("### Nova Conta")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Nome completo", key="reg_name", placeholder="João Silva")
            new_email = st.text_input("Email", key="reg_email", placeholder="joao@email.com")
        with col2:
            new_password = st.text_input("Senha", type="password", key="reg_pass", placeholder="Mínimo 6 caracteres")
            confirm_password = st.text_input("Confirmar senha", type="password", key="reg_confirm", placeholder="Repita a senha")
        
        if st.button("Cadastrar", use_container_width=True, type="primary"):
            if not all([new_name, new_email, new_password, confirm_password]):
                st.error("Preencha todos os campos.")
            elif len(new_password) < 6:
                st.error("Senha deve ter pelo menos 6 caracteres.")
            elif new_password != confirm_password:
                st.error("As senhas não coincidem.")
            elif "@" not in new_email:
                st.error("Email inválido.")
            else:
                try:
                    if services["db"].create_user(new_email, new_password, new_name):
                        st.success("✅ Conta criada! Faça login agora.")
                    else:
                        st.error("❌ Email já cadastrado.")
                except Exception as e:
                    logger.error(f"Erro no cadastro: {e}")
                    st.error(f"Erro ao criar conta: {str(e)}")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.85rem;">
        <p>🔒 Seus dados estão protegidos e nunca serão compartilhados.</p>
        <p>EmagreSim v2.0 • Monitoramento baseado em evidências</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar(user: dict, services: dict):
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #334155; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: #06b6d4;">💪 EmagreSim</h2>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #94a3b8;">v2.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        plan = user.get("plan", "free")
        if plan == "pro":
            st.markdown('<div style="background: linear-gradient(135deg, #f59e0b, #ef4444); color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: 600; margin-bottom: 1rem;">👑 PLANO PRO</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #334155; color: #94a3b8; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: 600; margin-bottom: 1rem;">🎁 GRATUITO</div>', unsafe_allow_html=True)
        
        st.markdown(f"**👤 {user.get('name', 'Usuário')}**")
        st.caption(f"📧 {user.get('email', '')}")
        
        # ✅ CORREÇÃO: Uso de funções seguras
        today_summary = get_daily_summary_safe(services["nutrition"])
        streak = get_streak_safe(services["gamification"])
        
        calories = today_summary.get("calories", 0)
        count = today_summary.get("count", 0)
        
        st.markdown("---")
        st.markdown("**📊 Resumo de Hoje**")
        st.metric("🔥 Calorias", f"{calories} kcal")
        st.metric("📝 Refeições", count)
        st.metric("🔥 Sequência", f"{streak} dias")
        
        st.markdown("---")
        st.markdown("**🧭 Navegação**")
        
        pages = {
            "🏠 Início": "home",
            "📊 Dashboard": "dashboard",
            "🍴 Registro Alimentar": "meals",
            "⚖️ Evolução Peso": "weight",
            "📈 Análise Estatística": "stats",
            "👤 Perfil": "profile"
        }
        
        for label, page_key in pages.items():
            if st.button(label, use_container_width=True, type="primary" if st.session_state.page == page_key else "secondary"):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()
        
        st.markdown('<div style="text-align: center; font-size: 0.7rem; color: #64748b; margin-top: 1rem;">EmagreSim © 2024</div>', unsafe_allow_html=True)


def render_home_page(user: dict, services: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="main-header">
        <h1 style="margin: 0;">{get_welcome_message()}</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.95;">{user.get('name', 'Usuário')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not check_onboarding_complete(user):
        st.warning("⚠️ Complete seu perfil para uma experiência personalizada!")
        if st.button("Completar Perfil Agora", use_container_width=True, type="primary"):
            st.session_state.page = "profile"
            st.rerun()
    
    # ✅ CORREÇÃO: Uso de função segura
    today_summary = get_daily_summary_safe(services["nutrition"])
    streak = get_streak_safe(services["gamification"])
    
    w = user.get("current_weight") or 70.0
    goal = user.get("goal_weight") or 65.0
    
    st.markdown("### 📊 Seu Progresso")
    col1, col2, col3, col4 = st.columns(4)
    
    calories = today_summary.get("calories", 0)
    
    with col1:
        st.markdown(f"""
        <div class="data-card">
            <div class="data-value">{calories}</div>
            <div class="data-label">🔥 Calorias Hoje</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="data-card">
            <div class="data-value">{streak}</div>
            <div class="data-label">🔥 Dias Seguidos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="data-card">
            <div class="data-value">{w:.1f}</div>
            <div class="data-label">⚖️ Peso Atual</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        diff = w - goal
        st.markdown(f"""
        <div class="data-card">
            <div class="data-value">{diff:+.1f}</div>
            <div class="data-label">🎯 Para Meta</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Barra de progresso com proteção
    try:
        tmb = services["nutrition"].calculate_tmb(
            weight=float(w),
            height=float(user.get("height", 170)),
            age=int(user.get("age", 30))
        )
        daily_goal = services["nutrition"].calculate_daily_goal(
            tmb, 
            user.get("activity_level", "moderate"), 
            user.get("goal", "lose")
        )
        percent = min(100, int((calories / daily_goal) * 100)) if daily_goal > 0 else 0
        
        st.markdown(f"""
        <div style="margin: 1.5rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-weight: 600;">Progresso da Meta Diária</span>
                <span style="color: {'#10b981' if percent <= 100 else '#ef4444'}; font-weight: 600;">{percent}%</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {percent}%; background: {'linear-gradient(90deg, #10b981, #34d399)' if percent <= 100 else 'linear-gradient(90deg, #ef4444, #f87171)'}"></div>
            </div>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                Meta: {daily_goal} kcal • Consumidas: {calories} kcal • Restam: {max(0, daily_goal - calories)} kcal
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Erro ao calcular meta: {e}")
        st.info(f"Meta diária: Configure seu perfil para ver o progresso.")
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🍴 Registrar Refeição", use_container_width=True, type="primary"):
            st.session_state.page = "meals"
            st.rerun()
    with col2:
        if st.button("⚖️ Registrar Peso", use_container_width=True):
            st.session_state.page = "weight"
            st.rerun()
    with col3:
        if st.button("📊 Ver Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    load_css_file()
    init_session_state()
    
    services = init_services()
    if not services:
        st.error("❌ Falha ao inicializar o sistema. Recarregue a página.")
        st.stop()
    
    if st.session_state.user is None:
        render_login_page(services)
        return
    
    user = st.session_state.user
    render_sidebar(user, services)
    
    if st.session_state.page == "home":
        render_home_page(user, services)
    elif st.session_state.page == "dashboard":
        try:
            st.switch_page("pages/01_Dashboard.py")
        except:
            st.info("Página Dashboard em construção.")
    elif st.session_state.page == "meals":
        try:
            st.switch_page("pages/02_Refeições.py")
        except:
            st.info("Página Refeições em construção.")
    elif st.session_state.page == "weight":
        try:
            st.switch_page("pages/03_Peso.py")
        except:
            st.info("Página Peso em construção.")
    elif st.session_state.page == "stats":
        try:
            st.switch_page("pages/04_Análise_Estatística.py")
        except:
            st.info("Página Análise em construção.")
    elif st.session_state.page == "profile":
        try:
            st.switch_page("pages/05_Perfil.py")
        except:
            st.info("Página Perfil em construção.")


if __name__ == "__main__":
    main()
