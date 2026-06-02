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
        try:
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                from supabase import create_client
                self.client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
                self.is_real = True
        except Exception as e:
            logger.warning(f"Supabase indisponível, usando MockDB: {e}")
        
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {
                "meals": [], 
                "weights": [], 
                "achievements": [], 
                "users": {
                    "demo@emagresim.com": {
                        "password": "demo", "name": "Usuário Demo", "email": "demo@emagresim.com", 
                        "plan": "free", "current_weight": 78.5, "goal_weight": 70.0, 
                        "height": 175, "age": 28, "activity_level": "moderate", "goal": "lose"
                    }
                }
            }
    
    def get_current_user_id(self) -> str:
        if self.is_real and self.client:
            try:
                user = self.client.auth.get_user()
                if user and user.user: return user.user.id
            except: pass
        return st.session_state.user.get("email") if st.session_state.get("user") else "anonymous"

    def save_meal(self, data: Dict):
        data["user_id"] = self.get_current_user_id()
        if self.is_real and self.client:
            try: 
                self.client.table("meals").insert(data).execute()
                return
            except Exception as e: 
                logger.error(f"Erro Supabase save_meal: {e}")
        st.session_state.mock_db["meals"].append(data)
    
    def get_meals(self, days: Optional[int] = 7) -> List[Dict]:
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
                
        meals = st.session_state.mock_db.get("meals", [])
        meals = [m for m in meals if m.get("user_id") == user_id]
        if days and meals:
            cutoff = datetime.date.today() - datetime.timedelta(days=days)
            return [m for m in meals if datetime.datetime.strptime(m.get("meal_date"), "%Y-%m-%d").date() >= cutoff]
        return meals
    
    def get_meals_by_date(self, date_str: str) -> List[Dict]:
        return [m for m in self.get_meals(days=None) if m.get("meal_date") == date_str]
    
    def save_weight(self, data: Dict):
        data["user_id"] = self.get_current_user_id()
        if self.is_real and self.client:
            try: 
                self.client.table("weight_logs").insert(data).execute()
                self.client.table("profiles").update({"current_weight": data["weight"]}).eq("id", data["user_id"]).execute()
                return
            except Exception as e: 
                logger.error(f"Erro Supabase save_weight: {e}")
        st.session_state.mock_db["weights"].append(data)
        u_email = data["user_id"]
        if u_email in st.session_state.mock_db["users"]:
            st.session_state.mock_db["users"][u_email]["current_weight"] = data["weight"]
    
    def get_weights(self, days: int = 30) -> pd.DataFrame:
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
            
        w = st.session_state.mock_db.get("weights", [])
        w = [log for log in w if log.get("user_id") == user_id]
        if w:
            df = pd.DataFrame(w)
            df['log_date'] = pd.to_datetime(df['log_date'])
            cutoff = pd.Timestamp(datetime.date.today() - datetime.timedelta(days=days))
            df = df[df['log_date'] >= cutoff]
            return df.sort_values('log_date')
        return pd.DataFrame(columns=['log_date', 'weight', 'notes'])
    
    def update_profile(self, profile_data: Dict):
        user_id = self.get_current_user_id()
        if self.is_real and self.client:
            try:
                self.client.table("profiles").update(profile_data).eq("id", user_id).execute()
                return True
            except Exception as e:
                logger.error(f"Erro Supabase update_profile: {e}")
                return False
        
        u_email = user_id
        if u_email in st.session_state.mock_db["users"]:
            st.session_state.mock_db["users"][u_email].update(profile_data)
            return True
        return False

    def unlock_achievement(self, achievement_name: str, title: str) -> bool:
        user_id = self.get_current_user_id()
        achievements = st.session_state.mock_db.get("achievements", [])
        
        if not any(a.get("achievement_name") == achievement_name and a.get("user_id") == user_id for a in achievements):
            data = {"user_id": user_id, "achievement_name": achievement_name, "title": title, "unlocked_at": str(datetime.date.today())}
            if self.is_real and self.client:
                try: self.client.table("achievements").insert(data).execute()
                except Exception as e: logger.error(f"Erro achievement: {e}")
            achievements.append(data)
            st.session_state.mock_db["achievements"] = achievements
            return True
        return False
    
    def get_achievements(self) -> List[Dict]:
        user_id = self.get_current_user_id()
        achievements = st.session_state.mock_db.get("achievements", [])
        return [a for a in achievements if a.get("user_id") == user_id]
    
    def create_user(self, email: str, password: str, name: str) -> bool:
        users = st.session_state.mock_db.get("users", {})
        if email in users: return False
        users[email] = {
            "password": password, "name": name, "email": email, "plan": "free",
            "current_weight": None, "goal_weight": None, "height": None, "age": None,
            "activity_level": "moderate", "goal": "lose"
        }
        st.session_state.mock_db["users"] = users
        return True
    
    def get_user(self, email: str, password: str) -> Optional[Dict]:
        users = st.session_state.mock_db.get("users", {})
        if email in users and users[email].get("password") == password: 
            return users[email]
        return None
