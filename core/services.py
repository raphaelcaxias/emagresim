from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .database import Database
from .gamification import GamificationSystem
from .psychology import PsychologyEngine

class NutritionService:
    def __init__(self, db: Database):
        self.db = db
    
    def calculate_meal_nutrition(self, food_name: str, weight_g: float) -> Dict:
        """Calcula nutrição baseada em alimento (simplificado)"""
        # Tabela nutricional simplificada (kcal por 100g)
        food_db = {
            "arroz": {"calories": 130, "proteins": 2.5, "carbs": 28, "fats": 0.3},
            "feijão": {"calories": 77, "proteins": 4.8, "carbs": 13.6, "fats": 0.5},
            "frango": {"calories": 165, "proteins": 31, "carbs": 0, "fats": 3.6},
            "salada": {"calories": 20, "proteins": 1, "carbs": 4, "fats": 0.2},
            "ovo": {"calories": 155, "proteins": 13, "carbs": 1.1, "fats": 11},
            "batata": {"calories": 77, "proteins": 2, "carbs": 17, "fats": 0.1},
            "peixe": {"calories": 120, "proteins": 24, "carbs": 0, "fats": 2.5},
        }
        
        # Busca alimento mais próximo
        for key in food_db:
            if key in food_name.lower():
                nutrition = food_db[key]
                multiplier = weight_g / 100
                return {
                    "calories": int(nutrition["calories"] * multiplier),
                    "proteins": round(nutrition["proteins"] * multiplier, 1),
                    "carbs": round(nutrition["carbs"] * multiplier, 1),
                    "fats": round(nutrition["fats"] * multiplier, 1)
                }
        
        # Valor padrão se não encontrado
        return {"calories": int(weight_g * 1.5), "proteins": 0, "carbs": 0, "fats": 0}
    
    def get_daily_summary(self, user_id: int) -> Dict:
        """Resumo nutricional do dia"""
        meals = self.db.get_daily_meals(user_id)
        
        total_calories = sum(meal.get('calories', 0) for meal in meals)
        total_proteins = sum(meal.get('proteins', 0) for meal in meals)
        total_carbs = sum(meal.get('carbs', 0) for meal in meals)
        total_fats = sum(meal.get('fats', 0) for meal in meals)
        
        return {
            "total_calories": total_calories,
            "total_proteins": total_proteins,
            "total_carbs": total_carbs,
            "total_fats": total_fats,
            "meal_count": len(meals),
            "meals": meals
        }
    
    def suggest_healthy_meal(self, meal_type: str) -> Dict:
        """Sugere uma refeição saudável"""
        suggestions = {
            "breakfast": [
                {"name": "Vitamina de frutas + aveia", "calories": 350},
                {"name": "Ovos mexidos + pão integral", "calories": 400},
                {"name": "Iogurte natural + granola + frutas", "calories": 320}
            ],
            "lunch": [
                {"name": "Frango grelhado + arroz integral + salada", "calories": 550},
                {"name": "Peixe assado + legumes + quinoa", "calories": 520},
                {"name": "Omelete de vegetais + batata doce", "calories": 480}
            ],
            "dinner": [
                {"name": "Sopa de legumes com frango", "calories": 350},
                {"name": "Salada completa com atum", "calories": 380},
                {"name": "Wrap de frango com vegetais", "calories": 420}
            ],
            "snack": [
                {"name": "Frutas + castanhas", "calories": 150},
                {"name": "Iogurte proteico", "calories": 120},
                {"name": "Pasta de amendoim com banana", "calories": 180}
            ]
        }
        
        import random
        return random.choice(suggestions.get(meal_type, suggestions["snack"]))

class UserService:
    def __init__(self, db: Database, gamification: GamificationSystem):
        self.db = db
        self.gamification = gamification
    
    def register_meal(self, user_id: int, meal_data: Dict) -> Dict:
        """Registra uma refeição e concede XP"""
        # Adiciona refeição ao banco
        self.db.add_meal(user_id, meal_data)
        
        # Calcula XP
        is_healthy = meal_data.get('calories', 0) < 600 and meal_data.get('proteins', 0) > 10
        xp_gained = self.gamification.reward_for_meal(
            meal_data.get('calories', 0),
            is_healthy
        )
        
        # Adiciona experiência
        xp_result = self.gamification.add_experience(user_id, xp_gained)
        
        return {
            "meal_registered": True,
            "xp_gained": xp_gained,
            **xp_result
        }
    
    def update_weight(self, user_id: int, new_weight: float) -> Dict:
        """Atualiza peso e registra progresso"""
        user = self.db.get_user_by_id(user_id)
        old_weight = user.get('weight')
        
        # Registra progresso
        self.db.add_progress(user_id, new_weight)
        self.db.update_user_stats(user_id, weight=new_weight)
        
        # Calcula mudança
        weight_change = new_weight - old_weight if old_weight else 0
        is_positive_change = weight_change < 0  # Perda de peso é positiva
        
        # Bônus de XP por perda de peso
        if is_positive_change and weight_change < -0.5:
            xp_bonus = 50
            self.gamification.add_experience(user_id, xp_bonus)
        else:
            xp_bonus = 0
        
        return {
            "old_weight": old_weight,
            "new_weight": new_weight,
            "weight_change": weight_change,
            "xp_bonus": xp_bonus,
            "message": f"🎉 Parabéns! Você perdeu {abs(weight_change):.1f}kg!" if weight_change < 0 else "Continue firme!"
        }
