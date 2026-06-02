import streamlit as st
from core.nutrition import NutritionService
from core.gamification import GamificationSystem

def render_dashboard(nutrition: NutritionService, gamification: GamificationSystem, user: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    today_summary = nutrition.get_daily_summary()
    
    w = user.get("current_weight") or 70.0
    h = user.get("height") or 170.0
    a = user.get("age") or 30
    
    tmb = nutrition.calculate_tmb(weight=float(w), height=float(h), age=int(a))
    daily_goal = nutrition.calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))
    remaining = daily_goal - today_summary["calories"]
    streak = gamification.calculate_streak()
    
    gamification.check_achievements(today_summary["count"], streak)
    
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
