import streamlit as st
import random
from datetime import datetime
from typing import Dict, List

class MessagesService:
    """Serviço de mensagens variadas para evitar repetição"""
    
    def __init__(self, db):
        self.db = db
    
    def get_random_message(self, category: str, context: str = None) -> Dict:
        """Retorna mensagem aleatória da categoria"""
        # Tenta buscar do Supabase
        if self.db.is_real and self.db.client:
            try:
                query = self.db.client.table("motivational_messages").select("*").eq("category", category).eq("is_active", True)
                if context:
                    query = query.eq("context", context)
                else:
                    query = query.in_("context", ["general", context or "random"])
                result = query.execute()
                if result.data:
                    return random.choice(result.data)
            except:
                pass
        
        # Fallback local com frases do Python
        fallback_messages = {
            "login": [
                {"message": "Que bom ter você de volta! 💪", "emoji": "👋"},
                {"message": "Cada dia é uma nova chance.", "emoji": "🌱"},
            ],
            "streak": [
                {"message": "Mais um dia registrado! 🔥", "emoji": ""},
            ],
            "meal": [
                {"message": "Registro feito! Consciência em ação.", "emoji": "✅"},
            ],
        }
        messages = fallback_messages.get(category, fallback_messages["login"])
        return random.choice(messages)
    
    def get_daily_tip(self, category: str = None) -> Dict:
        """Retorna dica do dia (rotaciona baseado na data)"""
        today = datetime.now().day  # Muda todo dia
        
        if self.db.is_real and self.db.client:
            try:
                query = self.db.client.table("daily_tips").select("*").eq("is_active", True)
                if category:
                    query = query.eq("category", category)
                result = query.execute()
                if result.data:
                    # Seleciona baseado no dia (determinístico)
                    idx = today % len(result.data)
                    return result.data[idx]
            except:
                pass
        
        # Fallback
        tips = [
            {"tip": "Beba água ao acordar!", "emoji": "💧"},
            {"tip": "Durma bem hoje.", "emoji": "😴"},
        ]
        return tips[today % len(tips)]
    
    def get_welcome_message(self) -> str:
        """Mensagem de boas-vindas baseada no horário"""
        hour = datetime.now().hour
        if hour < 12:
            return "☀️ Bom dia! Um novo dia, novas oportunidades."
        elif hour < 18:
            return "🌤️ Boa tarde! Que tal revisar suas metas?"
        else:
            return "🌙 Boa noite! Reflita sobre suas conquistas."
    
    def get_achievement_message(self, achievement_name: str) -> str:
        """Mensagem específica por conquista"""
        messages = {
            "first_meal": "🍽️ Primeira Refeição registrada! O começo de tudo.",
            "week_streak": "📅 7 dias seguidos! Você está no caminho certo.",
            "month_streak": " 30 dias! Poucos chegam até aqui. Parabéns!",
        }
        return messages.get(achievement_name, "✨ Nova conquista desbloqueada!")
