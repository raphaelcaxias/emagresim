# avatar_maker.py
import streamlit as st
import random

def gerar_avatar_svg(estilo="masculino1", pele="#F5C9A0", cabelo="#5C3A21", 
                     olhos="#2C2C2C", boca="#E8A0A0", roupa="#FF4D00"):
    
    if estilo == "masculino1":
        formato_rosto = 'rx="45" ry="45"'
        sombrancelha = 'M 65 35 L 75 32 M 135 35 L 125 32'
    elif estilo == "masculino2":
        formato_rosto = 'rx="40" ry="50"'
        sombrancelha = 'M 65 35 L 78 30 M 135 35 L 122 30'
    elif estilo == "feminino1":
        formato_rosto = 'rx="50" ry="45"'
        sombrancelha = 'M 65 33 L 78 34 M 135 33 L 122 34'
    else:
        formato_rosto = 'rx="55" ry="40"'
        sombrancelha = 'M 65 34 L 78 36 M 135 34 L 122 36'
    
    svg = f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="200" fill="none" rx="20" ry="20"/>
        <ellipse cx="100" cy="95" rx="55" ry="60" fill="{pele}" {formato_rosto} stroke="#D4A574" stroke-width="1.5"/>
        <ellipse cx="72" cy="90" rx="8" ry="9" fill="white" stroke="#2C2C2C" stroke-width="1.5"/>
        <ellipse cx="128" cy="90" rx="8" ry="9" fill="white" stroke="#2C2C2C" stroke-width="1.5"/>
        <circle cx="74" cy="91" r="4" fill="{olhos}"/>
        <circle cx="126" cy="91" r="4" fill="{olhos}"/>
        <circle cx="76" cy="89" r="1.5" fill="white"/>
        <circle cx="128" cy="89" r="1.5" fill="white"/>
        <path d="{sombrancelha}" stroke="#5C4033" stroke-width="2.5" stroke-linecap="round" fill="none"/>
        <path d="M 88 115 Q 100 125 112 115" stroke="{boca}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
        <path d="M 45 80 Q 50 40 100 35 Q 150 40 155 80" fill="{cabelo}"/>
        <ellipse cx="100" cy="50" rx="50" ry="25" fill="{cabelo}"/>
        <path d="M 97 100 L 100 108 L 103 100" stroke="#D4A574" stroke-width="1.5" fill="none"/>
        <rect x="45" y="155" width="110" height="40" rx="10" fill="{roupa}"/>
        <path d="M 60 155 L 100 180 L 140 155" fill="{roupa}"/>
        <path d="M 85 155 L 100 170 L 115 155" fill="#FFFFFF" opacity="0.8"/>
    </svg>'''
    return svg

def tela_avatar():
    st.markdown("<h1 style='text-align:center;'>🎨 Crie seu Avatar</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        estilo = st.selectbox("Estilo", ["masculino1", "masculino2", "feminino1", "feminino2"])
        pele = st.color_picker("Pele", "#F5C9A0")
        cabelo = st.color_picker("Cabelo", "#5C3A21")
        olhos = st.color_picker("Olhos", "#2C2C2C")
        boca = st.color_picker("Boca", "#E8A0A0")
        roupa = st.color_picker("Roupa", "#FF4D00")
        
        if st.button("🎲 Criar aleatório", use_container_width=True):
            estilos = ["masculino1", "masculino2", "feminino1", "feminino2"]
            estilo = random.choice(estilos)
            pele = random.choice(["#F5C9A0", "#F0B88A", "#E8A070", "#D4A574"])
            cabelo = random.choice(["#5C3A21", "#4A2E1A", "#8B5E3C", "#1A1A1A"])
            roupa = random.choice(["#FF4D00", "#22C55E", "#3B82F6", "#8B5CF6"])
            st.rerun()
    
    with col2:
        avatar_svg = gerar_avatar_svg(estilo, pele, cabelo, olhos, boca, roupa)
        st.markdown(f'<div style="display: flex; justify-content: center;">{avatar_svg}</div>', unsafe_allow_html=True)
        
        st.download_button("⬇️ Baixar Avatar (SVG)", avatar_svg, "meu_avatar.svg", "image/svg+xml", use_container_width=True)
    
    st.markdown("---")
    if st.button("✅ Salvar Avatar e Continuar", use_container_width=True):
        st.session_state["avatar_svg"] = avatar_svg
        st.session_state["avatar_estilo"] = estilo
        st.session_state["pagina"] = "criar_conta"
        st.rerun()
