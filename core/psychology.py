# core/psychology.py
import random
from datetime import date, datetime
from typing import List, Tuple
from models.state import AppState


def calculate_risk_score(state: AppState) -> float:
    risk = 0.0
    if state.last_checkin:
        days_gap = (date.today() - date.fromisoformat(state.last_checkin)).days
        if days_gap >= 3:
            risk += 30
        elif days_gap >= 1:
            risk += 10

    negative_emotions = {"ansioso", "cansado", "frustrado"}
    negatives = sum(1 for e in state.emotion_history[-7:] if e.emotion in negative_emotions)
    risk += negatives * 12

    if len(state.today_meals()) == 0:
        risk += 10
    return min(100.0, risk)


def get_psychological_mode(state: AppState) -> str:
    risk = calculate_risk_score(state)
    if risk >= 55:
        return "low_momentum"
    if risk >= 30:
        return "returning"
    if state.streak >= 7:
        return "stable"
    return "normal"


def get_micro_goal(mode: str) -> str:
    goals = {
        "low_momentum": [
            "Apenas abra o app hoje. Estar aqui já é vencer.",
            "Beba um copo d'água agora.",
            "Escreva uma palavra sobre como você se sente."
        ],
        "returning": [
            "Registre apenas uma refeição hoje. Sem cobrança.",
            "Dê um passo pequeno. O passado é passado.",
            "Lembre-se por que você começou."
        ],
        "stable": [
            "Adicione uma cor nova no seu prato hoje.",
            "Faça 5 minutos de respiração consciente.",
            "Mantenha o ritmo. Consistência é poder."
        ],
        "normal": [
            "Registre uma refeição em tempo real.",
            "Faça uma refeição longe de telas.",
            "Beba 500ml de água na próxima hora."
        ]
    }
    return random.choice(goals.get(mode, goals["normal"]))


def get_companion_message(state: AppState, mode: str) -> str:
    messages = {
        "low_momentum": "Você está em uma fase mais difícil. Um registro já conta como progresso.",
        "returning": "Você voltou. Voltar é o comportamento dos fortes. O placar recomeça agora.",
        "stable": f"Sua sequência de {state.streak} dias está gerando mudanças reais. Excelente.",
        "normal": "Um dia comum bem feito é um dia ganho. Continue."
    }
    return messages.get(mode, messages["normal"])


def get_memory_line(state: AppState) -> str:
    if state.total_points >= 1000:
        return f"⭐ Você já acumulou {state.total_points} pontos. Cada um representa um passo que você não desistiu."
    if state.longest_streak >= 14:
        return f"✨ Você já alcançou {state.longest_streak} dias seguidos. Essa força ainda está em você."
    return ""
