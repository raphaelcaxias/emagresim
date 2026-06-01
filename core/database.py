import streamlit as st
import datetime
import pandas as pd
from typing import List, Dict

class AppDatabase:
    def __init__(self):
        self.is_real = False
        self.client = None
        
        # Verifica se tem Supabase configurado
        try:
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                from supabase import create_client
                self.client = create_client(
                    st.secrets["SUPABASE_URL"],
                    st.secrets["SUPABASE_KEY"]
                )
                self.is_real = True
        except Exception as e:
            pass
        
        # Garante que mock_db existe
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {
                "meals": [],
                "weights": [],
                "achievements": [],
                "users": {
                    "demo@emagresim.com": {
                        "password": "demo123",
                        "name": "Usuário Demo",
                        "email": "demo@emagresim.com",
                        "is_demo": True
                    }
                }
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
                result = self.client.table("meals").select("*").gte("record_date", cutoff).execute()
                return result.data if result.data else []
            except:
                return []
        else:
            meals = st.session_state.mock_db["meals"]
            if days and meals:
                cutoff = datetime.date.today() - datetime.timedelta(days=days)
                filtered = []
                for m in meals:
                    try:
                        m_date = datetime.datetime.strptime(m.get("record_date", m.get("date", "2000-01-01")), "%Y-%m-%d").date()
                        if m_date >= cutoff:
                            filtered.append(m)
                    except:
                        filtered.append(m)
                return filtered
            return meals
    
    def get_meals_by_date(self, date_str: str) -> List[Dict]:
        all_meals = self.get_meals(days=None)
        return [m for m in all_meals if m.get("record_date", m.get("date")) == date_str]
    
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
                result = self.client.table("weights").select("*").gte("record_date", cutoff).execute()
                if result.data:
                    df = pd.DataFrame(result.data)
                    df['record_date'] = pd.to_datetime(df['record_date'])
                    return df.sort_values('record_date')
            except:
                pass
            return pd.DataFrame()
        else:
            weights = st.session_state.mock_db["weights"]
            if weights:
                df = pd.DataFrame(weights)
                if 'record_date' in df.columns:
                    df['date'] = pd.to_datetime(df['record_date'])
                elif 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                return df.sort_values('date')
            return pd.DataFrame(columns=['date', 'weight_val'])
    
    def _check_achievements(self):
        meals = self.get_meals(days=None)
        achs = st.session_state.mock_db.get("achievements", [])
        
        if len(meals) == 1 and not any(a.get("name") == "primeira" for a in achs):
            st.session_state.mock_db["achievements"].append({
                "name": "primeira",
                "title": "🍽️ Primeira Refeição",
                "date": str(datetime.date.today())
            })
            st.toast("🏆 Conquista: Primeira Refeição!", icon="🎉")
        
        dates = set()
        for m in meals:
            d = m.get("record_date", m.get("date"))
            if d:
                dates.add(d)
        
        if len(dates) >= 3 and not any(a.get("name") == "streak3" for a in achs):
            st.session_state.mock_db["achievements"].append({
                "name": "streak3",
                "title": "🔥 3 Dias de Consistência",
                "date": str(datetime.date.today())
            })
            st.toast("🏆 Conquista: 3 Dias!", icon="🎉")
    
    def get_achievements(self) -> List[Dict]:
        return st.session_state.mock_db.get("achievements", [])
    
    def reset_demo(self):
        st.session_state.mock_db = {
            "meals": [],
            "weights": [],
            "achievements": [],
            "users": st.session_state.mock_db.get("users", {})
        }
