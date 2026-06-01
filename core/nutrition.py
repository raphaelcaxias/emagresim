import datetime
from datetime import date  # ✅ FIX: Import adicionado
import pandas as pd
from utils.food_db import FOOD_DB, COMBOS

class NutritionService:
    def __init__(self, db):
        self.db = db
    
    def get_daily_summary(self, date_str: str = None):
        if not date_str:
            date_str = str(date.today())
        meals = self.db.get_meals_by_date(date_str)
        total_cal = sum(m.get("cal", 0) for m in meals)
        total_p = sum(m.get("p", 0) for m in meals)
        total_c = sum(m.get("c", 0) for m in meals)
        total_g = sum(m.get("g", 0) for m in meals)
        emotions = [m.get("emotion", "") for m in meals if m.get("emotion")]
        common_emotion = max(set(emotions), key=emotions.count) if emotions else None
        return {
            "cal": total_cal, "p": total_p, "c": total_c, "g": total_g,
            "count": len(meals), "meals": meals, "common_emotion": common_emotion
        }
    
    def get_weekly_summary(self) -> pd.DataFrame:
        meals = self.db.get_meals(days=7)
        if not meals:
            return pd.DataFrame()
        df = pd.DataFrame(meals)
        df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby(df['date'].dt.date).agg({'cal': 'sum', 'p': 'sum'}).reset_index()
        daily.columns = ['date', 'calories', 'protein']
        return daily
    
    def register_food(self, food_id, qty, emotion):
        food = FOOD_DB.get(food_id)
        if food:
            self.db.save_meal({
                "food": food["name"], "food_id": food_id,
                "cal": int(food["cal"] * qty),
                "p": food["p"] * qty, "c": food["c"] * qty, "g": food["g"] * qty,
                "portion": qty, "date": str(date.today()),
                "emotion": emotion, "timestamp": str(datetime.datetime.now())
            })
            return True, food["name"], food["cal"] * qty
        return False, None, 0
    
    def register_combo(self, combo_id, emotion):
        combo = COMBOS.get(combo_id)
        if combo:
            total_cal = 0
            for item_id in combo["items"]:
                success, name, cal = self.register_food(item_id, 1, emotion)
                if success:
                    total_cal += cal
            return True, combo["name"], total_cal
        return False, None, 0
    
    def get_macro_goal(self, weight: float, height: float, age: int, activity: str = "moderate") -> dict:
        tmb = 10 * weight + 6.25 * height - 5 * age + 5
        activity_factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
        maintenance = tmb * activity_factors.get(activity, 1.55)
        deficit = maintenance - 500
        return {
            "maintenance": int(maintenance), "deficit": int(deficit),
            "protein_goal": int(weight * 1.6),
            "carbs_goal": int((deficit * 0.5) / 4),
            "fat_goal": int((deficit * 0.25) / 9)
        }
