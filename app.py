import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import random
import math
from typing import Dict, List, Optional

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="EmagreSim - Sua Jornada Fitness",
    page_icon="💪",
    layout="wide"
)

# ==================== BANCO DE DADOS ====================
class Database:
    def __init__(self, db_path="emagresim.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                age INTEGER,
                weight REAL,
                height REAL,
                goal_weight REAL,
                experience INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                meal_type TEXT,
                food_name TEXT,
                calories INTEGER,
                proteins REAL,
                carbs REAL,
                fats REAL,
                meal_time TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                weight REAL,
                calories_consumed INTEGER,
                calories_burned INTEGER,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password: str, email: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                          (username, password, email))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user(self, username: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'username': row[1], 'password': row[2], 'email': row[3],
                   'age': row[4], 'weight': row[5], 'height': row[6], 'goal_weight': row[7],
                   'experience': row[8], 'level': row[9], 'created_at': row[10]}
        return None
    
    def get_user_by_id(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'username': row[1], 'password': row[2], 'email': row[3],
                   'age': row[4], 'weight': row[5], 'height': row[6], 'goal_weight': row[7],
                   'experience': row[8], 'level': row[9], 'created_at': row[10]}
        return None
    
    def update_user_stats(self, user_id: int, weight=None, experience=None, level=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        updates = []
        values = []
        if weight is not None:
            updates.append("weight = ?")
            values.append(weight)
        if experience is not None:
            updates.append("experience = ?")
            values.append(experience)
        if level is not None:
            updates.append("level = ?")
            values.append(level)
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            values.append(user_id)
            cursor.execute(query, values)
            conn.commit()
        conn.close()
    
    def update_user_profile(self, user_id: int, age: int, weight: float, height: int, goal_weight: float, email: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET age = ?, weight = ?, height = ?, goal_weight = ?, email = ?
            WHERE id = ?
        ''', (age, weight, height, goal_weight, email, user_id))
        conn.commit()
        conn.close()
    
    def add_meal(self, user_id: int, meal_data: Dict):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meals (user_id, meal_type, food_name, calories, proteins, carbs, fats, meal_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_data.get('meal_type'), meal_data.get('food_name'),
              meal_data.get('calories'), meal_data.get('proteins'), meal_data.get('carbs'),
              meal_data.get('fats'), meal_data.get('meal_time', datetime.now())))
        conn.commit()
        conn.close()
    
    def get_daily_meals(self, user_id: int, date_obj: datetime = None):
        if date_obj is None:
            date_obj = datetime.now()
        conn = self.get_connection()
        query = '''
            SELECT * FROM meals WHERE user_id = ? AND DATE(meal_time) = DATE(?)
            ORDER BY meal_time DESC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id, date_obj))
        conn.close()
        return df.to_dict('records')
    
    def add_progress(self, user_id: int, weight: float, calories_consumed=0, calories_burned=0, notes=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO progress (user_id, date, weight, calories_consumed, calories_burned, notes)
            VALUES (?, DATE('now'), ?, ?, ?, ?)
        ''', (user_id, weight, calories_consumed, calories_burned, notes))
        conn.commit()
        conn.close()
    
    def get_progress_history(self, user_id: int, days: int = 30):
        conn = self.get_connection()
        query = '''
            SELECT * FROM progress WHERE user_id = ? AND date >= DATE('now', ?)
            ORDER BY date ASC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id, f'-{days} days'))
        conn.close()
        return df

# ==================== GAMIFICAÇÃO ====================
class GamificationSystem:
    def __init__(self, db: Database):
        self.db = db
    
    def calculate_xp_for_level(self, level: int) -> int:
        return int(100 * (level ** 1.5))
    
    def add_experience(self, user_id: int, xp_gained: int) -> Dict:
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        new_xp = user['experience'] + xp_gained
        current_level = user['level']
        new_level = current_level
        
        while new_xp >= self.calculate_xp_for_level(new_level):
            new_xp -= self.calculate_xp_for_level(new_level)
            new_level += 1
        
        self.db.update_user_stats(user_id, experience=new_xp, level=new_level)
        
        return {
            "xp_gained": xp_gained,
            "new_total_xp": new_xp,
            "old_level": current_level,
            "new_level": new_level,
            "leveled_up": new_level > current_level
        }
    
    def reward_for_meal(self, calories: int, is_healthy: bool = True) -> int:
        base_xp = 10
        if is_healthy:
            base_xp += 5
        if 300 <= calories <= 600:
            base_xp += 10
        return base_xp
    
    def get_level_info(self, user_id: int) -> Dict:
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {}
        current_level = user['level']
        current_xp = user['experience']
        next_level_xp = self.calculate_xp_for_level(current_level)
        progress_percentage = (current_xp / next_level_xp) * 100 if next_level_xp > 0 else 0
        return {
            "level": current_level,
            "current_xp": current_xp,
            "xp_needed": next_level_xp,
            "progress_percentage": progress_percentage
        }

