"""
EmagreSim - Aplicação Principal
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from core.database import Database
from core.gamification import GamificationSystem
from core.psychology import PsychologyEngine
from core.services import NutritionService, UserService

# Configuração da Página
st.set_page_config(
    page_title="EmagreSim RPG", 
    page_icon="⚔️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado (Carrega o arquivo se existir)
try:
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- Inicialização de Recursos ---
@st.cache_resource
def init_app():
    db = Database()
    gamification = GamificationSystem(db)
    psychology = PsychologyEngine()
    nutrition = NutritionService(db)
    user_service = UserService(db, gamification)
    return db, gamification, psychology, nutrition, user_service

db, gamification, psychology, nutrition, user_service = init_app()

# --- Gerenciamento de Estado (Session State) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# Função segura de reload para compatibilidade
def safe_rerun():
    try:
        st.rerun()
    except:
        st.experimental_rerun()

# --- Funções de Autenticação ---
def login(username, password):
    user = db.get_user(username)
    if user:
        # Verifica hash da senha (SHA-256 conforme definido no DB)
        import hashlib
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] == hashed_input:
            st.session_state.auth = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['username']
            return True
    return False

def register(username, password, email):
    if db.create_user(username, password, email):
        return True
    return False

def logout():
    st.session_state.auth = False
    st.session_state.user_id = None
    st.session_state.username = None
    safe_rerun()

# --- Interface Principal ---

# Sidebar Lateral
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/fire-element.png", width=60)
    st.title("EmagreSim ⚔️")
    
    if not st.session_state.auth:
        st.subheader("Entrar no Jogo")
        login_user = st.text_input("Usuário", key="login_user")
        login_pass = st.text_input("Senha", type="password", key="login_pass")
        
        if st.button("️ Entrar", type="primary"):
            if login(login_user, login_pass):
                st.success("Login realizado!")
                safe_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        
        st.markdown("---")
        st.subheader("Nova Conta")
        reg_user = st.text_input("Novo Usuário", key="reg_user")
        reg_pass = st.text_input("Nova Senha", type="password", key="reg_pass")
        reg_email = st.text_input("Email (Opcional)", key="reg_email")
        
        if st.button("📜 Registrar"):
            if register(reg_user, reg_pass, reg_email):
                st.success("Conta criada! Faça login.")
            else:
                st.error("Usuário já existe ou dados inválidos.")
    
    else:
        st.success(f"Bem-vindo, {st.session_state.username}!")
        st.markdown(f"---")
        
        menu = st.radio("Menu", ["Dashboard", "Refeições", "Histórico", "Perfil"])
        st.session_state.page = menu
        
        if st.button("🚪 Sair", type="secondary"):
            logout()

# --- Telas (Conteúdo Principal) ---

if not st.session_state.auth:
    # Tela de Boas-Vindas para não logados
    st.title("Bem-vindo ao EmagreSim!")
    st.markdown("""
    ### Transforme sua jornada de emagrecimento em um RPG épico! 🛡️
    
    * 🍎 **Registre refeições** e ganhe XP.
    *  **Suba de nível** mantendo a consistência.
    *  **Desbloqueie conquistas** ao atingir metas.
    
    *Faça login na barra lateral para começar sua aventura!*
    """)
    st.info(" Faça login ou crie sua conta na barra lateral.")

else:
    # Rotas baseadas no Menu
    page = st.session_state.page
    
    # --- Dashboard ---
    if page == "Dashboard":
        st.title(f"📊 Dashboard - Nível {db.get_user_by_id(st.session_state.user_id)['level']}")
        
        user = db.get_user_by_id(st.session_state.user_id)
        summary = nutrition.get_daily_summary(st.session_state.user_id)
        level_info = gamification.get_level_info(st.session_state.user_id)
        streak_info = psychology.analyze_streak(st.session_state.user_id, db)
        
        # Métricas Principais
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(" XP Atual", f"{user['experience']}")
        c2.metric("️ Peso", f"{user['weight']} kg" if user['weight'] else "N/A")
        c3.metric(" Streak", f"{streak_info['current_streak']} dias")
        c4.metric("🏆 Maior Streak", f"{streak_info['longest_streak']} dias")
        
        # Barra de Progresso
        st.subheader("Progresso para Nível {}".format(level_info['level'] + 1))
        st.progress(level_info['progress_percentage'] / 100)
        st.caption(f"{level_info['current_xp']} / {level_info['xp_needed']} XP")
        
        # Resumo do Dia
        st.markdown("---")
        c5, c6 = st.columns(2)
        with c5:
            st.subheader("️ Refeições de Hoje")
            if summary['meals']:
                for m in summary['meals']:
                    st.write(f"**{m['food_name']}**: {m['calories']} kcal")
            else:
                st.info("Nenhuma refeição registrada hoje.")
        
        with c6:
            st.subheader("🧠 Motivação do Dia")
            st.success(psychology.get_daily_motivation())
            st.warning(f"Dica: {psychology.get_health_tip()}")

    # --- Refeições ---
    elif page == "Refeições":
        st.title("🍽️ Registrar Refeição")
        
        # Sugestão Inteligente
        sug = nutrition.suggest_healthy_meal("lanche")
        st.info(f"💡 Sugestão saudável: {sug['name']} (~{sug['calories']} kcal)")
        
        with st.form("meal_form"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["cafe", "almoco", "jantar", "lanche"])
                nome = st.text_input("Nome do Alimento")
            with col2:
                cal = st.number_input("Calorias", min_value=0, value=300)
                prot = st.number_input("Proteínas (g)", min_value=0.0, value=15.0, step=0.1)
            
            submitted = st.form_submit_button("✅ Registrar e Ganhar XP", type="primary")
            
            if submitted and nome:
                result = user_service.register_meal(st.session_state.user_id, {
                    "meal_type": tipo,
                    "food_name": nome,
                    "calories": cal,
                    "proteins": prot,
                    "carbs": 0,
                    "fats": 0
                })
                if result.get('meal_registered'):
                    st.balloons()
                    st.success(f"Refeição registrada! +{result['xp_gained']} XP")
                    if result.get('leveled_up'):
                        st.toast(f" LEVEL UP! Agora você é nível {result['new_level']}")
                    safe_rerun()
                else:
                    st.error("Erro ao registrar.")

    # --- Histórico ---
    elif page == "Histórico":
        st.title(" Histórico de Peso")
        df = db.get_progress_history(st.session_state.user_id, days=60)
        
        if not df.empty:
            # Garante que a coluna date é datetime
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            st.line_chart(df['weight'])
            st.dataframe(df.reset_index()[['date', 'weight']].sort_values('date', ascending=False))
        else:
            st.info("📝 Nenhum histórico de peso encontrado. Vá em 'Perfil' para registrar seu peso inicial.")

    # --- Perfil ---
    elif page == "Perfil":
        st.title("👤 Meu Perfil")
        user = db.get_user_by_id(st.session_state.user_id)
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                idade = st.number_input("Idade", value=user.get('age') or 25)
                peso = st.number_input("Peso Atual (kg)", value=float(user.get('weight') or 0.0), step=0.1)
            with col2:
                altura = st.number_input("Altura (cm)", value=user.get('height') or 170)
                meta = st.number_input("Peso Meta (kg)", value=float(user.get('goal_weight') or 0.0), step=0.1)
            
            email = st.text_input("Email", value=user.get('email') or "")
            
            if st.form_submit_button(" Salvar Alterações", type="primary"):
                # Salva perfil
                db.update_user_profile(st.session_state.user_id, int(idade), float(peso), float(altura), float(meta), email)
                
                # Se mudou o peso, registra progresso
                if float(peso) != user.get('weight'):
                    res = user_service.update_weight(st.session_state.user_id, float(peso))
                    st.success("Perfil atualizado e progresso registrado!")
                    st.info(res['message'])
                else:
                    st.success("Perfil atualizado!")
                safe_rerun()

# Rodapé
st.markdown("---")
st.caption("EmagreSim v1.0 | Feito com Python & Streamlit")
