# pages/refeicoes.py
import streamlit as st
from datetime import datetime
from utils.constants import TIPOS_REFEICAO

def mostrar_refeicoes():
    st.markdown('<div class="section-card"><div class="section-title">🍽️ Minhas Refeições</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Adicionar refeição", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", TIPOS_REFEICAO)
            hora = st.time_input("Horário", datetime.now().time())
            descricao = st.text_area("O que comeu?", placeholder="Ex: Arroz, feijão, frango grelhado")
        with col2:
            calorias = st.number_input("Calorias (kcal)", 0, 2000, 400, 50)
            foto = st.camera_input("Tirar foto (opcional)")
        if st.button("✅ Salvar", use_container_width=True):
            if descricao:
                st.session_state.refeicoes.append({
                    "hora": hora.strftime("%H:%M"), "tipo": tipo,
                    "descricao": descricao, "calorias": calorias, "foto": foto
                })
                st.success("Refeição registrada!")
                st.rerun()
            else:
                st.warning("Digite uma descrição")
    
    if st.session_state.refeicoes:
        for ref in reversed(st.session_state.refeicoes[-10:]):
            st.markdown(f"""
            <div style="background:#F7FAFC; border-left:3px solid #008080; padding:12px; border-radius:8px; margin-bottom:12px;">
                <span style="font-size:0.75rem; color:#718096;">{ref['hora']} - {ref['tipo']}</span>
                <p style="margin:4px 0; font-size:0.9rem;">{ref['descricao']}</p>
                <span style="font-size:0.85rem; color:#FF6F61;">🔥 {ref['calorias']} kcal</span>
            </div>
            """, unsafe_allow_html=True)
        total = sum(r["calorias"] for r in st.session_state.refeicoes)
        st.markdown(f"<div style='background:#00808010; padding:15px; border-radius:12px;'><b>📊 Resumo:</b> {len(st.session_state.refeicoes)} refeições | {total} kcal</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhuma refeição registrada.")
    st.markdown('</div>', unsafe_allow_html=True)
