import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from core.database import Database
from core.gamification import GamificationSystem
from core.psychology import PsychologyEngine
from core.services import NutritionService, UserService

# Configuração da página
st.set_page_config(
    page_title="EmagreSim - Sua Jornada Fitness",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar CSS
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inicializar serviços
@st.cache_resource
def init_services():
    db = Database()
    gamification = GamificationSystem(db)
    psychology = PsychologyEngine()
    nutrition = NutritionService(db)
    user_service = UserService(db, gamification)
    return db, gamification, psychology, nutrition, user_service

db, gamification, psychology, nutrition, user_service = init_services()

# Inicializar estado da sessão
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Sidebar - Login/Registro
st.sidebar.title("💪 EmagreSim")

if not st.session_state.authenticated:
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    
    if st.sidebar.button("Entrar"):
        user = db.get_user(username)
        if user and user['password'] == password:
            st.session_state.authenticated = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['username']
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha inválidos!")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Novo por aqui?")
    new_username = st.sidebar.text_input("Novo usuário")
    new_password = st.sidebar.text_input("Nova senha", type="password")
    
    if st.sidebar.button("Registrar"):
        if new_username and new_password:
            user_id = db.create_user(new_username, new_password)
            if user_id:
                st.sidebar.success("Conta criada! Faça login.")
            else:
                st.sidebar.error("Usuário já existe!")
        else:
            st.sidebar.error("Preencha todos os campos!")
else:
    # Menu principal
    st.sidebar.success(f"Bem-vindo, {st.session_state.username}! 🌟")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navegação
    page = st.sidebar.radio(
        "Navegação",
        ["📊 Dashboard", "🍽️ Refeições", "📈 Histórico", "👤 Perfil"]
    )
    
    # Conteúdo principal baseado na página
    if page == "📊 Dashboard":
        st.markdown('<h1 class="main-header">📊 Dashboard - EmagreSim</h1>', unsafe_allow_html=True)
        
        # Informações do usuário
        user = db.get_user_by_id(st.session_state.user_id)
        
        # Cards de progresso
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nível", user.get('level', 1))
        with col2:
            st.metric("XP Total", user.get('experience', 0))
        with col3:
            weight = user.get('weight', 0)
            goal = user.get('goal_weight', weight)
            progress_to_goal = max(0, (weight - goal) / weight * 100) if weight > 0 else 0
            st.metric("Progresso para Meta", f"{progress_to_goal:.1f}%")
        with col4:
            streak_data = psychology.analyze_streak(st.session_state.user_id, db)
            st.metric("🔥 Sequência", f"{streak_data['current_streak']} dias")
        
        # Barra de XP
        level_info = gamification.get_level_info(st.session_state.user_id)
        st.markdown(f"""
        <div class="card">
            <h3>Progresso para Nível {level_info['level'] + 1}</h3>
            <div class="xp-bar" style="width: {level_info['progress_percentage']}%">
                {level_info['progress_percentage']:.0f}%
            </div>
            <p>{level_info['current_xp']} / {level_info['xp_needed']} XP</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Resumo do dia
        st.subheader("📊 Resumo de Hoje")
        daily_summary = nutrition.get_daily_summary(st.session_state.user_id)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Calorias", f"{daily_summary['total_calories']} kcal")
        with col2:
            st.metric("Proteínas", f"{daily_summary['total_proteins']:.1f}g")
        with col3:
            st.metric("Refeições", daily_summary['meal_count'])
        
        # Motivação diária
        st.info(f"✨ **Motivação do dia:** {psychology.get_daily_motivation()}")
        
        # Últimas refeições
        if daily_summary['meals']:
            st.subheader("🍽️ Últimas Refeições")
            for meal in daily_summary['meals'][:5]:
                st.write(f"- **{meal['food_name']}** - {meal['calories']} kcal")
    
    elif page == "🍽️ Refeições":
        st.markdown('<h1 class="main-header">🍽️ Registrar Refeição</h1>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("meal_form"):
                meal_type = st.selectbox(
                    "Tipo de Refeição",
                    ["breakfast", "lunch", "dinner", "snack"],
                    format_func=lambda x: {
                        "breakfast": "Café da Manhã",
                        "lunch": "Almoço",
                        "dinner": "Jantar",
                        "snack": "Lanche"
                    }[x]
                )
                
                food_name = st.text_input("Alimento")
                calories = st.number_input("Calorias (kcal)", min_value=0
