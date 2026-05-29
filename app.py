import streamlit as st
import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

from core.database import Database
from core.gamification import GamificationSystem
from core.psychology import PsychologyEngine
from core.services import NutritionService, UserService

# Configuração da página
st.set_page_config(
    page_title="EmagreSim - Sua Jornada Fitness",
    page_icon="💪",
    layout="wide"
)

# Inicializar serviços
@st.cache_resource
def init_services():
    db = Database()
    gamification = GamificationSystem(db)
    psychology = PsychologyEngine()
    nutrition = NutritionService(db)
    user_service = UserService(db, gamification)
    return db, gamification, psychology, nutrition, user_service

try:
    db, gamification, psychology, nutrition, user_service = init_services()
except Exception as e:
    st.error(f"Erro ao inicializar: {e}")
    st.stop()

# Inicializar estado da sessão
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Sidebar
st.sidebar.title("💪 EmagreSim")

# Login/Registro
if not st.session_state.authenticated:
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Usuário", key="login_user")
    password = st.sidebar.text_input("Senha", type="password", key="login_pass")
    
    if st.sidebar.button("Entrar", key="btn_login"):
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
    new_username = st.sidebar.text_input("Novo usuário", key="new_user")
    new_password = st.sidebar.text_input("Nova senha", type="password", key="new_pass")
    
    if st.sidebar.button("Registrar", key="btn_register"):
        if new_username and new_password:
            user_id = db.create_user(new_username, new_password)
            if user_id:
                st.sidebar.success("Conta criada! Faça login.")
                st.rerun()
            else:
                st.sidebar.error("Usuário já existe!")
        else:
            st.sidebar.error("Preencha todos os campos!")
    
    # Mostra conteúdo básico para não logados
    st.title("💪 Bem-vindo ao EmagreSim!")
    st.markdown("""
    ### Sua jornada fitness com gamificação!
    
    - 📊 Acompanhe seu progresso
    - 🍽️ Registre suas refeições
    - 🎮 Ganhe XP e suba de nível
    - 🏆 Desbloqueie conquistas
    
    **Faça login ou crie uma conta para começar!**
    """)
    
