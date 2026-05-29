import streamlit as st
import pandas as pd
from datetime import date
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine

st.set_page_config(page_title="EmagreSim RPG", page_icon="️", layout="wide")

# Inicialização
@st.cache_resource
def init_services():
    db = SupabaseDB()
    return db, UserService(db), PsychologyEngine()

db, user_service, psychology = init_services()

# Estado
if "auth_token" not in st.session_state: st.session_state.auth_token = None
if "user" not in st.session_state: st.session_state.user = None
if "today_date" not in st.session_state: st.session_state.today_date = str(date.today())
if "page" not in st.session_state: st.session_state.page = "Dashboard"

# Sidebar Auth
with st.sidebar:
    st.title("⚔️ EmagreSim")
    
    if not st.session_state.user:
        tab1, tab2 = st.tabs(["🔑 Entrar", " Criar Conta"])
        with tab1:
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Senha", type="password", key="login_pwd")
            if st.button("Entrar", type="primary", use_container_width=True):
                res = db.sign_in(email, pwd)
                if res["success"]: st.rerun()
                else: st.error(res["error"].message if res["error"] else "Falha no login")
                
        with tab2:
            new_email = st.text_input("Email", key="reg_email")
            new_pwd = st.text_input("Senha", type="password", key="reg_pwd")
            new_user = st.text_input("Nome de Usuário", key="reg_user")
            if st.button("Registrar", use_container_width=True):
                res = db.sign_up(new_email, new_pwd, new_user)
                if res["success"]: st.success("Conta criada! Faça login.")
                else: st.error(res["error"].message if res["error"] else "Erro no registro")
    else:
        st.success(f"Olá, {st.session_state.user['user_metadata'].get('username', 'Aventureiro')}!")
        st.session_state.page = st.radio("Menu", ["Dashboard", "Refeições", "Histórico", "Perfil"])
        if st.button("🚪 Sair", use_container_width=True):
            db.sign_out()
            st.rerun()

# Conteúdo
if not st.session_state.user:
    st.title("🛡️ Bem-vindo ao EmagreSim!")
    st.markdown("Transforme sua jornada em um RPG. Login na barra lateral.")
else:
    profile = db.get_profile()
    
    if st.session_state.page == "Dashboard":
        st.title(f"📊 Dashboard - Nível {profile['level']}")
        c1, c2, c3 = st.columns(3)
        c1.metric(" XP", profile["experience"])
        c2.metric("⚖️ Peso", f"{profile.get('current_weight_kg', 0)} kg")
        c3.metric(" Streak", f"{profile.get('streak_days', 0)} dias")
        
        st.progress((profile["experience"] / (100 * (profile["level"]**1.5))) * 100)
        st.caption(f"Próximo nível: {int(100 * (profile['level']**1.5))} XP")
        
        st.info(psychology.get_daily_motivation())
        
    elif st.session_state.page == "Refeições":
        st.title("🍽️ Registrar Refeição")
        with st.form("meal"):
            c1, c2 = st.columns(2)
            with c1:
                tipo = st.selectbox("Tipo", ["cafe", "almoco", "jantar", "lanche"])
                nome = st.text_input("Alimento")
            with c2:
                cal = st.number_input("Calorias", min_value=0, value=350)
                prot = st.number_input("Proteínas (g)", min_value=0.0, value=15.0, step=0.1)
            
            if st.form_submit_button("✅ Registrar"):
                res = user_service.register_meal({"meal_type": tipo, "food_name": nome, "calories": cal, "proteins": prot})
                if res.get("success"):
                    st.balloons()
                    st.success(f"+{res['xp']} XP")
                    if res.get("leveled_up"): st.toast(f"🎉 LEVEL UP! Nível {res['level']}")
                    st.rerun()
                else: st.error(res["error"])
                
    elif st.session_state.page == "Histórico":
        st.title("📉 Histórico de Peso")
        logs = db.get_weight_history(60)
        if logs:
            df = pd.DataFrame(logs)[["recorded_at", "weight_kg"]].rename(columns={"recorded_at": "Data", "weight_kg": "Peso"})
            df["Data"] = pd.to_datetime(df["Data"]).dt.date
            st.line_chart(df.set_index("Data"))
            st.dataframe(df.sort_values("Data", ascending=False))
        else:
            st.info("Registre seu peso em 'Perfil' para ver o gráfico.")
            
    elif st.session_state.page == "Perfil":
        st.title("👤 Perfil")
        with st.form("profile"):
            c1, c2 = st.columns(2)
            with c1:
                idade = st.number_input("Idade", value=profile.get("age") or 25)
                peso = st.number_input("Peso Atual", value=float(profile.get("current_weight_kg") or 0.0), step=0.1)
            with c2:
                altura = st.number_input("Altura (cm)", value=profile.get("height_cm") or 170)
                meta = st.number_input("Meta (kg)", value=float(profile.get("goal_weight_kg") or 0.0), step=0.1)
            
            if st.form_submit_button("💾 Salvar"):
                db.update_profile({"age": idade, "height_cm": altura, "goal_weight_kg": meta})
                if peso != profile.get("current_weight_kg"):
                    res = user_service.update_weight(peso)
                    st.info(res["message"])
                st.success("Perfil atualizado!")
                st.rerun()

st.caption("EmagreSim v2.0 | Powered by Supabase & Streamlit")
