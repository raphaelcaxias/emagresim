import logging
from datetime import datetime, time
from typing import Dict, List

logger = logging.getLogger(__name__)

class NotificationService:
    """Sistema de notificações e lembretes inteligentes."""
    
    REMINDERS = {
        "morning": {
            "time": "07:00",
            "message": "☀️ Bom dia! Não esqueça de registrar seu café da manhã.",
            "type": "meal"
        },
        "lunch": {
            "time": "12:30",
            "message": "🍽️ Hora do almoço! Registre sua refeição.",
            "type": "meal"
        },
        "dinner": {
            "time": "19:00",
            "message": "🌙 Jantar em breve! Planeje sua refeição.",
            "type": "meal"
        },
        "water": {
            "time": "15:00",
            "message": "💧 Já bebeu água hoje? Mantenha-se hidratado!",
            "type": "hydration"
        },
        "weight": {
            "time": "08:00",
            "message": "⚖️ Dia de pesagem? Registre seu peso!",
            "type": "weight",
            "frequency": "weekly"  # Apenas uma vez por semana
        }
    }
    
    def __init__(self):
        self.active_reminders = set(self.REMINDERS.keys())
    
    def get_active_reminders(self) -> List[Dict]:
        """Retorna lembretes ativos baseado no horário atual."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A")
        
        active = []
        for key, reminder in self.REMINDERS.items():
            if key not in self.active_reminders:
                continue
            
            # Verifica se é hora do lembrete (janela de 30 min)
            reminder_time = datetime.strptime(reminder["time"], "%H:%M").time()
            now_time = now.time()
            
            time_diff = abs(
                (datetime.combine(datetime.today(), now_time) - 
                 datetime.combine(datetime.today(), reminder_time)).seconds
            )
            
            if time_diff <= 1800:  # 30 minutos
                # Verifica frequência semanal
                if reminder.get("frequency") == "weekly" and current_day != "Monday":
                    continue
                
                active.append({
                    "key": key,
                    "message": reminder["message"],
                    "type": reminder["type"],
                    "time": reminder["time"]
                })
        
        return active
    
    def toggle_reminder(self, reminder_key: str, active: bool):
        """Ativa ou desativa um lembrete."""
        if active:
            self.active_reminders.add(reminder_key)
            logger.info(f"Lembrete ativado: {reminder_key}")
        else:
            self.active_reminders.discard(reminder_key)
            logger.info(f"Lembrete desativado: {reminder_key}")
    
    def get_reminder_settings(self) -> Dict:
        """Retorna configuração atual dos lembretes."""
        return {
            key: key in self.active_reminders 
            for key in self.REMINDERS.keys()
        }
