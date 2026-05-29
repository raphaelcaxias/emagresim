# core/gamification.py
from typing import Dict, List
from models.state import AppState, Meal


LEVELS = [
    {"name": "Iniciante", "icon": "🌱", "min": 0, "desc": "Todo começo é válido."},
    {"name": "Explorador", "icon": "🔥", "min": 500, "desc": "Descobrindo seu ritmo."},
    {"name": "Persistente", "icon": "💪", "min": 1500, "desc": "Construindo consistência."},
    {"name": "Reconstrutor", "icon": "🔄", "min": 3000, "desc": "Recair faz parte. Voltar é força."},
    {"name": "Inabalável", "icon": "⚓", "min": 6000, "desc": "Sua consistência é sua âncora."},
    {"name": "Guia", "icon": "🌟", "min": 10000, "desc": "Você inspira pelo exemplo."},
]

POINTS_CONFIG = {
    "checkin": 10,
    "meal": 15,
    "meal_photo": 5,
    "weight": 10,
    "streak_7": 100,
}


def get_level(pts: int) -> Dict:
    for lvl in reversed(LEVELS):
        if pts >= lvl["min"]:
            return lvl
    return LEVELS[0]


def get_next_level(pts: int) -> Dict:
    for lvl in LEVELS:
        if pts < lvl["min"]:
            return lvl
    return LEVELS[-1]


def level_progress(pts: int) -> float:
    nl = get_next_level(pts)
    idx = LEVELS.index(nl)
    prev_min = LEVELS[idx - 1]["min"] if idx > 0 else 0
    span = nl["min"] - prev_min
    return min(100.0, (pts - prev_min) / span * 100) if span > 0 else 0


def calculate_meal_points(meal: Meal) -> int:
    pts = POINTS_CONFIG["meal"]
    if meal.has_photo:
        pts += POINTS_CONFIG["meal_photo"]
    return pts


def calculate_streak_bonus(streak: int) -> int:
    if streak > 0 and streak % 7 == 0:
        return POINTS_CONFIG["streak_7"]
    return 0
