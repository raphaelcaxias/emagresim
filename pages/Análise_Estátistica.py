import streamlit as st
from core.nutrition import NutritionService
from core.analytics import AnalyticsService

def render_stats(nutrition: NutritionService, analytics: AnalyticsService):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.header("📊 Inteligência Analítica e Métricas")
    report = analytics.get_full_report(days=30)
    
    tab1, tab2, tab3 = st.tabs(["Padrões de Consumo", "Tendência de Peso", "Conquistas Obtidas"])
    
    with tab1:
        patterns = report["meal_patterns"]
        if patterns.get("has_data"):
            col1, col2 = st.columns(2)
            col1.metric("Média por Refeição", f"{patterns['avg_calories_per_meal']} kcal")
            col2.metric("Calorias Noturnas (Pós 20h)", f"{patterns['percent_after_8pm']}%")
            st.markdown("#### Divisão Calórica por Período:")
            for period, cals in patterns["period_calories"].items():
                st.markdown(f"- **{period.capitalize()}**: {cals} kcal acumuladas")
        else: st.info("Dados alimentares insuficientes neste mês.")
            
    with tab2:
        trend = report["weight_trend"]
        if trend.get("has_data"):
            if trend.get("insufficient_data"): st.info("Gere pelo menos 2 registros de peso para extrair tendências matemáticas.")
            else:
                col1, col2 = st.columns(2)
                col1.metric("Variação Absoluta Bruta", f"{trend['total_change']:+.1f} kg")
                col2.metric("Velocidade de Mudança", f"{trend['trend_rate']:+.2f} kg / semana")
        else: st.info("Sem dados de pesagem cadastrados.")
            
    with tab3:
        achievements = nutrition.db.get_achievements()
        if achievements:
            st.markdown("#### Conquistas Desbloqueadas no Sistema:")
            for ac in achievements: st.markdown(f"- {ac.get('title')} — *Liberado em {ac.get('unlocked_at')}*")
        else: st.info("Continue registrando suas metas para desbloquear insígnias.")
    st.markdown('</div>', unsafe_allow_html=True)
