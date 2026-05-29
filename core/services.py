"""
Services - Regras de Negócio
"""
from typing import Dict
from datetime import datetime
import random

class NutritionService:
    def __init__(self, db):
        self.db = db
    
    def get_daily_summary(self, user_id: int) -> Dict:
        meals = self.db.get_daily_meals(user_id)
        return {
            "total_calories": sum(m.get('calories', 0) for m in meals),
            "total_proteins": sum(m.get('proteins', 0) for m in meals),
            "meal_count": len(meals),
            "meals": meals
        }
    
    def suggest_healthy_meal(self, meal_type: str) -> Dict:
        suggestions = {
            "cafe": [{"name": "Vitamina de frutas + aveia", "calories": 350}],
            "almoco": [{"name": "Frango grelhado + arroz integral + salada", "calories": 550}],
            "jantar": [{"name": "Sopa de legumes com frango", "calories": 350}],
            "lanche": [{"name": "Iogurte natural + frutas vermelhas", "calories": 150}]
        }
        # Retorna uma sugestão aleatória da categoria ou um lanche padrão
        options = suggestions.get(meal_type, suggestions["lanche"])
        return random.choice(options)

class UserService:
    def __init__(self, db, gamification):
        self.db = db
        self.gamification = gamification
    
    def register_meal(self, user_id: int, meal_data: Dict) -> Dict:
        """Registra refeição e aplica gamificação"""
        meal_id = self.db.add_meal(user_id, meal_data)
        if not meal_id:
            return {"error": "Erro ao salvar refeição"}
            
        calories = meal_data.get('calories', 0)
        proteins = meal_data.get('proteins', 0)
        # Lógica simples de saúde: calorias moderadas e alguma proteína
        is_healthy = calories < 700 and proteins > 5
        
        xp_gained = self.gamification.reward_for_meal(calories, is_healthy)
        xp_result = self.gamification.add_experience(user_id, xp_gained)
        
        return {"meal_registered": True, "xp_gained": xp_gained, **xp_result}
    
    def update_weight(self, user_id: int, new_weight: float) -> Dict:
        user = self.db.get_user_by_id(user_id)
        old_weight = user.get('weight', new_weight) if user else new_weight
        
        self.db.add_progress(user_id, new_weight)
        self.db.update_user_stats(user_id, weight=new_weight)
        
        weight_change = new_weight - old_weight
        # Ganha XP extra por registrar peso
        self.gamification.add_experience(user_id, 5)
        
        if weight_change < 0:
            msg = f"🎉 Você perdeu {abs(weight_change):.1f}kg! Parabéns!"
        elif weight_change > 0:
            msg = "⚠️ O peso subiu um pouco. Não desanime, o processo não é linear!"
        else:
            msg = "Peso mantido. Ótima consistência!"
            
        return {"message": msg, "change": weight_change}
