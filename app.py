import streamlit as st
import logging
import os
from datetime import datetime, date
from typing import Optional, Dict, List

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EmagreSim")

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "EmagreSim v2.0 - Monitoramento nutricional"
    }
)

# ============================================================
# CSS INLINE (fallback caso assets/style.css não exista)
# ============================================================
CSS_PADRAO = """
<style>
    .fade-in { animation: fadeIn 0.3s ease-in; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .data-card {
        background: white; border-radius: 12px; padding: 1.25rem;
        border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem; transition: transform 0.2s;
    }
    .data-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .data-value { font-size: 2rem; font-weight: 700; color: #0891b2; line-height: 1.2; }
    .data-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .main-header { 
        background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
        color: white; padding: 1.5rem; border-radius: 12px;
        margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .progress-container { 
        background: #e2e8f0; border-radius: 9999px; height: 0.75rem; 
        overflow: hidden; margin: 0.5rem 0;
    }
    .progress-bar { 
        background: linear-gradient(90deg, #0891b2, #06b6d4); 
        height: 100%; transition: width 0.5s ease;
    }
    [data-testid="stSidebar"] { background: #1e293b; }
    [data-testid="stSidebar"] * { color: #f1f5f9; }
</style>
"""

def load_css():
    try:
        if os.path.exists("assets/style.css"):
            with open("assets/style.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            st.markdown(CSS_PADRAO, unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"CSS não carregado: {e}")
        st.markdown(CSS_PADRAO, unsafe_allow_html=True)

# ============================================================
# ESTADO GLOBAL
# ============================================================
def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "home"

init_session_state()

# ============================================================
# DATABASE (Fallback embutido se core/database.py não existir)
# ============================================================
try:
    from core.database import AppDatabase
    logger.info("✅ core/database.py carregado")
except Exception as e:
    logger.warning(f"core/database.py não encontrado, usando fallback: {e}")
    
    class AppDatabase:
        """Fallback mínimo para o banco funcionar."""
        def __init__(self):
            self.is_real = False
            self.client = None
            if "mock_db" not in st.session_state:
                st.session_state.mock_db = {
                    "users": {
                        "demo@emagresim.com": {
                            "password": "demo", "name": "Usuário Demo", 
                            "email": "demo@emagresim.com", "plan": "free",
                            "current_weight": 75.0, "goal_weight": 70.0,
                            "height": 170, "age": 30,
                            "activity_level": "moderate", "goal": "lose"
                        }
                    },
                    "meals": [], "weights": [], "achievements": []
                }
        
        def get_current_user_id(self) -> str:
            u = st.session_state.get("user")
            return u.get("email", "anonymous") if u else "anonymous"
        
        def get_user(self, email: str, password: str) -> Optional[Dict]:
            users = st.session_state.mock_db.get("users", {})
            if email in users and users[email].get("password") == password:
                return users[email]
            return None
        
        def create_user(self, email: str, password: str, name: str) -> bool:
            users = st.session_state.mock_db.get("users", {})
            if email in users:
                return False
            users[email] = {
                "password": password, "name": name, "email": email,
                "plan": "free", "current_weight": 70.0, "goal_weight": 65.0,
                "height": 170, "age": 30, "activity_level": "moderate", "goal": "lose"
            }
            st.session_state.mock_db["users"] = users
            return True
        
        def update_profile(self, data: Dict) -> bool:
            uid = self.get_current_user_id()
            if uid in st.session_state.mock_db.get("users", {}):
                st.session_state.mock_db["users"][uid].update(data)
                return True
            return False
        
        def save_meal(self, data: Dict):
            data["user_id"] = self.get_current_user_id()
            st.session_state.mock_db["meals"].append(data)
        
        def get_meals(self, days: int = 7) -> List[Dict]:
            uid = self.get_current_user_id()
            meals = [m for m in st.session_state.mock_db.get("meals", []) 
                     if m.get("user_id") == uid]
            if days:
                cutoff = date.today() - __import__('datetime').timedelta(days=days)
                return [m for m in meals 
                        if __import__('datetime').datetime.strptime(
                            m.get("meal_date", "2000-01-01"), "%Y-%m-%d"
                        ).date() >= cutoff]
            return meals
        
        def get_meals_by_date(self, date_str: str) -> List[Dict]:
            return [m for m in self.get_meals(days=None) 
                    if m.get("meal_date") == date_str]
        
        def save_weight(self, data: Dict):
            data["user_id"] = self.get_current_user_id()
            st.session_state.mock_db["weights"].append(data)
            uid = data["user_id"]
            if uid in st.session_state.mock_db.get("users", {}):
                st.session_state.mock_db["users"][uid]["current_weight"] = data.get("weight")
        
        def get_weights(self, days: int = 30):
            import pandas as pd
            uid = self.get_current_user_id()
            w = [x for x in st.session_state.mock_db.get("weights", []) 
                 if x.get("user_id") == uid]
            if not w:
                return pd.DataFrame(columns=['log_date', 'weight'])
            df = pd.DataFrame(w)
            df['log_date'] = pd.to_datetime(df['log_date'])
            return df.sort_values('log_date')
        
        def unlock_achievement(self, name: str, title: str) -> bool:
            uid = self.get_current_user_id()
            achs = st.session_state.mock_db.get("achievements", [])
            if not any(a.get("achievement_name") == name and a.get("user_id") == uid for a in achs):
                achs.append({
                    "user_id": uid, "achievement_name": name,
                    "title": title, "unlocked_at": str(date.today())
                })
                st.session_state.mock_db["achievements"] = achs
                return True
            return False
        
        def get_achievements(self) -> List[Dict]:
            uid = self.get_current_user_id()
            return [a for a in st.session_state.mock_db.get("achievements", []) 
                    if a.get("user_id") == uid]

# ============================================================
# FOOD_DB (Fallback embutido)
# ============================================================
try:
    from utils.food_db import FOOD_DB, buscar_alimento, COMBOS
    logger.info("✅ utils/food_db.py carregado")
except Exception as e:
    logger.warning(f"utils/food_db.py não encontrado, usando fallback: {e}")
    
    FOOD_DB = {
        "arroz_branco": {"name": "Arroz Branco", "category": "almoco_jantar", "calories": 130, "protein": 2.5, "carbs": 28, "fat": 0.3, "fiber": 1.5, "portion": "100g"},
        "feijao_preto": {"name": "Feijão Preto", "category": "almoco_jantar", "calories": 77, "protein": 4.5, "carbs": 14, "fat": 0.5, "fiber": 8.5, "portion": "100g"},
        "peito_frango": {"name": "Peito de Frango Grelhado", "category": "almoco_jantar", "calories": 160, "protein": 32, "carbs": 0, "fat": 3.5, "fiber": 0, "portion": "100g"},
        "banana_prata": {"name": "Banana Prata", "category": "frutas", "calories": 90, "protein": 1.5, "carbs": 23, "fat": 0.2, "fiber": 2, "portion": "100g"},
        "ovo_cozido": {"name": "Ovo Cozido", "category": "cafe_manha", "calories": 145, "protein": 13, "carbs": 1.5, "fat": 9.5, "fiber": 0, "portion": "100g"},
        "pao_frances": {"name": "Pão Francês", "category": "cafe_manha", "calories": 300, "protein": 8, "carbs": 58, "fat": 3, "fiber": 2.5, "portion": "100g"},
        "leite_integral": {"name": "Leite Integral", "category": "cafe_manha", "calories": 60, "protein": 3, "carbs": 4.5, "fat": 3.3, "fiber": 0, "portion": "100ml"},
        "maca": {"name": "Maçã", "category": "frutas", "calories": 55, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.5, "portion": "100g"},
        "salada_mista": {"name": "Salada Mista", "category": "almoco_jantar", "calories": 20, "protein": 1, "carbs": 3, "fat": 0.2, "fiber": 1.5, "portion": "100g"},
        "batata_doce": {"name": "Batata Doce", "category": "almoco_jantar", "calories": 77, "protein": 0.6, "carbs": 18, "fat": 0.1, "fiber": 2.2, "portion": "100g"},
    }
    COMBOS = {
        "pf_basico": {"name": "PF Básico", "items": ["arroz_branco", "feijao_preto", "peito_frango", "salada_mista"]},
    }
    def buscar_alimento(termo: str) -> list:
        termo = termo.lower().strip()
        if not termo: return []
        return [{"key": k, "name": v["name"], "calories": v["calories"]} 
                for k, v in FOOD_DB.items() if termo in v["name"].lower()][:10]

# ============================================================
# NUTRITION SERVICE (Fallback)
# ============================================================
try:
    from core.nutrition import NutritionService
    logger.info("✅ core/nutrition.py carregado")
except Exception as e:
    logger.warning(f"core/nutrition.py não encontrado: {e}")
    
    class NutritionService:
        def __init__(self, db): self.db = db
        
        def calculate_tmb(self, weight, height, age, gender="male"):
            if not all([weight, height, age]): return 1500
            if gender == "male":
                return int(10 * weight + 6.25 * height - 5 * age + 5)
            return int(10 * weight + 6.25 * height - 5 * age - 161)
        
        def calculate_daily_goal(self, tmb, activity="moderate", goal="lose"):
            factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
            maintenance = int(tmb * factors.get(activity, 1.55))
            if goal == "lose": return max(1200, maintenance - 500)
            elif goal == "gain": return maintenance + 300
            return maintenance
        
        def get_daily_summary(self, date_str=None):
            if not date_str: date_str = str(date.today())
            meals = self.db.get_meals_by_date(date_str)
            return {
                "calories": sum(int(m.get("calories", 0)) for m in meals),
                "protein": sum(float(m.get("protein", 0)) for m in meals),
                "carbs": sum(float(m.get("carbs", 0)) for m in meals),
                "fat": sum(float(m.get("fat", 0)) for m in meals),
                "fiber": sum(float(m.get("fiber", 0)) for m in meals),
                "count": len(meals),
                "meals": sorted(meals, key=lambda x: x.get("meal_time", "00:00"))
            }
        
        def get_weekly_summary(self):
            import pandas as pd
            meals = self.db.get_meals(days=7)
            if not meals: return pd.DataFrame()
            df = pd.DataFrame(meals)
            df['meal_date'] = pd.to_datetime(df['meal_date'])
            return df.groupby(df['meal_date'].dt.date).agg(
                calories=('calories', 'sum')
            ).reset_index().rename(columns={'meal_date': 'date'})
        
        def register_food(self, food_id, quantity, meal_time=None):
            food = FOOD_DB.get(food_id)
            if not food: return False, None, 0
            if not meal_time: meal_time = datetime.now().strftime("%H:%M")
            meal_data = {
                "food": food["name"], "food_id": food_id,
                "quantity": float(quantity),
                "calories": int(food["calories"] * quantity),
                "protein": round(food["protein"] * quantity, 1),
                "carbs": round(food["carbs"] * quantity, 1),
                "fat": round(food["fat"] * quantity, 1),
                "fiber": round(food["fiber"] * quantity, 1),
                "meal_date": str(date.today()),
                "meal_time": meal_time
            }
            self.db.save_meal(meal_data)
            return True, food["name"], meal_data["calories"]

# ============================================================
# GAMIFICATION SERVICE (Fallback)
# ============================================================
try:
    from core.gamification import GamificationSystem
    logger.info("✅ core/gamification.py carregado")
except Exception as e:
    logger.warning(f"core/gamification.py não encontrado: {e}")
    
    class GamificationSystem:
        def __init__(self, db): self.db = db
        def calculate_streak(self):
            meals = self.db.get_meals(days=30)
            if not meals: return 0
            dates = sorted(set(m.get("meal_date") for m in meals if m.get("meal_date")))
            if not dates: return 0
            date_objs = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in dates])
            if date_objs[-1] not in [date.today(), date.today() - __import__('datetime').timedelta(days=1)]:
                return 0
            streak = 1
            for i in range(len(date_objs) - 1, 0, -1):
                diff = (date_objs[i] - date_objs[i-1]).days
                if diff == 1: streak += 1
                else: break
            return streak
        def check_achievements(self, meals_count, streak):
            unlocked = []
            if meals_count >= 1 and self.db.unlock_achievement("first_meal", "️ Primeira Refeição"):
                unlocked.append("️ Primeira Refeição")
            if streak >= 7 and self.db.unlock_achievement("week_streak", "📅 7 Dias"):
                unlocked.append("📅 7 Dias")
            return unlocked

