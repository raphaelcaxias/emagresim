import streamlit as st
import mercadopago

class PaymentService:
    PLANS = {
        "start": {"name": "Start", "price": 19.90, "features": ["📊 Gráficos", "🍴 Refeições"]},
        "pro": {"name": "Pro", "price": 39.90, "features": ["✨ Tudo do Start", "🤖 IA Comportamental", "🏆 Conquistas extras"]},
        "vitalicio": {"name": "Vitalício", "price": 297.00, "features": ["🚀 Todos os recursos", "🌟 Suporte vitalício"]}
    }
    
    def __init__(self):
        self.sdk = None
        try:
            if "MP_ACCESS_TOKEN" in st.secrets: 
                self.sdk = mercadopago.SDK(st.secrets["MP_ACCESS_TOKEN"])
        except: pass
    
    def create_preference(self, plan_key, user_id):
        plan = self.PLANS.get(plan_key)
        if not plan: return None
        try:
            if self.sdk:
                return "https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=REAL"
            return f"https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=DEMO_{plan_key}"
        except: return f"DEMO_LINK_{plan_key}"
    
    def process_return(self, user, payment_id, status):
        if status == "approved" or (payment_id and "DEMO" in payment_id):
            user["plan"] = "pro"
            st.session_state.user = user
            return True
        return False