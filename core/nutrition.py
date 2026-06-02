import datetime
from datetime import date
import pandas as pd
from utils.food_db import FOOD_DB, COMBOS
import logging

logger = logging.getLogger(__name__)

class NutritionService:
    def __init__(self, db):
        self.db = db
    
    def calculate_tmb(self, weight: float, height: float, age: int, gender: str = "male") -> int:
        if not weight or not height or not age: return 1500
        if gender == "male": return int(10 * weight + 6.25 * height - 5 * age + 5)
        return int(10 * weight + 6.25 * height - 5 * age - 161)
    
    def calculate_daily_goal(self, tmb: int, activity_level: str = "moderate", goal: str = "lose") -> int:
        factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
        maintenance = int(tmb * factors.get(activity_level, 1.55))
        if goal == "lose": return max(1200, maintenance - 500)
        elif goal == "gain": return maintenance + 300
        return maintenance
    
    def get_daily_summary(self, date_str: str = None) -> dict:
        if not date_str: date_str = str(date.today())
        meals = self.db.get_meals_by_date(date_str)
        
        # Soma usando as novas chaves
        return {
            "calories": sum(int(m.get("calories", 0)) for m in meals),
            "protein": sum(float(m.get("protein", 0)) for m in meals),
            "carbs": sum(float(m.get("carbs", 0)) for m in meals),
            "fat": sum(float(m.get("fat", 0)) for m in meals),
            "fiber": sum(float(m.get("fiber", 0)) for m in meals),
            "count": len(meals),
            "meals": sorted(meals, key=lambda x: x.get("meal_time", "00:00"))
        }
    
    def get_weekly_summary(self) -> pd.DataFrame:
        meals = self.db.get_meals(days=7)
        if not meals: return pd.DataFrame()
        df = pd.DataFrame(meals)
        df['meal_date'] = pd.to_datetime(df['meal_date'])
        return df.groupby(df['meal_date'].dt.date).agg({'calories': 'sum'}).reset_index().rename(columns={'meal_date': 'date'})
    
    def register_food(self, food_id: str, quantity: float, meal_time: str = None) -> tuple:
        food = FOOD_DB.get(food_id)
        if not food: return False, None, 0
        if not meal_time: meal_time = datetime.datetime.now().strftime("%H:%M")
        
        meal_data = {
            "food": food["name"], "food_id": food_id, "quantity": float(quantity),
            "calories": int(food["calories"] * quantity), 
            "protein": round(food["protein"] * quantity, 1),
            "carbs": round(food["carbs"] * quantity, 1), 
            "fat": round(food["fat"] * quantity, 1),
            "fiber": round(food["fiber"] * quantity, 1),
            "meal_date": str(date.today()), "meal_time": meal_time
        }
        self.db.save_meal(meal_data)
        return True, food["name"], meal_data["calories"]
