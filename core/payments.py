import streamlit as st
import mercadopago
from typing import Dict, Optional

class PaymentService:
    PLANS = {
        "start": {"name": "Plano Start", "price": 19.90, "monthly": True, "features": [
            "Acompanhamento básico", "Registro de refeições", "Gráficos de progresso"
        ]},
        "pro": {"name": "Plano Pro", "price": 39.90, "monthly": True, "features": [
            "Tudo do Start +", "IA de recomendações", "Análise emocional avançada", "Exportação de dados"
        ]},
        "vitalicio": {"name": "Vitalício", "price": 297.00, "monthly": False, "features": [
            "Todos os recursos PRO", "Pagamento único", "Suporte prioritário", "Atualizações vitalícias"
        ]}
    }
    
    def __init__(self):
        self.sdk = None
        try:
            if "MP_ACCESS_TOKEN" in st.secrets:
                self.sdk = mercadopago.SDK(st.secrets["MP_ACCESS_TOKEN"])
        except:
            pass
    
    def create_preference(self, plan_key: str, user_id: str) -> Optional[str]:
        plan = self.PLANS.get(plan_key)
        if not plan:
            return None
        try:
            if self.sdk:
                preference_data = {
                    "items": [{
                        "title": plan["name"], "quantity": 1,
                        "unit_price": plan["price"], "currency_id": "BRL",
                        "description": f"Assinatura {plan['name']} - EmagreSim"
                    }],
                    "back_urls": {
                        "success": st.query_params.get("app_url") or "https://emagresim.streamlit.app",
                        "failure": st.query_params.get("app_url") or "https://emagresim.streamlit.app",
                        "pending": st.query_params.get("app_url") or "https://emagresim.streamlit.app"
                    },
                    "auto_return": "approved"
                }
                response = self.sdk.preference().create(preference_data)
                return response["response"]["init_point"]
            else:
                return f"https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=DEMO_{plan_key}"
        except Exception as e:
            st.error(f"Erro ao criar pagamento: {e}")
            return f"DEMO_LINK_{plan_key}"
    
    def process_return(self, user: Dict, payment_id: str, status: str) -> bool:
        # ✅ FIX: st.query_params retorna string direta, não lista
        if status == "approved" or (payment_id and "DEMO" in payment_id):
            user["plan"] = "pro"
            user["plan_expires"] = None if "vitalicio" in payment_id else "30_days"
            st.session_state.user = user
            return True
        return False
    
    def get_payment_status(self, payment_id: str) -> Dict:
        if self.sdk and payment_id and "DEMO" not in payment_id:
            try:
                response = self.sdk.payment().get(payment_id)
                return response["response"]
            except:
                return {"status": "unknown"}
        return {"status": "approved", "message": "Demo - pagamento simulado"}
    
    def get_user_plan_display(self, user: Dict) -> str:
        plan = user.get("plan", "free")
        if plan == "free":
            return '<span class="badge-free">🎁 GRÁTIS</span>'
        else:
            return '<span class="badge-pro">👑 PRO</span>'
