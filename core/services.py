def register_meal(self, user_id: int, meal_data: Dict) -> Dict:
    """Registra uma refeição e concede XP"""
    # Adiciona refeição ao banco
    self.db.add_meal(user_id, meal_data)
    
    # Verifica se é saudável
    is_healthy = meal_data.get('calories', 0) < 600 and meal_data.get('proteins', 0) > 10
    
    # Calcula XP
    xp_gained = 10
    if is_healthy:
        xp_gained += 5
    if 300 <= meal_data.get('calories', 0) <= 600:
        xp_gained += 10
    
    # Adiciona experiência
    xp_result = self.gamification.add_experience(user_id, xp_gained)
    
    return {
        "meal_registered": True,
        "xp_gained": xp_gained,
        **xp_result
    }
