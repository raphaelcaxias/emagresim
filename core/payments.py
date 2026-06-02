class PaymentService:
    PLANS = {
        "free": {"name": "Gratuito", "price": 0},
        "pro": {"name": "Pro", "price": 29.90},
        "lifetime": {"name": "Vitalício", "price": 497.00}
    }
    
    def create_checkout_link(self, plan_key, user_email):
        return f"https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=DEMO_{plan_key}"
