import datetime
from datetime import date
import pandas as pd
from utils.food_db import FOOD_DB, COMBOS

class NutritionService:
    def __init__(self, db):
        self.db = db
    
    def calculate_tmb(self, weight: float, height: float, age: int, gender: str = "male") -> int:
        if not weight or not height or not age: return 1500
        if gender == "male": 
            return int(10 * weight + 6.25 * height - 5 * age + 5)
        else: 
            return int(10 * weight + 6.25 * height - 5 * age - 161)
    
    def calculate_daily_goal(self, tmb: int, activity_level: str = "moderate", goal: str = "lose") -> int:
        activity_factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
        maintenance = int(tmb * activity_factors.get(activity_level, 1.55))
        if goal == "lose": return max(1200, maintenance - 500)
        elif goal == "gain": return maintenance + 300
        else: return maintenance
    
    def get_daily_summary(self, date_str: str = None) -> dict:
        if not date_str: date_str = str(date.today())
        meals = self.db.get_meals_by_date(date_str)
        return {
            "calories": sum(int(m.get("calories", 0)) for m in meals),
            "proteins": sum(float(m.get("proteins", 0)) for m in meals),
            "carbs": sum(float(m.get("carbs", 0)) for m in meals),
            "fats": sum(float(m.get("fats", 0)) for m in meals),
            "count": len(meals),
            "meals": sorted(meals, key=lambda x: x.get("meal_time", "00:00"))
        }
    
    def register_food(self, food_id: str, quantity: float, meal_time: str = None, photo_path: str = None) -> tuple:
        food = FOOD_DB.get(food_id)
        if not food: return False, None, 0
        if meal_time is None: meal_time = datetime.datetime.now().strftime("%H:%M")
        
        meal_data = {
            "food": food["name"], "food_id": food_id, "quantity": float(quantity),
            "calories": int(food["cal"] * quantity), "proteins": round(float(food["p"] * quantity), 1),
            "carbs": round(float(food["c"] * quantity), 1), "fats": round(float(food["g"] * quantity), 1),
            "meal_date": str(date.today()), "meal_time": meal_time, "photo_path": photo_path
        }
        self.db.save_meal(meal_data)
        return True, food["name"], meal_data["calories"]
    
    def register_combo(self, combo_id: str) -> tuple:
        combo = COMBOS.get(combo_id)
        if not combo: return False, None, 0
        total_calories = 0
        meal_time = datetime.datetime.now().strftime("%H:%M")
        for item_id in combo["items"]:
            ok, _, cal = self.register_food(item_id, 1.0, meal_time=meal_time)
            if ok: total_calories += cal
        return True, combo["name"], total_calories
