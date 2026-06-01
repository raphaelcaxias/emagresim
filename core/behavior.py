import datetime
from typing import List, Dict

class BehaviorEngine:
    def __init__(self, db):
        self.db = db
    
    def calculate_streak(self, meals: List[Dict] = None) -> int:
        if meals is None:
            meals = self.db.get_meals(days=30)
        if not meals:
            return 0
        dates = sorted(set([m["date"] for m in meals]))
        if not dates:
            return 0
        streak = 1
        max_streak = 1
        current_streak = 1
        for i in range(1, len(dates)):
            curr = datetime.datetime.strptime(dates[i], "%Y-%m-%d").date()
            prev = datetime.datetime.strptime(dates[i-1], "%Y-%m-%d").date()
            if (curr - prev).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        today = datetime.date.today()
        last_date = datetime.datetime.strptime(dates[-1], "%Y-%m-%d").date()
        if (today - last_date).days <= 1:
            streak = current_streak
        else:
            streak = 0
        return streak
    
    def get_emotion_analysis(self, meals: List[Dict] = None) -> Dict:
        if meals is None:
            meals = self.db.get_meals(days=30)
        if not meals:
            return {"total": 0, "by_emotion": {}}
        emotions = {}
        for meal in meals:
            emotion = meal.get("emotion", "Não informado")
            emotions[emotion] = emotions.get(emotion, 0) + 1
        return {
            "total": len(meals),
            "by_emotion": emotions,
            "most_common": max(emotions, key=emotions.get) if emotions else None
        }
    
    def get_motivation_message(self, streak: int, daily_calories: int, goal_calories: int) -> str:
        if streak == 0:
            return "🌟 Comece hoje! Cada pequeno passo importa na sua jornada."
        elif streak < 3:
            return f"🔥 Você já tem {streak} dia(s) de consistência! Continue assim!"
        elif streak < 7:
            return f"⚡ Incrível! {streak} dias seguidos! Você está criando um hábito poderoso."
        elif streak < 14:
            return f"🎯 {streak} dias! Você está oficialmente viciado em cuidar de si mesmo!"
        elif streak < 30:
            return f"🏆 LENDÁRIO! {streak} dias de consistência. Você inspira!"
        else:
            return f"👑 MESTRE DA CONSISTÊNCIA! {streak} dias! Você é uma máquina!"
    
    def get_insights(self, meals: List[Dict]) -> List[str]:
        insights = []
        if not meals:
            return ["📝 Comece a registrar refeições para receber insights personalizados!"]
        morning_meals = [m for m in meals if "08" in m.get("timestamp", "")]
        if morning_meals:
            insights.append("☀️ Você costuma registrar refeições pela manhã - ótimo para criar rotina!")
        unique_foods = set(m.get("food_id") for m in meals if m.get("food_id"))
        if len(unique_foods) >= 5:
            insights.append("🌈 Você tem uma dieta variada! Isso é excelente para nutrientes.")
        emotions = [m.get("emotion") for m in meals if m.get("emotion")]
        if "Ansiedade" in emotions:
            insights.append("💭 Percebemos registros ligados à ansiedade. Considere técnicas de respiração antes das refeições.")
        if not insights:
            insights.append("💪 Continue registrando! Quanto mais dados, melhores os insights.")
        return insights
