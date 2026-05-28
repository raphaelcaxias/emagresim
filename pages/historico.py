# pages/historico.py
import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar_historico():
    st.markdown('<div class="section-card"><div class="section-title">📊 Histórico e Métricas</div>', unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.historico_pesos, columns=["data", "peso"])
    df["data"] = pd.to_datetime(df["data"])
    
    fig = px.line(df, x="data", y="peso", markers=True, labels={"data": "Data", "peso": "Peso (kg)"})
    fig.update_traces(line=dict(color="#008080", width=3), marker=dict(size=6, color="#FF6F61"))
    fig.update_layout(height=350, plot_bgcolor='white', xaxis=dict(tickformat="%d/%m"))
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    peso_inicial = st.session_state.historico_pesos[0][1]
    peso_atual = st.session_state.historico_pesos[-1][1]
    with col1: st.metric("Peso inicial", f"{peso_inicial:.1f} kg")
    with col2: st.metric("Peso atual", f"{peso_atual:.1f} kg", f"{peso_atual - peso_inicial:+.1f} kg")
    with col3: st.metric("Melhor", f"{min(p[1] for p in st.session_state.historico_pesos):.1f} kg")
    with col4: st.metric("Pior", f"{max(p[1] for p in st.session_state.historico_pesos):.1f} kg")
    
    if st.session_state.refeicoes:
        st.markdown("### 🍽️ Últimas refeições")
        for ref in reversed(st.session_state.refeicoes[-5:]):
            st.markdown(f"""
            <div style="background:#F7FAFC; border-left:3px solid #FF6F61; padding:10px; border-radius:8px; margin-bottom:8px;">
                <span style="font-size:0.75rem;">{ref.get('hora','--:--')} - {ref['tipo']}</span>
                <p style="margin:2px 0; font-size:0.85rem;">{ref['descricao']} - 🔥 {ref['calorias']} kcal</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
