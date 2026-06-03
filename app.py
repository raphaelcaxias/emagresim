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
    page_title="EmagreSim - Sua Jornada Fitness",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "EmagreSim v2.0 - Monitoramento nutricional inteligente"}
)

# ============================================================
# 2. CSS PROFISSIONAL
# ============================================================
CSS_PRO = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .fade-in { animation: fadeIn 0.5s ease-in; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .hero-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 3rem 2rem; border-radius: 20px;
        margin-bottom: 2rem; text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero-title { font-size: 3rem; font-weight: 700; margin: 0; }
    .hero-subtitle { font-size: 1.2rem; margin: 1rem 0 0 0; opacity: 0.95; }
    .feature-card {
        background: white; border-radius: 16px; padding: 2rem;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s; margin-bottom: 1rem;
    }
    .feature-card:hover { transform: translateY(-5px); }
    .data-card {
        background: white; border-radius: 12px; padding: 1.25rem;
        border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .data-value { font-size: 2rem; font-weight: 700; color: #667eea; }
    .data-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; }    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); }
    [data-testid="stSidebar"] * { color: #f1f5f9; }
</style>
"""

def load_css():
    try:
        if os.path.exists("assets/style.css"):
            with open("assets/style.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            st.markdown(CSS_PRO, unsafe_allow_html=True)
    except Exception:
        st.markdown(CSS_PRO, unsafe_allow_html=True)

# ============================================================
# 3. ESTADO GLOBAL
# ============================================================
def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "demo_data_loaded" not in st.session_state:
        st.session_state.demo_data_loaded = False

init_session_state()

# ============================================================
# 4. BANCO DE DADOS (com indentação correta)
# ============================================================
try:
    from core.database import AppDatabase
except Exception:
    class AppDatabase:
        def __init__(self):
            self.is_real = False
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
                            "activity_level": "moderate",                            "goal": "lose"
                        }
                    },
                    "meals": [],
                    "weights": [],
                    "achievements": []
                }

        def get_current_user_id(self):
            u = st.session_state.get("user")
            return u.get("email", "anonymous") if u else "anonymous"

        def get_user(self, email, password):
            users = st.session_state.mock_db.get("users", {})
            if email in users and users[email].get("password") == password:
                return users[email]
            return None

        def create_user(self, email, password, name):
            users = st.session_state.mock_db.get("users", {})
            if email in users:
                return False
            users[email] = {
                "password": password,
                "name": name,
                "email": email,
                "plan": "free",
                "current_weight": 70.0,
                "goal_weight": 65.0,
                "height": 170,
                "age": 30,
                "activity_level": "moderate",
                "goal": "lose"
            }
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
            uid = self.get_current_user_id()            meals = [m for m in st.session_state.mock_db.get("meals", []) if m.get("user_id") == uid]
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
            if not w:
                return pd.DataFrame(columns=['log_date', 'weight'])
            df = pd.DataFrame(w)
            df['log_date'] = pd.to_datetime(df['log_date'])
            return df.sort_values('log_date')

        def unlock_achievement(self, name, title):
            uid = self.get_current_user_id()
            achs = st.session_state.mock_db.get("achievements", [])
            for a in achs:
                if a.get("achievement_name") == name and a.get("user_id") == uid:
                    return False
            achs.append({
                "user_id": uid,
                "achievement_name": name,
                "title": title,
                "unlocked_at": str(date.today())
            })
            st.session_state.mock_db["achievements"] = achs
            return True

        def get_achievements(self):
            uid = self.get_current_user_id()
            return [a for a in st.session_state.mock_db.get("achievements", []) if a.get("user_id") == uid]

# ============================================================
# 5. FOOD SERVICE
# ============================================================
FALLBACK_FOODS = {
    "arroz_branco": {"name": "Arroz Branco", "category": "almoco_jantar", "calories": 130, "protein": 2.5, "carbs": 28, "fat": 0.3, "portion": "100g"},    "feijao_preto": {"name": "Feijão Preto", "category": "almoco_jantar", "calories": 77, "protein": 4.5, "carbs": 14, "fat": 0.5, "portion": "100g"},
    "peito_frango": {"name": "Peito de Frango", "category": "almoco_jantar", "calories": 160, "protein": 32, "carbs": 0, "fat": 3.5, "portion": "100g"},
    "banana_prata": {"name": "Banana Prata", "category": "frutas", "calories": 90, "protein": 1.5, "carbs": 23, "fat": 0.2, "portion": "1 unidade"},
    "ovo_cozido": {"name": "Ovo Cozido", "category": "cafe_manha", "calories": 145, "protein": 13, "carbs": 1.5, "fat": 9.5, "portion": "1 unidade"},
    "pao_frances": {"name": "Pão Francês", "category": "cafe_manha", "calories": 300, "protein": 8, "carbs": 58, "fat": 3, "portion": "1 unidade"},
    "leite_integral": {"name": "Leite Integral", "category": "cafe_manha", "calories": 60, "protein": 3, "carbs": 4.5, "fat": 3.3, "portion": "100ml"},
    "alface": {"name": "Alface", "category": "almoco_jantar", "calories": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2, "portion": "100g"},
}

class FoodService:
    def __init__(self):
        self.use_supabase = False

    def get_categories(self):
        return [
            {"name": "Café da Manhã", "code": "cafe_manha"},
            {"name": "Almoço", "code": "almoco_jantar"},
            {"name": "Lanche", "code": "lanche"},
            {"name": "Jantar", "code": "almoco_jantar"},
            {"name": "Ceia", "code": "ceia"}
        ]

    def get_foods_by_category(self, cat):
        return [v for v in FALLBACK_FOODS.values() if v.get("category") == cat]

    def search_foods(self, term, cat=None):
        term = term.lower() if term else ""
        return [
            v for v in FALLBACK_FOODS.values()
            if (not cat or v.get("category") == cat)
            and (not term or term in v["name"].lower())
        ]

# ============================================================
# 6. SERVIÇOS CORE
# ============================================================
class NutritionService:
    def __init__(self, db):
        self.db = db

    def calculate_tmb(self, w, h, a, g="male"):
        if not all([w, h, a]):
            return 1500
        if g == "male":
            return int(10 * w + 6.25 * h - 5 * a + 5)
        return int(10 * w + 6.25 * h - 5 * a - 161)

    def calculate_daily_goal(self, tmb, act="moderate", goal="lose"):
        factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
        maintenance = int(tmb * factors.get(act, 1.55))        if goal == "lose":
            return max(1200, maintenance - 500)
        elif goal == "gain":
            return maintenance + 300
        return maintenance

    def get_daily_summary(self, date_str=None):
        if not date_str:
            date_str = str(date.today())
        meals = self.db.get_meals_by_date(date_str)
        return {
            "calories": sum(int(m.get("calories", 0)) for m in meals),
            "protein": sum(float(m.get("protein", 0)) for m in meals),
            "carbs": sum(float(m.get("carbs", 0)) for m in meals),
            "fat": sum(float(m.get("fat", 0)) for m in meals),
            "count": len(meals),
            "meals": sorted(meals, key=lambda x: x.get("meal_time", "00:00"))
        }

    def get_weekly_summary(self):
        import pandas as pd
        meals = self.db.get_meals(days=7)
        if not meals:
            return pd.DataFrame()
        df = pd.DataFrame(meals)
        df['meal_date'] = pd.to_datetime(df['meal_date'])
        return df.groupby(df['meal_date'].dt.date).agg(
            calories=('calories', 'sum')
        ).reset_index().rename(columns={'meal_date': 'date'})

    def register_food(self, food_id, quantity, meal_time=None):
        food = FALLBACK_FOODS.get(food_id) if isinstance(food_id, str) else food_id
        if not food:
            return False, None, 0
        if not meal_time:
            meal_time = datetime.now().strftime("%H:%M")
        meal_data = {
            "food": food["name"],
            "quantity": float(quantity),
            "calories": int(food["calories"] * quantity),
            "protein": round(food.get("protein", 0) * quantity, 1),
            "carbs": round(food.get("carbs", 0) * quantity, 1),
            "fat": round(food.get("fat", 0) * quantity, 1),
            "meal_date": str(date.today()),
            "meal_time": meal_time
        }
        self.db.save_meal(meal_data)
        return True, food["name"], food["calories"]

class GamificationSystem:    def __init__(self, db):
        self.db = db

    def calculate_streak(self):
        meals = self.db.get_meals(days=30)
        if not meals:
            return 0
        dates = sorted(set(m.get("meal_date") for m in meals if m.get("meal_date")))
        if not dates:
            return 0
        date_objs = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in dates])
        if date_objs[-1] not in [date.today(), date.today() - timedelta(days=1)]:
            return 0
        streak = 1
        for i in range(len(date_objs) - 1, 0, -1):
            if (date_objs[i] - date_objs[i-1]).days == 1:
                streak += 1
            else:
                break
        return streak

class PaymentService:
    PLANS = {"free": {"name": "Gratuito"}, "pro": {"name": "Pro", "price": 29.90}}

    def create_checkout_link(self, plan, email):
        return "#"

# ============================================================
# 7. INICIALIZAÇÃO
# ============================================================
@st.cache_resource(show_spinner=False)
def init_services():
    db = AppDatabase()
    return {
        "db": db,
        "nutrition": NutritionService(db),
        "gamification": GamificationSystem(db),
        "payment": PaymentService(),
        "foods": FoodService()
    }

# ============================================================
# 8. CARREGAR DADOS DEMO
# ============================================================
def load_demo_data(services):
    if st.session_state.demo_data_loaded:
        return
    user = st.session_state.user
    if not user or user.get("email") != "demo@emagresim.com":
        return    db = services["db"]
    if len(db.get_meals(days=30)) > 0:
        st.session_state.demo_data_loaded = True
        return

    demo_meals = [
        {"food": "Café com Leite", "calories": 120, "protein": 6, "carbs": 12, "fat": 4, "meal_time": "07:30", "days_ago": 0},
        {"food": "Pão Francês", "calories": 150, "protein": 4, "carbs": 28, "fat": 2, "meal_time": "07:35", "days_ago": 0},
        {"food": "Arroz Branco", "calories": 200, "protein": 4, "carbs": 44, "fat": 0.5, "meal_time": "12:30", "days_ago": 0},
        {"food": "Feijão Preto", "calories": 100, "protein": 6, "carbs": 18, "fat": 0.5, "meal_time": "12:35", "days_ago": 0},
        {"food": "Peito de Frango", "calories": 180, "protein": 35, "carbs": 0, "fat": 4, "meal_time": "12:40", "days_ago": 0},
        {"food": "Banana Prata", "calories": 90, "protein": 1.5, "carbs": 23, "fat": 0.2, "meal_time": "15:30", "days_ago": 1},
        {"food": "Ovo Cozido", "calories": 75, "protein": 6.5, "carbs": 0.6, "fat": 5, "meal_time": "08:00", "days_ago": 2},
        {"food": "Alface", "calories": 10, "protein": 0.7, "carbs": 2, "fat": 0.1, "meal_time": "12:30", "days_ago": 3},
    ]
    for meal in demo_meals:
        meal_data = {
            "food": meal["food"],
            "quantity": 1.0,
            "calories": meal["calories"],
            "protein": meal["protein"],
            "carbs": meal["carbs"],
            "fat": meal["fat"],
            "meal_date": str(date.today() - timedelta(days=meal["days_ago"])),
            "meal_time": meal["meal_time"],
            "user_id": "demo@emagresim.com"
        }
        db.save_meal(meal_data)

    for i in range(7):
        db.save_weight({
            "weight": 75.0 - (i * 0.2),
            "log_date": str(date.today() - timedelta(days=i)),
            "notes": "Medição matinal",
            "user_id": "demo@emagresim.com"
        })

    st.session_state.demo_data_loaded = True

# ============================================================
# 9. LANDING PAGE
# ============================================================
def render_landing(services):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">💪 EmagreSim</h1>
        <p class="hero-subtitle">Transforme sua saúde com monitoramento inteligente e baseado em dados</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### ✨ Por que usar o EmagreSim?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3rem;">📊</div>
            <h3>Controle Total</h3>
            <p>Acompanhe calorias, macros e evolução de peso em tempo real</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3rem;">🎯</div>
            <h3>Metas Inteligentes</h3>
            <p>Cálculos automáticos baseados no seu perfil e objetivos</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3rem;">🏆</div>
            <h3>Gamificação</h3>
            <p>Conquistas e streaks para manter você motivado</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### 🚀 Comece agora mesmo!")
        st.markdown("**É grátis, rápido e você pode começar em segundos.**")
    with c2:
        if st.button("🎮 Experimentar Demo", use_container_width=True, type="primary"):
            demo_user = {
                "email": "demo@emagresim.com",
                "password": "demo",
                "name": "Usuário Demo",
                "plan": "pro",
                "current_weight": 75.0,
                "goal_weight": 70.0,
                "height": 170,
                "age": 30,
                "activity_level": "moderate",
                "goal": "lose"
            }
            if "mock_db" not in st.session_state:
                st.session_state.mock_db = {"users": {}, "meals": [], "weights": [], "achievements": []}
            if "users" not in st.session_state.mock_db:                st.session_state.mock_db["users"] = {}
            st.session_state.mock_db["users"]["demo@emagresim.com"] = demo_user
            st.session_state.user = demo_user
            st.session_state.page = "home"
            st.session_state.demo_data_loaded = False
            st.rerun()

    st.markdown("---")
    st.markdown("### 📈 Resultados que nossos usuários alcançam")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Usuários Ativos", "10,000+")
    with c2:
        st.metric("Refeições Registradas", "500,000+")
    with c3:
        st.metric("Média de Perda", "4.5 kg/mês")
    with c4:
        st.metric("Satisfação", "98%")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 10. SIDEBAR
# ============================================================
def render_sidebar(services):
    user = st.session_state.user
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0; border-bottom: 1px solid #334155;">
            <h2 style="margin: 0; color: #667eea;">💪 EmagreSim</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #94a3b8;">v2.0 Pro</p>
        </div>
        """, unsafe_allow_html=True)

        plan = user.get("plan", "free")
        badge_color = "#f59e0b" if plan in ["pro", "lifetime"] else "#64748b"
        st.markdown(f'<div style="background: {badge_color}20; color: {badge_color}; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: 600; margin: 1rem 0; border: 1px solid {badge_color};">👑 PLANO {plan.upper()}</div>', unsafe_allow_html=True)

        st.markdown(f"**👤 {user.get('name')}**\n📧 {user.get('email')}")

        summary = services["nutrition"].get_daily_summary()
        streak = services["gamification"].calculate_streak()

        st.markdown("---\n**📊 Resumo de Hoje**")
        st.metric("🔥 Calorias", f"{summary.get('calories', 0)} kcal")
        st.metric("🍽️ Refeições", summary.get('count', 0))
        st.metric("🔥 Sequência", f"{streak} dias")

        st.markdown("---\n** Menu**")
        pages = [            ("🏠 Início", "home"),
            ("📊 Dashboard", "dashboard"),
            (" Registrar Refeição", "meals"),
            ("⚖️ Evolução Peso", "weight"),
            ("📈 Análise", "analysis"),
            ("👤 Perfil", "profile")
        ]
        for label, key in pages:
            if st.button(label, use_container_width=True, type="primary" if st.session_state.page == key else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "landing"
            st.session_state.demo_data_loaded = False
            st.rerun()

# ============================================================
# 11. VIEWS
# ============================================================
def render_home(services, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    hour = datetime.now().hour
    saudacao = "☀️ Bom dia!" if hour < 12 else "🌤️ Boa tarde!" if hour < 18 else " Boa noite!"
    st.markdown(f'<div class="hero-banner" style="padding: 2rem;"><h1 style="margin:0; font-size: 2.5rem;">{saudacao} {user.get("name")}!</h1><p>Vamos analisar seu progresso de hoje</p></div>', unsafe_allow_html=True)

    summary = services["nutrition"].get_daily_summary()
    streak = services["gamification"].calculate_streak()
    w = user.get("current_weight", 70.0)
    goal = user.get("goal_weight", 65.0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="data-card"><div class="data-value">{summary.get("calories", 0)}</div><div class="data-label">🔥 Calorias</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="data-card"><div class="data-value">{streak}</div><div class="data-label">🔥 Dias</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="data-card"><div class="data-value">{w:.1f}</div><div class="data-label">⚖️ Peso</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="data-card"><div class="data-value">{w - goal:+.1f}</div><div class="data-label">🎯 Meta</div></div>', unsafe_allow_html=True)

    tmb = services["nutrition"].calculate_tmb(w, user.get("height", 170), user.get("age", 30))
    meta = services["nutrition"].calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))
    percent = min(100, int((summary['calories'] / meta) * 100)) if meta > 0 else 0

    st.markdown(f"**Meta diária:** {meta} kcal ({percent}%)")
    st.markdown(f"""
    <div style="background: #e2e8f0; border-radius: 9999px; height: 0.75rem; overflow: hidden; margin: 0.5rem 0;">        <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: {percent}%; transition: width 0.5s;"></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🍴 Registrar Refeição", use_container_width=True, type="primary"):
            st.session_state.page = "meals"
            st.rerun()
    with c2:
        if st.button("⚖️ Registrar Peso", use_container_width=True):
            st.session_state.page = "weight"
            st.rerun()
    with c3:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard(services, user):
    st.title("📊 Dashboard Completo")
    summary = services["nutrition"].get_daily_summary()
    streak = services["gamification"].calculate_streak()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🔥 Calorias Hoje", f"{summary.get('calories', 0)} kcal")
    with c2:
        st.metric("💪 Proteínas", f"{summary.get('protein', 0):.1f}g")
    with c3:
        st.metric("🔥 Sequência", f"{streak} dias")

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
        st.info("📊 Sem dados suficientes. Registre refeições para ver o gráfico.")

    st.subheader("🥗 Macronutrientes do Dia")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Proteínas", f"{summary.get('protein', 0):.1f}g")
    with m2:
        st.metric("Carboidratos", f"{summary.get('carbs', 0):.1f}g")
    with m3:        st.metric("Gorduras", f"{summary.get('fat', 0):.1f}g")

def render_meals(services, user):
    st.title("🍴 Registro Alimentar")
    st.markdown(f"**{user.get('name', 'Usuário')}** • {date.today().strftime('%d/%m/%Y')}")

    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 10:
        periodo_idx = 0
    elif 10 <= hora_atual < 14:
        periodo_idx = 1
    elif 14 <= hora_atual < 18:
        periodo_idx = 2
    elif 18 <= hora_atual < 21:
        periodo_idx = 3
    else:
        periodo_idx = 4

    opcoes_refeicao = ["Café da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"]
    mapeamento = {
        "Café da Manhã": "cafe_manha",
        "Almoço": "almoco_jantar",
        "Lanche da Tarde": "lanche",
        "Jantar": "almoco_jantar",
        "Ceia": "ceia"
    }

    tipo_refeicao = st.selectbox("🍽️ Qual refeição?", options=opcoes_refeicao, index=periodo_idx)
    categoria = mapeamento[tipo_refeicao]

    col1, col2 = st.columns([3, 2])
    with col1:
        hora_registro = st.time_input(" Horário", value=datetime.now().time())
    with col2:
        hora_int = int(hora_registro.strftime("%H"))
        periodo_dia = "Manhã" if hora_int < 12 else "Tarde" if hora_int < 18 else "Noite"
        st.info(f" Período: **{periodo_dia}**")

    st.markdown("---")
    st.subheader("🥗 O que você comeu?")

    alimentos = services["foods"].get_foods_by_category(categoria)
    if not alimentos:
        st.warning("⚠️ Nenhum alimento encontrado nesta categoria.")
        return

    opcoes = {f"{a['name']} • {a.get('portion', '100g')}": a for a in alimentos}
    opcoes_ordenadas = sorted(list(opcoes.keys()))

    alimento_selecionado = st.selectbox(        "Digite o nome do alimento...",
        options=opcoes_ordenadas,
        placeholder="Comece a digitar para buscar...",
        index=None
    )

    if alimento_selecionado:
        dados = opcoes[alimento_selecionado]
        food_key = next(k for k, v in opcoes.items() if v == dados)
        # Pega a key real do FALLBACK_FOODS
        for k, v in FALLBACK_FOODS.items():
            if v == dados:
                food_key = k
                break

        st.caption(f"📏 Porção padrão: **{dados.get('portion', '100g')}**")

        c1, c2 = st.columns([2, 2])
        with c1:
            qtd = st.number_input("Quantidade (em porções)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
        with c2:
            meia_porcao = st.checkbox("🔄 Meia porção (÷2)", value=False)

        qtd_final = qtd * 0.5 if meia_porcao else qtd
        if meia_porcao:
            st.info(f"✅ Quantidade ajustada para **{qtd_final:.1f}x**")

        st.markdown("---")
        if st.button("✅ Confirmar e Salvar", type="primary", use_container_width=True):
            ok, nome, cal = services["nutrition"].register_food(food_key, qtd_final, hora_registro.strftime("%H:%M"))
            if ok:
                summary = services["nutrition"].get_daily_summary()
                st.success(f"✅ **{nome}** registrado!")
                st.info(f"🔥 Total do dia: **{summary['calories']} kcal**")
                st.balloons()
                st.rerun()
            else:
                st.error(" Erro ao registrar.")

        st.markdown("---")
        st.subheader("📋 Suas refeições de hoje")
        summary = services["nutrition"].get_daily_summary()
        if summary.get('meals'):
            st.metric("🔥 Total calórico hoje", f"{summary['calories']} kcal")
            for m in summary['meals']:
                st.markdown(f"• **{m.get('meal_time', '--:--')}** - {m.get('food', '?')}")
        else:
            st.info("🍽️ Nenhuma refeição registrada hoje")

def render_weight(services, user):    st.title("⚖️ Evolução de Peso")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Registrar Pesagem**")
        peso = st.number_input("Peso (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)), 0.1)
        notas = st.text_area("Observações", placeholder="Ex: Jejum, pós-treino...")
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            services["db"].save_weight({
                "weight": peso,
                "log_date": str(date.today()),
                "notes": notas,
                "user_id": user.get("email")
            })
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
                fig.add_trace(go.Scatter(x=df['log_date'], y=df['weight'], mode='lines+markers', line=dict(color='#667eea', width=3)))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Data", yaxis_title="Peso (kg)", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.write(df)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Primeiro", f"{df.iloc[0]['weight']:.1f} kg")
            with c2:
                st.metric("Atual", f"{df.iloc[-1]['weight']:.1f} kg")
            with c3:
                st.metric("Variação", f"{df.iloc[-1]['weight'] - df.iloc[0]['weight']:+.1f} kg", delta_color="inverse")
        else:
            st.info("⚖️ Sem pesagens. Faça seu primeiro registro ao lado.")

def render_analysis(services, user):
    st.title(" Análise e Desafios")
    achs = services["db"].get_achievements()
    if achs:
        st.subheader(" Conquistas")
        cols = st.columns(min(3, len(achs)))
        for i, a in enumerate(achs):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 2rem;">🏅</div>                    <div style="font-weight: 600;">{a.get('title', 'Conquista')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma conquista ainda. Continue registrando!")

    st.markdown("---")
    st.subheader("🎯 Desafios da Semana")
    desafios = [
        {"t": "7 Refeições Registradas", "xp": 50},
        {"t": "Meta Calórica Atingida", "xp": 120},
        {"t": "Hidratação Total", "xp": 60}
    ]
    for d in desafios:
        st.markdown(f"""
        <div style="background: #f0f9ff; border-left: 4px solid #0891b2; padding: 1rem; margin-bottom: 0.5rem; border-radius: 4px;">
            <b>🎯 {d['t']}</b>
            <span style="float:right; color: #f59e0b; font-weight:bold;">+{d['xp']} XP</span>
        </div>
        """, unsafe_allow_html=True)

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

        if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
            dados = {
                "name": nome,
                "current_weight": peso,
                "height": altura,
                "age": idade,
                "goal_weight": meta,
                "goal": objetivo,
                "activity_level": atividade
            }            user.update(dados)
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
# 12. MAIN
# ============================================================
def main():
    load_css()
    services = init_services()

    if st.session_state.user is None:
        render_landing(services)
        return

    # Carrega dados demo
    if st.session_state.user.get("email") == "demo@emagresim.com":
        load_demo_data(services)

    render_sidebar(services)

    page = st.session_state.page
    if page == "landing":
        render_landing(services)
    elif page == "home":        render_home(services, st.session_state.user)
    elif page == "dashboard":
        render_dashboard(services, st.session_state.user)
    elif page == "meals":
        render_meals(services, st.session_state.user)
    elif page == "weight":
        render_weight(services, st.session_state.user)
    elif page == "analysis":
        render_analysis(services, st.session_state.user)
    elif page == "profile":
        render_profile(services, st.session_state.user)
    else:
        render_home(services, st.session_state.user)

if __name__ == "__main__":
    main()