# pages/historico.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

def mostrar_historico():
    st.markdown('<div class="section-card"><div class="section-title">📊 Histórico e Métricas</div>', unsafe_allow_html=True)
    
    # Inicializar histórico de pesos no session_state (se não existir)
    if "historico_pesos" not in st.session_state:
        # Criar dados de exemplo para os últimos 30 dias
        datas = [datetime.now() - timedelta(days=i) for i in range(30, -1, -1)]
        pesos = [108.0 - (i * 0.08) + random.uniform(-0.3, 0.3) for i in range(31)]
        st.session_state.historico_pesos = list(zip(datas, pesos))
    
    # Gráfico de evolução do peso
    st.markdown("### 📈 Evolução do Peso (30 dias)")
    
    df = pd.DataFrame(st.session_state.historico_pesos, columns=["data", "peso"])
    df["data"] = pd.to_datetime(df["data"])
    
    fig = px.line(df, x="data", y="peso", markers=True,
                  labels={"data": "Data", "peso": "Peso (kg)"})
    fig.update_traces(line=dict(color="#008080", width=3), marker=dict(size=6, color="#FF6F61"))
    fig.update_layout(
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickformat="%d/%m", gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0', range=[95, 110])
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Estatísticas do período
    st.markdown("### 📊 Estatísticas do período")
    
    col1, col2, col3, col4 = st.columns(4)
    peso_inicial = st.session_state.historico_pesos[0][1]
    peso_atual = st.session_state.historico_pesos[-1][1]
    variacao = peso_atual - peso_inicial
    melhor_peso = min(p[1] for p in st.session_state.historico_pesos)
    pior_peso = max(p[1] for p in st.session_state.historico_pesos)
    
    with col1:
        st.metric("Peso inicial", f"{peso_inicial:.1f} kg")
    with col2:
        st.metric("Peso atual", f"{peso_atual:.1f} kg", f"{variacao:+.1f} kg")
    with col3:
        st.metric("Melhor peso", f"{melhor_peso:.1f} kg")
    with col4:
        st.metric("Pior peso", f"{pior_peso:.1f} kg")
    
    # Lista de refeições (simulada)
    st.markdown("### 🍽️ Últimas refeições")
    
    if "refeicoes" in st.session_state and st.session_state.refeicoes:
        for ref in reversed(st.session_state.refeicoes[-5:]):  # últimas 5
            st.markdown(f"""
            <div style="background: #F7FAFC; border-left: 3px solid #FF6F61; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                <span style="font-size: 0.75rem; color: #718096;">{ref.get('hora', '--:--')} - {ref['tipo']}</span>
                <p style="margin: 2px 0; font-size: 0.85rem;">{ref['descricao']}</p>
                <span style="font-size: 0.8rem; color: #FF6F61;">🔥 {ref['calorias']} kcal</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma refeição registrada ainda. Vá em 'Refeições' para adicionar.")
    
    st.markdown('</div>', unsafe_allow_html=True)
