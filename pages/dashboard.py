# pages/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import random

from utils.helpers import calcular_imc, calcular_avatar, mensagem_bom_dia
from utils.constants import CORES

def mostrar_dashboard():
    # Dados do usuário (mock para demo)
    usuario = {
        "nome": "Adriano",
        "altura": 1.75,
        "current_weight": st.session_state.get("peso_atual", 105.8),
        "meta_mensal_kg": 3.0,
        "peso_inicio_mes": 108.0
    }
    
    peso_atual = usuario["current_weight"]
    meta_kg = usuario["meta_mensal_kg"]
    progresso = usuario["peso_inicio_mes"] - peso_atual
    percentual = min(100, max(0, (progresso / meta_kg) * 100)) if meta_kg > 0 else 0
    avatar, msg_avatar = calcular_avatar(percentual)
    imc = calcular_imc(peso_atual, usuario["altura"])
    
    # Hero card
    st.markdown(f"""
    <div class="hero-card">
        <div class="avatar-container">{avatar}</div>
        <div class="hero-text">
            <h2>Bem-vindo de volta, {usuario['nome']}!</h2>
            <p>🎯 {msg_avatar}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("⚖️ Peso Atual", f"{peso_atual:.1f} kg", f"-{progresso:.1f} kg no mês")
    with k2:
        st.metric("📊 IMC", f"{imc:.1f}", "Referência 18.5 - 24.9")
    with k3:
        st.metric("🎯 Meta do Mês", f"{meta_kg:.1f} kg", f"{percentual:.1f}% concluído")
    with k4:
        st.metric("🔥 Consistência", "14 Dias", "Sequência ativa!")
    
    # Barra de progresso
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg_avatar)
    
    # Gráfico de evolução
    st.markdown("### 📈 Evolução do Peso")
    
    datas = [date.today() - timedelta(days=i) for i in range(15, -1, -1)]
    pesos = [108.0 - (i * 0.15) + random.uniform(-0.1, 0.1) for i in range(15)] + [peso_atual]  # ← CORRIGIDO
    df = pd.DataFrame({"Data": datas, "Peso (kg)": pesos})
    
    fig = px.line(df, x="Data", y="Peso (kg)", markers=True)
    fig.update_traces(line=dict(color=CORES["secondary"], width=3), marker=dict(size=8, color=CORES["primary"]))
    fig.update_layout(
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickformat="%d/%m", gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Mensagem do dia
    st.info(mensagem_bom_dia())
    
    # Registrar peso
    with st.expander("⚖️ Registrar peso hoje"):
        novo_peso = st.number_input("Peso (kg)", 40.0, 200.0, peso_atual, 0.1)
        if st.button("Salvar"):
            st.session_state["peso_atual"] = novo_peso
            st.success(f"✅ Peso registrado: {novo_peso:.1f} kg")
            st.rerun()
