import streamlit as st
import logging
from typing import Optional, Dict
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class AuthService:
    """Serviço de autenticação via Supabase."""
    
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.is_authenticated = False
        self.user = None
    
    def signup(self, email: str, password: str, user_metadata: Dict = None) -> Dict:
        """Registra novo usuário no Supabase Auth."""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            if response.user:
                logger.info(f"Usuário criado: {email}")
                return {
                    "success": True,
                    "user": response.user,
                    "message": "Conta criada com sucesso! Verifique seu email."
                }
            else:
                return {"success": False, "message": "Erro ao criar conta."}
                
        except Exception as e:
            logger.error(f"Erro no signup: {e}")
            return {"success": False, "message": str(e)}
    
    def login(self, email: str, password: str) -> Dict:
        """Autentica usuário existente."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                self.is_authenticated = True
                self.user = response.user
                logger.info(f"Login bem-sucedido: {email}")
                
                # Salva sessão no Streamlit
                st.session_state.supabase_session = response.session
                
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "name": response.user.user_metadata.get("name", ""),
                        "created_at": response.user.created_at
                    }
                }
            else:
                return {"success": False, "message": "Credenciais inválidas."}
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return {"success": False, "message": "Email ou senha incorretos."}
    
    def logout(self):
        """Encerra sessão do usuário."""
        try:
            self.client.auth.sign_out()
            self.is_authenticated = False
            self.user = None
            st.session_state.supabase_session = None
            logger.info("Logout realizado")
        except Exception as e:
            logger.error(f"Erro no logout: {e}")
    
    def get_current_user(self) -> Optional[Dict]:
        """Retorna usuário atual da sessão."""
        try:
            if st.session_state.get("supabase_session"):
                response = self.client.auth.get_user()
                if response.user:
                    return {
                        "id": response.user.id,
                        "email": response.user.email,
                        "name": response.user.user_metadata.get("name", "")
                    }
        except Exception as e:
            logger.error(f"Erro ao obter usuário: {e}")
        return None
    
    def reset_password(self, email: str) -> Dict:
        """Envia email de recuperação de senha."""
        try:
            self.client.auth.reset_password_for_email(email)
            logger.info(f"Email de recuperação enviado para: {email}")
            return {"success": True, "message": "Email de recuperação enviado!"}
        except Exception as e:
            logger.error(f"Erro ao resetar senha: {e}")
            return {"success": False, "message": str(e)}
