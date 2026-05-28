# core/services.py
from datetime import datetime, date
from typing import Optional, Tuple
import random

from utils.helpers import calcular_avatar as _calcular_avatar
from utils.constants import CORES

def calcular_meta_automatica(peso: float, altura: float, objetivo: str = "emagrecer") -> float:
    """Calcula meta mensal saudável baseada no IMC"""
    imc = peso / (altura ** 2) if altura > 0 else 0
    
    if objetivo == "emagrecer":
        if imc > 30:
            return 4.0  # obesidade: até 4kg/mês
        elif imc > 25:
            return 2.0  # sobrepeso: até 2kg/mês
        else:
            return 1.0  # peso normal: até 1kg/mês
    elif objetivo == "ganhar_massa":
        return 1.0
    else:
        return 0.0

def calcular_desafio_semanal() -> dict:
    """Retorna desafio aleatório da semana"""
    desafios = [
        {"nome": "💧 Hidratação", "descricao": "Beba 2L de água por 5 dias", "xp": 100},
        {"nome": "🥚 Proteína", "descricao": "Registre proteína em todas as refeições", "xp": 150},
        {"nome": "🚶 Movimento", "descricao": "Caminhe 30min por dia durante 4 dias", "xp": 120},
        {"nome": "😴 Sono", "descricao": "Durma 7h+ por 5 dias", "xp": 100},
        {"nome": "🍎 Fruta", "descricao": "Coma uma fruta em todas as refeições", "xp": 80},
    ]
    return random.choice(desafios)

def calcular_dica_dia(humor: Optional[str] = None) -> str:
    """Retorna dica baseada no humor ou aleatória"""
    dicas = [
        "Mastigue devagar: a saciedade leva cerca de 20 minutos.",
        "Beba um copo de água antes de cada refeição.",
        "Durma 7-8h por noite para regular os hormônios.",
        "Inclua proteína em todas as refeições para mais saciedade.",
        "Não pule o café da manhã – ele ativa seu metabolismo.",
        "Faça pequenas caminhadas após as refeições.",
    ]
    return random.choice(dicas)

def calcular_avatar(percentual: float) -> Tuple[str, str]:
    return _calcular_avatar(percentual)
