import streamlit as st
from supabase import create_client, Client
import os

class SupabaseDB:
    def __init__(self):
        st.info("🔍 Iniciando diagnóstico de conexão...")
        
        try:
            # Ler secrets
            if "supabase" not in st.secrets:
                st.error("❌ Secrets não encontrados! Verifique se [supabase] existe no TOML")
                st.stop()
            
            secrets_data = st.secrets["supabase"]
            self.url = secrets_data.get("url", "").strip()
            self.key = secrets_data.get("key", "").strip()
            self.service_key = secrets_data.get("service_role_key", "").strip()
            
            st.write(f"📍 URL carregada: {self.url[:30]}...")
            st.write(f"🔑 Key carregada: {self.key[:20]}...")
            
            if not self.url:
                st.error("❌ URL está vazia!")
                st.stop()
            if not self.key and not self.service_key:
                st.error("❌ Nenhuma chave encontrada!")
                st.stop()
            
            # Usar service_role_key se existir, senão usa key normal
            final_key = self.service_key if self.service_key else self.key
            
            st.info("🔄 Criando cliente Supabase...")
            
            # Criar cliente
            self.client: Client = create_client(self.url, final_key)
            
            st.success("✅ Conexão estabelecida com sucesso!")
            st.success("🎉 Supabase pronto para uso!")
            
        except Exception as e:
            st.error(f"❌ ERRO CRÍTICO: {type(e).__name__}")
            st.error(f"📄 Detalhes: {str(e)}")
            st.warning("💡 Possíveis causas:")
            st.warning("1. Biblioteca 'supabase' não instalada (verifique requirements.txt)")
            st.warning("2. URL ou chave inválidas")
            st.warning("3. Problema de rede temporário no Streamlit Cloud")
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
                self.client.table("profiles").update({
                    "username": username
                }).eq("id", res.user.id).execute()
            return {"success": True, "error": None}
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
            res = self._auth_client().table("profiles").select("*").eq(
                "id", st.session_state["user"]["id"]
            ).execute()
            return res.data[0] if res.data else None
        except:
            return None

    def update_profile(self, data):
        try:
            res = self._auth_client().table("profiles").update(data).eq(
                "id", st.session_state["user"]["id"]
            ).execute()
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
            res = self._auth_client().table("meals").select("*").eq(
                "user_id", st.session_state["user"]["id"]
            ).gte("recorded_at", f"{today}T00:00:00").order(
                "recorded_at", desc=True
            ).execute()
            return res.data or []
        except:
            return []

    def add_weight_log(self, weight, notes=""):
        try:
            res = self._auth_client().table("weight_logs").insert({
                "user_id": st.session_state["user"]["id"], 
                "weight_kg": weight, 
                "notes": notes
            }).execute()
            return res.data is not None
        except:
            return False

    def get_weight_history(self, days=30):
        try:
            res = self._auth_client().table("weight_logs").select("*").eq(
                "user_id", st.session_state["user"]["id"]
            ).order("recorded_at", desc=True).limit(days).execute()
            return res.data or []
        except:
            return []

    def update_xp(self, xp_gain):
        profile = self.get_profile()
        if not profile:
            return {"error": "Profile not found"}
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
            self._auth_client().table("profiles").update({
                "experience": new_xp, 
                "level": new_level
            }).eq("id", st.session_state["user"]["id"]).execute()
            return {"xp": new_xp, "level": new_level, "leveled_up": leveled_up}
        except:
            return {"error": "Failed"}
