import datetime
from datetime import datetime as dt
from typing import Dict, List
from core.database import AppDatabase

class GamificationSystem:
    def __init__(self, db: AppDatabase): 
        self.db = db
    
    def calculate_streak(self) -> int:
        meals = self.db.get_meals(days=30)
        if not meals: return 0
        dates = sorted(list(set(m.get("meal_date") for m in meals if m.get("meal_date"))))
        if not dates: return 0
        date_objects = [dt.strptime(d, "%Y-%m-%d").date() for d in dates]
        streak = 0
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        
        if date_objects[-1] != today and date_objects[-1] != yesterday: return 0
        streak = 1
        for i in range(len(date_objects) - 1, 0, -1):
            diff = (date_objects[i] - date_objects[i-1]).days
            if diff == 1: streak += 1
            elif diff > 1: break
        return streak
    
    def check_achievements(self, meals_count: int, streak: int) -> List[str]:
        unlocked = []
        if meals_count >= 1 and self.db.unlock_achievement("first_meal", "🍽️ Primeira Refeição"): 
            unlocked.append("🍽️ Primeira Refeição")
        if streak >= 7 and self.db.unlock_achievement("week_streak", "📅 7 Dias de Registro"): 
            unlocked.append(" 7 Dias de Registro")
        return unlocked
