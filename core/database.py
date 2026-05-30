import streamlit as st
from supabase import create_client, Client
from datetime import date

class SupabaseDB:
    def __init__(self):
        try:
            secrets = st.secrets["supabase"]
            self.url = secrets["url"].strip()
            self.key = secrets.get("service_role_key", secrets["key"]).strip()
            self.client: Client = create_client(self.url, self.key)
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            st.stop()

    def _auth_client(self):
        if st.session_state.get("auth_token"):
            self.client.auth.set_session(st.session_state["auth_token"], st.session_state.get("refresh_token", ""))
        return self.client

    def sign_up(self, email, password, username):
        try:
            res = self.client.auth.sign_up({"email": email, "password": password, "options": {"data": {"username": username}}})
            if res.user:
                # Inicia onboarding pendente
                self.client.table("profiles").insert({
                    "id": res.user.id,
                    "username": username,
                    "email": email,
                    "is_onboarding_complete": False
                }).execute()
            return {"success": res.user is not None, "error": None}
        except Exception as e: return {"success": False, "error": str(e)}

    def sign_in(self, email, password):
        try:
            res = self.client.auth.sign_in_with_password({"email": email, "password": password})
            if res.session:
                st.session_state["auth_token"] = res.session.access_token
                st.session_state["refresh_token"] = res.session.refresh_token
                st.session_state["user"] = res.user.dict()
            return {"success": res.session is not None, "error": None}
        except Exception as e: return {"success": False, "error": str(e)}

    def sign_out(self):
        self.client.auth.sign_out()
        for k in ["auth_token", "refresh_token", "user"]: st.session_state.pop(k, None)

    def get_profile(self):
        if not st.session_state.get("user"): return None
        try:
            res = self._auth_client().table("profiles").select("*").eq("id", st.session_state["user"]["id"]).execute()
            return res.data[0] if res.data else None
        except: return None

    def update_profile(self, data):
        try:
            return self._auth_client().table("profiles").update(data).eq("id", st.session_state["user"]["id"]).execute().data is not None
        except: return False

    # --- NOVOS MÉTODOS ANALÍTICOS ---

    def save_daily_log(self, log_data):
        try:
            log_data["user_id"] = st.session_state["user"]["id"]
            # Upsert (atualiza se já existir hoje)
            res = self._auth_client().table("daily_logs").upsert(log_data, on_conflict=["user_id", "log_date"]).execute()
            return res.data is not None
        except: return False

    def get_daily_log(self, target_date=None):
        try:
            d = target_date or date.today().isoformat()
            res = self._auth_client().table("daily_logs").select("*").eq("user_id", st.session_state["user"]["id"]).eq("log_date", d).execute()
            return res.data[0] if res.data else None
        except: return None

    def get_logs_history(self, days=30):
        try:
            res = self._auth_client().table("daily_logs").select("*").eq("user_id", st.session_state["user"]["id"]).order("log_date", desc=True).limit(days).execute()
            return res.data or []
        except: return []

    def get_achievements(self):
        try:
            res = self._auth_client().table("user_achievements").select("achievement_id").eq("user_id", st.session_state["user"]["id"]).execute()
            return [r["achievement_id"] for r in res.data]
        except: return []
