import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """Serviço de pagamentos (Integração Mercado Pago)."""
    
    PLANS = {
        "free": {"name": "Gratuito", "price": 0, "features": ["Registro básico", "Gráficos simples"]},
        "pro": {"name": "Pro", "price": 29.90, "features": ["Análises avançadas", "Relatórios PDF", "Sem anúncios"]},
        "lifetime": {"name": "Vitalício", "price": 497.00, "features": ["Acesso eterno", "Suporte prioritário"]}
    }

    def __init__(self):
        self.sdk = None
        # Inicialização do SDK seria feita aqui com st.secrets em produção
        logger.info("PaymentService inicializado em modo sandbox.")

    def create_checkout_link(self, plan_key: str, user_email: str) -> str:
        if plan_key not in self.PLANS:
            raise ValueError(f"Plano inválido: {plan_key}")
        # Em produção, chamar self.sdk.preference().create()
        return f"https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=DEMO_{plan_key}_{user_email}"
