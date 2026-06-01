import streamlit as st
import datetime
import pandas as pd
from typing import List, Dict, Optional

class AppDatabase:
    def __init__(self):
        self.is_real = False
        try:
            if "SUPABASE_URL" in st.secrets:
                self.is_real = True
        except:
            pass
        
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {
                "meals": [], 
                "weights": [],
                "achievements": []
            }
    
    def save_meal(self, data):
        if self.is_real:
            pass  # 🔜 self.client.table('meals').insert(data)
        else:
            st.session_state.mock_db["meals"].append(data)
            self._check_achievements(data)
    
    def get_meals(self, days: int = 7) -> List[Dict]:
        if self.is_real:
            return []
        meals = st.session_state.mock_db["meals"]
        if days:
            cutoff = datetime.date.today() - datetime.timedelta(days=days)
            meals = [m for m in meals if datetime.datetime.strptime(m.get("date", "2000-01-01"), "%Y-%m-%d").date() >= cutoff]
        return meals
    
    def get_meals_by_date(self, date_str: str) -> List[Dict]:
        all_meals = self.get_meals(days=None)
        return [m for m in all_meals if m.get("date") == date_str]
    
    def save_weight(self, data):
        if self.is_real:
            pass
        else:
            st.session_state.mock_db["weights"].append(data)
    
    def get_weights(self, days: int = 30) -> pd.DataFrame:
        if self.is_real:
            return pd.DataFrame()
        weights = st.session_state.mock_db["weights"]
        if weights:
            df = pd.DataFrame(weights)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            return df
        return pd.DataFrame(columns=['date', 'val'])
    
    def _check_achievements(self, meal_data):
        meals = self.get_meals(days=None)
        achievements = st.session_state.mock_db["achievements"]
        if len(meals) == 1 and "primeira_refeicao" not in [a["name"] for a in achievements]:
            st.session_state.mock_db["achievements"].append({
                "name": "primeira_refeicao",
                "title": "🍽️ Primeira Refeição",
                "date": str(datetime.date.today())
            })
            st.toast("🏆 Conquista desbloqueada: Primeira Refeição!", icon="🎉")
        dates = set(m["date"] for m in meals)
        if len(dates) >= 3 and "streak_3" not in [a["name"] for a in achievements]:
            st.session_state.mock_db["achievements"].append({
                "name": "streak_3",
                "title": "🔥 3 Dias de Consistência",
                "date": str(datetime.date.today())
            })
            st.toast("🏆 Conquista desbloqueada: 3 Dias de Consistência!", icon="🎉")
    
    def get_achievements(self) -> List[Dict]:
        return st.session_state.mock_db["achievements"]
    
    def reset_demo(self):
        st.session_state.mock_db = {"meals": [], "weights": [], "achievements": []}
