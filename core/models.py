# core/models.py
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List

@dataclass
class User:
    id: str
    nome: str
    idade: int
    altura: float
    genero: str
    current_weight: float
    target_weight: float
    meta_mensal_kg: float
    peso_inicio_mes: float
    data_inicio_mes: date
    foto_url: Optional[str] = None

@dataclass
class WeightLog:
    id: str
    user_id: str
    peso_kg: float
    registered_at: datetime
    nota: Optional[str] = None

@dataclass
class MealLog:
    id: str
    user_id: str
    date: date
    meal_type: str
    description: str
    calories: int
    foto_url: Optional[str] = None
