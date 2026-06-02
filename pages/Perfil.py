# MUDE DE:
from core.payment import PaymentService

# PARA:
class PaymentService:
    PLANS = {
        "free": {"name": "Gratuito", "price": 0},
        "pro": {"name": "Pro", "price": 29.90}
    }