# ============================================================
# PAYMENT SERVICE (Fallback)
# ============================================================
try:
    from core.payment import PaymentService
    logger.info("✅ core/payment.py carregado")
except Exception as e:
    logger.warning(f"core/payment.py não encontrado: {e}")
    
    class PaymentService:
        PLANS = {
            "free": {"name": "Gratuito", "price": 0},
            "pro": {"name": "Pro", "price": 29.90},
            "lifetime": {"name": "Vitalício", "price": 497.00}
        }
        def __init__(self): pass
        def create_checkout_link(self, plan_key, user_email):
            return f"https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=DEMO_{plan_key}"

# ============================================================
# INICIALIZAÇÃO DE SERVIÇOS
# ============================================================
@st.cache_resource(show_spinner=False)
def init_services():
    try:
        db = AppDatabase()
        return {
            "db": db,
            "nutrition": NutritionService(db),
            "gamification": GamificationSystem(db),
            "payment": PaymentService()
        }
    except Exception as e:
        logger.critical(f"Falha fatal: {e}")
        return None

# ============================================================
# COMPONENTES UI
# ============================================================
def card_metric(valor, label, icon="📊", cor="#0891b2"):
    st.markdown(f"""
    <div class="data-card">
        <div class="data-value" style="color:{cor}">{valor}</div>
        <div class="data-label">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)

def progress_bar(percent, cor="auto"):
    if cor == "auto":
        cor = "#10b981" if percent <= 100 else "#ef4444"
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width:{max(0, min(100, percent))}%; background:{cor}"></div>
    </div>
    """, unsafe_allow_html=True)