# ==================== PSICOLOGIA ====================
class PsychologyEngine:
    def __init__(self):
        self.motivation_phrases = [
            "💪 Cada pequeno passo conta! Você está no caminho certo!",
            "🌟 Hoje é um novo dia para fazer escolhas saudáveis!",
            "🎯 Lembre-se: consistência é mais importante que perfeição!",
            "✨ Seu eu do futuro vai agradecer pelos esforços de hoje!"
        ]
        self.tips = [
            "Beba um copo de água antes de cada refeição",
            "Faça pequenas pausas ativas durante o dia",
            "Durma 7-8 horas por noite para melhor recuperação",
            "Coma devagar e mastigue bem os alimentos"
        ]
    
    def get_daily_motivation(self) -> str:
        return random.choice(self.motivation_phrases)
    
    def get_health_tip(self) -> str:
        return random.choice(self.tips)
    
    def analyze_streak(self, user_id: int, db) -> Dict:
        progress = db.get_progress_history(user_id, days=30)
        if progress.empty:
            return {"current_streak": 0, "longest_streak": 0}
        
        current_streak = 0
        longest_streak = 0
        streak = 0
        last_date = None
        
        for _, row in progress.iterrows():
            current_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            if last_date and (current_date - last_date).days == 1:
                streak += 1
            else:
                streak = 1
            longest_streak = max(longest_streak, streak)
            if current_date == datetime.now().date():
                current_streak = streak
            last_date = current_date
        
        return {"current_streak": current_streak, "longest_streak": longest_streak}

# ==================== SERVIÇOS ====================
class NutritionService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_daily_summary(self, user_id: int) -> Dict:
        meals = self.db.get_daily_meals(user_id)
        return {
            "total_calories": sum(m.get('calories', 0) for m in meals),
            "total_proteins": sum(m.get('proteins', 0) for m in meals),
            "meal_count": len(meals),
            "meals": meals
        }
    
    def suggest_healthy_meal(self, meal_type: str) -> Dict:
        suggestions = {
            "breakfast": [{"name": "Vitamina de frutas + aveia", "calories": 350}],
            "lunch": [{"name": "Frango grelhado + arroz integral + salada", "calories": 550}],
            "dinner": [{"name": "Sopa de legumes com frango", "calories": 350}],
            "snack": [{"name": "Frutas + castanhas", "calories": 150}]
        }
        return random.choice(suggestions.get(meal_type, suggestions["snack"]))

class UserService:
    def __init__(self, db: Database, gamification: GamificationSystem):
        self.db = db
        self.gamification = gamification
    
    def register_meal(self, user_id: int, meal_data: Dict) -> Dict:
        self.db.add_meal(user_id, meal_data)
        calories = meal_data.get('calories', 0)
        proteins = meal_data.get('proteins', 0)
        is_healthy = calories < 600 and proteins > 10
        xp_gained = self.gamification.reward_for_meal(calories, is_healthy)
        xp_result = self.gamification.add_experience(user_id, xp_gained)
        return {"meal_registered": True, "xp_gained": xp_gained, **xp_result}
    
    def update_weight(self, user_id: int, new_weight: float) -> Dict:
        user = self.db.get_user_by_id(user_id)
        old_weight = user.get('weight', new_weight)
        self.db.add_progress(user_id, new_weight)
        self.db.update_user_stats(user_id, weight=new_weight)
        weight_change = new_weight - old_weight if old_weight else 0
        message = f"🎉 Você perdeu {abs(weight_change):.1f}kg!" if weight_change < 0 else "Continue firme!"
        return {"old_weight": old_weight, "new_weight": new_weight, "weight_change": weight_change, "message": message}

# ==================== INICIALIZAÇÃO ====================
@st.cache_resource
def init_services():
    db = Database()
    gamification = GamificationSystem(db)
    psychology = PsychologyEngine()
    nutrition = NutritionService(db)
    user_service = UserService(db, gamification)
    return db, gamification, psychology, nutrition, user_service

db, gamification, psychology, nutrition, user_service = init_services()

