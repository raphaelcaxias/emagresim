# app.py - Entry point principal
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Carregar CSS
with open("assets/style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicializar estado da sessão
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "dashboard"

# Importar páginas (serão criadas depois)
from pages.dashboard import mostrar_dashboard
from pages.perfil import mostrar_perfil
from pages.refeicoes import mostrar_refeicoes
from pages.historico import mostrar_historico

# Topbar fixa
st.markdown(f"""
<div class="topbar">
    <div class="topbar-logo">🌱 Emagre<span>Sim</span></div>
    <div class="topbar-user">👤 {st.session_state.get("usuario_nome", "Adriano")} &nbsp;|&nbsp; Modo Demonstração</div>
</div>
""", unsafe_allow_html=True)

# Navegação
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
with col_nav1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state["pagina"] = "dashboard"
        st.rerun()
with col_nav2:
    if st.button("🍽️ Refeições", use_container_width=True):
        st.session_state["pagina"] = "refeicoes"
        st.rerun()
with col_nav3:
    if st.button("📈 Histórico", use_container_width=True):
        st.session_state["pagina"] = "historico"
        st.rerun()
with col_nav4:
    if st.button("👤 Perfil", use_container_width=True):
        st.session_state["pagina"] = "perfil"
        st.rerun()

# Roteamento
pagina = st.session_state["pagina"]

if pagina == "dashboard":
    mostrar_dashboard()
elif pagina == "refeicoes":
    mostrar_refeicoes()
elif pagina == "historico":
    mostrar_historico()
elif pagina == "perfil":
    mostrar_perfil()
else:
    mostrar_dashboard()
