import streamlit as st
import logging

logger = logging.getLogger(__name__)

def render_login(db=None):
    """Tela de login - versão robusta sem dependências complexas."""
    try:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0 3rem 0;">
            <h1 style="font-size: 3rem; margin: 0; color: #0891b2;">💪 EmagreSim</h1>
            <p style="color: #64748b; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                Monitoramento nutricional baseado em dados
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Acessar Conta", "📝 Criar Conta"])
        
        # ===== LOGIN =====
        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
            password = st.text_input("Senha", type="password", key="login_pass", placeholder="••••••••")
            
            if st.button("Entrar", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Preencha email e senha.")
                elif db is not None:
                    try:
                        user_data = db.get_user(email, password)
                        if user_data:
                            st.session_state.user = user_data
                            st.success(f"Bem-vindo, {user_data.get('name', 'Usuário')}!")
                            logger.info(f"Login: {email}")
                            st.rerun()
                        else:
                            st.error("Email ou senha incorretos.")
                    except Exception as e:
                        logger.error(f"Erro no login: {e}")
                        st.error(f"Erro ao fazer login: {str(e)}")
                else:
                    st.error("Sistema de autenticação indisponível.")
            
            st.markdown("---")
            
            # MODO DEMO (independente do banco)
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
                
                # Garante que mock_db existe
                if "mock_db" not in st.session_state:
                    st.session_state.mock_db = {
                        "users": {},
                        "meals": [],
                        "weights": [],
                        "achievements": []
                    }
                if "users" not in st.session_state.mock_db:
                    st.session_state.mock_db["users"] = {}
                
                # Injeta usuário demo diretamente
                st.session_state.mock_db["users"]["demo@emagresim.com"] = demo_user
                st.session_state.user = demo_user
                
                st.success("✅ Modo demonstração ativado!")
                logger.info("Modo demo ativado")
                st.rerun()
        
        # ===== CADASTRO =====
        with tab2:
            new_name = st.text_input("Nome completo", key="reg_name", placeholder="João Silva")
            new_email = st.text_input("Email", key="reg_email", placeholder="joao@email.com")
            new_password = st.text_input("Senha", type="password", key="reg_pass", placeholder="Mínimo 6 caracteres")
            confirm_password = st.text_input("Confirmar senha", type="password", key="reg_confirm", placeholder="Repita a senha")
            
            if st.button("Cadastrar", use_container_width=True, type="primary"):
                # Validações
                if not all([new_name, new_email, new_password, confirm_password]):
                    st.error("Preencha todos os campos.")
                elif len(new_password) < 6:
                    st.error("Senha deve ter pelo menos 6 caracteres.")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem.")
                elif "@" not in new_email or "." not in new_email:
                    st.error("Email inválido.")
                elif db is not None:
                    try:
                        if db.create_user(new_email, new_password, new_name):
                            st.success("✅ Conta criada! Faça login na aba ao lado.")
                            logger.info(f"Novo cadastro: {new_email}")
                        else:
                            st.error("❌ Email já cadastrado.")
                    except Exception as e:
                        logger.error(f"Erro no cadastro: {e}")
                        st.error(f"Erro ao criar conta: {str(e)}")
                else:
                    st.error("Sistema de cadastro indisponível.")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 2rem;">
            <p>🔒 Seus dados estão protegidos</p>
            <p>EmagreSim v2.0 • Monitoramento baseado em evidências</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        logger.critical(f"Falha crítica no render_login: {e}", exc_info=True)
        st.error("❌ Erro crítico ao carregar tela de login.")
        st.exception(e)  # Mostra traceback completo em desenvolvimento
