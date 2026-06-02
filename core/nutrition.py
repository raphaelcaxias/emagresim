import datetime
from datetime import date
import pandas as pd
from utils.food_db import FOOD_DB, COMBOS

class NutritionService:
    def __init__(self, db): self.db = db
    
    def get_daily_summary(self, date_str=None):
        if not date_str: date_str = str(date.today())
        meals = self.db.get_meals_by_date(date_str)
        return {"cal": sum(m.get("cal", 0) for m in meals), "count": len(meals), "meals": meals}
    
    def get_weekly_summary(self) -> pd.DataFrame:
        meals = self.db.get_meals(days=7)
        if not meals: return pd.DataFrame()
        df = pd.DataFrame(meals)
        df['date'] = pd.to_datetime(df['date'])
        return df.groupby(df['date'].dt.date).agg(calories=('cal','sum')).reset_index()
    
    def register_food(self, food_id, qty, emotion):
        food = FOOD_DB.get(food_id)
        if food:
            self.db.save_meal({
                "food": food["name"], "food_id": food_id,
                "cal": int(food["cal"] * qty), "p": food["p"]*qty, "c": food["c"]*qty, "g": food["g"]*qty,
                "date": str(date.today()), "emotion": emotion, "timestamp": str(datetime.datetime.now())
            })
            return True, food["name"], food["cal"] * qty
        return False, None, 0
    
    def get_macro_goal(self, weight, height, age):
        tmb = 10 * weight + 6.25 * height - 5 * age + 5
        return {"maintenance": int(tmb * 1.55), "deficit": int((tmb * 1.55) - 500)}