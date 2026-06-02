import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_daily_summary_safe(nutrition_service) -> Dict[str, Any]:
    """Wrapper seguro para evitar KeyError em resumos diários."""
    default = {"calories": 0, "count": 0, "meals": [], "proteins": 0, "carbs": 0, "fats": 0}
    try:
        summary = nutrition_service.get_daily_summary()
        if not summary:
            return default
        # Normalização de chaves
        return {
            "calories": int(summary.get("calories", summary.get("cal", 0))),
            "count": int(summary.get("count", 0)),
            "meals": summary.get("meals", []),
            "proteins": float(summary.get("proteins", summary.get("p", 0))),
            "carbs": float(summary.get("carbs", summary.get("c", 0))),
            "fats": float(summary.get("fats", summary.get("g", 0))),
        }
    except Exception as e:
        logger.error(f"Erro em get_daily_summary_safe: {e}")
        return default

def get_streak_safe(gamification_service) -> int:
    """Wrapper seguro para cálculo de streak."""
    try:
        streak = gamification_service.calculate_streak()
        return int(streak) if streak else 0
    except Exception as e:
        logger.error(f"Erro em get_streak_safe: {e}")
        return 0
