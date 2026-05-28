# pages/historico.py
import streamlit as st

def mostrar_historico():
    st.markdown('<div class="section-card"><div class="section-title">📊 Histórico e Métricas</div>', unsafe_allow_html=True)
    
    st.info("📌 Em desenvolvimento. Em breve você terá histórico completo de peso, refeições e métricas avançadas.")
    
    st.markdown("### Resumo do período (demo)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Peso inicial (mês)", "108.0 kg")
        st.metric("Peso atual", "105.8 kg", "-2.2 kg")
    with col2:
        st.metric("Meta do mês", "3.0 kg", "73% concluído")
        st.metric("Consistência", "14 dias", "sequência ativa")
    
    st.markdown('</div>', unsafe_allow_html=True)
