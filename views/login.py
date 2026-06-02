import streamlit as st
import logging
from core.database import AppDatabase

logger = logging.getLogger(__name__)

def render_login(db: AppDatabase):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header" style="text-align: center;">
        <h1 style="margin: 0; font-size: 3rem;">💪 EmagreSim</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            Monitoramento baseado em evidências
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Acessar Conta", "📝 Criar Conta"])
    
    with tab1:
        email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", key="login_pass", placeholder="••••••••")
        
        if st.button("Entrar", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Preencha email e senha.")
            else:
                user_data = db.get_user(email, password)
                if user_data:
                    st.session_state.user = user_data
                    logger.info(f"Login bem-sucedido: {email}")
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos.")
                    logger.warning(f"Tentativa de login falhou: {email}")
        
        st.markdown("---")
        
        # CORREÇÃO CRÍTICA: Modo demo sem depender de get_user()
        if st.button(" Entrar no Modo Demonstração", use_container_width=True):
            demo_user = {
                "email": "demo@emagresim.com",
                "password": "demo",
                "name": "Usuário Demo",
                "plan": "free",
                "current_weight": 75.0,
                "goal_weight": 70.0,
                "height": 170,
                "age": 30,
                "activity_level": "moderate",
                "goal": "lose"
            }
            
            if "mock_db" not in st.session_state:
                st.session_state.mock_db = {"users": {}, "meals": [], "weights": [], "achievements": []}
            if "users" not in st.session_state.mock_db:
                st.session_state.mock_db["users"] = {}
            
            st.session_state.mock_db["users"]["demo@emagresim.com"] = demo_user
            st.session_state.user = demo_user
            
            logger.info("Modo demonstração ativado via injeção direta de estado.")
            st.success("✅ Modo demonstração ativado!")
            st.rerun()
    
    with tab2:
        new_name = st.text_input("Nome completo", key="reg_name", placeholder="João Silva")
        new_email = st.text_input("Email", key="reg_email", placeholder="joao@email.com")
        new_password = st.text_input("Senha", type="password", key="reg_pass", placeholder="Mínimo 6 caracteres")
        confirm_password = st.text_input("Confirmar senha", type="password", key="reg_confirm", placeholder="Repita a senha")
        
        if st.button("Cadastrar", use_container_width=True, type="primary"):
            if not all([new_name, new_email, new_password, confirm_password]):
                st.error("Preencha todos os campos.")
            elif len(new_password) < 6:
                st.error("Senha deve ter pelo menos 6 caracteres.")
            elif new_password != confirm_password:
                st.error("As senhas não coincidem.")
            elif "@" not in new_email:
                st.error("Email inválido.")
            else:
                if db.create_user(new_email, new_password, new_name):
                    st.success("✅ Conta criada! Faça login agora.")
                else:
                    st.error("❌ Email já cadastrado.")
    
    st.markdown('</div>', unsafe_allow_html=True)
