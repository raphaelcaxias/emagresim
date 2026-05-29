import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PsychologyEngine:
    def __init__(self):
        self.motivation_phrases = [
            "💪 Cada pequeno passo conta! Você está no caminho certo!",
            "🌟 Hoje é um novo dia para fazer escolhas saudáveis!",
            "🎯 Lembre-se: consistência é mais importante que perfeição!",
            "✨ Seu eu do futuro vai agradecer pelos esforços de hoje!",
            "🏆 Você é mais forte do que seus desafios!",
            "🌱 Pequenas mudanças hoje, grandes resultados amanhã!",
            "⚡ Você tem o poder de transformar sua saúde!",
            "💚 Cada refeição saudável é um ato de amor próprio!"
        ]
        
        self.tips = [
            "Beba um copo de água antes de cada refeição",
            "Faça pequenas pausas ativas durante o dia",
            "Durma 7-8 horas por noite para melhor recuperação",
            "Coma devagar e mastigue bem os alimentos",
            "Inclua proteína em todas as refeições",
            "Varie as cores do seu prato para garantir nutrientes diversos",
            "Evite distrações enquanto come (celular, TV)",
            "Prepare suas refeições com antecedência"
        ]
    
    def get_daily_motivation(self) -> str:
        """Retorna uma frase motivacional aleatória"""
        return random.choice(self.motivation_phrases)
    
    def get_health_tip(self) -> str:
        """Retorna uma dica de saúde aleatória"""
        return random.choice(self.tips)
    
    def analyze_streak(self, user_id: int, db) -> Dict:
        """Analisa a sequência de dias consistentes do usuário"""
        progress_history = db.get_progress_history(user_id, days=30)
        
        if progress_history.empty:
            return {"current_streak": 0, "longest_streak": 0}
        
        # Calcula streak de dias consecutivos com registro
        current_streak = 0
        longest_streak = 0
        streak = 0
        last_date = None
        
        for _, row in progress_history.iterrows():
            current_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            
            if last_date and (current_date - last_date).days == 1:
                streak += 1
            else:
                streak = 1
            
            longest_streak = max(longest_streak, streak)
            
            # Verifica se é streak atual
            if current_date == datetime.now().date():
                current_streak = streak
            
            last_date = current_date
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "message": self.get_streak_message(current_streak)
        }
    
    def get_streak_message(self, streak: int) -> str:
        """Mensagem motivacional baseada na streak"""
        if streak == 0:
            return "🌱 Comece hoje sua jornada! Cada dia conta!"
        elif streak < 3:
            return "🎯 Ótimo início! Continue assim!"
        elif streak < 7:
            return "⚡ Você está criando um hábito! Parabéns!"
        elif streak < 14:
            return "🔥 Incrível! Você está no caminho da consistência!"
        elif streak < 30:
            return "🏆 Você é um guerreiro! Mantenha o ritmo!"
        else:
            return "👑 LENDÁRIO! 30+ dias de consistência!"
    
    def predict_motivation_level(self, weight_loss_rate: float) -> str:
        """Prevê nível de motivação baseado na taxa de perda de peso"""
        if weight_loss_rate < 0.2:
            return "⚠️ Ritmo lento. Considere ajustar sua estratégia."
        elif weight_loss_rate < 0.5:
            return "📈 Bom ritmo! Continue consistente!"
        elif weight_loss_rate <= 1.0:
            return "⚡ Ritmo excelente! Você está arrasando!"
        else:
            return "🎯 Perda muito rápida. Certifique-se de que é saudável!"
    
    def get_encouragement_for_missed_day(self, missed_days: int) -> str:
        """Mensagem encorajadora para dias perdidos"""
        if missed_days == 1:
            return "📅 Um dia não define sua jornada. Volte hoje mais forte!"
        elif missed_days <= 3:
            return "💪 Você ainda pode recuperar! O importante é recomeçar!"
        else:
            return "🌟 Nunca é tarde para recomeçar. Você tem o poder de mudar!"
