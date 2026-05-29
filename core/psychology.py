"""
Psychology Engine - Motivação e Análise Comportamental
"""
import random
from datetime import datetime, date
from typing import Dict

class PsychologyEngine:
    def __init__(self):
        self.motivation_phrases = [
            "💪 Cada pequeno passo conta! Você está no caminho certo!",
            " Hoje é um novo dia para fazer escolhas saudáveis!",
            "🎯 Lembre-se: consistência é mais importante que perfeição!",
            "✨ Seu eu do futuro vai agradecer pelos esforços de hoje!",
            "🔥 Você é mais forte do que suas desculpas!",
            "🍎 A alimentação é o combustível da sua mudança!"
        ]
        self.tips = [
            "Beba um copo de água antes de cada refeição",
            "Faça pequenas pausas ativas durante o dia",
            "Durma 7-8 horas por noite para melhor recuperação",
            "Coma devagar e mastigue bem os alimentos",
            "Substitua refrigerantes por água com limão"
        ]
    
    def get_daily_motivation(self) -> str:
        return random.choice(self.motivation_phrases)
    
    def get_health_tip(self) -> str:
        return random.choice(self.tips)
    
    def analyze_streak(self, user_id: int, db) -> Dict:
        """Analisa a sequência de dias consecutivos de registro"""
        progress = db.get_progress_history(user_id, days=30)
        
        if progress.empty:
            return {"current_streak": 0, "longest_streak": 0}
        
        current_streak = 0
        longest_streak = 0
        streak = 0
        last_date = None
        
        today = date.today()
        yesterday = date.fromordinal(today.toordinal() - 1)
        
        for _, row in progress.iterrows():
            try:
                current_date = row['date']
                if isinstance(current_date, str):
                    current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
            except:
                continue
                
            if last_date:
                diff = (current_date - last_date).days
                if diff == 1:
                    streak += 1
                elif diff == 0:
                    continue # Mesmo dia, ignora
                else:
                    streak = 1
            else:
                streak = 1
            
            longest_streak = max(longest_streak, streak)
            
            # Se o último registro é hoje ou ontem, o streak está ativo
            if current_date in (today, yesterday):
                current_streak = streak
            
            last_date = current_date
            
        return {"current_streak": current_streak, "longest_streak": longest_streak}
