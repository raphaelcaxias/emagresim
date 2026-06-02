import streamlit as st
from core.database import AppDatabase
from core.nutrition import NutritionService
from core.analytics import AnalyticsService
from core.gamification import GamificationSystem
from components import card_metric, progress_bar, empty_state

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

@st.cache_resource(show_spinner=False)
def init():
    db = AppDatabase()
    return db, NutritionService(db), AnalyticsService(db), GamificationSystem(db)

db, nutrition, analytics, gamification = init()
user = st.session_state.user

st.title("📊 Dashboard Completo")
st.markdown(f"Olá, **{user.get('name', 'Usuário')}**! Aqui está seu panorama geral.")

# Resumo do dia
summary = nutrition.get_daily_summary()
streak = gamification.calculate_streak()

w = user.get("current_weight") or 70.0
h = user.get("height") or 170
a = user.get("age") or 30
tmb = nutrition.calculate_tmb(w, h, a)
meta = nutrition.calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))

col1, col2, col3, col4 = st.columns(4)
with col1: card_metric(summary['calories'], "Calorias Hoje", "")
with col2: card_metric(summary['count'], "Refeições", "🍽️")
with col3: card_metric(f"{w:.1f} kg", "Peso Atual", "⚖️")
with col4: card_metric(streak, "Dias Seguidos", "")

# Progresso
percent = min(100, int((summary['calories'] / meta) * 100)) if meta > 0 else 0
st.markdown(f"**Meta diária:** {meta} kcal ({percent}% consumido)")
progress_bar(percent)

# Macronutrientes
st.subheader("🥗 Macronutrientes")
col1, col2, col3 = st.columns(3)
with col1: st.metric("Proteínas", f"{summary.get('proteins', 0):.1f}g")
with col2: st.metric("Carboidratos", f"{summary.get('carbs', 0):.1f}g")
with col3: st.metric("Gorduras", f"{summary.get('fats', 0):.1f}g")

# Gráfico semanal
st.subheader(" Últimos 7 Dias")
semanal = nutrition.get_weekly_summary()
if not semanal.empty:
    import plotly.express as px
    fig = px.line(semanal, x='date', y='calories', markers=True)
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    empty_state("📊", "Sem dados ainda", "Registre refeições para ver seu gráfico")
