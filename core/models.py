from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List

@dataclass
class User:
    id: Optional[int]
    username: str
    password: str
    email: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goal_weight: Optional[float] = None
    experience: int = 0
    level: int = 1
    created_at: datetime = None
    
    def calculate_bmi(self) -> Optional[float]:
        if self.weight and self.height:
            height_m = self.height / 100
            return self.weight / (height_m ** 2)
        return None
    
    def calculate_daily_calories(self) -> int:
        """Calcula calorias diárias recomendadas (TMB x fator atividade)"""
        if not self.weight or not self.height or not self.age:
            return 2000  # Valor padrão
        
        # Fórmula de Mifflin-St Jeor
        if self.gender == 'male':
            tmb = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            tmb = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        
        # Fator de atividade (assumindo moderadamente ativo)
        return int(tmb * 1.55)

@dataclass
class Meal:
    id: Optional[int]
    user_id: int
    meal_type: str  # breakfast, lunch, dinner, snack
    food_name: str
    calories: int
    proteins: float = 0
    carbs: float = 0
    fats: float = 0
    meal_time: datetime = None
    
    def is_healthy(self) -> bool:
        """Avalia se a refeição é saudável baseada nos macros"""
        if self.calories <= 0:
            return False
        
        protein_ratio = (self.proteins * 4) / self.calories
        fat_ratio = (self.fats * 9) / self.calories
        
        # Refeição saudável: mínimo 20% proteína e máximo 35% gordura
        return protein_ratio >= 0.20 and fat_ratio <= 0.35

@dataclass
class Progress:
    id: Optional[int]
    user_id: int
    date: date
    weight: float
    calories_consumed: int = 0
    calories_burned: int = 0
    notes: str = ""
    
    @property
    def net_calories(self) -> int:
        return self.calories_consumed - self.calories_burned
    
    def weight_change(self, previous_weight: float) -> float:
        return self.weight - previous_weight

@dataclass
class Achievement:
    id: Optional[int]
    user_id: int
    achievement_name: str
    unlocked_at: datetime = None
