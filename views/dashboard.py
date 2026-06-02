import streamlit as st
import plotly.express as px
from components import card_metric, progress_bar, section_header, empty_state
from utils.safe_data import get_daily_summary_safe, get_streak_safe

def render_dashboard(services: dict, user: dict):
    section_header("Dashboard Completo", "Visão geral do seu desempenho nutricional.", "📊")
    
    summary = get_daily_summary_safe(services["nutrition"])
    streak = get_streak_safe(services["gamification"])
    
    # Cards Superiores
    col1, col2, col3 = st.columns(3)
    with col1: card_metric(f"{summary.get('calories', 0)} kcal", "Consumo Hoje", "")
    with col2: card_metric(f"{summary.get('proteins', 0):.1f}g", "Proteínas", "", "#10b981")
    with col3: card_metric(f"{streak} dias", "Sequência Atual", "", "#f59e0b")

    # Gráfico de 7 Dias (Requisito Fase 2)
    st.markdown("---")
    section_header("Evolução Calórica", "Últimos 7 dias", "📈")
    
    weekly_data = services["nutrition"].get_weekly_summary()
    if not weekly_data.empty:
        fig = px.line(weekly_data, x='date', y='calories', markers=True, 
                      title="Calorias Consumidas por Dia", 
                      template="plotly_white")
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        empty_state("📊", "Sem dados suficientes", "Registre refeições por 2 dias para ver o gráfico.")

    # Macronutrientes Detalhados
    section_header("Macronutrientes do Dia", "Distribuição dos macros", "")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1: st.metric("Proteínas", f"{summary.get('proteins', 0):.1f}g")
    with m_col2: st.metric("Carboidratos", f"{summary.get('carbs', 0):.1f}g")
    with m_col3: st.metric("Gorduras", f"{summary.get('fats', 0):.1f}g")

    # Conquistas Recentes
    section_header("Conquistas Recentes", "Suas insígnias desbloqueadas", "🏆")
    achs = services["db"].get_achievements()
    if achs:
        cols = st.columns(min(3, len(achs)))
        for i, a in enumerate(achs[:3]):
            with cols[i]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 2rem;">🏅</div>
                    <div style="font-weight: 600; font-size: 0.9rem;">{a.get('title', 'Conquista')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        empty_state("🏆", "Nenhuma conquista ainda", "Continue registrando para desbloquear!")
