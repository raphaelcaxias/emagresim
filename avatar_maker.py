# avatar_maker.py - Avatar interativo que dança e fica triste
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
    """Gera SVG do avatar com expressão baseada no humor"""
    emoji = avatar_data["emoji"]
    cor = avatar_data["cor"]
    
    # Expressões baseadas no humor
    if humor == "feliz":
        boca = 'M 80 115 Q 100 140 120 115'
        olhos = 'M 70 85 Q 75 80 80 85 M 120 85 Q 125 80 130 85'
        sobrancelha = 'M 65 75 Q 75 70 85 75 M 135 75 Q 125 70 115 75'
    elif humor == "triste":
        boca = 'M 85 120 Q 100 110 115 120'
        olhos = 'M 70 85 Q 75 90 80 85 M 120 85 Q 125 90 130 85'
        sobrancelha = 'M 65 80 Q 75 85 85 80 M 135 80 Q 125 85 115 80'
    else:  # normal
        boca = 'M 80 115 Q 100 125 120 115'
        olhos = 'M 70 85 Q 75 85 80 85 M 120 85 Q 125 85 130 85'
        sobrancelha = 'M 65 75 Q 75 75 85 75 M 135 75 Q 125 75 115 75'
    
    svg = f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="200" rx="30" fill="#1A1A1A"/>
        <circle cx="100" cy="100" r="70" fill="{cor}" stroke="white" stroke-width="3"/>
        
        <!-- Olhos -->
        <ellipse cx="75" cy="90" rx="10" ry="12" fill="white"/>
        <ellipse cx="125" cy="90" rx="10" ry="12" fill="white"/>
        <circle cx="78" cy="92" r="5" fill="black"/>
        <circle cx="122" cy="92" r="5" fill="black"/>
        
        <!-- Olhos felizes/tristes -->
        <path d="{olhos}" stroke="black" stroke-width="2" fill="none"/>
        
        <!-- Sobrancelhas -->
        <path d="{sombrancelha}" stroke="black" stroke-width="2.5" stroke-linecap="round" fill="none"/>
        
        <!-- Boca -->
        <path d="{boca}" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
        
        <!-- Emoji central -->
        <text x="100" y="180" text-anchor="middle" font-size="35" fill="white">{emoji}</text>
    </svg>'''
    return svg

def tela_avatar():
    st.markdown("<h1 style='text-align:center;'>🎨 Escolha seu Avatar</h1>", unsafe_allow_html=True)
    
    # Selecionar gênero primeiro
    genero = st.radio("Seu gênero", ["Masculino", "Feminino"], horizontal=True)
    
    # Mostrar avatares disponíveis
    if genero == "Masculino":
        avatares = AVATARES_MASCULINOS
    else:
        avatares = AVATARES_FEMININOS
    
    st.markdown("### Escolha seu personagem:")
    
    # Grid de avatares (3 colunas)
    cols = st.columns(3)
    avatar_selecionado = None
    
    for i, (key, data) in enumerate(avatares.items()):
        with cols[i]:
            # Mostrar avatar normal
            svg = gerar_avatar_svg(data, humor="normal")
            st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'><b>{data['nome']}</b></p>", unsafe_allow_html=True)
            
            if st.button(f"Escolher {data['nome']}", key=f"btn_{key}", use_container_width=True):
                avatar_selecionado = data
                avatar_selecionado["key"] = key
    
    if avatar_selecionado:
        st.markdown("---")
        st.markdown(f"### ✅ Você escolheu **{avatar_selecionado['nome']}**!")
        
        # Mostrar preview com expressões
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Normal**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="normal"), unsafe_allow_html=True)
        with col2:
            st.markdown("**😊 Feliz (quando bater meta)**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="feliz"), unsafe_allow_html=True)
        with col3:
            st.markdown("**😢 Triste (apoio emocional)**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="triste"), unsafe_allow_html=True)
        
        st.info("💡 Seu avatar vai **dançar** quando você bater uma meta e vai **ficar triste** quando você pedir apoio emocional!")
        
        if st.button("✅ Confirmar Avatar", use_container_width=True):
            st.session_state["avatar_data"] = avatar_selecionado
            st.session_state["avatar_humor"] = "normal"
            st.session_state["pagina"] = "criar_conta"
            st.rerun()

def atualizar_humor_avatar(humor):
    """Atualiza o humor do avatar (chamado quando o usuário atinge meta ou pede apoio)"""
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = humor

def celebrar_meta():
    """Avatar dança quando meta é atingida"""
    atualizar_humor_avatar("feliz")
    st.balloons()
    st.toast("🎉 PARABÉNS! Você atingiu sua meta! 🎉", icon="🏆")
    time.sleep(3)
    atualizar_humor_avatar("normal")

def modo_apoio():
    """Avatar fica triste quando usuário precisa de apoio"""
    atualizar_humor_avatar("triste")
    st.toast("💙 Você não está sozinho. Um dia de cada vez.", icon="🤗")
    time.sleep(3)
    atualizar_humor_avatar("normal")

def mostrar_avatar():
    """Mostra o avatar com o humor atual"""
    if "avatar_data" in st.session_state:
        avatar = st.session_state["avatar_data"]
        humor = st.session_state.get("avatar_humor", "normal")
        svg = gerar_avatar_svg(avatar, humor=humor)
        st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 3rem; text-align: center;">🔥</div>', unsafe_allow_html=True)
