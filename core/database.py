import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import streamlit as st

class SupabaseDB:
    def __init__(self):
        try:
            self.url = st.secrets["supabase"]["url"]
            secrets_data = st.secrets["supabase"]
            
            # Tenta pegar service_role_key primeiro (para bypass RLS em operações admin)
            # Se não existir, usa a key normal
            self.key = secrets_data.get("service_role_key") or secrets_data.get("key") or secrets_data.get("anon_key")
            
            if not self.key:
                raise KeyError("Nenhuma chave encontrada")
                
        except KeyError as e:
            st.error(f"🔑 Erro de Configuração: {e}")
            st.info("Verifique Manage App → Advanced Settings → Secrets")
            st.stop()
            
        self.client: Client = create_client(self.url, self.key)
        
    def _auth_client(self):
        """Retorna cliente com sessão do usuário (para RLS funcionar nas queries do usuário)"""
        if st.session_state.get("auth_token"):
            try:
                self.client.auth.set_session(
                    st.session_state["auth_token"], 
                    st.session_state.get("refresh_token", "")
                )
            except:
                pass  # Ignora se não conseguir setar sessão
        return self.client

    def sign_up(self, email: str, password: str, username: str = None) -> Dict:
        """Registra usuário e cria perfil automaticamente"""
        try:
            # Usa o cliente direto (sem auth) para bypass RLS na criação
            res = self.client.auth.sign_up({
                "email": email, 
                "password": password,
                "options": {"data": {"username": username}}
            })
            
            if res.user:
                # Aguarda um pouco para a trigger criar o perfil
                import time
                time.sleep(0.5)
                
                # Atualiza o username se necessário
                if username:
                    self.client.table("profiles").update({
                        "username": username
                    }).eq("id", res.user.id).execute()
                    
            return {"success": res.user is not None, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_in(self, email: str, password: str) -> Dict:
        """Faz login do usuário"""
        try:
            res = self.client.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            
            if res.session:
                st.session_state["auth_token"] = res.session.access_token
                st.session_state["refresh_token"] = res.session.refresh_token
                st.session_state["user"] = res.user.dict()
                
            return {"success": res.session is not None, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_out(self):
        """Faz logout"""
        try:
            self.client.auth.sign_out()
        except:
            pass
        finally:
            for key in ["auth_token", "refresh_token", "user"]:
                st.session_state.pop(key, None)

    def get_profile(self) -> Optional[Dict]:
        """Busca perfil do usuário logado"""
        if not st.session_state.get("user"): 
            return None
            
        try:
            res = self._auth_client().table("profiles").select("*").eq(
                "id", st.session_state["user"]["id"]
            ).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            st.error(f"Erro ao carregar perfil: {e}")
            return None

    def update_profile(self, data: Dict) -> bool:
        """Atualiza perfil do usuário"""
        try:
            res = self._auth_client().table("profiles").update(data).eq(
                "id", st.session_state["user"]["id"]
            ).execute()
            return res.data is not None
        except:
            return False

    def add_meal(self, meal: Dict) -> bool:
        """Adiciona refeição"""
        try:
            meal["user_id"] = st.session_state["user"]["id"]
            res = self._auth_client().table("meals").insert(meal).execute()
            return res.data is not None
        except:
            return False

    def get_daily_meals(self) -> List[Dict]:
        """Busca refeições do dia"""
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

    def add_weight_log(self, weight: float, notes: str = "") -> bool:
        """Adiciona registro de peso"""
        try:
            res = self._auth_client().table("weight_logs").insert({
                "user_id": st.session_state["user"]["id"], 
                "weight_kg": weight, 
                "notes": notes
            }).execute()
            return res.data is not None
        except:
            return False

    def get_weight_history(self, days: int = 30) -> List[Dict]:
        """Busca histórico de peso"""
        try:
            res = self._auth_client().table("weight_logs").select("*").eq(
                "user_id", st.session_state["user"]["id"]
            ).order("recorded_at", desc=True).limit(days).execute()
            return res.data or []
        except:
            return []

    def update_xp(self, xp_gain: int) -> Dict:
        """Atualiza XP e nível do usuário"""
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
            return {"error": "Failed to update XP"}
