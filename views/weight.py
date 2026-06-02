import streamlit as st
import plotly.graph_objects as go
from datetime import date
from components import section_header, empty_state, card_metric

def render_weight(services: dict, user: dict):
    section_header("Evolução de Peso", "Monitore sua trajetória corporal.", "⚖️")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**Registrar Pesagem**")
        peso = st.number_input("Peso (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)), 0.1)
        notas = st.text_area("Observações", placeholder="Ex: Jejum, pós-treino...")
        
        if st.button("💾 Salvar Pesagem", type="primary", use_container_width=True):
            services["db"].save_weight({"weight": peso, "log_date": str(date.today()), "notes": notas})
            user["current_weight"] = peso
            st.session_state.user = user
            st.success("✅ Peso registrado e perfil atualizado!")
            st.rerun()

    with col2:
        st.markdown("**Histórico (90 dias)**")
        df = services["db"].get_weights(days=90)
        
        if not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['log_date'], y=df['weight'], 
                                    mode='lines+markers', name='Peso',
                                    line=dict(color='#0891b2', width=3)))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), 
                             xaxis_title="Data", yaxis_title="Peso (kg)", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            # Indicadores de Tendência (Requisito Fase 2)
            primeira = df.iloc[0]['weight']
            ultima = df.iloc[-1]['weight']
            variacao = ultima - primeira
            
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Primeiro", f"{primeira:.1f} kg")
            with c2: st.metric("Atual", f"{ultima:.1f} kg")
            with c3: st.metric("Variação", f"{variacao:+.1f} kg", delta_color="inverse")
        else:
            empty_state("⚖️", "Sem pesagens registradas", "Faça seu primeiro registro ao lado.")
