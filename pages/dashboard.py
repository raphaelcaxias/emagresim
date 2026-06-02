import streamlit as st
from core.database import AppDatabase
from core.nutrition import NutritionService
from core.gamification import GamificationSystem
from core.analytics import AnalyticsService

# Verifica se está logado
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

# Inicializa serviços
@st.cache_resource
def get_services():
    db = AppDatabase()
    return {
        "db": db,
        "nutrition": NutritionService(db),
        "gamification": GamificationSystem(db),
        "analytics": AnalyticsService(db)
    }

services = get_services()
user = st.session_state.user

# Conteúdo da página
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.title("📊 Dashboard Completo")

today_summary = services["nutrition"].get_daily_summary()
streak = services["gamification"].calculate_streak()

w = user.get("current_weight") or 70.0
h = user.get("height") or 170.0
a = user.get("age") or 30

tmb = services["nutrition"].calculate_tmb(weight=float(w), height=float(h), age=int(a))
daily_goal = services["nutrition"].calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))
remaining = daily_goal - today_summary["calories"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="data-card"><div class="data-value">{today_summary["calories"]}</div><div class="data-label">Calorias</div><div style="font-size:0.75rem;color:{"#10b981" if remaining>=0 else "#ef4444"}">Restam {remaining} kcal</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="data-card"><div class="data-value">{today_summary["count"]}</div><div class="data-label">Refeições</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="data-card"><div class="data-value">{w} kg</div><div class="data-label">Peso Atual</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="data-card"><div class="data-value"> {streak}</div><div class="data-label">Dias Seguidos</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
