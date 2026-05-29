"""
Gamification System - Lógica de RPG e Progressão
"""
from typing import Dict, Optional

class GamificationSystem:
    def __init__(self, db):
        self.db = db
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calcula o XP necessário para o próximo nível (fórmula exponencial leve)"""
        return int(100 * (level ** 1.5))
    
    def add_experience(self, user_id: int, xp_gained: int) -> Dict:
        """
        Adiciona XP ao usuário e verifica se subiu de nível.
        
        Returns:
            Dicionário com status, XP total e info de level up.
        """
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        new_xp = user['experience'] + xp_gained
        current_level = user['level']
        new_level = current_level
        
        # Verifica level up (pode subir mais de um nível de uma vez)
        xp_needed = self.calculate_xp_for_level(new_level)
        while new_xp >= xp_needed:
            new_xp -= xp_needed
            new_level += 1
            xp_needed = self.calculate_xp_for_level(new_level)
        
        # Atualiza no banco
        self.db.update_user_stats(user_id, experience=new_xp, level=new_level)
        
        return {
            "xp_gained": xp_gained,
            "new_total_xp": new_xp,
            "old_level": current_level,
            "new_level": new_level,
            "leveled_up": new_level > current_level
        }
    
    def reward_for_meal(self, calories: int, is_healthy: bool = True) -> int:
        """Calcula XP ganho com base na qualidade da refeição"""
        base_xp = 10
        if is_healthy:
            base_xp += 15  # Bônus por ser saudável
        if 300 <= calories <= 600:
            base_xp += 10  # Bônus por estar na faixa ideal
        return base_xp
    
    def get_level_info(self, user_id: int) -> Dict:
        """Retorna informações para a barra de progresso"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {}
        
        current_level = user['level']
        current_xp = user['experience']
        xp_needed = self.calculate_xp_for_level(current_level)
        progress_pct = (current_xp / xp_needed) * 100 if xp_needed > 0 else 0
        
        return {
            "level": current_level,
            "current_xp": current_xp,
            "xp_needed": xp_needed,
            "progress_percentage": min(progress_pct, 100)
        }
