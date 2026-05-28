# pages/perfil.py
import streamlit as st

def mostrar_perfil():
    st.markdown('<div class="section-card"><div class="section-title">👤 Meu Perfil</div>', unsafe_allow_html=True)
    
    usuario = {"nome": "Adriano", "idade": 39, "altura": 1.75, "meta_mensal_kg": 3.0}
    
    with st.form("editar_perfil"):
        nome = st.text_input("Nome", usuario["nome"])
        idade = st.number_input("Idade", 18, 100, usuario["idade"])
        altura = st.number_input("Altura (m)", 1.40, 2.20, usuario["altura"], 0.01)
        meta = st.number_input("Meta mensal (kg)", 0.0, 10.0, usuario["meta_mensal_kg"], 0.5)
        if st.form_submit_button("Salvar"):
            st.success("Perfil atualizado (modo demo)")
    
    st.markdown("### 📸 Foto de perfil")
    st.camera_input("Tirar foto")
    
    st.markdown("---")
    st.info("📌 Modo demonstração. Dados não são salvos permanentemente.")
    st.markdown('</div>', unsafe_allow_html=True)
