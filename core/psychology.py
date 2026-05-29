import random

class PsychologyEngine:
    MOTIVATIONS = [
        "💪 Cada passo conta! Você está no caminho certo.",
        "🌟 Consistência vence intensidade. Continue!",
        " Seu eu do futuro agradece as escolhas de hoje.",
        "🎯 Foco no processo, o resultado vem naturalmente."
    ]
    TIPS = [
        "Beba 500ml de água antes das refeições.",
        "Durma 7-8h para regular hormônios da fome.",
        "Coma devagar: 20 minutos por refeição.",
        "Substitua ultraprocessados por comida de verdade."
    ]

    @staticmethod
    def get_daily_motivation() -> str:
        return random.choice(PsychologyEngine.MOTIVATIONS)

    @staticmethod
    def get_tip() -> str:
        return random.choice(PsychologyEngine.TIPS)
