import streamlit as st
import datetime
import pandas as pd
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class AppDatabase:
    def __init__(self):
        self.is_real = False
        self.client = None
        
        # Tenta conectar ao Supabase
        try:
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                from supabase import create_client
                self.client = create_client(
                    st.secrets["SUPABASE_URL"], 
                    st.secrets["SUPABASE_KEY"]
                )
                self.is_real = True
                logger.info("✅ Conectado ao Supabase")
        except Exception as e:
            logger.warning(f"⚠️ Supabase indisponível, usando MockDB: {e}")
        
        # Inicializa mock_db com usuário demo
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {
                "meals": [], 
                "weights": [], 
                "achievements": [], 
                "users": {
                    "demo@emagresim.com": {
                        "password": "demo",
                        "name": "Usuário Demo",
                        "email": "demo@emagresim.com",
                        "plan": "free",
                        "current_weight": 75.0,
                        "goal_weight": 70.0,
                        "height": 170,
                        "age": 30,
                        "activity_level": "moderate",
                        "goal": "lose"
                    }
                }
            }
    
    def get_current_user_id(self) -> str:
        """Retorna ID do usuário atual (Supabase ou email)"""
        if self.is_real and self.client:
            try:
                user = self.client.auth.get_user()
                if user and user.user:
                    return user.user.id
            except:
                pass
        return st.session_state.user.get("email") if st.session_state.get("user") else "anonymous"

    # ========== AUTENTICAÇÃO ==========
    
    def get_user(self, email: str, password: str) -> Optional[Dict]:
        """Autentica usuário e retorna dados"""
        try:
            users = st.session_state.mock_db.get("users", {})
            if email in users and users[email].get("password") == password:
                return users[email]
            return None
        except Exception as e:
            logger.error(f"Erro em get_user: {e}")
            return None
    
    def create_user(self, email: str, password: str, name: str) -> bool:
        """Cria novo usuário"""
        try:
            users = st.session_state.mock_db.get("users", {})
            if email in users:
                return False
            
            users[email] = {
                "password": password,
                "name": name,
                "email": email,
                "plan": "free",
                "current_weight": None,
                "goal_weight": None,
                "height": None,
                "age": None,
                "activity_level": "moderate",
                "goal": "lose"
            }
            st.session_state.mock_db["users"] = users
            return True
        except Exception as e:
            logger.error(f"Erro em create_user: {e}")
            return False
    
    def update_profile(self, profile_data: Dict) -> bool:
        """Atualiza perfil do usuário"""
        try:
            user_id = self.get_current_user_id()
            
            if self.is_real and self.client:
                try:
                    self.client.table("profiles").update(profile_data).eq("id", user_id).execute()
                    return True
                except Exception as e:
                    logger.error(f"Erro Supabase update_profile: {e}")
                    return False
            
            # Mock
            if user_id in st.session_state.mock_db["users"]:
                st.session_state.mock_db["users"][user_id].update(profile_data)
                return True
            return False
        except Exception as e:
            logger.error(f"Erro em update_profile: {e}")
            return False

    # ========== REFEIÇÕES ==========
    
    def save_meal(self, data: Dict):
        """Salva refeição"""
        try:
            data["user_id"] = self.get_current_user_id()
            
            if self.is_real and self.client:
                try:
                    self.client.table("meals").insert(data).execute()
                    return
                except Exception as e:
                    logger.error(f"Erro Supabase save_meal: {e}")
            
            st.session_state.mock_db["meals"].append(data)
        except Exception as e:
            logger.error(f"Erro em save_meal: {e}")
    
    def get_meals(self, days: Optional[int] = 7) -> List[Dict]:
        """Retorna refeições dos últimos N dias"""
        try:
            user_id = self.get_current_user_id()
            
            if self.is_real and self.client:
                try:
                    query = self.client.table("meals").select("*").eq("user_id", user_id)
                    if days:
                        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
                        query = query.gte("meal_date", cutoff)
                    res = query.execute()
                    return res.data or []
                except Exception as e:
                    logger.error(f"Erro Supabase get_meals: {e}")
                    return []
            
            # Mock
            meals = st.session_state.mock_db.get("meals", [])
            meals = [m for m in meals if m.get("user_id") == user_id]
            
            if days and meals:
                cutoff = datetime.date.today() - datetime.timedelta(days=days)
                return [
                    m for m in meals 
                    if datetime.datetime.strptime(m.get("meal_date", "2000-01-01"), "%Y-%m-%d").date() >= cutoff
                ]
            return meals
        except Exception as e:
            logger.error(f"Erro em get_meals: {e}")
            return []
    
    def get_meals_by_date(self, date_str: str) -> List[Dict]:
        """Retorna refeições de uma data específica"""
        try:
            return [m for m in self.get_meals(days=None) if m.get("meal_date") == date_str]
        except Exception as e:
            logger.error(f"Erro em get_meals_by_date: {e}")
            return []

    # ========== PESO ==========
    
    def save_weight(self, data: Dict):
        """Salva registro de peso"""
        try:
            data["user_id"] = self.get_current_user_id()
            
            if self.is_real and self.client:
                try:
                    self.client.table("weight_logs").insert(data).execute()
                    # Atualiza perfil também
                    self.client.table("profiles").update(
                        {"current_weight": data["weight"]}
                    ).eq("id", data["user_id"]).execute()
                    return
                except Exception as e:
                    logger.error(f"Erro Supabase save_weight: {e}")
            
            # Mock
            st.session_state.mock_db["weights"].append(data)
            user_email = data["user_id"]
            if user_email in st.session_state.mock_db["users"]:
                st.session_state.mock_db["users"][user_email]["current_weight"] = data["weight"]
        except Exception as e:
            logger.error(f"Erro em save_weight: {e}")
    
    def get_weights(self, days: int = 30) -> pd.DataFrame:
        """Retorna histórico de peso"""
        try:
            user_id = self.get_current_user_id()
            
            if self.is_real and self.client:
                try:
                    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
                    res = self.client.table("weight_logs").select("*").eq("user_id", user_id).gte("log_date", cutoff).execute()
                    if res.data:
                        df = pd.DataFrame(res.data)
                        df['log_date'] = pd.to_datetime(df['log_date'])
                        return df.sort_values('log_date')
                except Exception as e:
                    logger.error(f"Erro Supabase get_weights: {e}")
                return pd.DataFrame(columns=['log_date', 'weight', 'notes'])
            
            # Mock
            weights = st.session_state.mock_db.get("weights", [])
            weights = [log for log in weights if log.get("user_id") == user_id]
            
            if weights:
                df = pd.DataFrame(weights)
                df['log_date'] = pd.to_datetime(df['log_date'])
                cutoff = pd.Timestamp(datetime.date.today() - datetime.timedelta(days=days))
                df = df[df['log_date'] >= cutoff]
                return df.sort_values('log_date')
            
            return pd.DataFrame(columns=['log_date', 'weight', 'notes'])
        except Exception as e:
            logger.error(f"Erro em get_weights: {e}")
            return pd.DataFrame(columns=['log_date', 'weight', 'notes'])

    # ========== CONQUISTAS ==========
    
    def unlock_achievement(self, achievement_name: str, title: str) -> bool:
        """Desbloqueia conquista"""
        try:
            user_id = self.get_current_user_id()
            achievements = st.session_state.mock_db.get("achievements", [])
            
            if not any(
                a.get("achievement_name") == achievement_name and a.get("user_id") == user_id 
                for a in achievements
            ):
                data = {
                    "user_id": user_id,
                    "achievement_name": achievement_name,
                    "title": title,
                    "unlocked_at": str(datetime.date.today())
                }
                
                if self.is_real and self.client:
                    try:
                        self.client.table("achievements").insert(data).execute()
                    except Exception as e:
                        logger.error(f"Erro Supabase achievement: {e}")
                
                achievements.append(data)
                st.session_state.mock_db["achievements"] = achievements
                return True
            return False
        except Exception as e:
            logger.error(f"Erro em unlock_achievement: {e}")
            return False
    
    def get_achievements(self) -> List[Dict]:
        """Retorna conquistas do usuário"""
        try:
            user_id = self.get_current_user_id()
            achievements = st.session_state.mock_db.get("achievements", [])
            return [a for a in achievements if a.get("user_id") == user_id]
        except Exception as e:
            logger.error(f"Erro em get_achievements: {e}")
            return []