else:
    # Usuário logado
    st.sidebar.success(f"Bem-vindo, {st.session_state.username}! 🌟")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Menu de navegação
    page = st.sidebar.radio(
        "Navegação",
        ["📊 Dashboard", "🍽️ Refeições", "📈 Histórico", "👤 Perfil"]
    )
    
    # ==================== DASHBOARD ====================
    if page == "📊 Dashboard":
        st.markdown("# 📊 Dashboard")
        
        user = db.get_user_by_id(st.session_state.user_id)
        
        if user:
            # Cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nível", user.get('level', 1))
            with col2:
                st.metric("XP Total", user.get('experience', 0))
            with col3:
                peso = user.get('weight', 0)
                meta = user.get('goal_weight', peso)
                if peso and meta and peso > 0:
                    progresso = max(0, (peso - meta) / peso * 100)
                    st.metric("Progresso da Meta", f"{progresso:.1f}%")
                else:
                    st.metric("Progresso da Meta", "0%")
            with col4:
                streak = psychology.analyze_streak(st.session_state.user_id, db)
                st.metric("Sequência", f"{streak.get('current_streak', 0)} dias")
            
            # Barra de XP
            level_info = gamification.get_level_info(st.session_state.user_id)
            if level_info:
                st.markdown(f"**Progresso para Nível {level_info['level'] + 1}**")
                st.progress(level_info['progress_percentage'] / 100)
                st.caption(f"{level_info['current_xp']} / {level_info['xp_needed']} XP")
            
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
            
            # Motivação
            st.info(f"✨ **Motivação do dia:** {psychology.get_daily_motivation()}")
            
            # Últimas refeições
            if daily_summary['meals']:
                st.subheader("🍽️ Últimas Refeições")
                for meal in daily_summary['meals'][:3]:
                    st.write(f"- **{meal['food_name']}** - {meal['calories']} kcal")
    
    # ==================== REFEIÇÕES ====================
    elif page == "🍽️ Refeições":
        st.markdown("# 🍽️ Registrar Refeição")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("meal_form"):
                meal_type = st.selectbox(
                    "Tipo de Refeição",
                    ["breakfast", "lunch", "dinner", "snack"],
                    format_func=lambda x: {"breakfast": "Café da Manhã", 
                                          "lunch": "Almoço", 
                                          "dinner": "Jantar", 
                                          "snack": "Lanche"}[x]
                )
                
                food_name = st.text_input("Nome do Alimento*")
                calories = st.number_input("Calorias (kcal)", min_value=0, step=10, value=300)
                proteins = st.number_input("Proteínas (g)", min_value=0.0, step=0.5, value=15.0)
                carbs = st.number_input("Carboidratos (g)", min_value=0.0, step=0.5, value=30.0)
                fats = st.number_input("Gorduras (g)", min_value=0.0, step=0.5, value=10.0)
                
                submitted = st.form_submit_button("Registrar Refeição", use_container_width=True)
                
                if submitted:
                    if not food_name:
                        st.error("Digite o nome do alimento!")
                    else:
                        from datetime import datetime
                        meal_data = {
                            "meal_type": meal_type,
                            "food_name": food_name,
                            "calories": calories,
                            "proteins": proteins,
                            "carbs": carbs,
                            "fats": fats,
                            "meal_time": datetime.now()
                        }
                        
                        result = user_service.register_meal(st.session_state.user_id, meal_data)
                        st.success(f"✅ Refeição registrada! +{result['xp_gained']} XP")
                        
                        if result.get('leveled_up'):
                            st.balloons()
                            st.success(f"🎉 PARABÉNS! Você subiu para o Nível {result['new_level']}! 🎉")
                        
                        st.rerun()
        
        with col2:
            st.subheader("🍽️ Refeições de Hoje")
            meals_today = db.get_daily_meals(st.session_state.user_id)
            
            if meals_today:
                import pandas as pd
                df = pd.DataFrame(meals_today)
                st.dataframe(df[['food_name', 'calories', 'proteins']], use_container_width=True)
                
                total_cals = sum(m['calories'] for m in meals_today)
                st.metric("Total de calorias hoje", f"{total_cals} kcal")
            else:
                st.info("Nenhuma refeição registrada hoje.")
            
            st.subheader("💡 Sugestão Saudável")
            suggestion = nutrition.suggest_healthy_meal("lunch")
            st.info(f"🍽️ **{suggestion['name']}** - {suggestion['calories']} kcal")
    
    # ==================== HISTÓRICO ====================
    elif page == "📈 Histórico":
        st.markdown("# 📈 Histórico de Progresso")
        
        progress_df = db.get_progress_history(st.session_state.user_id, days=30)
        
        if not progress_df.empty:
            import plotly.express as px
            
            fig = px.line(progress_df, x='date', y='weight', 
                         title="Evolução do Peso - Últimos 30 dias",
                         markers=True)
            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Peso (kg)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                peso_inicial = progress_df.iloc[0]['weight']
                peso_atual = progress_df.iloc[-1]['weight']
                perda = peso_inicial - peso_atual
                st.metric("Perda Total", f"{abs(perda):.1f} kg")
            with col2:
                streak = psychology.analyze_streak(st.session_state.user_id, db)
                st.metric("Maior Sequência", f"{streak.get('longest_streak', 0)} dias")
            with col3:
                st.metric("Registros", len(progress_df))
            
            st.subheader("📋 Registros Detalhados")
            st.dataframe(progress_df[['date', 'weight', 'notes']], use_container_width=True)
        else:
            st.info("Nenhum registro de progresso encontrado. Vá em Perfil e registre seu peso!")
    
    # ==================== PERFIL ====================
    elif page == "👤 Perfil":
        st.markdown("# 👤 Meu Perfil")
        
        user = db.get_user_by_id(st.session_state.user_id)
        
        if user:
            with st.form("profile_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    age = st.number_input("Idade", min_value=0, max_value=120, 
                                         value=user.get('age') or 0)
                    weight = st.number_input("Peso (kg)", min_value=0.0, max_value=300.0,
                                            value=user.get('weight') or 0.0, step=0.5)
                
                with col2:
                    height = st.number_input("Altura (cm)", min_value=0, max_value=250,
                                            value=user.get('height') or 0)
                    goal_weight = st.number_input("Peso Alvo (kg)", min_value=0.0, max_value=300.0,
                                                 value=user.get('goal_weight') or 0.0, step=0.5)
                
                submitted = st.form_submit_button("Atualizar Perfil", use_container_width=True)
                
                if submitted:
                    db.update_user_profile(st.session_state.user_id, age, weight, height, goal_weight, "")
                    st.success("Perfil atualizado com sucesso!")
                    
                    if weight != user.get('weight'):
                        result = user_service.update_weight(st.session_state.user_id, weight)
                        st.info(result['message'])
                    
                    st.rerun()
            
            # Conquistas
            st.subheader("🏆 Conquistas")
            st.info("Complete desafios para desbloquear conquistas!")
            st.caption("🎯 Nível 5: Iniciante Dedicado")
            st.caption("⚡ Nível 10: Guerreiro Fitness")
            st.caption("🔥 Nível 20: Lenda do EmagreSim")
    
    # Dica na sidebar
    st.sidebar.markdown("---")
    st.sidebar.info(f"💡 **Dica de Saúde:**\n{psychology.get_health_tip()}")

# Rodapé
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>EmagreSim - Transforme sua saúde com gamificação 🎮</p>",
    unsafe_allow_html=True
)
