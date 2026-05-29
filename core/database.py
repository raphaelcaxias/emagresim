"""
Database module - Gerenciamento do banco de dados SQLite
"""
import sqlite3
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import os
import hashlib


class Database:
    """Classe principal de gerenciamento de banco de dados"""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa o banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        if db_path is None:
            # Detectar ambiente Streamlit Cloud
            if os.getenv("STREAMLIT_CLOUD"):
                db_path = "/mount/data/emagresim.db"
            else:
                db_path = "emagresim.db"
        
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self) -> None:
        """Inicializa as tabelas do banco de dados"""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Tabela de refeições
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_type TEXT NOT NULL,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                proteins REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fats REAL DEFAULT 0,
                meal_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de progresso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                weight REAL NOT NULL,
                calories_consumed INTEGER DEFAULT 0,
                calories_burned INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, date)
            )
        ''')
        
        # Tabela de conquistas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hasheia a senha usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: str = None) -> Optional[int]:
        """
        Cria um novo usuário
        
        Args:
            username: Nome de usuário
            password: Senha (será hasheada)
            email: Email do usuário
            
        Returns:
            ID do usuário criado ou None se falhar
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Busca usuário por nome de usuário
        
        Args:
            username: Nome de usuário
            
        Returns:
            Dicionário com dados do usuário ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca usuário por ID
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com dados do usuário ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_user_stats(self, user_id: int, **kwargs) -> bool:
        """
        Atualiza estatísticas do usuário
        
        Args:
            user_id: ID do usuário
            **kwargs: Campos a atualizar (weight, experience, level, etc.)
            
        Returns:
            True se atualizou com sucesso
        """
        if not kwargs:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            values.append(value)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        values.append(user_id)
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    
    def update_user_profile(self, user_id: int, age: int, weight: float, 
                           height: float, goal_weight: float, email: str) -> bool:
        """
        Atualiza perfil completo do usuário
        
        Args:
            user_id: ID do usuário
            age: Idade
            weight: Peso atual
            height: Altura em cm
            goal_weight: Peso objetivo
            email: Email
            
        Returns:
            True se atualizou com sucesso
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET age = ?, weight = ?, height = ?, goal_weight = ?, email = ?
            WHERE id = ?
        ''', (age, weight, height, goal_weight, email, user_id))
        conn.commit()
        conn.close()
        return True
    
    def add_meal(self, user_id: int, meal_data: Dict[str, Any]) -> Optional[int]:
        """
        Adiciona uma refeição
        
        Args:
            user_id: ID do usuário
            meal_data: Dicionário com dados da refeição
            
        Returns:
            ID da refeição criada ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO meals (user_id, meal_type, food_name, calories, 
                             proteins, carbs, fats, meal_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            meal_data.get('meal_type', 'snack'),
            meal_data.get('food_name', ''),
            meal_data.get('calories', 0),
            meal_data.get('proteins', 0),
            meal_data.get('carbs', 0),
            meal_data.get('fats', 0),
            meal_data.get('meal_time', datetime.now())
        ))
        meal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return meal_id
    
    def get_daily_meals(self, user_id: int, date_obj: date = None) -> List[Dict]:
        """
        Busca refeições do dia
        
        Args:
            user_id: ID do usuário
            date_obj: Data (padrão: hoje)
            
        Returns:
            Lista de refeições
        """
        if date_obj is None:
            date_obj = date.today()
        
        conn = self.get_connection()
        query = '''
            SELECT * FROM meals 
            WHERE user_id = ? AND DATE(meal_time) = DATE(?)
            ORDER BY meal_time DESC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id, date_obj))
        conn.close()
        return df.to_dict('records')
    
    def add_progress(self, user_id: int, weight: float, 
                    calories_consumed: int = 0, calories_burned: int = 0, 
                    notes: str = "") -> bool:
        """
        Adiciona registro de progresso
        
        Args:
            user_id: ID do usuário
            weight: Peso registrado
            calories_consumed: Calorias consumidas no dia
            calories_burned: Calorias queimadas no dia
            notes: Observações
            
        Returns:
            True se adicionou com sucesso
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO progress 
                (user_id, date, weight, calories_consumed, calories_burned, notes)
                VALUES (?, DATE('now'), ?, ?, ?, ?)
            ''', (user_id, weight, calories_consumed, calories_burned, notes))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_progress_history(self, user_id: int, days: int = 30) -> pd.DataFrame:
        """
        Busca histórico de progresso
        
        Args:
            user_id: ID do usuário
            days: Número de dias para buscar
            
        Returns:
            DataFrame com histórico
        """
        conn = self.get_connection()
        query = '''
            SELECT * FROM progress 
            WHERE user_id = ? AND date >= DATE('now', ?)
            ORDER BY date ASC
        '''
        df = pd.read_sql_query(query, conn, params=(user_id, f'-{days} days'))
        conn.close()
        return df
    
    def add_achievement(self, user_id: int, achievement_name: str, 
                       description: str = "") -> bool:
        """
        Adiciona conquista ao usuário
        
        Args:
            user_id: ID do usuário
            achievement_name: Nome da conquista
            description: Descrição da conquista
            
        Returns:
            True se adicionou com sucesso
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO achievements (user_id, achievement_name, description)
                VALUES (?, ?, ?)
            ''', (user_id, achievement_name, description))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_achievements(self, user_id: int) -> List[Dict]:
        """
        Busca conquistas do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de conquistas
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM achievements WHERE user_id = ? ORDER BY earned_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
