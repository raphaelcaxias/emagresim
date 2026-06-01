# Banco de alimentos brasileiro (TACO simplificado)
FOOD_DB = {
    "arroz": {"name": "Arroz Branco", "portion": "1 concha (150g)", "cal": 190, "p": 3.8, "c": 42, "g": 0.3},
    "feijao": {"name": "Feijão Preto", "portion": "1 concha (100g)", "cal": 77, "p": 4.5, "c": 14, "g": 0.5},
    "frango": {"name": "Peito Frango Grelhado", "portion": "1 filé (120g)", "cal": 198, "p": 36, "c": 0, "g": 4.2},
    "pao": {"name": "Pão Francês", "portion": "1 unidade", "cal": 150, "p": 4.5, "c": 28, "g": 1.8},
    "banana": {"name": "Banana Prata", "portion": "1 média", "cal": 89, "p": 1.1, "c": 23, "g": 0.3},
    "ovo": {"name": "Ovo Cozido", "portion": "1 unidade", "cal": 78, "p": 6.3, "c": 0.6, "g": 5.3},
    "cafe": {"name": "Café c/ Leite", "portion": "1 xícara", "cal": 65, "p": 2.1, "c": 10, "g": 1.8},
    "macarrao": {"name": "Macarrão Cozido", "portion": "1 prato", "cal": 260, "p": 9, "c": 52, "g": 1.2},
    "salada": {"name": "Salada Mista", "portion": "1 prato", "cal": 25, "p": 1.5, "c": 5, "g": 0.2}
}

COMBOS = {
    "pf": {"name": "PF (Prato Feito)", "items": ["arroz", "feijao", "frango", "salada"]},
    "cafe": {"name": "Café da Manhã", "items": ["pao", "cafe", "banana"]},
    "lanche": {"name": "Lanche Tarde", "items": ["banana", "ovo"]}
}
