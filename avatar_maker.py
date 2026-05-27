# avatar_maker.py - Versão SIMPLES e FUNCIONAL
import streamlit as st
import random
import time

# Avatares pré-definidos
AVATARES_MASCULINOS = {
    "joao": {"nome": "João", "emoji": "👨", "feliz": "🕺", "triste": "😞", "cor": "#4A90D9"},
    "carlos": {"nome": "Carlos", "emoji": "🧔", "feliz": "💪", "triste": "😔", "cor": "#E67E22"},
    "pedro": {"nome": "Pedro", "emoji": "👦", "feliz": "🏃", "triste": "😕", "cor": "#2ECC71"},
}

AVATARES_FEMININOS = {
    "maria": {"nome": "Maria", "emoji": "👩", "feliz": "💃", "triste": "😢", "cor": "#E84393"},
    "ana": {"nome": "Ana", "emoji": "👧", "feliz": "🌸", "triste": "😟", "cor": "#F39C12"},
    "julia": {"nome": "Julia", "emoji": "💁", "feliz": "✨", "triste": "😥", "cor": "#9B59B6"},
}

def gerar_avatar_svg(avatar_data, humor="normal"):
    """Gera SVG do avatar com expressão baseada no humor (versão SIMPLES)"""
    emoji = avatar_data["emoji"]
    cor = avatar_data["cor"]
    
    # Define o emoji de acordo com o humor
    if humor == "feliz":
        emoji_principal = avatar_data["feliz"]
    elif humor == "triste":
        emoji_principal = avatar_data["triste"]
    else:
        emoji_principal = emoji
    
    svg = f'''<svg width="180" height="180" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg">
        <rect width="180" height="180" rx="30" fill="#1A1A1A"/>
        <circle cx="90" cy="90" r="65" fill="{cor}" stroke="white" stroke-width="3"/>
        
        <!-- Olhos -->
        <circle cx="65" cy="80" r="8" fill="white"/>
        <circle cx="115" cy="80" r="8" fill="white"/>
        <circle cx="67" cy="82" r="4" fill="black"/>
        <circle cx="113" cy="82" r="4" fill="black"/>
        
        <!-- Emoji central grande -->
        <text x="90" y="170" text-anchor="middle" font-size="55" fill="white">{emoji_principal}</text>
    </svg>'''
    return svg

def tela_avatar():
    st.markdown("<h1 style='text-align:center;'>🎨 Escolha seu Avatar</h1>", unsafe_allow_html=True)
    
    genero = st.radio("Seu gênero", ["Masculino", "Feminino"], horizontal=True)
    
    if genero == "Masculino":
        avatares = AVATARES_MASCULINOS
    else:
        avatares = AVATARES_FEMININOS
    
    st.markdown("### Escolha seu personagem:")
    
    cols = st.columns(3)
    avatar_selecionado = None
    
    for i, (key, data) in enumerate(avatares.items()):
        with cols[i]:
            svg = gerar_avatar_svg(data, humor="normal")
            st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'><b>{data['nome']}</b></p>", unsafe_allow_html=True)
            
            if st.button(f"Escolher {data['nome']}", key=f"btn_{key}", use_container_width=True):
                avatar_selecionado = data
                avatar_selecionado["key"] = key
    
    if avatar_selecionado:
        st.markdown("---")
        st.markdown(f"### ✅ Você escolheu **{avatar_selecionado['nome']}**!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Normal**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="normal"), unsafe_allow_html=True)
        with col2:
            st.markdown("**😊 Feliz**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="feliz"), unsafe_allow_html=True)
        with col3:
            st.markdown("**😢 Triste**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="triste"), unsafe_allow_html=True)
        
        st.info("💡 Seu avatar vai **dançar** quando você bater uma meta e vai **ficar triste** quando você pedir apoio emocional!")
        
        if st.button("✅ Confirmar Avatar", use_container_width=True):
            st.session_state["avatar_data"] = avatar_selecionado
            st.session_state["avatar_humor"] = "normal"
            st.session_state["pagina"] = "criar_conta"
            st.rerun()

def mostrar_avatar():
    """Mostra o avatar com o humor atual"""
    if "avatar_data" in st.session_state:
        avatar = st.session_state["avatar_data"]
        humor = st.session_state.get("avatar_humor", "normal")
        svg = gerar_avatar_svg(avatar, humor=humor)
        st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 3rem; text-align: center;">🔥</div>', unsafe_allow_html=True)

def celebrar_meta():
    """Avatar dança quando meta é atingida"""
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "feliz"
        st.balloons()
        st.toast("🎉 PARABÉNS! Você atingiu sua meta! 🎉", icon="🏆")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"
        st.rerun()

def modo_apoio():
    """Avatar fica triste quando usuário precisa de apoio"""
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "triste"
        st.toast("💙 Você não está sozinho. Um dia de cada vez.", icon="🤗")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"
        st.rerun()
