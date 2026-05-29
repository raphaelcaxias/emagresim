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
                calories = st.number_input("Calorias (kcal)", min_value=0, step=10)
                proteins = st.number_input("Proteínas (g)", min_value=0.0, step=0.5)
                carbs = st.number_input("Carboidratos (g)", min_value=0.0, step=0.5)
                fats = st.number_input("Gorduras (g)", min_value=0.0, step=0.5)
                
                submitted = st.form_submit_button("Registrar Refeição")
                
                if submitted and food_name:
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
                    
                    if result['meal_registered']:
                        st.success(f"✅ Refeição registrada! +{result['xp_gained']} XP")
                        if result['leveled_up']:
                            st.balloons()
                            st.success(f"🎉 PARABÉNS! Você subiu para o Nível {result['new_level']}! 🎉")
        
        with col2:
            st.subheader("🍽️ Refeições de Hoje")
            meals_today = db.get_daily_meals(st.session_state.user_id)
            
            if meals_today:
                df = pd.DataFrame(meals_today)
                st.dataframe(df[['food_name', 'calories', 'proteins', 'carbs', 'fats']])
                
                # Gráfico de calorias
                fig = px.bar(df, x='food_name', y='calories', 
                             title="Calorias por Refeição")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhuma refeição registrada hoje.")
            
            # Sugestão saudável
            st.subheader("💡 Sugestão Saudável")
            suggestion = nutrition.suggest_healthy_meal(meal_type if 'meal_type' in locals() else "snack")
            st.info(f"🍽️ **{suggestion['name']}**\n\nCalorias: {suggestion['calories']} kcal")
    
    elif page == "📈 Histórico":
        st.markdown('<h1 class="main-header">📈 Histórico de Progresso</h1>', unsafe_allow_html=True)
        
        # Gráfico de peso
        progress_df = db.get_progress_history(st.session_state.user_id, days=30)
        
        if not progress_df.empty:
            fig = px.line(progress_df, x='date', y='weight', 
                         title="Evolução do Peso - Últimos 30 dias",
                         markers=True)
            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Peso (kg)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                initial_weight = progress_df.iloc[0]['weight']
                current_weight = progress_df.iloc[-1]['weight']
                total_loss = initial_weight - current_weight
                st.metric("Perda Total", f"{total_loss:.1f} kg" if total_loss > 0 else f"{total_loss:.1f} kg")
            with col2:
                avg_loss = progress_df['weight'].diff().mean()
                st.metric("Média por Dia", f"{avg_loss:.2f} kg")
            with col3:
                streak_data = psychology.analyze_streak(st.session_state.user_id, db)
                st.metric("Maior Sequência", f"{streak_data['longest_streak']} dias")
            
            # Tabela de histórico
            st.subheader("📋 Registros Detalhados")
            st.dataframe(progress_df[['date', 'weight', 'calories_consumed', 'calories_burned', 'notes']])
        else:
            st.info("Nenhum registro de progresso encontrado. Comece a registrar seu peso!")
    
    elif page == "👤 Perfil":
        st.markdown('<h1 class="main-header">👤 Meu Perfil</h1>', unsafe_allow_html=True)
        
        user = db.get_user_by_id(st.session_state.user_id)
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("Idade", min_value=0, max_value=120, 
                                     value=user.get('age', 0))
                weight = st.number_input("Peso (kg)", min_value=0.0, max_value=300.0,
                                        value=user.get('weight', 0.0), step=0.5)
                height = st.number_input("Altura (cm)", min_value=0, max_value=250,
                                        value=user.get('height', 0))
            
            with col2:
                goal_weight = st.number_input("Peso Alvo (kg)", min_value=0.0, max_value=300.0,
                                             value=user.get('goal_weight', weight), step=0.5)
                email = st.text_input("Email", value=user.get('email', ''))
            
            submitted = st.form_submit_button("Atualizar Perfil")
            
            if submitted:
                # Atualizar dados
                db.update_user_profile(st.session_state.user_id, age, weight, height, goal_weight, email)
                st.success("Perfil atualizado com sucesso!")
                
                # Registrar peso se mudou
                if weight != user.get('weight'):
                    result = user_service.update_weight(st.session_state.user_id, weight)
                    st.info(result['message'])
        
        # Conquistas
        st.subheader("🏆 Conquistas")
        # Buscar conquistas do usuário (implementar no database.py)
        st.info("Complete desafios para desbloquear conquistas!")
    
    # Dica de saúde na sidebar
    st.sidebar.markdown("---")
    st.sidebar.info(f"💡 **Dica de Saúde:**\n{psychology.get_health_tip()}")

# Rodapé
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>EmagreSim - Transforme sua saúde com gamificação 🎮</p>",
    unsafe_allow_html=True
)
