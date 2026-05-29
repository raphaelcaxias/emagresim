"""Core module for EmagreSim"""

from .database import Database
from .models import User, Meal, Progress
from .gamification import GamificationSystem
from .psychology import PsychologyEngine
from .services import NutritionService

__all__ = [
    'Database',
    'User', 
    'Meal',
    'Progress',
    'GamificationSystem',
    'PsychologyEngine',
    'NutritionService'
]
