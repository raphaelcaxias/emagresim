def render_login(db):
    """Tela de Login / Cadastro / Demo"""
    load_css()
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
        <h1 style="font-size: 3.5rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            💪 EmagreSim
        </h1>
        <p style="color: #6b7280; font-size: 1.25rem;">Transforme sua jornada de emagrecimento em um jogo!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Garante que users existe
    if "users" not in st.session_state.mock_db:
        st.session_state.mock_db["users"] = {
            "demo@emagresim.com": {
                "password": "demo123",
                "name": "Usuário Demo",
                "email": "demo@emagresim.com",
                "is_demo": True
            }
        }
    
    tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
    
    with tab1:
        st.markdown("### Login")
        login_email = st.text_input("Email", key="login_email_input", value="")
        login_password = st.text_input("Senha", type="password", key="login_pass_input", value="")
        
        col_btn, col_demo = st.columns([2, 1])
        with col_btn:
            if st.button("Entrar", use_container_width=True, type="primary", key="btn_login"):
                users = st.session_state.mock_db.get("users", {})
                if login_email in users and users[login_email].get("password") == login_password:
                    st.session_state.user = {
                        "email": login_email, 
                        "name": users[login_email]["name"],
                        "is_demo": users[login_email].get("is_demo", False),
                        "onboarded": False, 
                        "plan": "free"
                    }
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos")
        
        with col_demo:
            if st.button("🎮 Modo Demo", use_container_width=True, key="btn_demo"):
                st.session_state.user = {
                    "email": "demo@emagresim.com", 
                    "name": "Usuário Demo",
                    "is_demo": True, 
                    "onboarded": False, 
                    "plan": "free"
                }
                st.rerun()
    
    with tab2:
        st.markdown("### Criar Nova Conta")
        
        # Usa session_state para controlar os valores
        if "reg_name" not in st.session_state:
            st.session_state.reg_name = ""
        if "reg_email" not in st.session_state:
            st.session_state.reg_email = ""
        if "reg_password" not in st.session_state:
            st.session_state.reg_password = ""
        if "reg_confirm" not in st.session_state:
            st.session_state.reg_confirm = ""
        
        new_name = st.text_input("Nome completo", key="input_reg_name", value=st.session_state.reg_name)
        new_email = st.text_input("Email", key="input_reg_email", value=st.session_state.reg_email)
        new_password = st.text_input("Senha", type="password", key="input_reg_pass", value=st.session_state.reg_password)
        confirm_password = st.text_input("Confirmar senha", type="password", key="input_reg_confirm", value=st.session_state.reg_confirm)
        
        if st.button("Cadastrar", use_container_width=True, type="primary", key="btn_register"):
            if new_name and new_email and new_password:
                if new_password == confirm_password:
                    users = st.session_state.mock_db.get("users", {})
                    
                    # Verifica se email já existe (case insensitive)
                    email_lower = new_email.lower().strip()
                    users_lower = {k.lower(): v for k, v in users.items()}
                    
                    if email_lower in users_lower:
                        st.error("Este email já está cadastrado! Tente fazer login.")
                    else:
                        # Cria novo usuário
                        users[email_lower] = {
                            "password": new_password, 
                            "name": new_name,
                            "email": email_lower, 
                            "is_demo": False
                        }
                        st.session_state.mock_db["users"] = users
                        
                        # Limpa campos
                        st.session_state.reg_name = ""
                        st.session_state.reg_email = ""
                        st.session_state.reg_password = ""
                        st.session_state.reg_confirm = ""
                        
                        st.success("✅ Conta criada com sucesso! Agora faça login.")
                        st.balloons()
                        st.rerun()
                else:
                    st.error("❌ As senhas não coincidem")
            else:
                st.error("❌ Preencha todos os campos obrigatórios")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; margin-top: 1rem;">
        <p>🎯 <strong>Dica Demo:</strong> Use <code>demo@emagresim.com</code> / <code>demo123</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False
