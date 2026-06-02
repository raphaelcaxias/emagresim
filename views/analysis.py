import streamlit as st
import random
from datetime import datetime
from components import section_header, empty_state, card_metric

def render_analysis(services: dict, user: dict):
    section_header("Análise Inteligente", "Seus dados trabalhando por você.", "📈")
    
    tab1, tab2, tab3 = st.tabs(["🍽️ Padrões", "️ Tendências", "🎯 Desafios"])
    
    with tab1:
        st.markdown("**Padrões Alimentares (30 dias)**")
        patterns = services["analytics"].analyze_meal_patterns(30)
        if patterns.get("has_data"):
            col1, col2 = st.columns(2)
            with col1: st.metric("Média por refeição", f"{patterns['avg_calories_per_meal']:.0f} kcal")
            with col2: st.metric("Consumo Noturno (>20h)", f"{patterns['percent_after_8pm']}%")
            
            st.markdown("**Distribuição por período:**")
            for periodo, cal in patterns.get('period_calories', {}).items():
                st.markdown(f"- **{periodo.capitalize()}**: {cal:.0f} kcal")
        else:
            empty_state("📊", "Dados insuficientes", "Registre refeições por 15 dias para ver seus padrões.")

    with tab2:
        st.markdown("**Tendência de Peso (60 dias)**")
        trend = services["analytics"].analyze_weight_trend(60)
        if trend.get("has_data"):
            if trend.get("insufficient_data"):
                st.info("Precisamos de mais pesagens para calcular sua tendência.")
            else:
                col1, col2 = st.columns(2)
                with col1: st.metric("Variação Total", f"{trend['total_change']:+.1f} kg")
                with col2: st.metric("Velocidade", f"{trend['trend_rate']:+.2f} kg/semana")
        else:
            empty_state("⚖️", "Sem dados de peso", "Registre seu peso na aba Evolução Peso.")

    with tab3:
        st.markdown("**Desafios da Semana**")
        semana = datetime.now().isocalendar()[1]
        desafios_pool = [
            {"t": "7 Refeições Registradas", "xp": 50, "i": "️"},
            {"t": "Zero Calorias Noturnas", "xp": 80, "i": ""},
            {"t": "Hidratação Total (2L/dia)", "xp": 60, "i": "💧"},
            {"t": "Meta Calórica Atingida", "xp": 120, "i": "🎯"},
        ]
        random.seed(semana)
        desafios = random.sample(desafios_pool, 3)
        
        for d in desafios:
            st.markdown(f"""
            <div style="background: #f0f9ff; border-left: 4px solid #0891b2; padding: 1rem; margin-bottom: 0.5rem; border-radius: 4px;">
                <b>{d['i']} {d['t']}</b> <span style="float:right; color: #f59e0b; font-weight:bold;">+{d['xp']} XP</span>
            </div>
            """, unsafe_allow_html=True)
