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
        "current_weight": 105.8,
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
        st.markdown('<div class="metric-coral">', unsafe_allow_html=True)
        st.metric("⚖️ Peso Atual", f"{peso_atual:.1f} kg", f"-{progresso:.1f} kg no mês")
        st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="metric-teal">', unsafe_allow_html=True)
        st.metric("📊 IMC", f"{imc:.1f}", "Referência 18.5 - 24.9")
        st.markdown('</div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="metric-blue">', unsafe_allow_html=True)
        st.metric("🎯 Meta do Mês", f"{meta_kg:.1f} kg", f"{percentual:.1f}% concluído")
        st.markdown('</div>', unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="metric-orange">', unsafe_allow_html=True)
        st.metric("🔥 Consistência", "14 Dias", "Sequência ativa!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico de evolução
    st.markdown('<div class="section-card"><div class="section-title">📈 Evolução do Peso</div>', unsafe_allow_html=True)
    
    datas = [date.today() - timedelta(days=i) for i in range(15, -1, -1)]
    pesos = [108.0 - (i * 0.15) + random.uniform(-0.1, 0.1) for i in range(15)] + [peso_atual]
    df = pd.DataFrame({"Data": datas, "Peso (kg)": pesos})
    
    fig = px.line(df, x="Data", y="Peso (kg)", markers=True)
    fig.update_traces(line=dict(color=CORES["secondary"], width=3), marker=dict(size=8, color=CORES["primary"]))
    fig.update_layout(
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickformat="%d/%m", gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Barra de progresso da meta
    st.markdown('<div class="section-card"><div class="section-title">📅 Progresso da Meta Mensal</div>', unsafe_allow_html=True)
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apoio emocional e dica do dia
    col_apoio, col_dica = st.columns(2)
    with col_apoio:
        st.markdown("""
        <div class="apoio-card">
            <h4 style="margin: 0 0 8px 0; color: #E53E3E;">🫂 Suporte & Acolhimento</h4>
            <p style="margin: 0; font-size: 0.95rem; color: #2D3748; line-height: 1.5;">
                "Dias difíceis e oscilações no peso fazem parte de jornadas reais. 
                Não se julgue por ontem, foque no próximo pequeno passo certo."
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_dica:
        dicas = [
            "Mastigue devagar: a saciedade leva cerca de 20 minutos.",
            "Beba um copo de água antes de cada refeição.",
            "Durma 7-8h por noite para regular os hormônios.",
            "Inclua proteína em todas as refeições para mais saciedade."
        ]
        import random
        st.markdown(f"""
        <div class="dica-card">
            <h4 style="margin: 0 0 8px 0; color: #008080;">💡 Dica Saudável</h4>
            <p style="margin: 0; font-size: 0.95rem; color: #2D3748; line-height: 1.5;">
                "{random.choice(dicas)}"
            </p>
        </div>
        """, unsafe_allow_html=True)
