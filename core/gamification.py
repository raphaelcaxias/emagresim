import math
from typing import Dict, List
from .database import Database

class GamificationSystem:
    def __init__(self, db: Database):
        self.db = db
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calcula XP necessário para atingir um nível"""
        return int(100 * (level ** 1.5))
    
    def add_experience(self, user_id: int, xp_gained: int) -> Dict:
        """Adiciona experiência e verifica level up"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        new_xp = user['experience'] + xp_gained
        current_level = user['level']
        new_level = current_level
        
        # Verifica se subiu de nível
        while new_xp >= self.calculate_xp_for_level(new_level):
            new_xp -= self.calculate_xp_for_level(new_level)
            new_level += 1
        
        # Atualiza no banco
        self.db.update_user_stats(user_id, experience=new_xp, level=new_level)
        
        # Verifica conquistas
        achievements = self.check_achievements(user_id, new_level)
        
        return {
            "xp_gained": xp_gained,
            "new_total_xp": new_xp,
            "old_level": current_level,
            "new_level": new_level,
            "leveled_up": new_level > current_level,
            "achievements": achievements
        }
    
    def check_achievements(self, user_id: int, new_level: int) -> List[str]:
        achievements_unlocked = []
        
        # Conquistas de nível
        level_achievements = {5: "🌱 Iniciante Dedicado", 
                             10: "⚡ Guerreiro Fitness",
                             20: "🔥 Lenda do EmagreSim"}
        
        if new_level in level_achievements:
            achievement = level_achievements[new_level]
            self.db.unlock_achievement(user_id, achievement)
            achievements_unlocked.append(achievement)
        
        return achievements_unlocked
    
    def reward_for_meal(self, calories: int, is_healthy: bool = True) -> int:
        """Calcula XP ganho por registrar refeição"""
        base_xp = 10
        
        # Bônus por refeição saudável
        if is_healthy:
            base_xp += 5
        
        # Bônus por calorias dentro do recomendado
        if 300 <= calories <= 600:
            base_xp += 10
        elif calories < 300:
            base_xp += 5  # Refeição leve
        
        return base_xp
    
    def reward_for_workout(self, duration_minutes: int, intensity: str = "medium") -> int:
        """Calcula XP por treino"""
        xp_per_minute = {
            "low": 2,
            "medium": 3,
            "high": 5
        }
        
        xp = duration_minutes * xp_per_minute.get(intensity, 3)
        return min(xp, 100)  # Limite máximo de 100 XP por treino
    
    def reward_for_consistency(self, consecutive_days: int) -> int:
        """Bônus por consistência"""
        if consecutive_days >= 30:
            return 200
        elif consecutive_days >= 14:
            return 100
        elif consecutive_days >= 7:
            return 50
        elif consecutive_days >= 3:
            return 20
        return 0
    
    def get_level_info(self, user_id: int) -> Dict:
        """Retorna informações detalhadas do nível do usuário"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {}
        
        current_level = user['level']
        current_xp = user['experience']
        next_level_xp = self.calculate_xp_for_level(current_level)
        
        progress_percentage = (current_xp / next_level_xp) * 100
        
        return {
            "level": current_level,
            "current_xp": current_xp,
            "xp_needed": next_level_xp,
            "progress_percentage": progress_percentage,
            "title": self.get_level_title(current_level)
        }
    
    def get_level_title(self, level: int) -> str:
        if level < 5:
            return "🥉 Iniciante"
        elif level < 10:
            return "🥈 Aprendiz"
        elif level < 20:
            return "🥇 Guerreiro"
        elif level < 35:
            return "💪 Mestre"
        else:
            return "🏆 Lendário"
