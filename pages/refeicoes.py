# pages/refeicoes.py
import streamlit as st
from datetime import datetime
import random

def mostrar_refeicoes():
    st.markdown('<div class="section-card"><div class="section-title">🍽️ Minhas Refeições</div>', unsafe_allow_html=True)
    
    # Inicializar lista de refeições no session_state
    if "refeicoes" not in st.session_state:
        st.session_state.refeicoes = [
            {"hora": "08:00", "tipo": "Café da manhã", "descricao": "Ovos mexidos, café sem açúcar", "calorias": 320, "foto": None},
            {"hora": "12:30", "tipo": "Almoço", "descricao": "Arroz, feijão, frango grelhado, salada", "calorias": 580, "foto": None},
            {"hora": "16:00", "tipo": "Lanche", "descricao": "Iogurte com whey e aveia", "calorias": 240, "foto": None},
        ]
    
    # Formulário para adicionar nova refeição
    with st.expander("➕ Adicionar refeição", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de refeição", [
                "Café da manhã", "Almoço", "Jantar", "Lanche", "Pré-treino", "Pós-treino"
            ])
            hora = st.time_input("Horário", datetime.now().time())
            descricao = st.text_area("O que você comeu?", placeholder="Ex: Arroz, feijão, frango grelhado")
        with col2:
            calorias = st.number_input("Calorias (kcal)", min_value=0, max_value=2000, value=400, step=50)
            foto = st.camera_input("Tirar foto do prato (opcional)")
        
        if st.button("✅ Salvar refeição", use_container_width=True):
            if descricao:
                nova_refeicao = {
                    "hora": hora.strftime("%H:%M"),
                    "tipo": tipo,
                    "descricao": descricao,
                    "calorias": calorias,
                    "foto": foto
                }
                st.session_state.refeicoes.append(nova_refeicao)
                st.success(f"✅ {tipo} registrado! +{calorias} kcal")
                st.rerun()
            else:
                st.warning("Digite uma descrição da refeição.")
    
    # Exibir refeições do dia
    st.markdown("### 📅 Refeições de hoje")
    
    if st.session_state.refeicoes:
        for ref in st.session_state.refeicoes:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div style="background: #F7FAFC; border-left: 3px solid #008080; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                    <span style="font-size: 0.8rem; color: #718096;">{ref['hora']} - {ref['tipo']}</span>
                    <p style="margin: 4px 0; font-size: 0.9rem;">{ref['descricao']}</p>
                    <span style="font-size: 0.85rem; color: #FF6F61;">🔥 {ref['calorias']} kcal</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if ref.get('foto'):
                    st.image(ref['foto'], width=80)
        
        # Resumo do dia
        total_calorias = sum(r["calorias"] for r in st.session_state.refeicoes)
        st.markdown(f"""
        <div style="background: #00808010; border-radius: 12px; padding: 15px; margin-top: 15px;">
            <span style="font-weight: 600;">📊 Resumo do dia</span><br>
            Total de calorias: <strong>{total_calorias} kcal</strong><br>
            Refeições registradas: <strong>{len(st.session_state.refeicoes)}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma refeição registrada hoje. Clique em 'Adicionar refeição' para começar.")
    
    st.markdown('</div>', unsafe_allow_html=True)
