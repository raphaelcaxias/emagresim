import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import streamlit as st

class SupabaseDB:
    def __init__(self):
        try:
            # Pega a URL
            self.url = st.secrets["supabase"]["url"]
            
            # Tenta ler 'key' (como você colocou), se falhar tenta 'anon_key'
            secrets_data = st.secrets["supabase"]
            self.key = secrets_data.get("key") or secrets_data.get("anon_key")
            
            if not self.key:
                raise KeyError("Nenhuma chave encontrada (key ou anon_key)")
                
        except KeyError:
            st.error("🔑 Erro de Configuração do Supabase!")
            st.code("""
[supabase]
url = "https://...supabase.co"
key = "sb_publishable_..."
            """)
            st.stop()
            
        # Inicializa o cliente
        self.client: Client = create_client(self.url, self.key)
        
    def _auth_client(self):
        """Retorna cliente com sessão do usuário logado (para RLS funcionar)"""
        if st.session_state.get("auth_token"):
            self.client.auth.set_session(
                st.session_state["auth_token"], 
                st.session_state.get("refresh_token", "")
            )
        return self.client

    def sign_up(self, email: str, password: str, username: str = None) -> Dict:
        try:
            res = self.client.auth.sign_up({"email": email, "password": password})
            if res.user:
                # Atualiza o perfil com o username após criar o auth
                self.client.table("profiles").update({"username": username or email}).eq("id", res.user.id).execute()
            return {"success": res.user is not None, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_in(self, email: str, password: str) -> Dict:
        try:
            res = self.client.auth.sign_in_with_password({"email": email, "password": password})
            if res.session:
                st.session_state["auth_token"] = res.session.access_token
                st.session_state["refresh_token"] = res.session.refresh_token
                st.session_state["user"] = res.user.dict()
            return {"success": res.session is not None, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_out(self):
        self.client.auth.sign_out()
        for key in ["auth_token", "refresh_token", "user"]:
            st.session_state.pop(key, None)

    def get_profile(self) -> Optional[Dict]:
        if not st.session_state.get("user"): return None
        try:
            res = self._auth_client().table("profiles").select("*").eq("id", st.session_state["user"]["id"]).execute()
            return res.data[0] if res.data else None
        except:
            return None

    def update_profile(self, data: Dict) -> bool:
        try:
            res = self._auth_client().table("profiles").update(data).eq("id", st.session_state["user"]["id"]).execute()
            return res.data is not None
        except:
            return False

    def add_meal(self, meal: Dict) -> bool:
        try:
            meal["user_id"] = st.session_state["user"]["id"]
            res = self._auth_client().table("meals").insert(meal).execute()
            return res.data is not None
        except:
            return False

    def get_daily_meals(self) -> List[Dict]:
        today = st.session_state.get("today_date")
        try:
            res = self._auth_client().table("meals").select("*").eq("user_id", st.session_state["user"]["id"]).gte("recorded_at", f"{today}T00:00:00").order("recorded_at", desc=True).execute()
            return res.data or []
        except:
            return []

    def add_weight_log(self, weight: float, notes: str = "") -> bool:
        try:
            res = self._auth_client().table("weight_logs").insert({"user_id": st.session_state["user"]["id"], "weight_kg": weight, "notes": notes}).execute()
            return res.data is not None
        except:
            return False

    def get_weight_history(self, days: int = 30) -> List[Dict]:
        try:
            res = self._auth_client().table("weight_logs").select("*").eq("user_id", st.session_state["user"]["id"]).order("recorded_at", desc=True).limit(days).execute()
            return res.data or []
        except:
            return []

    def update_xp(self, xp_gain: int) -> Dict:
        profile = self.get_profile()
        if not profile: return {"error": "Profile not found"}
        
        new_xp = profile["experience"] + xp_gain
        new_level = profile["level"]
        leveled_up = False
        
        xp_needed = int(100 * (new_level ** 1.5))
        while new_xp >= xp_needed:
            new_xp -= xp_needed
            new_level += 1
            xp_needed = int(100 * (new_level ** 1.5))
            leveled_up = True
            
        try:
            self._auth_client().table("profiles").update({"experience": new_xp, "level": new_level}).eq("id", st.session_state["user"]["id"]).execute()
            return {"xp": new_xp, "level": new_level, "leveled_up": leveled_up}
        except:
            return {"error": "Failed to update XP"}
