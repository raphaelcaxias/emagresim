# avatar_maker.py - Versão SIMPLES e FUNCIONAL
import streamlit as st
import random
import time

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
    emoji = avatar_data["emoji"]
    cor = avatar_data["cor"]
    
    if humor == "feliz":
        emoji_principal = avatar_data["feliz"]
    elif humor == "triste":
        emoji_principal = avatar_data["triste"]
    else:
        emoji_principal = emoji
    
    svg = f'''<svg width="150" height="150" viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg">
        <circle cx="75" cy="75" r="65" fill="{cor}" stroke="white" stroke-width="3"/>
        <circle cx="55" cy="65" r="6" fill="white"/>
        <circle cx="95" cy="65" r="6" fill="white"/>
        <circle cx="57" cy="67" r="3" fill="black"/>
        <circle cx="93" cy="67" r="3" fill="black"/>
        <text x="75" y="135" text-anchor="middle" font-size="50" fill="white">{emoji_principal}</text>
    </svg>'''
    return svg

def tela_avatar():
    st.markdown("<h1 style='text-align:center;'>🎨 Escolha seu Avatar</h1>", unsafe_allow_html=True)
    
    genero = st.radio("Seu gênero", ["Masculino", "Feminino"], horizontal=True)
    avatares = AVATARES_MASCULINOS if genero == "Masculino" else AVATARES_FEMININOS
    
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
    
    if avatar_selecionado:
        if st.button("✅ Confirmar Avatar", use_container_width=True):
            st.session_state["avatar_data"] = avatar_selecionado
            st.session_state["avatar_humor"] = "normal"
            st.session_state["pagina"] = "criar_conta"
            st.rerun()

def mostrar_avatar():
    if "avatar_data" in st.session_state:
        avatar = st.session_state["avatar_data"]
        humor = st.session_state.get("avatar_humor", "normal")
        svg = gerar_avatar_svg(avatar, humor=humor)
        st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 3rem; text-align: center;">🔥</div>', unsafe_allow_html=True)

def celebrar_meta():
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "feliz"
        st.balloons()
        st.toast("🎉 PARABÉNS! Você atingiu sua meta! 🎉", icon="🏆")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"

def modo_apoio():
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "triste"
        st.toast("💙 Você não está sozinho. Um dia de cada vez.", icon="🤗")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"
