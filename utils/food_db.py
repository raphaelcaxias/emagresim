from datetime import datetime
import hashlib

# Schema Obrigatório: calories, protein, carbs, fat, fiber (por 100g ou porção padrão)
FOOD_DB = {
    # --- PÃES E CEREAIS ---
    "pao_frances": {"name": "Pão Francês", "category": "cafe_manha", "calories": 300, "protein": 8.0, "carbs": 58.0, "fat": 3.0, "fiber": 2.5, "portion": "100g (1 unidade)"},
    "pao_integral": {"name": "Pão de Forma Integral", "category": "cafe_manha", "calories": 250, "protein": 9.0, "carbs": 45.0, "fat": 3.5, "fiber": 6.0, "portion": "100g (2 fatias)"},
    "pao_queijo": {"name": "Pão de Queijo", "category": "cafe_manha", "calories": 430, "protein": 11.0, "carbs": 50.0, "fat": 20.0, "fiber": 1.5, "portion": "100g (2 unidades)"},
    "tapioca": {"name": "Goma de Tapioca", "category": "cafe_manha", "calories": 340, "protein": 0.2, "carbs": 83.0, "fat": 0.1, "fiber": 0.5, "portion": "100g"},
    "cuscuz_milho": {"name": "Cuscuz de Milho", "category": "cafe_manha", "calories": 360, "protein": 6.5, "carbs": 75.0, "fat": 2.5, "fiber": 3.0, "portion": "100g"},
    "aveia_flocos": {"name": "Aveia em Flocos", "category": "cafe_manha", "calories": 390, "protein": 14.0, "carbs": 66.0, "fat": 8.5, "fiber": 9.0, "portion": "100g"},
    "granola": {"name": "Granola Tradicional", "category": "cafe_manha", "calories": 470, "protein": 10.0, "carbs": 64.0, "fat": 20.0, "fiber": 7.5, "portion": "100g"},
    "granola_fit": {"name": "Granola Fit (s/ açúcar)", "category": "cafe_manha", "calories": 380, "protein": 12.0, "carbs": 55.0, "fat": 15.0, "fiber": 8.0, "portion": "100g"},
    
    # --- LATICÍNIOS ---
    "leite_integral": {"name": "Leite Integral", "category": "cafe_manha", "calories": 60, "protein": 3.0, "carbs": 4.5, "fat": 3.3, "fiber": 0.0, "portion": "100ml"},
    "leite_desnatado": {"name": "Leite Desnatado", "category": "cafe_manha", "calories": 35, "protein": 3.4, "carbs": 5.0, "fat": 0.1, "fiber": 0.0, "portion": "100ml"},
    "iogurte_natural": {"name": "Iogurte Natural Integral", "category": "cafe_manha", "calories": 60, "protein": 3.5, "carbs": 4.7, "fat": 3.3, "fiber": 0.0, "portion": "100g"},
    "iogurte_grego": {"name": "Iogurte Grego", "category": "cafe_manha", "calories": 100, "protein": 9.0, "carbs": 4.0, "fat": 5.0, "fiber": 0.0, "portion": "100g"},
    "queijo_minas": {"name": "Queijo Minas Frescal", "category": "cafe_manha", "calories": 260, "protein": 18.0, "carbs": 3.0, "fat": 20.0, "fiber": 0.0, "portion": "100g"},
    "queijo_branco": {"name": "Queijo Branco (Prato)", "category": "cafe_manha", "calories": 320, "protein": 22.0, "carbs": 2.0, "fat": 26.0, "fiber": 0.0, "portion": "100g"},
    "requeijao": {"name": "Requeijão Cremoso", "category": "cafe_manha", "calories": 300, "protein": 8.0, "carbs": 4.0, "fat": 28.0, "fiber": 0.0, "portion": "100g"},
    "ricota": {"name": "Ricota", "category": "cafe_manha", "calories": 170, "protein": 11.0, "carbs": 3.0, "fat": 13.0, "fiber": 0.0, "portion": "100g"},
    "ovos": {"name": "Ovo de Galinha (Cozido)", "category": "cafe_manha", "calories": 145, "protein": 13.0, "carbs": 1.5, "fat": 9.5, "fiber": 0.0, "portion": "100g (2 un)"},

    # --- FRUTAS ---
    "banana_prata": {"name": "Banana Prata", "category": "frutas", "calories": 90, "protein": 1.5, "carbs": 23.0, "fat": 0.2, "fiber": 2.0, "portion": "100g"},
    "banana_nanica": {"name": "Banana Nanica", "category": "frutas", "calories": 85, "protein": 1.2, "carbs": 22.0, "fat": 0.1, "fiber": 1.8, "portion": "100g"},
    "maca": {"name": "Maçã com Casca", "category": "frutas", "calories": 55, "protein": 0.3, "carbs": 14.0, "fat": 0.2, "fiber": 2.5, "portion": "100g"},
    "laranja": {"name": "Laranja Pera", "category": "frutas", "calories": 45, "protein": 0.9, "carbs": 11.0, "fat": 0.1, "fiber": 2.0, "portion": "100g"},
    "mamao": {"name": "Mamão Papaia", "category": "frutas", "calories": 40, "protein": 0.5, "carbs": 10.0, "fat": 0.1, "fiber": 1.5, "portion": "100g"},
    "melancia": {"name": "Melancia", "category": "frutas", "calories": 30, "protein": 0.6, "carbs": 7.5, "fat": 0.1, "fiber": 0.5, "portion": "100g"},
    "morango": {"name": "Morango", "category": "frutas", "calories": 30, "protein": 0.9, "carbs": 7.0, "fat": 0.3, "fiber": 2.0, "portion": "100g"},
    "abacate": {"name": "Abacate", "category": "frutas", "calories": 95, "protein": 1.2, "carbs": 6.0, "fat": 8.5, "fiber": 2.5, "portion": "100g"},
    "acai_puro": {"name": "Açaí Puro (sem xarope)", "category": "frutas", "calories": 55, "protein": 1.0, "carbs": 6.0, "fat": 3.5, "fiber": 3.0, "portion": "100g"},

    # --- PROTEÍNAS (CARNES) ---
    "peito_frango": {"name": "Peito de Frango Grelhado", "category": "almoco_jantar", "calories": 160, "protein": 32.0, "carbs": 0.0, "fat": 3.5, "fiber": 0.0, "portion": "100g"},
    "coxa_frango": {"name": "Coxa de Frango Assada", "category": "almoco_jantar", "calories": 210, "protein": 26.0, "carbs": 0.0, "fat": 11.0, "fiber": 0.0, "portion": "100g"},
    "patinho": {"name": "Patinho Moído (Refogado)", "category": "almoco_jantar", "calories": 190, "protein": 28.0, "carbs": 0.0, "fat": 8.0, "fiber": 0.0, "portion": "100g"},
    "alcatra": {"name": "Alcatra Grelhada", "category": "almoco_jantar", "calories": 215, "protein": 28.0, "carbs": 0.0, "fat": 11.0, "fiber": 0.0, "portion": "100g"},
    "picanha": {"name": "Picanha Grelhada", "category": "almoco_jantar", "calories": 290, "protein": 25.0, "carbs": 0.0, "fat": 21.0, "fiber": 0.0, "portion": "100g"},
    "tilapia": {"name": "Tilápia Grelhada", "category": "almoco_jantar", "calories": 110, "protein": 23.0, "carbs": 0.0, "fat": 2.0, "fiber": 0.0, "portion": "100g"},
    "salmao": {"name": "Salmão Grelhado", "category": "almoco_jantar", "calories": 205, "protein": 22.0, "carbs": 0.0, "fat": 13.0, "fiber": 0.0, "portion": "100g"},
    "atum_lata": {"name": "Atum em Lata (em água)", "category": "almoco_jantar", "calories": 130, "protein": 28.0, "carbs": 0.0, "fat": 1.5, "fiber": 0.0, "portion": "100g"},
    "carne_seca": {"name": "Carne Seca (Charque)", "category": "almoco_jantar", "calories": 290, "protein": 36.0, "carbs": 0.0, "fat": 16.0, "fiber": 0.0, "portion": "100g"},
    "linguica": {"name": "Linguiça de Frango", "category": "almoco_jantar", "calories": 240, "protein": 15.0, "carbs": 2.0, "fat": 19.0, "fiber": 0.0, "portion": "100g"},

    # --- CARBOIDRATOS COMPLEXOS ---
    "arroz_branco": {"name": "Arroz Branco Cozido", "category": "almoco_jantar", "calories": 130, "protein": 2.5, "carbs": 28.0, "fat": 0.3, "fiber": 1.5, "portion": "100g"},
    "arroz_integral": {"name": "Arroz Integral Cozido", "category": "almoco_jantar", "calories": 125, "protein": 2.7, "carbs": 26.0, "fat": 1.0, "fiber": 2.5, "portion": "100g"},
    "feijao_preto": {"name": "Feijão Preto Cozido", "category": "almoco_jantar", "calories": 75, "protein": 4.5, "carbs": 14.0, "fat": 0.5, "fiber": 8.5, "portion": "100g"},
    "feijao_carioca": {"name": "Feijão Carioca Cozido", "category": "almoco_jantar", "calories": 78, "protein": 4.8, "carbs": 13.5, "fat": 0.6, "fiber": 8.0, "portion": "100g"},
    "lentilha": {"name": "Lentilha Cozida", "category": "almoco_jantar", "calories": 100, "protein": 7.5, "carbs": 17.0, "fat": 0.4, "fiber": 10.0, "portion": "100g"},
    "graos_bico": {"name": "Grão-de-Bico Cozido", "category": "almoco_jantar", "calories": 165, "protein": 9.0, "carbs": 27.0, "fat": 2.5, "fiber": 8.0, "portion": "100g"},
    "batata_inglesa": {"name": "Batata Inglesa Cozida", "category": "almoco_jantar", "calories": 75, "protein": 2.0, "carbs": 17.0, "fat": 0.1, "fiber": 1.5, "portion": "100g"},
    "batata_doce": {"name": "Batata Doce Cozida", "category": "almoco_jantar", "calories": 77, "protein": 0.6, "carbs": 18.0, "fat": 0.1, "fiber": 2.2, "portion": "100g"},
    "mandioca": {"name": "Mandioca (Aipim) Cozida", "category": "almoco_jantar", "calories": 125, "protein": 0.6, "carbs": 30.0, "fat": 0.3, "fiber": 1.8, "portion": "100g"},
    "macarrao": {"name": "Macarrão Cozido", "category": "almoco_jantar", "calories": 100, "protein": 3.5, "carbs": 20.0, "fat": 0.5, "fiber": 1.5, "portion": "100g"},

    # --- LEGUMES E VERDURAS ---
    "alface": {"name": "Alface Americana", "category": "almoco_jantar", "calories": 12, "protein": 1.0, "carbs": 2.0, "fat": 0.2, "fiber": 1.5, "portion": "100g"},
    "rucula": {"name": "Rúcula", "category": "almoco_jantar", "calories": 25, "protein": 2.6, "carbs": 3.7, "fat": 0.7, "fiber": 1.6, "portion": "100g"},
    "tomate": {"name": "Tomate", "category": "almoco_jantar", "calories": 18, "protein": 1.0, "carbs": 3.5, "fat": 0.2, "fiber": 1.2, "portion": "100g"},
    "cenoura": {"name": "Cenoura Crua", "category": "almoco_jantar", "calories": 35, "protein": 1.0, "carbs": 8.0, "fat": 0.2, "fiber": 3.0, "portion": "100g"},
    "brocolis": {"name": "Brócolis Cozido", "category": "almoco_jantar", "calories": 30, "protein": 2.5, "carbs": 6.0, "fat": 0.4, "fiber": 3.5, "portion": "100g"},
    "couve_flor": {"name": "Couve-Flor Cozida", "category": "almoco_jantar", "calories": 25, "protein": 2.0, "carbs": 4.0, "fat": 0.3, "fiber": 2.5, "portion": "100g"},
    "abobrinha": {"name": "Abobrinha Cozida", "category": "almoco_jantar", "calories": 15, "protein": 1.2, "carbs": 3.0, "fat": 0.2, "fiber": 1.0, "portion": "100g"},
    "berinjela": {"name": "Berinjela Cozida", "category": "almoco_jantar", "calories": 20, "protein": 1.0, "carbs": 4.5, "fat": 0.2, "fiber": 2.5, "portion": "100g"},
    "espinafre": {"name": "Espinafre Refogado", "category": "almoco_jantar", "calories": 25, "protein": 3.0, "carbs": 3.5, "fat": 0.5, "fiber": 2.5, "portion": "100g"},

    # --- LANCHES E FAST FOOD ---
    "x_salada": {"name": "X-Salada", "category": "lanche", "calories": 300, "protein": 18.0, "carbs": 35.0, "fat": 12.0, "fiber": 2.0, "portion": "1 sanduíche"},
    "x_burger": {"name": "X-Burger", "category": "lanche", "calories": 350, "protein": 20.0, "carbs": 38.0, "fat": 15.0, "fiber": 1.5, "portion": "1 sanduíche"},
    "x_bacon": {"name": "X-Bacon", "category": "lanche", "calories": 450, "protein": 24.0, "carbs": 40.0, "fat": 22.0, "fiber": 1.5, "portion": "1 sanduíche"},
    "pizza_mussarela": {"name": "Pizza de Mussarela", "category": "lanche", "calories": 270, "protein": 12.0, "carbs": 33.0, "fat": 10.0, "fiber": 2.0, "portion": "1 fatia"},
    "pastel_carne": {"name": "Pastel de Carne", "category": "lanche", "calories": 350, "protein": 12.0, "carbs": 35.0, "fat": 20.0, "fiber": 1.0, "portion": "1 unidade"},
    "coxinha": {"name": "Coxinha de Frango", "category": "lanche", "calories": 280, "protein": 10.0, "carbs": 32.0, "fat": 14.0, "fiber": 1.0, "portion": "1 unidade"},
    "acai_xarope": {"name": "Açaí com Xarope e Granola", "category": "lanche", "calories": 250, "protein": 3.0, "carbs": 45.0, "fat": 8.0, "fiber": 4.0, "portion": "300ml"},
    "barra_proteica": {"name": "Barra de Proteína", "category": "lanche", "calories": 200, "protein": 20.0, "carbs": 15.0, "fat": 6.0, "fiber": 3.0, "portion": "40g"},
    "mix_castanhas": {"name": "Mix de Castanhas", "category": "lanche", "calories": 600, "protein": 18.0, "carbs": 20.0, "fat": 55.0, "fiber": 6.0, "portion": "100g"},
    "chocolate_70": {"name": "Chocolate 70% Cacau", "category": "lanche", "calories": 600, "protein": 9.0, "carbs": 45.0, "fat": 45.0, "fiber": 10.0, "portion": "100g"},
    "chocolate_leite": {"name": "Chocolate ao Leite", "category": "lanche", "calories": 540, "protein": 8.0, "carbs": 59.0, "fat": 30.0, "fiber": 3.0, "portion": "100g"},

    # --- BEBIDAS ---
    "agua_coco": {"name": "Água de Coco", "category": "bebidas", "calories": 20, "protein": 0.2, "carbs": 4.5, "fat": 0.0, "fiber": 0.0, "portion": "100ml"},
    "suco_laranja": {"name": "Suco de Laranja Natural", "category": "bebidas", "calories": 45, "protein": 0.7, "carbs": 10.0, "fat": 0.1, "fiber": 0.2, "portion": "100ml"},
    "cafe_sem_acucar": {"name": "Café sem Açúcar", "category": "bebidas", "calories": 2, "protein": 0.1, "carbs": 0.0, "fat": 0.0, "fiber": 0.0, "portion": "100ml"},
    "refri_zero": {"name": "Refrigerante Zero", "category": "bebidas", "calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "fiber": 0.0, "portion": "100ml"},
    "cerveja_lata": {"name": "Cerveja Pilsen", "category": "bebidas", "calories": 42, "protein": 0.4, "carbs": 3.5, "fat": 0.0, "fiber": 0.0, "portion": "100ml"},
}

COMBOS = {
    "pf_basico": {"name": "PF Básico", "items": ["arroz_branco", "feijao_carioca", "peito_frango", "alface", "tomate"]},
    "cafe_fit": {"name": "Café da Manhã Fit", "items": ["ovos", "pao_integral", "cafe_sem_acucar", "maca"]},
    "pos_treino": {"name": "Pós-Treino", "items": ["banana_prata", "aveia_flocos", "leite_desnatado"]}
}

DICAS = [
    "💧 Beba 35ml de água para cada kg do seu peso corporal.",
    "🥗 Comece o almoço e jantar pela salada para aumentar a saciedade.",
    " Tente manter horários regulares para as refeições.",
    "🛑 Evite calorias líquidas (sucos com açúcar, refrigerantes).",
    "🍳 Prefira preparações grelhadas, assadas ou cozidas.",
    "🛒 Nunca vá ao supermercado com fome.",
    " Pese-se apenas 1 vez por semana, sempre nas mesmas condições."
]

def buscar_alimento(termo: str) -> list:
    termo = termo.lower().strip()
    if not termo: return []
    return [
        {"key": k, "name": v["name"], "calories": v["calories"], "category": v.get("category", "geral")}
        for k, v in FOOD_DB.items() if termo in v["name"].lower()
    ][:10]

def get_dica_do_dia() -> str:
    hoje = datetime.now().strftime("%Y-%m-%d")
    hash_dia = int(hashlib.md5(hoje.encode()).hexdigest(), 16)
    return DICAS[hash_dia % len(DICAS)]
