import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import streamlit as st

class SupabaseDB:
    def __init__(self):
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        self.client: Client = create_client(url, key)
        
    def _auth_client(self):
        """Retorna cliente com sessão do usuário logado (para RLS funcionar)"""
        if st.session_state.get("auth_token"):
            self.client.auth.set_session(
                st.session_state["auth_token"], 
                st.session_state.get("refresh_token", "")
            )
        return self.client

    def sign_up(self, email: str, password: str, username: str = None) -> Dict:
        res = self.client.auth.sign_up({"email": email, "password": password})
        if res.user:
            self.client.table("profiles").update({"username": username or email}).eq("id", res.user.id).execute()
        return {"success": res.user is not None, "error": getattr(res, "error", None)}

    def sign_in(self, email: str, password: str) -> Dict:
        res = self.client.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            st.session_state["auth_token"] = res.session.access_token
            st.session_state["refresh_token"] = res.session.refresh_token
            st.session_state["user"] = res.user.dict()
        return {"success": res.session is not None, "error": getattr(res, "error", None)}

    def sign_out(self):
        self.client.auth.sign_out()
        for key in ["auth_token", "refresh_token", "user"]:
            st.session_state.pop(key, None)

    def get_profile(self) -> Optional[Dict]:
        if not st.session_state.get("user"): return None
        res = self._auth_client().table("profiles").select("*").eq("id", st.session_state["user"]["id"]).execute()
        return res.data[0] if res.data else None

    def update_profile(self, data: Dict) -> bool:
        res = self._auth_client().table("profiles").update(data).eq("id", st.session_state["user"]["id"]).execute()
        return res.data is not None

    def add_meal(self, meal: Dict) -> bool:
        meal["user_id"] = st.session_state["user"]["id"]
        res = self._auth_client().table("meals").insert(meal).execute()
        return res.data is not None

    def get_daily_meals(self) -> List[Dict]:
        today = st.session_state.get("today_date")
        res = self._auth_client().table("meals").select("*").eq("user_id", st.session_state["user"]["id"]).gte("recorded_at", f"{today}T00:00:00").order("recorded_at", desc=True).execute()
        return res.data or []

    def add_weight_log(self, weight: float, notes: str = "") -> bool:
        res = self._auth_client().table("weight_logs").insert({"user_id": st.session_state["user"]["id"], "weight_kg": weight, "notes": notes}).execute()
        return res.data is not None

    def get_weight_history(self, days: int = 30) -> List[Dict]:
        res = self._auth_client().table("weight_logs").select("*").eq("user_id", st.session_state["user"]["id"]).order("recorded_at", desc=True).limit(days).execute()
        return res.data or []

    def update_xp(self, xp_gain: int) -> Dict:
        profile = self.get_profile()
        new_xp = profile["experience"] + xp_gain
        new_level = profile["level"]
        leveled_up = False
        
        xp_needed = int(100 * (new_level ** 1.5))
        while new_xp >= xp_needed:
            new_xp -= xp_needed
            new_level += 1
            xp_needed = int(100 * (new_level ** 1.5))
            leveled_up = True
            
        self._auth_client().table("profiles").update({"experience": new_xp, "level": new_level}).eq("id", st.session_state["user"]["id"]).execute()
        return {"xp": new_xp, "level": new_level, "leveled_up": leveled_up}
