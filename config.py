# config.py
import streamlit as st

# Feature flags (liga/desliga funcionalidades)
FEATURES = {
    "enable_avatar": True,
    "enable_family_ranking": True,
    "enable_challenges": True,
    "enable_meal_reminder": True,
    "enable_mood_support": True,
    "enable_recipe_suggestion": True,
}

# Constantes
DIETAS = {
    "mediterranea": {"nome": "Mediterrânea", "calorias": 1800},
    "low_carb": {"nome": "Low Carb", "calorias": 1700},
    "dash": {"nome": "DASH", "calorias": 1900},
}

DESAFIOS = [
    {"nome": "?? Hidratação", "descricao": "Beba 2L de água por 5 dias", "meta": 5, "xp": 100},
    {"nome": "?? Proteína", "descricao": "Registre proteína em todas as refeições", "meta": 3, "xp": 150},
    {"nome": "?? Movimento", "descricao": "Caminhe 30min por dia durante 4 dias", "meta": 4, "xp": 120},
]

RECEITAS = [
    {"nome": "Omelete de claras com espinafre", "calorias": 250},
    {"nome": "Salada de quinoa com frango", "calorias": 380},
    {"nome": "Smoothie de morango com whey", "calorias": 200},
]

CONQUISTAS = [
    {"key": "first_step", "nome": "?? Primeiro passo", "desc": "Primeiro check-in"},
    {"key": "week_warrior", "nome": "?? 7 dias seguidos", "desc": "7 dias de consistência"},
    {"key": "hydrated", "nome": "?? Hidratação elite", "desc": "30 dias de água"},
    {"key": "weight_5kg", "nome": "?? -5kg", "desc": "Perdeu 5kg"},
]