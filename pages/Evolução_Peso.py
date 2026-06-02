import streamlit as st
import plotly.graph_objects as go
from datetime import date
from core.nutrition import NutritionService

def render_weight(nutrition: NutritionService, user: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.header("⚖️ Evolução de Peso")
    col1, col2 = st.columns([3, 5])
    
    with col1:
        current_w = user.get("current_weight") or 70.0
        new_weight = st.number_input("Peso Corporais Atual (kg)", min_value=30.0, max_value=250.0, value=float(current_w), step=0.1)
        notes = st.text_area("Notas e Contexto", placeholder="Ex: Em jejum, pós treino...")
        if st.button("Salvar Pesagem", use_container_width=True, type="primary"):
            nutrition.db.save_weight({"weight": new_weight, "log_date": str(date.today()), "notes": notes})
            user["current_weight"] = new_weight
            st.session_state.user = user
            st.success("Pesagem armazenada e atualizada!")
            st.rerun()
            
    with col2:
        weights_df = nutrition.db.get_weights(days=60)
        if not weights_df.empty and len(weights_df) >= 1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=weights_df['log_date'], y=weights_df['weight'], mode='lines+markers', name='Peso', line=dict(color='#0891b2', width=3)))
            fig.update_layout(title="Histórico de Pesagens (Últimos 60 dias)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insira a primeira pesagem para gerar o histórico gráfico.")
    st.markdown('</div>', unsafe_allow_html=True)
