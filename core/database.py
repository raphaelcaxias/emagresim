import streamlit as st
import datetime
import pandas as pd
from typing import List, Dict

class AppDatabase:
    def __init__(self):
        self.is_real = False
        
        # Verifica se tem Supabase configurado
        try:
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                from supabase import create_client
                self.client = create_client(
                    st.secrets["SUPABASE_URL"],
                    st.secrets["SUPABASE_KEY"]
                )
                self.is_real = True
        except:
            self.client = None
        
        # Inicializa mock_db se não existir
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {
                "meals": [],
                "weights": [],
                "achievements": [],
                "user_profile": {}
            }
    
    def save_meal(self, data):
        if self.is_real and self.client:
            try:
                self.client.table("meals").insert(data).execute()
            except:
                pass
        else:
            st.session_state.mock_db["meals"].append(data)
            self._check_achievements()
    
    def get_meals(self, days: int = 7) -> List[Dict]:
        if self.is_real and self.client:
            try:
                cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
                result = self.client.table("meals").select("*").gte("date", cutoff).execute()
                return result.data
            except:
                return []
        else:
            meals = st.session_state.mock_db["meals"]
            if days:
                cutoff = datetime.date.today() - datetime.timedelta(days=days)
                meals = [m for m in meals if datetime.datetime.strptime(m.get("date", "2000-01-01"), "%Y-%m-%d").date() >= cutoff]
            return meals
    
    def get_meals_by_date(self, date_str: str) -> List[Dict]:
        all_meals = self.get_meals(days=None)
        return [m for m in all_meals if m.get("date") == date_str]
    
    def save_weight(self, data):
        if self.is_real and self.client:
            try:
                self.client.table("weights").insert(data).execute()
            except:
                pass
        else:
            st.session_state.mock_db["weights"].append(data)
    
    def get_weights(self, days: int = 30) -> pd.DataFrame:
        if self.is_real and self.client:
            try:
                cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
                result = self.client.table("weights").select("*").gte("date", cutoff).execute()
                if result.data:
                    df = pd.DataFrame(result.data)
                    df['date'] = pd.to_datetime(df['date'])
                    return df.sort_values('date')
            except:
                pass
            return pd.DataFrame()
        else:
            weights = st.session_state.mock_db["weights"]
            if weights:
                df = pd.DataFrame(weights)
                df['date'] = pd.to_datetime(df['date'])
                return df.sort_values('date')
            return pd.DataFrame(columns=['date', 'val'])
    
    def _check_achievements(self):
        meals = self.get_meals(days=None)
        achs = st.session_state.mock_db["achievements"]
        
        if len(meals) == 1 and not any(a["name"] == "primeira" for a in achs):
            st.session_state.mock_db["achievements"].append({
                "name": "primeira",
                "title": "🍽️ Primeira Refeição",
                "date": str(datetime.date.today())
            })
            st.toast("🏆 Conquista: Primeira Refeição!", icon="🎉")
        
        dates = set(m["date"] for m in meals)
        if len(dates) >= 3 and not any(a["name"] == "streak3" for a in achs):
            st.session_state.mock_db["achievements"].append({
                "name": "streak3",
                "title": "🔥 3 Dias de Consistência",
                "date": str(datetime.date.today())
            })
            st.toast("🏆 Conquista: 3 Dias!", icon="🎉")
    
    def get_achievements(self) -> List[Dict]:
        return st.session_state.mock_db["achievements"]
    
    def reset_demo(self):
        st.session_state.mock_db = {
            "meals": [],
            "weights": [],
            "achievements": [],
            "user_profile": {}
        }