# ==================== ESTADO DA SESSÃO ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# ==================== INTERFACE ====================
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
    st.sidebar.success(f"Bem-vindo, {st.session_state.username}! 🌟")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Navegação", ["📊 Dashboard", "🍽️ Refeições", "📈 Histórico", "👤 Perfil"])
    
    # ========== DASHBOARD ==========
    if page == "📊 Dashboard":
        st.title("📊 Dashboard - EmagreSim")
        
        user = db.get_user_by_id(st.session_state.user_id)
        if user:
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Nível", user.get('level', 1))
            with col2: st.metric("XP Total", user.get('experience', 0))
            with col3: 
                weight = user.get('weight', 0)
                goal = user.get('goal_weight', weight)
                progress_to_goal = max(0, (weight - goal) / weight * 100) if weight > 0 else 0
                st.metric("Progresso para Meta", f"{progress_to_goal:.1f}%")
            with col4:
                streak = psychology.analyze_streak(st.session_state.user_id, db)
                st.metric("🔥 Sequência", f"{streak['current_streak']} dias")
            
            level_info = gamification.get_level_info(st.session_state.user_id)
            if level_info:
                st.progress(level_info['progress_percentage'] / 100, text=f"XP: {level_info['current_xp']}/{level_info['xp_needed']}")
            
            daily_summary = nutrition.get_daily_summary(st.session_state.user_id)
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Calorias", f"{daily_summary['total_calories']} kcal")
            with col2: st.metric("Proteínas", f"{daily_summary['total_proteins']:.1f}g")
            with col3: st.metric("Refeições", daily_summary['meal_count'])
            
            st.info(f"✨ **Motivação:** {psychology.get_daily_motivation()}")
    
    # ========== REFEIÇÕES ==========
    elif page == "🍽️ Refeições":
        st.title("🍽️ Registrar Refeição")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("meal_form"):
                meal_type = st.selectbox("Tipo", ["breakfast", "lunch", "dinner", "snack"],
                                        format_func=lambda x: {"breakfast": "Café", "lunch": "Almoço", 
                                                              "dinner": "Jantar", "snack": "Lanche"}[x])
                food_name = st.text_input("Alimento")
                calories = st.number_input("Calorias", min_value=0, value=300)
                proteins = st.number_input("Proteínas (g)", min_value=0.0, value=15.0)
                carbs = st.number_input("Carboidratos (g)", min_value=0.0, value=30.0)
                fats = st.number_input("Gorduras (g)", min_value=0.0, value=10.0)
                
                if st.form_submit_button("Registrar", use_container_width=True) and food_name:
                    result = user_service.register_meal(st.session_state.user_id, {
                        "meal_type": meal_type, "food_name": food_name, "calories": calories,
                        "proteins": proteins, "carbs": carbs, "fats": fats, "meal_time": datetime.now()
                    })
                    st.success(f"✅ +{result['xp_gained']} XP!")
                    if result.get('leveled_up'):
                        st.balloons()
                        st.success(f"🎉 SUBIU PARA NÍVEL {result['new_level']}! 🎉")
        
        with col2:
            st.subheader("Refeições de Hoje")
            meals = db.get_daily_meals(st.session_state.user_id)
            if meals:
                df = pd.DataFrame(meals)
                st.dataframe(df[['food_name', 'calories']], use_container_width=True)
            else:
                st.info("Nenhuma refeição hoje.")
    
    # ========== HISTÓRICO ==========
    elif page == "📈 Histórico":
        st.title("📈 Histórico de Progresso")
        
        progress_df = db.get_progress_history(st.session_state.user_id, days=30)
        if not progress_df.empty:
            fig = px.line(progress_df, x='date', y='weight', title="Evolução do Peso", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                initial = progress_df.iloc[0]['weight']
                current = progress_df.iloc[-1]['weight']
                st.metric("Perda Total", f"{initial - current:.1f} kg")
            with col2:
                streak = psychology.analyze_streak(st.session_state.user_id, db)
                st.metric("Maior Sequência", f"{streak['longest_streak']} dias")
            
            st.dataframe(progress_df[['date', 'weight', 'notes']], use_container_width=True)
        else:
            st.info("Nenhum registro de progresso ainda.")
    
    # ========== PERFIL ==========
    elif page == "👤 Perfil":
        st.title("👤 Meu Perfil")
        
        user = db.get_user_by_id(st.session_state.user_id)
        if user:
            with st.form("profile_form"):
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input("Idade", min_value=0, value=user.get('age', 0) or 0)
                    weight = st.number_input("Peso (kg)", min_value=0.0, value=user.get('weight', 0.0) or 0.0, step=0.5)
                with col2:
                    height = st.number_input("Altura (cm)", min_value=0, value=user.get('height', 0) or 0)
                    goal = st.number_input("Peso Alvo", min_value=0.0, value=user.get('goal_weight', weight) or weight, step=0.5)
                
                if st.form_submit_button("Atualizar", use_container_width=True):
                    db.update_user_profile(st.session_state.user_id, age, weight, height, goal, "")
                    st.success("Perfil atualizado!")
                    if weight != user.get('weight'):
                        result = user_service.update_weight(st.session_state.user_id, weight)
                        st.info(result['message'])
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"💡 {psychology.get_health_tip()}")

st.markdown("---")
st.markdown("<p style='text-align: center;'>💪 EmagreSim - Transforme sua saúde com gamificação</p>", unsafe_allow_html=True)
