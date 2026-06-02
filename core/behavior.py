import datetime
from typing import List, Dict

class BehaviorEngine:
    def __init__(self, db): self.db = db
    
    def calculate_streak(self, meals=None) -> int:
        if meals is None: meals = self.db.get_meals(days=30)
        if not meals: return 0
        dates = sorted(set(m["date"] for m in meals))
        if len(dates) < 2: return 1
        
        streak = 1
        for i in range(1, len(dates)):
            d1 = datetime.datetime.strptime(dates[i], "%Y-%m-%d").date()
            d0 = datetime.datetime.strptime(dates[i-1], "%Y-%m-%d").date()
            streak = streak + 1 if (d1 - d0).days == 1 else 1
            
        today = datetime.date.today()
        last = datetime.datetime.strptime(dates[-1], "%Y-%m-%d").date()
        return streak if (today - last).days <= 1 else 0
    
    def get_motivation_message(self, streak, cal, goal):
        if streak == 0: return "🌟 Comece hoje! Cada passo conta."
        if streak < 3: return f"🔥 {streak} dia(s)! Continue assim."
        return f"🏆 LENDÁRIO! {streak} dias de consistência."
    
    def get_insights(self, meals):
        if not meals: return ["Registre refeições para ver insights."]
        return ["🌈 Dieta variada!", "💧 Beba mais água."]