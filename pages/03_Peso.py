import streamlit as st
import plotly.graph_objects as go
from datetime import date
from core.database import AppDatabase
from core.nutrition import NutritionService
from components import card_metric, empty_state

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

@st.cache_resource(show_spinner=False)
def init():
    db = AppDatabase()
    return db, NutritionService(db)

db, nutrition = init()
user = st.session_state.user

st.title("⚖️ Evolução de Peso")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Registrar hoje")
    peso = st.number_input("Peso (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)), 0.1)
    notas = st.text_area("Observações", placeholder="Ex: manhã, jejum")
    
    if st.button("💾 Salvar", type="primary", use_container_width=True):
        db.save_weight({"weight": peso, "log_date": str(date.today()), "notes": notas})
        user["current_weight"] = peso
        st.session_state.user = user
        st.success("Peso salvo!")
        st.rerun()

with col2:
    st.markdown("### 📈 Histórico")
    df = db.get_weights(days=90)
    
    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['log_date'], y=df['weight'], 
                                mode='lines+markers', name='Peso',
                                line=dict(color='#0891b2', width=3)))
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         xaxis_title="Data", yaxis_title="Peso (kg)")
        st.plotly_chart(fig, use_container_width=True)
        
        primeira = df.iloc[0]['weight']
        ultima = df.iloc[-1]['weight']
        variacao = ultima - primeira
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Primeiro", f"{primeira:.1f} kg")
        with col2: st.metric("Atual", f"{ultima:.1f} kg")
        with col3: st.metric("Variação", f"{variacao:+.1f} kg", delta_color="inverse")
    else:
        empty_state("⚖️", "Sem pesagens ainda", "Faça sua primeira pesagem ao lado")
