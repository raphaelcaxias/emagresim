import streamlit as st
import datetime
import pandas as pd
from typing import List, Dict

class AppDatabase:
    def __init__(self):
        self.is_real = False
        self.client = None
        try:
            if "SUPABASE_URL" in st.secrets:
                from supabase import create_client
                self.client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
                self.is_real = True
        except: pass
        
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {"meals": [], "weights": [], "achievements": [], "users": {}}
    
    def save_meal(self, data):
        if self.is_real and self.client:
            try: self.client.table("meals").insert(data).execute()
            except: pass
        else:
            st.session_state.mock_db["meals"].append(data)
            self._check_achievements()
    
    def get_meals(self, days=7) -> List[Dict]:
        if self.is_real and self.client:
            try:
                cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
                res = self.client.table("meals").select("*").gte("record_date", cutoff).execute()
                return res.data or []
            except: return []
        meals = st.session_state.mock_db.get("meals", [])
        if days and meals:
            cutoff = datetime.date.today() - datetime.timedelta(days=days)
            return [m for m in meals if datetime.datetime.strptime(m.get("record_date", m.get("date", "2000-01-01")), "%Y-%m-%d").date() >= cutoff]
        return meals

    def get_meals_by_date(self, date_str: str) -> List[Dict]:
        return [m for m in self.get_meals(days=None) if m.get("record_date", m.get("date")) == date_str]
    
    def save_weight(self, data):
        if self.is_real and self.client:
            try: self.client.table("weights").insert(data).execute()
            except: pass
        else: st.session_state.mock_db["weights"].append(data)
    
    def get_weights(self, days=30) -> pd.DataFrame:
        if self.is_real and self.client:
            try:
                cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
                res = self.client.table("weights").select("*").gte("record_date", cutoff).execute()
                if res.data:
                    df = pd.DataFrame(res.data)
                    df['record_date'] = pd.to_datetime(df['record_date'])
                    return df.sort_values('record_date')
            except: pass
            return pd.DataFrame()
        w = st.session_state.mock_db.get("weights", [])
        if w:
            df = pd.DataFrame(w)
            df['date'] = pd.to_datetime(df.get('record_date', df.get('date')))
            return df.sort_values('date')
        return pd.DataFrame()
    
    def _check_achievements(self):
        meals = self.get_meals(days=None)
        achs = st.session_state.mock_db.get("achievements", [])
        if len(meals) == 1 and not any(a.get("name") == "primeira" for a in achs):
            st.session_state.mock_db["achievements"].append({"name": "primeira", "title": "🍽️ Primeira Refeição", "date": str(datetime.date.today())})
            st.toast("🏆 Conquista: Primeira Refeição!", icon="🎉")
    
    def get_achievements(self): return st.session_state.mock_db.get("achievements", [])