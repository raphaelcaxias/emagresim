import streamlit as st
from supabase import create_client, Client

class SupabaseDB:
    def __init__(self):
        try:
            secrets_data = st.secrets["supabase"]
            self.url = secrets_data["url"].strip()
            self.key = secrets_data.get("service_role_key", secrets_data.get("key")).strip()
            
            if not self.url or not self.key:
                raise KeyError("URL ou chave não encontradas")
                
            self.client: Client = create_client(self.url, self.key)
            
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            st.stop()

    def _auth_client(self):
        if st.session_state.get("auth_token"):
            try:
                self.client.auth.set_session(
                    st.session_state["auth_token"], 
                    st.session_state.get("refresh_token", "")
                )
            except:
                pass
        return self.client

    def sign_up(self, email, password, username=None):
        try:
            res = self.client.auth.sign_up({
                "email": email, 
                "password": password,
                "options": {"data": {"username": username}}
            })
            if res.user:
                import time
                time.sleep(0.5)
                if username:
                    try:
                        self.client.table("profiles").update({
                            "username": username
                        }).eq("id", res.user.id).execute()
                    except:
                        pass
            return {"success": res.user is not None, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_in(self, email, password):
        try:
            res = self.client.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            if res.session:
                st.session_state["auth_token"] = res.session.access_token
                st.session_state["refresh_token"] = res.session.refresh_token
                st.session_state["user"] = res.user.dict()
                return {"success": True, "error": None}
            else:
                return {"success": False, "error": "Falha na autenticação"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_out(self):
        try:
            self.client.auth.sign_out()
        except:
            pass
        for k in ["auth_token", "refresh_token", "user"]:
            st.session_state.pop(k, None)

    def get_profile(self):
        if not st.session_state.get("user"):
            return None
        try:
            user_id = st.session_state["user"]["id"]
            # Busca todos os dados do perfil
            res = self._auth_client().table("profiles").select("*").eq("id", user_id).execute()
            return res.data[0] if res.data else None
        except:
            return None

    def update_profile(self, data):
        try:
            user_id = st.session_state["user"]["id"]
            res = self._auth_client().table("profiles").update(data).eq("id", user_id).execute()
            return res.data is not None
        except:
            return False

    def add_meal(self, meal):
        try:
            meal["user_id"] = st.session_state["user"]["id"]
            res = self._auth_client().table("meals").insert(meal).execute()
            return res.data is not None
        except:
            return False

    def get_daily_meals(self):
        today = st.session_state.get("today_date")
        try:
            user_id = st.session_state["user"]["id"]
            res = self._auth_client().table("meals").select("*").eq(
                "user_id", user_id
            ).gte("recorded_at", f"{today}T00:00:00").order(
                "recorded_at", desc=True
            ).execute()
            return res.data or []
        except:
            return []

    def add_weight_log(self, weight, notes=""):
        try:
            user_id = st.session_state["user"]["id"]
            res = self._auth_client().table("weight_logs").insert({
                "user_id": user_id, 
                "weight_kg": weight, 
                "notes": notes
            }).execute()
            return res.data is not None
        except:
            return False

    def get_weight_history(self, days=30):
        try:
            user_id = st.session_state["user"]["id"]
            res = self._auth_client().table("weight_logs").select("*").eq(
                "user_id", user_id
            ).order("recorded_at", desc=True).limit(days).execute()
            return res.data or []
        except:
            return []

    def update_xp(self, xp_gain):
        profile = self.get_profile()
        if not profile:
            return {"error": "Perfil não encontrado"}
        
        new_xp = profile.get("experience", 0) + xp_gain
        new_level = profile.get("level", 1)
        leveled_up = False
        
        xp_needed = int(100 * (new_level ** 1.5))
        while new_xp >= xp_needed:
            new_xp -= xp_needed
            new_level += 1
            xp_needed = int(100 * (new_level ** 1.5))
            leveled_up = True
        
        try:
            user_id = st.session_state["user"]["id"]
            self._auth_client().table("profiles").update({
                "experience": new_xp, 
                "level": new_level
            }).eq("id", user_id).execute()
            return {"xp": new_xp, "level": new_level, "leveled_up": leveled_up}
        except:
            return {"error": "Falha ao atualizar XP"}
