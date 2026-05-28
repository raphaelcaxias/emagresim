# pages/perfil.py
import streamlit as st

def mostrar_perfil():
    st.markdown('<div class="section-card"><div class="section-title">👤 Meu Perfil</div>', unsafe_allow_html=True)
    
    st.info("📌 Em desenvolvimento. Em breve você poderá editar seus dados e fazer upload da foto de perfil.")
    
    st.markdown("### Dados atuais (modo demonstração)")
    st.write("**Nome:** Adriano")
    st.write("**Idade:** 39 anos")
    st.write("**Altura:** 1.75m")
    st.write("**Peso atual:** 105.8 kg")
    st.write("**Meta mensal:** 3.0 kg/mês")
    
    st.markdown('</div>', unsafe_allow_html=True)
