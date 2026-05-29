import streamlit as st
import pandas as pd
from datetime import date
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine

st.set_page_config(
    page_title="EmagreSim RPG", 
    page_icon="⚔️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Moderno e Profissional
st.markdown("""
<style>
    /* Fundo gradiente moderno */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Cards com glassmorphism */
    .stAlert, .stInfo, .stSuccess, .stWarning {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Métricas estilizadas */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Inputs modernos */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px;
    }
    
    /* Título principal */
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        font-weight: 700;
    }
    
    /* Animação de fade in */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main > div {
        animation: fadeIn 0.5s ease-in;
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
if "auth_token" not in st.session_state: 
    st.session_state.auth_token = None
if "user" not in st.session_state: 
    st.session_state.user = None
if "today_date" not in st.session_state: 
    st.session_state.today_date = str(date.today())
if "page" not in st.session_state: 
    st.session_state.page = "Dashboard"

# Layout Principal
if not st.session_state.user:
    # PÁGINA INICIAL MODERNA
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style='padding: 40px;'>
            <h1 style='font-size: 3.5em; margin-bottom: 20px;'>⚔️ EmagreSim</h1>
            <h2 style='color: white; font-weight: 300;'>Transforme sua jornada em um RPG épico!</h2>
            
            <div style='background: rgba(255,255,255,0.15); padding: 30px; border-radius: 15px; margin-top: 30px; backdrop-filter: blur(10px);'>
                <h3 style='color: white;'>🎮 Como funciona:</h3>
                <ul style='color: white; font-size: 1.1em; line-height: 2;'>
                    <li>🍽️ Registre refeições e ganhe XP</li>
                    <li>📈 Suba de nível com consistência</li>
                    <li>🏆 Desbloqueie conquistas épicas</li>
                    <li>📊 Acompanhe seu progresso</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='padding: 40px;'></div>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        with tab1:
            st.markdown("### Bem-vindo de volta!")
            email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
            pwd = st.text_input("Senha", type="password", key="login_pwd", placeholder="••••••••")
            
            if st.button("Entrar na Aventura", type="primary", use_container_width=True):
                res = db.sign_in(email, pwd)
                if res["success"]: 
                    st.balloons()
                    st.rerun()
                else: 
                    st.error("Email ou senha incorretos!")
        
        with tab2:
            st.markdown("### Comece sua jornada!")
            new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com")
            new_pwd = st.text_input("Senha", type="password", key="reg_pwd", placeholder="Mínimo 6 caracteres")
            new_user = st.text_input("Nome de Usuário", key="reg_user", placeholder="Como quer ser chamado?")
            
            if st.button("Criar Conta Grátis", type="primary", use_container_width=True):
                if len(new_pwd) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres!")
                else:
                    res = db.sign_up(new_email, new_pwd, new_user)
                    if res["success"]: 
                        st.success("✅ Conta criada! Faça login.")
                        st.balloons()
                    else: 
                        error_msg = res["error"] if res["error"] else "Erro no registro"
                        st.error(error_msg)

else:
    # SIDEBAR PARA USUÁRIOS LOGADOS
    with st.sidebar:
        st.title("⚔️ EmagreSim")
        st.success(f"Olá, {st.session_state.user['user_metadata'].get('username', 'Aventureiro')}!")
        st.markdown("---")
        
        menu = st.radio(
            "Menu", 
            ["Dashboard", "Refeições", "Histórico", "Perfil"],
            label_visibility="collapsed"
        )
        st.session_state.page = menu
        
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            db.sign_out()
            st.rerun()
    
    # CONTEÚDO PRINCIPAL
    profile = db.get_profile()
    
    if st.session_state.page == "Dashboard":
        st.title(f"📊 Dashboard - Nível {profile['level']}")
        
        # Métricas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("⚡ XP", f"{profile['experience']}")
        c2.metric("⚖️ Peso", f"{profile.get('current_weight_kg', 0)} kg")
        c3.metric("🔥 Streak", f"{profile.get('streak_days', 0)} dias")
        c4.metric("🎯 Meta", f"{profile.get('goal_weight_kg', 0)} kg")
        
        # Barra de progresso
        st.markdown("### 📈 Progresso para o Próximo Nível")
        xp_needed = int(100 * (profile['level'] ** 1.5))
        progress = (profile["experience"] / xp_needed) * 100
        st.progress(min(progress / 100, 1.0))
        st.caption(f"{profile['experience']} / {xp_needed} XP")
        
        # Motivação
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"💭 {psychology.get_daily_motivation()}")
        with col2:
            st.warning(f"💡 Dica: {psychology.get_tip()}")
        
        # Refeições de hoje
        st.markdown("### 🍽️ Refeições de Hoje")
        meals = db.get_daily_meals()
        if meals:
            for meal in meals:
                st.markdown(f"**{meal['food_name']}** - {meal['calories']} kcal ({meal['meal_type']})")
        else:
            st.info("Nenhuma refeição registrada hoje.")
            
    elif st.session_state.page == "Refeições":
        st.title("🍽️ Registrar Refeição")
        
        with st.form("meal_form"):
            c1, c2 = st.columns(2)
            with c1:
                tipo = st.selectbox("Tipo", ["cafe", "almoco", "jantar", "lanche"])
                nome = st.text_input("Nome do Alimento")
            with c2:
                cal = st.number_input("Calorias", min_value=0, value=350)
                prot = st.number_input("Proteínas (g)", min_value=0.0, value=15.0, step=0.1)
            
            submitted = st.form_submit_button("✅ Registrar e Ganhar XP", type="primary", use_container_width=True)
            
            if submitted and nome:
                res = user_service.register_meal({
                    "meal_type": tipo, 
                    "food_name": nome, 
                    "calories": cal, 
                    "proteins": prot
                })
                if res.get("success"):
                    st.balloons()
                    st.success(f"🎉 +{res['xp']} XP ganhos!")
                    if res.get("leveled_up"): 
                        st.toast(f"🏆 LEVEL UP! Você alcançou o nível {res['level']}")
                    st.rerun()
                else: 
                    st.error("Erro ao registrar refeição")
                    
    elif st.session_state.page == "Histórico":
        st.title("📉 Histórico de Peso")
        logs = db.get_weight_history(60)
        if logs:
            df = pd.DataFrame(logs)[["recorded_at", "weight_kg"]]
            df.columns = ["Data", "Peso"]
            df["Data"] = pd.to_datetime(df["Data"]).dt.date
            df = df.sort_values("Data", ascending=False)
            
            st.line_chart(df.set_index("Data"))
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📝 Registre seu peso em 'Perfil' para ver o histórico.")
            
    elif st.session_state.page == "Perfil":
        st.title("👤 Meu Perfil")
        
        with st.form("profile_form"):
            c1, c2 = st.columns(2)
            with c1:
                idade = st.number_input("Idade", value=profile.get("age") or 25)
                peso = st.number_input("Peso Atual (kg)", value=float(profile.get("current_weight_kg") or 0.0), step=0.1)
            with c2:
                altura = st.number_input("Altura (cm)", value=profile.get("height_cm") or 170)
                meta = st.number_input("Peso Meta (kg)", value=float(profile.get("goal_weight_kg") or 0.0), step=0.1)
            
            if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                db.update_profile({
                    "age": idade, 
                    "height_cm": altura, 
                    "goal_weight_kg": meta
                })
                
                if peso != profile.get("current_weight_kg"):
                    res = user_service.update_weight(peso)
                    st.info(res.get("message", "Peso atualizado"))
                
                st.success("✅ Perfil atualizado com sucesso!")
                st.rerun()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.8);'>EmagreSim v2.0 | Powered by Supabase & Streamlit ⚔️</p>", unsafe_allow_html=True)
