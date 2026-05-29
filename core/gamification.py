from typing import Dict

class GamificationSystem:
    @staticmethod
    def calculate_meal_xp(calories: int, proteins: float) -> int:
        xp = 10
        if 300 <= calories <= 700: xp += 15
        if proteins > 15: xp += 10
        return xp

    @staticmethod
    def check_achievements(profile: Dict, meals_count: int, streak: int) -> list:
        unlocked = []
        if profile["level"] >= 5 and "Nível 5" not in profile.get("unlocked_achievements", []):
            unlocked.append("Nível 5")
        if streak >= 7 and "Semana Dourada" not in profile.get("unlocked_achievements", []):
            unlocked.append("Semana Dourada")
        if meals_count >= 50 and "Consistente" not in profile.get("unlocked_achievements", []):
            unlocked.append("Consistente")
        return unlocked
