"""
Core module - Lógica principal do EmagreSim
"""
from .database import Database
from .gamification import GamificationSystem
from .psychology import PsychologyEngine
from .services import NutritionService, UserService

__all__ = [
    'Database',
    'GamificationSystem', 
    'PsychologyEngine',
    'NutritionService',
    'UserService'
]
