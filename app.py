import streamlit as st
import pandas as pd
from datetime import date
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine

# Configuração da Página
st.set_page_config(
    page_title="EmagreSim RPG", 
    page_icon="⚔️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Moderno (Glassmorphism e Gradientes)
st.markdown("""
<style>
    /* Fundo principal */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        min-height: 100vh;
        color: white;
    }
    
    /* Cards transparentes */
    .stAlert, .stInfo, .stSuccess {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,114,255,0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(255,255,255,0.9);
        border-radius: 8px;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Inicialização
@st.cache_resource
def init_services():
    db = SupabaseDB()
    return db, UserService(db), PsychologyEngine()

db, user_service, psychology = init_services()

# Estado
if "user" not in st.session_state: st.session_state.user = None
if "page" not in st.session_state: st.session_state.page = "Dashboard"

# TELA DE LOGIN (NÃO LOGADO)
if not st.session_state.user:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image("https://img.icons8.com/fluency/96/swords.png", width=100)
        st.title("Bem-vindo ao EmagreSim!")
        st.markdown("### Transforme sua dieta em um RPG épico ⚔️")
        st.info("""
        ✅ Registre refeições e ganhe XP  
        📈 Suba de nível com consistência  
        🏆 Desbloqueie conquistas  
        📊 Acompanhe sua evolução
        """)
        
    with col2:
        tab1, tab2 = st.tabs(["🔑 Entrar", " Criar Conta"])
        
        with tab1:
            st.subheader("Acessar Conta")
            email = st.text_input("Email", key="login_email", label_visibility="collapsed", placeholder="seu@email.com")
            pwd = st.text_input("Senha", type="password", key="login_pwd", label_visibility="collapsed", placeholder="••••••••")
            
            if st.button("Entrar", type="primary", use_container_width=True):
                if not email or not pwd:
                    st.warning("Preencha todos os campos!")
                else:
                    res = db.sign_in(email, pwd)
                    if res["success"]: 
                        st.rerun()
                    else: 
                        st.error("Email ou senha incorretos.")
        
        with tab2:
            st.subheader("Nova Conta")
            new_email = st.text_input("Email", key="reg_email", label_visibility="collapsed", placeholder="seu@email.com")
            new_pwd = st.text_input("Senha", type="password", key="reg_pwd", label_visibility="collapsed", placeholder="Mín. 6 caracteres")
            new_user = st.text_input("Nome de Usuário", key="reg_user", label_visibility="collapsed", placeholder="Seu nick")
            
            if st.button("Registrar", type="primary", use_container_width=True):
                if not new_email or not new_pwd or not new_user:
                    st.warning("Preencha todos os campos!")
                elif len(new_pwd) < 6:
                    st.warning("Senha muito curta!")
                else:
                    res = db.sign_up(new_email, new_pwd, new_user)
                    if res["success"]: 
                        st.success("✅ Conta criada! Faça login na aba ao lado.")
                        st.balloons()
                    else: 
                        st.error(f"Erro: {res['error']}")

else:
    # TELA PRINCIPAL (LOGADO)
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/swords.png", width=60)
        st.title("EmagreSim")
        st.success(f"Olá, {st.session_state.user.get('user_metadata', {}).get('username', 'Herói')}!")
        
        menu = st.radio("Menu", ["Dashboard", "Refeições", "Histórico", "Perfil"])
        st.session_state.page = menu
        
        if st.button("🚪 Sair", use_container_width=True):
            db.sign_out()
            st.rerun()

    profile = db.get_profile()
    if not profile:
        st.error("Erro ao carregar perfil. Tente logar novamente.")
    else:
        # Dashboard
        if st.session_state.page == "Dashboard":
            st.title(f"📊 Dashboard - Nível {profile['level']}")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(" XP", profile["experience"])
            c2.metric("⚖️ Peso", f"{profile.get('current_weight_kg', 0)} kg")
            c3.metric("🔥 Streak", f"{profile.get('streak_days', 0)} dias")
            c4.metric(" Meta", f"{profile.get('goal_weight_kg', 0)} kg")
            
            xp_needed = int(100 * (profile['level'] ** 1.5))
            progress = (profile["experience"] / xp_needed)
            
            st.subheader(f"Progresso (XP: {profile['experience']} / {xp_needed})")
            st.progress(min(progress, 1.0))
            
            st.markdown("---")
            st.info(f"💭 {psychology.get_daily_motivation()}")
            
            st.subheader("️ Refeições de Hoje")
            meals = db.get_daily_meals()
            if not meals: st.info("Nenhuma refeição hoje.")
            else:
                for m in meals:
                    st.write(f"🍴 **{m['food_name']}**: {m['calories']} kcal")

        # Refeições
        elif st.session_state.page == "Refeições":
            st.title("🍽️ Registrar Refeição")
            with st.form("meal"):
                c1, c2 = st.columns(2)
                with c1:
                    tipo = st.selectbox("Tipo", ["cafe", "almoco", "jantar", "lanche"])
                    nome = st.text_input("Nome do Alimento")
                with c2:
                    cal = st.number_input("Calorias", min_value=0, value=350)
                    prot = st.number_input("Proteínas", min_value=0.0, value=15.0, step=0.1)
                
                if st.form_submit_button("Registrar"):
                    if nome:
                        res = user_service.register_meal({"meal_type": tipo, "food_name": nome, "calories": cal, "proteins": prot})
                        if res.get("success"):
                            st.balloons()
                            st.success(f"+{res['xp']} XP!")
                            if res.get("leveled_up"): st.toast(f"🏆 Level Up! Nível {res['level']}")
                            st.rerun()
                        else: st.error("Erro ao salvar.")
                    else: st.warning("Digite o nome do alimento.")

        # Histórico
        elif st.session_state.page == "Histórico":
            st.title("📉 Histórico de Peso")
            logs = db.get_weight_history(60)
            if logs:
                df = pd.DataFrame(logs)
                df["recorded_at"] = pd.to_datetime(df["recorded_at"]).dt.date
                df = df.sort_values("recorded_at", ascending=False)
                st.line_chart(df.set_index("recorded_at")["weight_kg"])
                st.dataframe(df[["recorded_at", "weight_kg"]])
            else:
                st.info("Vá em Perfil para registrar seu peso.")

        # Perfil
        elif st.session_state.page == "Perfil":
            st.title("👤 Meu Perfil")
            with st.form("profile"):
                c1, c2 = st.columns(2)
                with c1:
                    idade = st.number_input("Idade", value=profile.get("age") or 25)
                    peso = st.number_input("Peso Atual", value=float(profile.get("current_weight_kg") or 0.0), step=0.1)
                with c2:
                    altura = st.number_input("Altura", value=profile.get("height_cm") or 170)
                    meta = st.number_input("Meta (kg)", value=float(profile.get("goal_weight_kg") or 0.0), step=0.1)
                
                if st.form_submit_button("Salvar"):
                    db.update_profile({"age": idade, "height_cm": altura, "goal_weight_kg": meta})
                    if peso != profile.get("current_weight_kg"):
                        user_service.update_weight(peso)
                    st.success("Salvo!")
                    st.rerun()

st.markdown("---")
st.caption("EmagreSim v2.0")
