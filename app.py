import streamlit as st
import pandas as pd
from datetime import date
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine

# 1. Configuração Inicial
st.set_page_config(
    page_title="EmagreSim", 
    page_icon="⚔️", 
    layout="centered",  # Centraliza o conteúdo na tela
    initial_sidebar_state="collapsed"
)

# 2. CSS FORÇADO (Para garantir o fundo e botões bonitos)
st.markdown("""
<style>
    /* Fundo Gradiente */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Esconder rodapé padrão do Streamlit se quiser */
    footer {visibility: hidden;}

    /* Estilo dos Cards/Blocos Brancos */
    .stAlert, .stInfo, .stSuccess {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        color: black;
    }
    
    /* Botões Gradientes */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Títulos Brancos */
    h1, h2, h3 {
        color: white;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Input de texto arredondado */
    .stTextInput > div > div > input {
        border-radius: 10px;
        background-color: rgba(255,255,255,0.9);
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicialização
@st.cache_resource
def init_services():
    db = SupabaseDB()
    return db, UserService(db), PsychologyEngine()

db, user_service, psychology = init_services()

# 4. Estado da Sessão
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "today_date" not in st.session_state: st.session_state.today_date = str(date.today())

# ==========================================
# TELA 1: LOGIN / REGISTRO (NÃO LOGADO)
# ==========================================
if not st.session_state.user:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("⚔️ EmagreSim")
    st.subheader("Sua jornada fitness começa aqui")
    st.markdown("---")

    # Cria uma coluna para centralizar o formulário
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        with tab1:
            st.markdown("### 👋 Bem-vindo de volta!")
            email = st.text_input("Email", placeholder="seu@email.com", label_visibility="collapsed")
            pwd = st.text_input("Senha", type="password", placeholder="Sua senha", label_visibility="collapsed")
            
            if st.button("Entrar", use_container_width=True):
                if email and pwd:
                    res = db.sign_in(email, pwd)
                    if res["success"]: st.rerun()
                    else: st.error("Email ou senha incorretos!")
                else: st.warning("Preencha todos os campos.")

        with tab2:
            st.markdown("### 🚀 Nova Conta")
            new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com", label_visibility="collapsed")
            new_pwd = st.text_input("Senha", key="reg_pwd", type="password", placeholder="Mín. 6 caracteres", label_visibility="collapsed")
            new_user = st.text_input("Nome de Usuário", key="reg_user", placeholder="Seu apelido", label_visibility="collapsed")
            
            if st.button("Criar Conta", use_container_width=True):
                if new_email and new_pwd and new_user:
                    if len(new_pwd) >= 6:
                        res = db.sign_up(new_email, new_pwd, new_user)
                        if res["success"]: st.success("Conta criada! Faça login."); st.balloons()
                        else: st.error(res['error'])
                    else: st.warning("Senha muito curta!")

# ==========================================
# TELA 2: APP PRINCIPAL (LOGADO)
# ==========================================
else:
    # Barra Lateral de Navegação
    with st.sidebar:
        st.title("⚔️ Menu")
        profile = db.get_profile()
        
        if profile:
            st.metric(label="Nível", value=profile['level'])
            st.metric(label="XP", value=profile['experience'])
            st.metric(label="Peso", value=f"{profile.get('current_weight_kg', 0)} kg")
        
        st.markdown("---")
        page = st.radio("Ir para:", ["Dashboard", "Refeições", "Histórico", "Perfil"])
        st.session_state.page = page
        
        if st.button("Sair", use_container_width=True):
            db.sign_out()
            st.rerun()

    # Conteúdo Central
    if st.session_state.page == "Dashboard":
        st.title("📊 Dashboard")
        profile = db.get_profile()
        
        # Cards de informação
        c1, c2, c3 = st.columns(3)
        c1.metric("Calorias Hoje", "0 kcal") # Você pode ligar ao banco depois
        c2.metric("XP Acumulado", profile['experience'])
        c3.metric("Meta", f"{profile.get('goal_weight_kg', 0)} kg")
        
        st.info(f"💭 {psychology.get_daily_motivation()}")

    elif st.session_state.page == "Refeições":
        st.title("🍽️ Registrar Refeição")
        with st.form("meal_form"):
            nome = st.text_input("Nome do Alimento")
            cal = st.number_input("Calorias", value=300)
            if st.form_submit_button("Registrar"):
                if nome:
                    st.success("Registrado com sucesso!")
                    st.rerun()

    elif st.session_state.page == "Histórico":
        st.title("📈 Histórico")
        logs = db.get_weight_history(30)
        if logs:
            df = pd.DataFrame(logs)
            st.line_chart(df.set_index("recorded_at")["weight_kg"])
        else:
            st.info("Registre seu peso no Perfil para ver o gráfico.")

    elif st.session_state.page == "Perfil":
        st.title("👤 Meu Perfil")
        profile = db.get_profile()
        with st.form("profile_form"):
            peso = st.number_input("Seu Peso Atual (kg)", value=float(profile.get("current_weight_kg") or 0.0), step=0.1)
            meta = st.number_input("Meta de Peso (kg)", value=float(profile.get("goal_weight_kg") or 0.0), step=0.1)
            
            if st.form_submit_button("Salvar"):
                db.update_profile({"current_weight_kg": peso, "goal_weight_kg": meta})
                user_service.update_weight(peso)
                st.success("Salvo com sucesso!")
                st.rerun()