def empty_state(icon, mensagem, dica=""):
    st.markdown(f"""
    <div style="text-align:center; padding:2rem; color:#94a3b8; background:#f8fafc; border-radius:12px; margin:1rem 0;">
        <div style="font-size:3rem; margin-bottom:0.5rem;">{icon}</div>
        <p style="margin:0; font-weight:600;">{mensagem}</p>
        {f'<p style="font-size:0.85rem; margin-top:0.5rem; color:#64748b;">{dica}</p>' if dica else ''}
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TELA DE LOGIN (EMBUTIDA)
# ============================================================
def render_login(db):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0 3rem 0;">
        <h1 style="font-size: 3rem; margin: 0; color: #0891b2;">💪 EmagreSim</h1>
        <p style="color: #64748b; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Monitoramento nutricional baseado em dados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Acessar Conta", "📝 Criar Conta"])
    
    with tab1:
        email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", key="login_pass", placeholder="••••••••")
        
        if st.button("Entrar", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Preencha email e senha.")
            else:
                try:
                    user_data = db.get_user(email, password)
                    if user_data:
                        st.session_state.user = user_data
                        st.success(f"Bem-vindo, {user_data.get('name', 'Usuário')}!")
                        st.rerun()
                    else:
                        st.error("Email ou senha incorretos.")
                except Exception as e:
                    logger.error(f"Erro no login: {e}")
                    st.error(f"Erro ao fazer login.")
        
        st.markdown("---")
        
        if st.button(" Entrar no Modo Demonstração", use_container_width=True):
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
    
    with tab2:
        new_name = st.text_input("Nome completo", key="reg_name", placeholder="João Silva")
        new_email = st.text_input("Email", key="reg_email", placeholder="joao@email.com")
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
                    if db.create_user(new_email, new_password, new_name):
                        st.success("✅ Conta criada! Faça login agora.")
                    else:
                        st.error("❌ Email já cadastrado.")
                except Exception as e:
                    st.error(f"Erro ao criar conta.")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 2rem;">
        <p>🔒 Seus dados estão protegidos</p>
        <p>EmagreSim v2.0</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar(services):
    user = st.session_state.user
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #334155; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: #06b6d4;">💪 EmagreSim</h2>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #94a3b8;">v2.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        plan = user.get("plan", "free")
        badge_color = "#f59e0b" if plan in ["pro", "lifetime"] else "#64748b"
        st.markdown(f'<div style="background: {badge_color}20; color: {badge_color}; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: 600; margin-bottom: 1.5rem; border: 1px solid {badge_color};">👑 PLANO {plan.upper()}</div>', unsafe_allow_html=True)
        
        st.markdown(f"**👤 {user.get('name', 'Usuário')}**")
        st.caption(f"📧 {user.get('email', '')}")
        
        summary = services["nutrition"].get_daily_summary()
        streak = services["gamification"].calculate_streak()
        
        st.markdown("---")
        st.markdown("**📊 Resumo de Hoje**")
        st.metric("🔥 Calorias", f"{summary.get('calories', 0)} kcal")
        st.metric("️ Refeições", summary.get('count', 0))
        st.metric("🔥 Sequência", f"{streak} dias")
        
        st.markdown("---")
        st.markdown("** Navegação**")
        
        pages = [
            ("🏠 Início", "home"),
            ("📊 Dashboard", "dashboard"),
            ("🍴 Registro Alimentar", "meals"),
            ("⚖️ Evolução Peso", "weight"),
            (" Análise", "analysis"),
            ("👤 Perfil", "profile")
        ]
        
        for label, page_key in pages:
            btn_type = "primary" if st.session_state.page == page_key else "secondary"
            if st.button(label, use_container_width=True, type=btn_type):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

# ============================================================
# PÁGINAS (todas embutidas)
# ============================================================
def render_home(services, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    hour = datetime.now().hour
    if hour < 12: saudacao = "☀️ Bom dia!"
    elif hour < 18: saudacao = "🌤️ Boa tarde!"
    else: saudacao = "🌙 Boa noite!"
    
    st.markdown(f"""
    <div class="main-header">
        <h1 style="margin: 0;">{saudacao} {user.get('name', 'Usuário')}!</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.95;">Vamos analisar seu progresso de hoje.</p>
    </div>
    """, unsafe_allow_html=True)
    
    required = ["current_weight", "height", "age", "goal_weight"]
    if any(user.get(f) is None for f in required):
        st.warning("⚠️ Complete seu perfil para uma experiência personalizada!")
        if st.button("Completar Perfil Agora", use_container_width=True, type="primary"):
            st.session_state.page = "profile"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    summary = services["nutrition"].get_daily_summary()
    streak = services["gamification"].calculate_streak()
    
    w = user.get("current_weight", 70.0)
    goal = user.get("goal_weight", 65.0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: card_metric(f"{summary.get('calories', 0)}", "Calorias Hoje", "🔥")
    with col2: card_metric(f"{streak}", "Dias Seguidos", "🔥", "#f59e0b")
    with col3: card_metric(f"{w:.1f} kg", "Peso Atual", "⚖️", "#10b981")
    with col4: card_metric(f"{w - goal:+.1f} kg", "Para a Meta", "", "#8b5cf6")
    
    tmb = services["nutrition"].calculate_tmb(w, user.get("height", 170), user.get("age", 30))
    meta = services["nutrition"].calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))
    percent = min(100, int((summary['calories'] / meta) * 100)) if meta > 0 else 0
    
    st.markdown(f"**Meta diária:** {meta} kcal ({percent}% consumido)")
    progress_bar(percent)
    
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
        if st.button(" Ver Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard(services, user):
    st.title("📊 Dashboard Completo")
    
    summary = services["nutrition"].get_daily_summary()
    streak = services["gamification"].calculate_streak()
    
    col1, col2, col3 = st.columns(3)
    with col1: card_metric(f"{summary.get('calories', 0)} kcal", "Consumo Hoje", "🔥")
    with col2: card_metric(f"{summary.get('protein', 0):.1f}g", "Proteínas", "", "#10b981")
    with col3: card_metric(f"{streak} dias", "Sequência", "🔥", "#f59e0b")
    
    st.subheader("📈 Últimos 7 Dias")
    weekly = services["nutrition"].get_weekly_summary()
    if not weekly.empty:
        try:
            import plotly.express as px
            fig = px.line(weekly, x='date', y='calories', markers=True, template="plotly_white")
            fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.write(weekly)
    else:
        empty_state("📊", "Sem dados suficientes", "Registre refeições por 2 dias para ver o gráfico.")
    
    st.subheader("🥗 Macronutrientes do Dia")
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Proteínas", f"{summary.get('protein', 0):.1f}g")
    with m2: st.metric("Carboidratos", f"{summary.get('carbs', 0):.1f}g")
    with m3: st.metric("Gorduras", f"{summary.get('fat', 0):.1f}g")
    with m4: st.metric("Fibras", f"{summary.get('fiber', 0):.1f}g")

def render_meals(services, user):
    st.title("🍽️ Registro Alimentar")
    st.markdown(f"**{user.get('name', 'Usuário')}** - {date.today().strftime('%d/%m/%Y')}")
    
    periodo = st.selectbox("Qual refeição?", 
        ["☕ Café da Manhã", " Almoço", "🌙 Jantar", "🥪 Lanche", "🌃 Ceia"])
    
    mapeamento = {
        "☕ Café da Manhã": "cafe_manha", "🍴 Almoço": "almoco_jantar",
        " Jantar": "almoco_jantar", "🥪 Lanche": "lanche", "🌃 Ceia": "ceia"
    }
    categoria = mapeamento[periodo]
    
    termo = st.text_input("🔍 Buscar alimento...", placeholder="Ex: arroz, frango...")
    food_key = None
    
    if termo:
        resultados = buscar_alimento(termo)
        if resultados:
            opcoes = {f"{r['name']} ({r['calories']} kcal)": r['key'] for r in resultados}
            sel = st.selectbox("Resultados:", list(opcoes.keys()))
            food_key = opcoes[sel]
        else:
            st.warning("Nenhum alimento encontrado.")
    else:
        alimentos_cat = {k: v for k, v in FOOD_DB.items() if v.get("category") == categoria}
        if alimentos_cat:
            opcoes = {f"{v['name']} ({v['calories']} kcal)": k for k, v in alimentos_cat.items()}
            sel = st.selectbox(f"Ou escolha de {periodo}:", list(opcoes.keys()))
            food_key = opcoes[sel]
    
    c1, c2 = st.columns(2)
    with c1: qtd = st.number_input("Quantidade (x)", 0.1, 10.0, 1.0, 0.1)
    with c2: hora = st.time_input("Horário", value=datetime.now().time())
    
    if st.button("✅ Registrar Refeição", type="primary", use_container_width=True):
        if food_key:
            ok, nome, cal = services["nutrition"].register_food(food_key, qtd, hora.strftime("%H:%M"))
            if ok:
                st.success(f"✅ {nome} registrado! (+{cal * qtd:.0f} kcal)")
                st.rerun()
        else:
            st.error("Selecione um alimento primeiro.")
    
    st.markdown("---")
    st.subheader("📋 Refeições de Hoje")
    summary = services["nutrition"].get_daily_summary()
    if summary.get('meals'):
        for meal in summary['meals']:
            st.markdown(f"• **{meal.get('meal_time', '--:--')}** - {meal.get('food', '?')} ({meal.get('calories', 0)} kcal)")
    else:
        empty_state("🍽️", "Nenhuma refeição registrada hoje", "Use o seletor acima para começar.")

def render_weight(services, user):
    st.title("⚖️ Evolução de Peso")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Registrar Pesagem**")
        peso = st.number_input("Peso (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)), 0.1)
        notas = st.text_area("Observações", placeholder="Ex: Jejum...")
        
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            services["db"].save_weight({"weight": peso, "log_date": str(date.today()), "notes": notas})
            user["current_weight"] = peso
            st.session_state.user = user
            st.success("✅ Peso registrado!")
            st.rerun()
    
    with c2:
        st.markdown("**Histórico (90 dias)**")
        df = services["db"].get_weights(days=90)
        if not df.empty:
            try:
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['log_date'], y=df['weight'],
                    mode='lines+markers', name='Peso',
                    line=dict(color='#0891b2', width=3)))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20),
                    xaxis_title="Data", yaxis_title="Peso (kg)", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.write(df)
            
            primeira = df.iloc[0]['weight']
            ultima = df.iloc[-1]['weight']
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Primeiro", f"{primeira:.1f} kg")
            with c2: st.metric("Atual", f"{ultima:.1f} kg")
            with c3: st.metric("Variação", f"{ultima - primeira:+.1f} kg", delta_color="inverse")
        else:
            empty_state("⚖️", "Sem pesagens", "Faça seu primeiro registro ao lado.")

def render_analysis(services, user):
    st.title("📈 Análise e Desafios")
    
    achs = services["db"].get_achievements()
    if achs:
        st.subheader("🏆 Conquistas")
        cols = st.columns(min(3, len(achs)))
        for i, a in enumerate(achs):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 2rem;">🏅</div>
                    <div style="font-weight: 600;">{a.get('title', 'Conquista')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma conquista ainda. Continue registrando!")
    
    st.markdown("---")
    st.subheader("🎯 Desafios da Semana")
    desafios = [
        {"t": "7 Refeições Registradas", "xp": 50},
        {"t": "Meta Calórica Atingida", "xp": 120},
        {"t": "Hidratação Total", "xp": 60},
    ]
    for d in desafios:
        st.markdown(f"<div style='background: #f0f9ff; border-left: 4px solid #0891b2; padding: 1rem; margin-bottom: 0.5rem; border-radius: 4px;'><b>🎯 {d['t']}</b> <span style='float:right; color: #f59e0b; font-weight:bold;'>+{d['xp']} XP</span></div>", unsafe_allow_html=True)

def render_profile(services, user):
    st.title("👤 Perfil")
    
    with st.form("perfil_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome", value=user.get("name", ""))
            st.text_input("Email", value=user.get("email", ""), disabled=True)
            idade = st.number_input("Idade", 10, 110, int(user.get("age", 30)))
            altura = st.number_input("Altura (cm)", 100, 250, int(user.get("height", 170)))
        with c2:
            peso = st.number_input("Peso Atual (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)))
            meta = st.number_input("Meta (kg)", 30.0, 250.0, float(user.get("goal_weight", 70.0)))
            objetivo = st.selectbox("Objetivo", ["lose", "maintain", "gain"],
                index=["lose", "maintain", "gain"].index(user.get("goal", "lose")),
                format_func=lambda x: {"lose": "Emagrecer", "maintain": "Manter", "gain": "Ganhar Massa"}[x])
            atividade = st.selectbox("Atividade", ["sedentary", "light", "moderate", "active"],
                index=["sedentary", "light", "moderate", "active"].index(user.get("activity_level", "moderate")),
                format_func=lambda x: {"sedentary": "Sedentário", "light": "Leve", "moderate": "Moderado", "active": "Ativo"}[x])
        
        if st.form_submit_button(" Salvar", type="primary", use_container_width=True):
            dados = {"name": nome, "current_weight": peso, "height": altura,
                     "age": idade, "goal_weight": meta, "goal": objetivo, "activity_level": atividade}
            user.update(dados)
            services["db"].update_profile(dados)
            st.session_state.user = user
            st.success("✅ Perfil atualizado!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("💳 Plano Atual")
    plano = user.get("plan", "free")
    st.info(f"Plano atual: **{plano.upper()}**")
    
    if plano == "free":
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Plano Pro** - R$ 29,90/mês")
            if st.button("Assinar Pro", use_container_width=True):
                user["plan"] = "pro"
                st.session_state.user = user
                services["db"].update_profile({"plan": "pro"})
                st.success("Plano PRO ativado!")
                st.rerun()
        with c2:
            st.markdown("**Vitalício** - R$ 497,00")
            if st.button("Assinar Vitalício", use_container_width=True):
                user["plan"] = "lifetime"
                st.session_state.user = user
                services["db"].update_profile({"plan": "lifetime"})
                st.success("Plano Vitalício ativado!")
                st.rerun()

# ============================================================
# MAIN
# ============================================================
def main():
    load_css()
    
    services = init_services()
    if not services:
        st.error(" Falha ao inicializar o sistema.")
        st.stop()
    
    user = st.session_state.user
    
    if user is None:
        render_login(services["db"])
        return
    
    render_sidebar(services)
    
    page = st.session_state.page
    logger.debug(f"Navegando: {page}")
    
    try:
        if page == "home": render_home(services, user)
        elif page == "dashboard": render_dashboard(services, user)
        elif page == "meals": render_meals(services, user)
        elif page == "weight": render_weight(services, user)
        elif page == "analysis": render_analysis(services, user)
        elif page == "profile": render_profile(services, user)
        else: render_home(services, user)
    except Exception as e:
        logger.error(f"Erro ao renderizar '{page}': {e}")
        st.error(f"Erro ao carregar a página.")

if __name__ == "__main__":
    main()
