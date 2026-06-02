import streamlit as st

class PaymentService:
    PLANS = {
        "free": {"name": "Gratuito", "price": 0, "features": ["Registro alimentar", "Registro de peso", "Gráficos básicos"]},
        "pro": {"name": "Pro", "price": 29.90, "features": ["Análises avançadas", "Relatórios completos", "Foco em Metas"]},
        "lifetime": {"name": "Vitalício", "price": 497.00, "features": ["Todos os recursos", "Acesso permanente para sempre"]}
    }
    
    def __init__(self):
        self.sdk = None
        try:
            if "MP_ACCESS_TOKEN" in st.secrets:
                import mercadopago
                self.sdk = mercadopago.SDK(st.secrets["MP_ACCESS_TOKEN"])
        except: pass
    
    def create_checkout_link(self, plan_key: str, user_email: str) -> str:
        return f"https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=DEMO_{plan_key}_{user_email}"
