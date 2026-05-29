from .database import SupabaseDB
from .gamification import GamificationSystem
from datetime import datetime

class UserService:
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.game = GamificationSystem()

    def register_meal(self, meal_data: dict) -> dict:
        success = self.db.add_meal(meal_data)
        if not success: return {"error": "Falha ao salvar"}
        
        xp = self.game.calculate_meal_xp(meal_data["calories"], meal_data["proteins"])
        result = self.db.update_xp(xp)
        return {"success": True, "xp": xp, **result}

    def update_weight(self, weight: float) -> dict:
        self.db.add_weight_log(weight)
        self.db.update_xp(5)
        profile = self.db.get_profile()
        diff = weight - (profile.get("current_weight_kg") or weight)
        self.db.update_profile({"current_weight_kg": weight})
        
        msg = f"🎉 Perdeu {abs(diff):.1f}kg!" if diff < 0 else f"📈 Ganhou {diff:.1f}kg. Continue firme!"
        return {"message": msg}
