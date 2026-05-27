# avatar_central.py - Avatar simbólico do EmagreSim
import streamlit as st
import time

# Estados simbólicos do avatar
ESTADOS = {
    "despertar": {"simbolo": "🌅", "nome": "Despertar", "cor": "#FF8C42", "mensagem": "Todo recomeço é uma semente. Hoje é o primeiro dia."},
    "transformacao": {"simbolo": "🔥", "nome": "Transformação", "cor": "#E63946", "mensagem": "Você está queimando hábitos antigos. Continue."},
    "crescimento": {"simbolo": "🌱", "nome": "Crescimento", "cor": "#2ECC71", "mensagem": "Pequenos passos. Grandes mudanças."},
    "energia": {"simbolo": "⚡", "nome": "Energia", "cor": "#F4D03F", "mensagem": "Você está no caminho. Mantenha o ritmo."},
    "resiliencia": {"simbolo": "⛰️", "nome": "Resiliência", "cor": "#5D6D7E", "mensagem": "Consistência é mais importante que intensidade."},
    "conquista": {"simbolo": "🏆", "nome": "Conquista", "cor": "#D4AF37", "mensagem": "Meta alcançada! Você é capaz de mais."},
    "apoio": {"simbolo": "🫂", "nome": "Apoio", "cor": "#8E44AD", "mensagem": "Você não está sozinho. Um dia de cada vez."},
    "alerta": {"simbolo": "👂", "nome": "Atenção", "cor": "#E67E22", "mensagem": "Atenção. Pequenos desvios viram grandes hábitos."},
}

def tela_avatar():
    """Tela de escolha do avatar simbólico"""
    st.markdown("<h1 style='text-align:center;'>🌅 Escolha seu Símbolo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>O símbolo representa sua jornada de transformação.</p>", unsafe_allow_html=True)
    
    # Exibir opções de símbolos
    cols = st.columns(3)
    simbolo_escolhido = None
    
    for i, (chave, estado) in enumerate(ESTADOS.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; margin: 10px 0;">
                <div style="font-size: 3rem;">{estado['simbolo']}</div>
                <div style="font-weight: bold; margin: 10px 0;">{estado['nome']}</div>
                <div style="font-size: 0.75rem; color: #888;">{estado['mensagem'][:50]}...</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Escolher {estado['nome']}", key=f"choose_{chave}", use_container_width=True):
                simbolo_escolhido = estado
    
    if simbolo_escolhido:
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, {simbolo_escolhido['cor']}20, transparent); border-radius: 30px;">
            <div style="font-size: 5rem;">{simbolo_escolhido['simbolo']}</div>
            <h2>{simbolo_escolhido['nome']}</h2>
            <p style="color: #aaa;">{simbolo_escolhido['mensagem']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Confirmar Símbolo", use_container_width=True):
            st.session_state["avatar"] = simbolo_escolhido
            st.session_state["avatar_estado"] = "despertar"
            st.session_state["pagina"] = "criar_conta"
            st.rerun()

def mostrar_avatar():
    """Exibe o avatar com estado atual"""
    if "avatar" in st.session_state:
        avatar = st.session_state["avatar"]
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 4rem;">{avatar['simbolo']}</div>
            <div style="font-weight: 500; margin-top: 5px;">{avatar['nome']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 3rem; text-align: center;">🌅</div>', unsafe_allow_html=True)

def avatar_evoluir():
    """Avança para o próximo estágio da jornada"""
    if "avatar" in st.session_state:
        estados_ordem = ["despertar", "transformacao", "crescimento", "energia", "resiliencia", "conquista"]
        estado_atual = st.session_state.get("avatar_estado", "despertar")
        
        if estado_atual in estados_ordem:
            idx = estados_ordem.index(estado_atual)
            if idx + 1 < len(estados_ordem):
                proximo = estados_ordem[idx + 1]
                st.session_state["avatar_estado"] = proximo
                st.session_state["avatar"] = ESTADOS[proximo]
                st.toast(f"✨ Seu símbolo evoluiu para: {ESTADOS[proximo]['nome']}!", icon="🌱")
                return True
    return False

def avatar_mensagem(estado):
    """Define o estado do avatar sem evoluir"""
    if "avatar" in st.session_state and estado in ESTADOS:
        st.session_state["avatar"] = ESTADOS[estado]
        st.session_state["avatar_estado"] = estado
        st.toast(ESTADOS[estado]["mensagem"], icon=ESTADOS[estado]["simbolo"])
