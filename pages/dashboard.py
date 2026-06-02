import streamlit as st
import random
from datetime import datetime
from core.nutrition import NutritionService
from core.gamification import GamificationSystem
from core.database import AppDatabase

def get_random_message(category: str, db: AppDatabase) -> dict:
    """Busca mensagem aleatória do banco ou fallback"""
    if db.is_real and db.client:
        try:
            result = db.client.table("motivational_messages").select("*").eq("category", category).eq("is_active", True).execute()
            if result.data:
                return random.choice(result.data)
        except:
            pass
    
    # Fallback local
    fallbacks = {
        "login": [
            {"message": "Que bom ter você de volta! 💪", "emoji": "👋"},
            {"message": "Cada dia é uma nova chance.", "emoji": "🌱"},
        ],
        "streak": [
            {"message": "Mais um dia registrado! 🔥", "emoji": ""},
        ],
        "meal": [
            {"message": "Registro feito! Consciência em ação.", "emoji": "✅"},
        ],
    }
    return random.choice(fallbacks.get(category, fallbacks["login"]))

def get_daily_tip(db: AppDatabase) -> dict:
    """Busca dica do dia"""
    if db.is_real and db.client:
        try:
            result = db.client.table("daily_tips").select("*").eq("is_active", True).execute()
            if result.data:
                today = datetime.now().day
                return result.data[today % len(result.data)]
        except:
            pass
    
    return {"tip": "Beba água ao acordar!", "emoji": "💧"}

def get_welcome_message() -> str:
    """Mensagem baseada no horário"""
    hour = datetime.now().hour
    if hour < 12:
        return "☀️ Bom dia! Um novo dia, novas oportunidades."
    elif hour < 18:
        return "🌤️ Boa tarde! Que tal revisar suas metas?"
    else:
        return "🌙 Boa noite! Reflita sobre suas conquistas."

def render_dashboard(nutrition: NutritionService, gamification: GamificationSystem, user: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # Mensagem de boas-vindas dinâmica
    st.info(get_welcome_message())
    
    # Dica do dia
    tip = get_daily_tip(nutrition.db)
    st.success(f"{tip.get('emoji', '💡')} {tip.get('tip', 'Dica do dia')}")
    
    today_summary = nutrition.get_daily_summary()
    
    w = user.get("current_weight") or 70.0
    h = user.get("height") or 170.0
    a = user.get("age") or 30
    
    tmb = nutrition.calculate_tmb(weight=float(w), height=float(h), age=int(a))
    daily_goal = nutrition.calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))
    remaining = daily_goal - today_summary["calories"]
    streak = gamification.calculate_streak()
    
    # Verifica conquistas e mostra mensagem
    unlocked = gamification.check_achievements(today_summary["count"], streak)
    if unlocked:
        for achievement in unlocked:
            msg = get_random_message("achievement", nutrition.db)
            st.success(f"🏆 {achievement} - {msg.get('message', '')} {msg.get('emoji', '')}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.markdown(f'<div class="data-card"><div class="data-value">{today_summary["calories"]}</div><div class="data-label">Calorias Consumidas</div><div style="font-size:0.75rem;margin-top:4px;color:{"#10b981" if remaining>=0 else "#ef4444"}">Restam {remaining} kcal</div></div>', unsafe_allow_html=True)
    with col2: 
        st.markdown(f'<div class="data-card"><div class="data-value">{today_summary["count"]}</div><div class="data-label">Refeições Hoje</div></div>', unsafe_allow_html=True)
    with col3: 
        st.markdown(f'<div class="data-card"><div class="data-value">{w} <span style="font-size:1rem;">kg</span></div><div class="data-label">Peso Atual</div></div>', unsafe_allow_html=True)
    with col4: 
        st.markdown(f'<div class="data-card"><div class="data-value">🔥 {streak}</div><div class="data-label">Dias Seguidos</div></div>', unsafe_allow_html=True)
    
    percent = min(100, int((today_summary['calories'] / daily_goal) * 100)) if daily_goal > 0 else 0
    st.markdown(f'<div style="margin:0.5rem 0 1.5rem 0;"><div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#475569;"><span>Consumo da Meta Diária ({daily_goal} kcal)</span><span>{percent}%</span></div><div class="progress-container"><div class="progress-bar" style="width:{percent}%;"></div></div></div>', unsafe_allow_html=True)
    
    st.subheader("Macronutrientes do Dia")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Proteínas", f"{today_summary['proteins']}g")
    m_col2.metric("Carboidratos", f"{today_summary['carbs']}g")
    m_col3.metric("Gorduras", f"{today_summary['fats']}g")
    
    if today_summary['meals']:
        st.markdown("### 📋 Alimentos Registrados Hoje")
        for meal in today_summary['meals']:
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.75rem 0;border-bottom:1px solid #e2e8f0;"><div><span style="font-weight:600;color:#0f172a;">{meal.get("meal_time", "--:--")}</span><span style="margin-left:1rem;color:#334155;">{meal.get("food", "?")}</span><span style="margin-left:0.5rem;font-size:0.8rem;color:#64748b;">(x{meal.get("quantity", 1)})</span></div><div style="font-weight:600;color:#0891b2;">{meal.get("calories", 0)} kcal</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
