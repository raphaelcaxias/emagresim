import streamlit as st
import pandas as pd
from datetime import date
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine

st.set_page_config(
    page_title="EmagreSim RPG", 
    page_icon="⚔️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Otimizado
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
    
    h1 {
        color: white;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_services():
    db = SupabaseDB()
    return db, UserService(db), PsychologyEngine()

db, user_service, psychology = init_services()

if "user" not in st.session_state: 
    st.session_state.user = None
if "page" not in st.session_state: 
    st.session_state.page = "Dashboard"

# TELA DE LOGIN
if not st.session_state.user:
    # Cabeçalho centralizado
    st.title("⚔️ EmagreSim")
    st.markdown("### Transforme sua dieta em um RPG épico!")
    st.markdown("---")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.15); padding: 2rem; border-radius: 15px; color: white;'>
            <h3>🎮 Como funciona:</h3>
            <ul style='line-height: 2.5;'>
                <li>✅ Registre refeições e ganhe XP</li>
                <li>📈 Suba de nível com consistência</li>
                <li>🏆 Desbloqueie conquistas épicas</li>
                <li>📊 Acompanhe sua evolução</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        with tab1:
            st.markdown("**Acessar Conta**")
            email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
            pwd = st.text_input("Senha", type="password", key="login_pwd", placeholder="••••••••")
            
            if st.button("Entrar", type="primary"):
                if email and pwd:
                    res = db.sign_in(email, pwd)
                    if res["success"]: 
                        st.rerun()
                    else: 
                        st.error("Email ou senha incorretos")
                else:
                    st.warning("Preencha todos os campos")
        
        with tab2:
            st.markdown("**Nova Conta**")
            new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com")
            new_pwd = st.text_input("Senha", type="password", key="reg_pwd", placeholder="Mín. 6 caracteres")
            new_user = st.text_input("Nome de Usuário", key="reg_user", placeholder="Seu nick")
            
            if st.button("Registrar", type="primary"):
                if new_email and new_pwd and new_user:
                    if len(new_pwd) >= 6:
                        res = db.sign_up(new_email, new_pwd, new_user)
                        if res["success"]: 
                            st.success("✅ Conta criada! Faça login.")
                            st.balloons()
                        else: 
                            st.error(f"Erro: {res['error']}")
                    else:
                        st.error("Senha deve ter 6+ caracteres")
                else:
                    st.warning("Preencha todos os campos")

else:
    # USUÁRIO LOGADO
    with st.sidebar:
        st.title("⚔️ EmagreSim")
        st.success(f"Olá, {st.session_state.user.get('user_metadata', {}).get('username', 'Herói')}!")
        st.markdown("---")
        
        menu = st.radio("Menu", ["Dashboard", "Refeições", "Histórico", "Perfil"])
        st.session_state.page = menu
        
        if st.button("🚪 Sair", use_container_width=True):
            db.sign_out()
            st.rerun()

    profile = db.get_profile()
    
    if profile:
        if st.session_state.page == "Dashboard":
            st.title(f"📊 Dashboard - Nível {profile['level']}")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(" XP", profile["experience"])
            c2.metric("⚖️ Peso", f"{profile.get('current_weight_kg', 0)} kg")
            c3.metric("🔥 Streak", f"{profile.get('streak_days', 0)} dias")
            c4.metric(" Meta", f"{profile.get('goal_weight_kg', 0)} kg")
            
            xp_needed = int(100 * (profile['level'] ** 1.5))
            progress = min(profile["experience"] / xp_needed, 1.0)
            
            st.markdown(f"**Progresso:** {profile['experience']}/{xp_needed} XP")
            st.progress(progress)
            
            st.info(f"💭 {psychology.get_daily_motivation()}")
            
            st.markdown("### 🍽️ Refeições de Hoje")
            meals = db.get_daily_meals()
            if meals:
                for m in meals:
                    st.write(f"🍴 **{m['food_name']}**: {m['calories']} kcal")
            else:
                st.info("Nenhuma refeição registrada hoje.")
                
        elif st.session_state.page == "Refeições":
            st.title("🍽️ Registrar Refeição")
            with st.form("meal"):
                c1, c2 = st.columns(2)
                with c1:
                    tipo = st.selectbox("Tipo", ["cafe", "almoco", "jantar", "lanche"])
                    nome = st.text_input("Nome do Alimento")
                with c2:
                    cal = st.number_input("Calorias", min_value=0, value=350)
                    prot = st.number_input("Proteínas (g)", min_value=0.0, value=15.0, step=0.1)
                
                if st.form_submit_button("✅ Registrar"):
                    if nome:
                        res = user_service.register_meal({
                            "meal_type": tipo, 
                            "food_name": nome, 
                            "calories": cal, 
                            "proteins": prot
                        })
                        if res.get("success"):
                            st.balloons()
                            st.success(f"+{res['xp']} XP!")
                            if res.get("leveled_up"): 
                                st.toast(f"🏆 Level Up! Nível {res['level']}")
                            st.rerun()
                        else:
                            st.error("Erro ao salvar")
                    else:
                        st.warning("Digite o nome do alimento")
                        
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
                st.info("Registre seu peso em 'Perfil'")
                
        elif st.session_state.page == "Perfil":
            st.title("👤 Meu Perfil")
            with st.form("profile"):
                c1, c2 = st.columns(2)
                with c1:
                    idade = st.number_input("Idade", value=profile.get("age") or 25)
                    peso = st.number_input("Peso Atual (kg)", value=float(profile.get("current_weight_kg") or 0.0), step=0.1)
                with c2:
                    altura = st.number_input("Altura (cm)", value=profile.get("height_cm") or 170)
                    meta = st.number_input("Peso Meta (kg)", value=float(profile.get("goal_weight_kg") or 0.0), step=0.1)
                
                if st.form_submit_button("💾 Salvar"):
                    db.update_profile({"age": idade, "height_cm": altura, "goal_weight_kg": meta})
                    if peso != profile.get("current_weight_kg"):
                        user_service.update_weight(peso)
                    st.success("Perfil atualizado!")
                    st.rerun()

st.markdown("---")
st.caption("EmagreSim v2.0 | Powered by Supabase")
