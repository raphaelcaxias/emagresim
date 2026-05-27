# avatar_maker.py - Avatar Central do EmagreSim
import streamlit as st
import random
import time

# Avatares disponíveis (3 de cada gênero)
AVATARES_MASCULINOS = {
    "joao": {"nome": "João", "emoji": "👨", "emoji_feliz": "🕺", "emoji_triste": "😞", "emoji_bravo": "😠", "emoji_cansado": "😴", "cor": "#4A90D9"},
    "carlos": {"nome": "Carlos", "emoji": "🧔", "emoji_feliz": "💪", "emoji_triste": "😔", "emoji_bravo": "🤬", "emoji_cansado": "🥱", "cor": "#E67E22"},
    "pedro": {"nome": "Pedro", "emoji": "👦", "emoji_feliz": "🏃", "emoji_triste": "😕", "emoji_bravo": "😤", "emoji_cansado": "😪", "cor": "#2ECC71"},
}

AVATARES_FEMININOS = {
    "maria": {"nome": "Maria", "emoji": "👩", "emoji_feliz": "💃", "emoji_triste": "😢", "emoji_bravo": "😠", "emoji_cansado": "😴", "cor": "#E84393"},
    "ana": {"nome": "Ana", "emoji": "👧", "emoji_feliz": "🌸", "emoji_triste": "😟", "emoji_bravo": "😤", "emoji_cansado": "🥱", "cor": "#F39C12"},
    "julia": {"nome": "Julia", "emoji": "💁", "emoji_feliz": "✨", "emoji_triste": "😥", "emoji_bravo": "🤬", "emoji_cansado": "😪", "cor": "#9B59B6"},
}

def gerar_avatar_svg(avatar_data, humor="normal"):
    """Gera SVG do avatar com expressão baseada no humor"""
    cor = avatar_data["cor"]
    
    # Define emoji conforme humor
    if humor == "feliz":
        emoji = avatar_data["emoji_feliz"]
    elif humor == "triste":
        emoji = avatar_data["emoji_triste"]
    elif humor == "bravo":
        emoji = avatar_data["emoji_bravo"]
    elif humor == "cansado":
        emoji = avatar_data["emoji_cansado"]
    else:
        emoji = avatar_data["emoji"]
    
    # Animação para avatar feliz (dançando)
    animacao = 'style="animation: bounce 0.5s ease infinite;"' if humor == "feliz" else ''
    
    svg = f'''<svg width="180" height="180" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg" {animacao}>
        <rect width="180" height="180" rx="30" fill="#1A1A1A"/>
        <circle cx="90" cy="85" r="65" fill="{cor}" stroke="white" stroke-width="3"/>
        
        <!-- Olhos -->
        <circle cx="65" cy="75" r="7" fill="white"/>
        <circle cx="115" cy="75" r="7" fill="white"/>
        <circle cx="67" cy="77" r="3.5" fill="black"/>
        <circle cx="113" cy="77" r="3.5" fill="black"/>
        
        <!-- Boca conforme humor -->
        <path d="{get_boca(humor)}" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
        
        <!-- Emoji central grande -->
        <text x="90" y="160" text-anchor="middle" font-size="55" fill="white">{emoji}</text>
        
        <style>
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        </style>
    </svg>'''
    return svg

def get_boca(humor):
    """Retorna o traço da boca conforme humor"""
    if humor == "feliz":
        return "M 70 105 Q 90 125 110 105"
    elif humor == "triste":
        return "M 70 110 Q 90 95 110 110"
    elif humor == "bravo":
        return "M 70 100 L 90 110 L 110 100"
    elif humor == "cansado":
        return "M 75 105 Q 90 100 105 105"
    else:  # normal
        return "M 70 105 Q 90 112 110 105"

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
                avatar_selecionado["key"] = key
    
    if avatar_selecionado:
        st.markdown("---")
        st.markdown(f"### ✅ Você escolheu **{avatar_selecionado['nome']}**!")
        
        # Preview dos humores
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Normal**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="normal"), unsafe_allow_html=True)
        with col2:
            st.markdown("**😊 Feliz/Dançando**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="feliz"), unsafe_allow_html=True)
        with col3:
            st.markdown("**😢 Triste**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="triste"), unsafe_allow_html=True)
        with col4:
            st.markdown("**😠 Bravo**")
            st.markdown(gerar_avatar_svg(avatar_selecionado, humor="bravo"), unsafe_allow_html=True)
        
        st.info("💡 **Seu avatar vai:**\n- 💃 Dançar quando bater a meta\n- 😢 Ficar triste no apoio emocional\n- 😠 Puxar a orelha quando você exagerar\n- 😴 Ficar cansado quando dormir pouco")
        
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

def avatar_feliz():
    """Avatar dança (bateu a meta)"""
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "feliz"
        st.balloons()
        st.toast("🎉 PARABÉNS! Você atingiu sua meta! 🎉", icon="🏆")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"
        st.rerun()

def avatar_triste():
    """Avatar triste (modo apoio)"""
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "triste"
        st.toast("💙 Você não está sozinho. Um dia de cada vez.", icon="🤗")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"
        st.rerun()

def avatar_bravo(mensagem=""):
    """Avatar bravo (puxa a orelha - quando comeu muito ou não registrou)"""
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "bravo"
        if mensagem:
            st.warning(f"👂 {mensagem}")
        else:
            st.warning("👂 Atenção! Cuidado com os exageros. Seu avatar está de olho!")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"
        st.rerun()

def avatar_cansado():
    """Avatar cansado (quando dormiu pouco)"""
    if "avatar_data" in st.session_state:
        st.session_state["avatar_humor"] = "cansado"
        st.info("😴 Você dormiu pouco hoje. Descanse para render melhor amanhã!")
        time.sleep(2)
        st.session_state["avatar_humor"] = "normal"
        st.rerun()
