import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_path="emagresim.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de usuários
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
        
        # Tabela de refeições
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
        
        # Tabela de progresso
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
        
        # Tabela de conquistas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_name TEXT,
                unlocked_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password: str, email: str = None) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, password, email)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user(self, username: str) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'email': row[3],
                'age': row[4],
                'weight': row[5],
                'height': row[6],
                'goal_weight': row[7],
                'experience': row[8],
                'level': row[9],
                'created_at': row[10]
            }
        return None
    
    def update_user_stats(self, user_id: int, weight: float = None, 
                         experience: int = None, level: int = None):
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
    
    def add_meal(self, user_id: int, meal_data: Dict):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meals (user_id, meal_type, food_name, calories, 
                             proteins, carbs, fats, meal_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            meal_data.get('meal_type'),
            meal_data.get('food_name'),
            meal_data.get('calories'),
            meal_data.get('proteins'),
            meal_data.get('carbs'),
            meal_data.get('fats'),
            meal_data.get('meal_time', datetime.now())
        ))
        conn.commit()
        conn.close()
    
    def get_daily_meals(self, user_id: int, date: datetime = None) -> List[Dict]:
        if date is None:
            date = datetime.now()
        
        conn = self.get_connection()
        query = '''
            SELECT * FROM meals 
            WHERE user_id = ? AND DATE(meal_time) = DATE(?)
            ORDER BY meal_time DESC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id, date))
        conn.close()
        return df.to_dict('records')
    
    def add_progress(self, user_id: int, weight: float, calories_consumed: int = 0,
                    calories_burned: int = 0, notes: str = ""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO progress (user_id, date, weight, calories_consumed, 
                                calories_burned, notes)
            VALUES (?, DATE('now'), ?, ?, ?, ?)
        ''', (user_id, weight, calories_consumed, calories_burned, notes))
        conn.commit()
        conn.close()
    
    def get_progress_history(self, user_id: int, days: int = 30) -> pd.DataFrame:
        conn = self.get_connection()
        query = '''
            SELECT * FROM progress 
            WHERE user_id = ? AND date >= DATE('now', ?)
            ORDER BY date ASC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id, f'-{days} days'))
        conn.close()
        return df
    
    def unlock_achievement(self, user_id: int, achievement_name: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO achievements (user_id, achievement_name, unlocked_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, achievement_name))
        conn.commit()
        conn.close()
