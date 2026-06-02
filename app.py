import streamlit as st
import logging
from core.bootstrap import init_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EmagreSim.App")

st.set_page_config(page_title="EmagreSim", page_icon="💪", layout="wide", initial_sidebar_state="expanded")

def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"CSS não carregado: {e}")

def main():
    load_css()
    state, services = init_app()
    
    if not services:
        st.error("❌ Falha ao inicializar o sistema. Verifique os logs.")
        st.stop()

    if st.session_state.user is None:
        from views.login import render_login
        render_login(services["db"])
        return

    from views.sidebar import render_sidebar
    render_sidebar(services)

    page = st.session_state.page
    logger.debug(f"Roteamento: {page}")

    try:
        if page == "home":
            from views.home import render_home; render_home(services, st.session_state.user)
        elif page == "dashboard":
            from views.dashboard import render_dashboard; render_dashboard(services, st.session_state.user)
        elif page == "meals":
            from views.meals import render_meals; render_meals(services, st.session_state.user)
        elif page == "weight":
            from views.weight import render_weight; render_weight(services, st.session_state.user)
        elif page == "analysis":
            from views.analysis import render_analysis; render_analysis(services, st.session_state.user)
        elif page == "profile":
            from views.profile import render_profile; render_profile(services, st.session_state.user)
    except Exception as e:
        logger.error(f"Erro fatal na renderização de '{page}': {e}")
        st.error(f"Erro ao carregar a página.")

if __name__ == "__main__":
    main()
