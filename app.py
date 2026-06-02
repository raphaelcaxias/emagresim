import streamlit as st
import logging
import os
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List

# ============================================================
# 1. LOGGING E CONFIGURAÇÃO
# ============================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EmagreSim")

st.set_page_config(
    page_title="EmagreSim",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "EmagreSim v2.0 - Monitoramento nutricional"}
)

# ============================================================
# 2. CSS (Com Fallback)
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
    .progress-container { background: #e2e8f0; border-radius: 9999px; height: 0.75rem; overflow: hidden; margin: 0.5rem 0; }
    .progress-bar { background: linear-gradient(90deg, #0891b2, #06b6d4); height: 100%; transition: width 0.5s ease; }
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
    except Exception:
        st.markdown(CSS_PADRAO, unsafe_allow_html=True)

# ============================================================
# 3. ESTADO GLOBAL
# ============================================================
def init_session_state():
    if "user" not in st.session_state: st.session_state.user = None
    if "page" not in st.session_state: st.session_state.page = "home"

init_session_state()

# ============================================================
# 4. BANCO DE DADOS (Fallback Seguro)
# ============================================================
try:
    from core.database import AppDatabase
except Exception:
    class AppDatabase:
        def __init__(self):
            self.is_real = False
            if "mock_db" not in st.session_state:
                st.session_state.mock_db = {
                    "users": {"demo@emagresim.com": {"password": "demo", "name": "Usuário Demo", "email": "demo@emagresim.com", "plan": "free", "current_weight": 75.0, "goal_weight": 70.0, "height": 170, "age": 30, "activity_level": "moderate", "goal": "lose"}},
                    "meals": [], "weights": [], "achievements": []
                }
        def get_current_user_id(self) -> str:
            u = st.session_state.get("user")
            return u.get("email", "anonymous") if u else "anonymous"
        def get_user(self, email, password):
            users = st.session_state.mock_db.get("users", {})
            return users[email] if email in users and users[email].get("password") == password else None
        def create_user(self, email, password, name):
            users = st.session_state.mock_db.get("users", {})
            if email in users: return False
            users[email] = {"password": password, "name": name, "email": email, "plan": "free", "current_weight": 70.0, "goal_weight": 65.0, "height": 170, "age": 30, "activity_level": "moderate", "goal": "lose"}
            st.session_state.mock_db["users"] = users
            return True
        def update_profile(self, data):
            uid = self.get_current_user_id()
            if uid in st.session_state.mock_db.get("users", {}):
                st.session_state.mock_db["users"][uid].update(data)
                return True
            return False
        def save_meal(self, data):
            data["user_id"] = self.get_current_user_id()
            st.session_state.mock_db["meals"].append(data)
        def get_meals(self, days=7):
            uid = self.get_current_user_id()
            meals = [m for m in st.session_state.mock_db.get("meals", []) if m.get("user_id") == uid]
            if days:
                cutoff = date.today() - timedelta(days=days)
                return [m for m in meals if datetime.strptime(m.get("meal_date", "2000-01-01"), "%Y-%m-%d").date() >= cutoff]
            return meals
        def get_meals_by_date(self, date_str):
            return [m for m in self.get_meals(days=None) if m.get("meal_date") == date_str]
        def save_weight(self, data):
            data["user_id"] = self.get_current_user_id()
            st.session_state.mock_db["weights"].append(data)
            uid = data["user_id"]
            if uid in st.session_state.mock_db.get("users", {}):
                st.session_state.mock_db["users"][uid]["current_weight"] = data.get("weight")
        def get_weights(self, days=30):
            import pandas as pd
            uid = self.get_current_user_id()
            w = [x for x in st.session_state.mock_db.get("weights", []) if x.get("user_id") == uid]
            if not w: return pd.DataFrame(columns=['log_date', 'weight'])
            df = pd.DataFrame(w)
            df['log_date'] = pd.to_datetime(df['log_date'])
            return df.sort_values('log_date')
        def unlock_achievement(self, name, title):
            uid = self.get_current_user_id()
            achs = st.session_state.mock_db.get("achievements", [])
            if not any(a.get("achievement_name") == name and a.get("user_id") == uid for a in achs):
                achs.append({"user_id": uid, "achievement_name": name, "title": title, "unlocked_at": str(date.today())})
                st.session_state.mock_db["achievements"] = achs
                return True
            return False
        def get_achievements(self):
            uid = self.get_current_user_id()
            return [a for a in st.session_state.mock_db.get("achievements", []) if a.get("user_id") == uid]

# ============================================================
# 5. BANCO DE ALIMENTOS (FOOD DB + FOOD SERVICE)
# ============================================================
try:
    from utils.food_db import FOOD_DB
except Exception:
    FOOD_DB = {
        "arroz_branco": {"name": "Arroz Branco", "category": "almoco_jantar", "calories": 130, "protein": 2.5, "carbs": 28, "fat": 0.3, "fiber": 1.5, "portion": "100g"},
        "feijao_preto": {"name": "Feijão Preto", "category": "almoco_jantar", "calories": 77, "protein": 4.5, "carbs": 14, "fat": 0.5, "fiber": 8.5, "portion": "100g"},
        "peito_frango": {"name": "Peito de Frango Grelhado", "category": "almoco_jantar", "calories": 160, "protein": 32, "carbs": 0, "fat": 3.5, "fiber": 0, "portion": "100g"},
        "banana_prata": {"name": "Banana Prata", "category": "frutas", "calories": 90, "protein": 1.5, "carbs": 23, "fat": 0.2, "fiber": 2, "portion": "1 unidade"},
        "ovo_cozido": {"name": "Ovo Cozido", "category": "cafe_manha", "calories": 145, "protein": 13, "carbs": 1.5, "fat": 9.5, "fiber": 0, "portion": "1 unidade"},
        "pao_frances": {"name": "Pão Francês", "category": "cafe_manha", "calories": 300, "protein": 8, "carbs": 58, "fat": 3, "fiber": 2.5, "portion": "1 unidade"},
        "leite_integral": {"name": "Leite Integral", "category": "cafe_manha", "calories": 60, "protein": 3, "carbs": 4.5, "fat": 3.3, "fiber": 0, "portion": "100ml"},
        "maca": {"name": "Maçã", "category": "frutas", "calories": 55, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.5, "portion": "1 unidade"},
        "alface": {"name": "Alface", "category": "almoco_jantar", "calories": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2, "fiber": 1.5, "portion": "100g"},
        "batata_doce": {"name": "Batata Doce", "category": "almoco_jantar", "calories": 77, "protein": 0.6, "carbs": 18, "fat": 0.1, "fiber": 2.2, "portion": "100g"},
    }

class FoodService:
    """Serviço de alimentos com fallback local."""
    def __init__(self, supabase_client=None):
        self.client = supabase_client
        
    def get_categories(self):
        if self.client:
            try:
                res = self.client.table("meal_categories").select("*").order("display_order").execute()
                return res.data or []
            except Exception: pass
        return [
            {"name": "Café da Manhã", "code": "cafe_manha", "icon": "☕"},
            {"name": "Almoço", "code": "almoco_jantar", "icon": "🍴"},
            {"name": "Lanche", "code": "lanche", "icon": "🥪"},
            {"name": "Jantar", "code": "almoco_jantar", "icon": ""},
            {"name": "Ceia", "code": "ceia", "icon": "🌃"},
        ]

    def get_foods_by_category(self, category_code):
        if self.client:
            try:
                res = self.client.table("foods").select("*").eq("category_code", category_code).eq("is_active", True).execute()
                return res.data or []
            except Exception: pass
        
        # Fallback local
        return [v for v in FOOD_DB.values() if v.get("category") == category_code]

    def search_foods(self, term, category_code=None):
        if self.client and term:
            try:
                query = self.client.table("foods").select("*").ilike("name", f"%{term}%").eq("is_active", True)
                if category_code: query = query.eq("category_code", category_code)
                res = query.execute()
                return res.data or []
            except Exception: pass
            
        # Fallback local
        term = term.lower()
        foods = []
        for v in FOOD_DB.values():
            if category_code and v.get("category") != category_code: continue
            if term and term not in v["name"].lower(): continue
            foods.append(v)
        return foods

# ============================================================
# 6. OUTROS SERVIÇOS (Nutrition, Gamification, Payment)
# ============================================================
try:
    from core.nutrition import NutritionService
    from core.gamification import GamificationSystem
    from core.payment import PaymentService
except Exception:
    class NutritionService:
        def __init__(self, db): self.db = db
        def calculate_tmb(self, w, h, a, g="male"):
            if not all([w,h,a]): return 1500
            return int(10*w + 6.25*h - 5*a + 5) if g=="male" else int(10*w + 6.25*h - 5*a - 161)
        def calculate_daily_goal(self, tmb, act="moderate", goal="lose"):
            factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
            maintenance = int(tmb * factors.get(act, 1.55))
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
            return df.groupby(df['meal_date'].dt.date).agg(calories=('calories', 'sum')).reset_index().rename(columns={'meal_date': 'date'})
        def register_food(self, food_id, quantity, meal_time=None):
            # Tenta achar no banco local se o ID for string do fallback
            food = FOOD_DB.get(food_id) if isinstance(food_id, str) else None
            if not food and isinstance(food_id, dict):
                food = food_id
            if not food: return False, None, 0
            if not meal_time: meal_time = datetime.now().strftime("%H:%M")
            
            meal_data = {
                "food": food["name"], "food_id": food.get("id", food_id),
                "quantity": float(quantity),
                "calories": int(food["calories"] * quantity),
                "protein": round(food.get("protein", 0) * quantity, 1),
                "carbs": round(food.get("carbs", 0) * quantity, 1),
                "fat": round(food.get("fat", 0) * quantity, 1),
                "fiber": round(food.get("fiber", 0) * quantity, 1),
                "meal_date": str(date.today()), "meal_time": meal_time
            }
            self.db.save_meal(meal_data)
            return True, food["name"], food["calories"]
    class GamificationSystem:
        def __init__(self, db): self.db = db
        def calculate_streak(self):
            meals = self.db.get_meals(days=30)
            if not meals: return 0
            dates = sorted(set(m.get("meal_date") for m in meals if m.get("meal_date")))
            if not dates: return 0
            date_objs = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in dates])
            if date_objs[-1] not in [date.today(), date.today() - timedelta(days=1)]: return 0
            streak = 1
            for i in range(len(date_objs) - 1, 0, -1):
                diff = (date_objs[i] - date_objs[i-1]).days
                if diff == 1: streak += 1
                else: break
            return streak
    class PaymentService:
        PLANS = {"free": {"name": "Gratuito"}, "pro": {"name": "Pro", "price": 29.90}}
        def __init__(self): pass
        def create_checkout_link(self, plan, email): return "#"

# ============================================================
# 7. INICIALIZAÇÃO
# ============================================================
@st.cache_resource(show_spinner=False)
def init_services():
    try:
        db = AppDatabase()
        supabase_client = None
        try:
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                from supabase import create_client
                supabase_client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        except Exception: pass
        
        return {
            "db": db,
            "nutrition": NutritionService(db),
            "gamification": GamificationSystem(db),
            "payment": PaymentService(),
            "foods": FoodService(supabase_client)
        }
    except Exception as e:
        logger.critical(f"Falha fatal: {e}")
        return None

# ============================================================
# 8. COMPONENTES UI
# ============================================================
def card_metric(valor, label, icon="📊", cor="#0891b2"):
    st.markdown(f"""
    <div class="data-card">
        <div class="data-value" style="color:{cor}">{valor}</div>
        <div class="data-label">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)

def progress_bar(percent, cor="auto"):
    if cor == "auto": cor = "#10b981" if percent <= 100 else "#ef4444"
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
# 9. VIEWS
# ============================================================
def render_login(db):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0 3rem 0;">
        <h1 style="font-size: 3rem; margin: 0; color: #0891b2;">💪 EmagreSim</h1>
        <p style="color: #64748b; margin: 0.5rem 0 0 0; font-size: 1.1rem;">Monitoramento nutricional baseado em dados</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Acessar Conta", "📝 Criar Conta"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar", use_container_width=True, type="primary"):
            if email and password:
                user = db.get_user(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else: st.error("Credenciais inválidas.")
        st.markdown("---")
        if st.button("🎮 Modo Demonstração", use_container_width=True):
            demo_user = {"email": "demo@emagresim.com", "password": "demo", "name": "Usuário Demo", "plan": "free", "current_weight": 75.0, "goal_weight": 70.0, "height": 170, "age": 30, "activity_level": "moderate", "goal": "lose"}
            if "mock_db" not in st.session_state: st.session_state.mock_db = {"users": {}, "meals": [], "weights": [], "achievements": []}
            if "users" not in st.session_state.mock_db: st.session_state.mock_db["users"] = {}
            st.session_state.mock_db["users"]["demo@emagresim.com"] = demo_user
            st.session_state.user = demo_user
            st.rerun()
    with tab2:
        name = st.text_input("Nome", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        p1 = st.text_input("Senha", type="password", key="reg_p1")
        p2 = st.text_input("Confirmar", type="password", key="reg_p2")
        if st.button("Cadastrar", use_container_width=True, type="primary"):
            if name and email and p1 and p1 == p2 and len(p1) >= 6:
                if db.create_user(email, p1, name): st.success("Conta criada!")
                else: st.error("Email já cadastrado.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar(services):
    user = st.session_state.user
    with st.sidebar:
        st.markdown('<h2 style="text-align:center;color:#06b6d4;">💪 EmagreSim</h2>', unsafe_allow_html=True)
        plan = user.get("plan", "free")
        st.markdown(f'<div style="background:#334155; color:#94a3b8; padding:0.5rem; border-radius:8px; text-align:center; font-weight:600; margin-bottom:1rem;">👑 {plan.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f"** {user.get('name')}**\n📧 {user.get('email')}")
        
        summary = services["nutrition"].get_daily_summary()
        streak = services["gamification"].calculate_streak()
        
        st.markdown("---\n**📊 Resumo de Hoje**")
        st.metric("🔥 Calorias", f"{summary.get('calories', 0)} kcal")
        st.metric("🍽️ Refeições", summary.get('count', 0))
        st.metric("🔥 Sequência", f"{streak} dias")
        
        st.markdown("---\n**🧭 Navegação**")
        pages = [("🏠 Início", "home"), (" Dashboard", "dashboard"), ("🍴 Registro", "meals"), ("⚖️ Peso", "weight"), ("📈 Análise", "analysis"), ("👤 Perfil", "profile")]
        for label, key in pages:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.page == key else "secondary"):
                st.session_state.page = key
                st.rerun()
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.user = None
            st.rerun()

def render_home(services, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    hour = datetime.now().hour
    saudacao = "☀️ Bom dia!" if hour < 12 else "🌤️ Boa tarde!" if hour < 18 else "🌙 Boa noite!"
    st.markdown(f'<div class="main-header"><h1 style="margin:0;">{saudacao} {user.get("name")}!</h1></div>', unsafe_allow_html=True)
    
    required = ["current_weight", "height", "age", "goal_weight"]
    if any(user.get(f) is None for f in required):
        st.warning("⚠️ Complete seu perfil!")
        if st.button("Completar Perfil", use_container_width=True, type="primary"):
            st.session_state.page = "profile"
            st.rerun()
        return
    
    summary = services["nutrition"].get_daily_summary()
    streak = services["gamification"].calculate_streak()
    w = user.get("current_weight", 70.0)
    goal = user.get("goal_weight", 65.0)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: card_metric(f"{summary.get('calories', 0)}", "Calorias", "🔥")
    with c2: card_metric(f"{streak}", "Dias", "🔥", "#f59e0b")
    with c3: card_metric(f"{w:.1f} kg", "Peso", "️", "#10b981")
    with c4: card_metric(f"{w - goal:+.1f} kg", "Meta", "🎯", "#8b5cf6")
    
    tmb = services["nutrition"].calculate_tmb(w, user.get("height", 170), user.get("age", 30))
    meta = services["nutrition"].calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))
    percent = min(100, int((summary['calories'] / meta) * 100)) if meta > 0 else 0
    st.markdown(f"**Meta diária:** {meta} kcal ({percent}%)")
    progress_bar(percent)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🍴 Registrar Refeição", use_container_width=True, type="primary"):
            st.session_state.page = "meals"; st.rerun()
    with c2:
        if st.button("️ Registrar Peso", use_container_width=True):
            st.session_state.page = "weight"; st.rerun()
    with c3:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard(services, user):
    st.title("📊 Dashboard Completo")
    summary = services["nutrition"].get_daily_summary()
    streak = services["gamification"].calculate_streak()
    
    c1, c2, c3 = st.columns(3)
    with c1: card_metric(f"{summary.get('calories', 0)} kcal", "Consumo", "🔥")
    with c2: card_metric(f"{summary.get('protein', 0):.1f}g", "Proteínas", "", "#10b981")
    with c3: card_metric(f"{streak} dias", "Sequência", "🔥", "#f59e0b")
    
    st.subheader("📈 Últimos 7 Dias")
    weekly = services["nutrition"].get_weekly_summary()
    if not weekly.empty:
        try:
            import plotly.express as px
            fig = px.line(weekly, x='date', y='calories', markers=True, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        except: st.write(weekly)
    else: empty_state("", "Sem dados", "Registre refeições por 2 dias.")
    
    st.subheader("🥗 Macronutrientes do Dia")
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Proteínas", f"{summary.get('protein', 0):.1f}g")
    with m2: st.metric("Carbos", f"{summary.get('carbs', 0):.1f}g")
    with m3: st.metric("Gorduras", f"{summary.get('fat', 0):.1f}g")
    with m4: st.metric("Fibras", f"{summary.get('fiber', 0):.1f}g")

# =====================================================================
# 10. RENDER MEALS (A TELA MELHORADA QUE VOCÊ PEDIU)
# =====================================================================
def render_meals(services, user):
    """Tela de registro alimentar otimizada e motivacional."""
    st.title("️ Registro Alimentar")
    st.markdown(f"**{user.get('name', 'Usuário')}** • {date.today().strftime('%d/%m/%Y')}")
    
    # 1. TIPO DE REFEIÇÃO (Detecção automática de período)
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 10: periodo_idx = 0
    elif 10 <= hora_atual < 14: periodo_idx = 1
    elif 14 <= hora_atual < 18: periodo_idx = 2
    elif 18 <= hora_atual < 21: periodo_idx = 3
    else: periodo_idx = 4
    
    # Categorias fixas para garantir que Almoço e Jantar apareçam
    opcoes_refeicao = ["Café da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"]
    mapeamento_categoria = {
        "Café da Manhã": "cafe_manha",
        "Almoço": "almoco_jantar",
        "Lanche da Tarde": "lanche",
        "Jantar": "almoco_jantar",
        "Ceia": "ceia"
    }
    
    tipo_refeicao = st.selectbox(
        "🍽️ Qual refeição?",
        options=opcoes_refeicao,
        index=periodo_idx
    )
    categoria = mapeamento_categoria[tipo_refeicao]
    
    # 2. HORÁRIO (Obrigatório e automático)
    col1, col2 = st.columns([3, 2])
    with col1:
        hora_registro = st.time_input(
            "⏰ Horário da refeição", 
            value=datetime.now().time(),
            help="O sistema marcará exatamente o horário para suas análises futuras."
        )
    with col2:
        hora_int = int(hora_registro.strftime("%H"))
        periodo_dia = "Manhã" if hora_int < 12 else "Tarde" if hora_int < 18 else "Noite"
        st.info(f"🌅 Período detectado: **{periodo_dia}**")
    
    # 3. BUSCA E SELEÇÃO DE ALIMENTOS
    st.markdown("---")
    st.subheader("🥗 O que você comeu?")
    
    # Campo de texto que filtra a lista abaixo
    termo = st.text_input(
        "🔍 Digite o nome do alimento...", 
        placeholder="Ex: arroz, frango, banana...",
        help="Comece a digitar para filtrar a lista abaixo"
    )
    
    # Busca os alimentos do banco (Supabase ou Local)
    if termo:
        alimentos = services["foods"].search_foods(termo, categoria)
    else:
        alimentos = services["foods"].get_foods_by_category(categoria)
    
    if not alimentos:
        st.warning("⚠️ Nenhum alimento encontrado nesta categoria.")
        st.info(" Dica: Tente buscar por outra categoria ou adicione um alimento personalizado.")
        return
    
    # Prepara opções para o Selectbox
    # ATENÇÃO: Sem mostrar calorias aqui, conforme solicitado!
    opcoes_display = {}
    for food in alimentos:
        # Compatibilidade entre Supabase dict e Local dict
        food_name = food.get("name", "")
        portion = food.get("portion_size", food.get("portion", "100g"))
        label = f"{food_name} • {portion}"
        opcoes_display[label] = food
    
    # Ordena alfabeticamente
    opcoes_ordenadas = sorted(list(opcoes_display.keys()))
    
    alimento_selecionado = st.selectbox(
        "Selecione o alimento na lista",
        options=opcoes_ordenadas,
        placeholder="Digite no campo acima para filtrar...",
        index=0 if opcoes_ordenadas else None
    )
    
    if alimento_selecionado:
        dados_alimento = opcoes_display[alimento_selecionado]
        food_key = dados_alimento.get("id", dados_alimento.get("name", ""))
        porcao_info = dados_alimento.get("portion_size", dados_alimento.get("portion", "100g"))
        
        st.caption(f"📏 Porção padrão: **{porcao_info}**")
        
        # 4. QUANTIDADE E MEIA PORÇÃO
        col1, col2 = st.columns([2, 2])
        with col1:
            qtd = st.number_input(
                "Quantidade (em porções)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="Quantas vezes a porção padrão você consumiu?"
            )
        with col2:
            meia_porcao = st.checkbox(
                "🔄 Marcar como Meia Porção (÷2)",
                value=False,
                help="Ideal para lanches rápidos ou porções pequenas"
            )
        
        qtd_final = qtd * 0.5 if meia_porcao else qtd
        if meia_porcao:
            st.info(f"✅ Quantidade ajustada para **{qtd_final:.1f}x** da porção padrão.")
        
        # 5. BOTÃO DE REGISTRO
        st.markdown("---")
        if st.button("✅ Confirmar e Salvar Refeição", type="primary", use_container_width=True):
            ok, nome, cal_unit = services["nutrition"].register_food(
                food_key, 
                qtd_final, 
                hora_registro.strftime("%H:%M")
            )
            
            if ok:
                # Busca o total atualizado
                summary = services["nutrition"].get_daily_summary()
                
                st.success(f"✅ **{nome}** registrado com sucesso!")
                # Mostra APENAS o total do dia, não as calorias do item
                st.info(f" Seu total calórico do dia agora é: **{summary['calories']} kcal**")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Erro ao registrar a refeição.")
        
        # 6. RESUMO DO DIA
        st.markdown("---")
        st.subheader("📋 Suas refeições de hoje")
        summary = services["nutrition"].get_daily_summary()
        
        if summary.get('meals'):
            # Mostra apenas o total geral
            st.metric("🔥 Total calórico acumulado hoje", f"{summary['calories']} kcal")
            
            st.markdown("**Histórico do dia:**")
            for m in summary['meals']:
                st.markdown(f"• **{m.get('meal_time', '--:--')}** - {m.get('food', '?')}")
        else:
            empty_state("🍽️", "Nenhuma refeição registrada hoje", "Que tal começar agora? É rápido e fácil!")

def render_weight(services, user):
    st.title("⚖️ Evolução de Peso")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Registrar Pesagem**")
        peso = st.number_input("Peso (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)), 0.1)
        notas = st.text_area("Observações", placeholder="Ex: Jejum, pós-treino...")
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
                fig.add_trace(go.Scatter(x=df['log_date'], y=df['weight'], mode='lines+markers', line=dict(color='#0891b2', width=3)))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Data", yaxis_title="Peso (kg)", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            except: st.write(df)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Primeiro", f"{df.iloc[0]['weight']:.1f} kg")
            with c2: st.metric("Atual", f"{df.iloc[-1]['weight']:.1f} kg")
            with c3: st.metric("Variação", f"{df.iloc[-1]['weight'] - df.iloc[0]['weight']:+.1f} kg", delta_color="inverse")
        else: empty_state("⚖️", "Sem pesagens", "Faça seu primeiro registro ao lado.")

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
    desafios = [{"t": "7 Refeições Registradas", "xp": 50}, {"t": "Meta Calórica Atingida", "xp": 120}, {"t": "Hidratação Total", "xp": 60}]
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
            objetivo = st.selectbox("Objetivo", ["lose", "maintain", "gain"], index=["lose", "maintain", "gain"].index(user.get("goal", "lose")), format_func=lambda x: {"lose": "Emagrecer", "maintain": "Manter", "gain": "Ganhar Massa"}[x])
            atividade = st.selectbox("Atividade", ["sedentary", "light", "moderate", "active"], index=["sedentary", "light", "moderate", "active"].index(user.get("activity_level", "moderate")), format_func=lambda x: {"sedentary": "Sedentário", "light": "Leve", "moderate": "Moderado", "active": "Ativo"}[x])
        if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
            dados = {"name": nome, "current_weight": peso, "height": altura, "age": idade, "goal_weight": meta, "goal": objetivo, "activity_level": atividade}
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
                user["plan"] = "pro"; st.session_state.user = user; services["db"].update_profile({"plan": "pro"}); st.success("Plano PRO ativado!"); st.rerun()
        with c2:
            st.markdown("**Vitalício** - R$ 497,00")
            if st.button("Assinar Vitalício", use_container_width=True):
                user["plan"] = "lifetime"; st.session_state.user = user; services["db"].update_profile({"plan": "lifetime"}); st.success("Plano Vitalício ativado!"); st.rerun()

# ============================================================
# 11. MAIN
# ============================================================
def main():
    load_css()
    services = init_services()
    if not services:
        st.error("❌ Falha ao inicializar o sistema.")
        st.stop()
    
    user = st.session_state.user
    if user is None:
        render_login(services["db"])
        return
    
    render_sidebar(services)
    page = st.session_state.page
    
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
