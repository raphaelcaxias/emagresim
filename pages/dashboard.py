# pages/dashboard.py
import streamlit as st
import random
from utils.helpers import calcular_imc, calcular_avatar, mensagem_bom_dia
from utils.constants import CORES

def mostrar_dashboard():
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
    
    st.markdown(f"""
    <div class="hero-card">
        <div class="avatar-container">{avatar}</div>
        <div class="hero-text">
            <h2>Bem-vindo de volta, {usuario['nome']}!</h2>
            <p>🎯 {msg_avatar}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg_avatar)
    
    st.info(mensagem_bom_dia())
    
    with st.expander("⚖️ Registrar peso hoje"):
        novo_peso = st.number_input("Peso (kg)", 40.0, 200.0, peso_atual, 0.1)
        if st.button("Salvar"):
            st.session_state["peso_atual"] = novo_peso
            st.success(f"✅ Peso registrado: {novo_peso:.1f} kg")
            st.rerun()
    
    col_apoio, col_dica = st.columns(2)
    with col_apoio:
        st.markdown("""
        <div class="apoio-card">
            <h4 style="margin: 0 0 8px 0; color: #E53E3E;">🫂 Suporte & Acolhimento</h4>
            <p style="margin: 0; font-size: 0.95rem;">"Dias difíceis e oscilações no peso fazem parte de jornadas reais. Não se julgue por ontem, foque no próximo passo certo."</p>
        </div>
        """, unsafe_allow_html=True)
    with col_dica:
        dicas = ["Mastigue devagar", "Beba água antes das refeições", "Durma 7-8h por noite"]
        st.markdown(f"""
        <div class="dica-card">
            <h4 style="margin: 0 0 8px 0; color: #008080;">💡 Dica do Dia</h4>
            <p style="margin: 0; font-size: 0.95rem;">"{random.choice(dicas)}"</p>
        </div>
        """, unsafe_allow_html=True)
