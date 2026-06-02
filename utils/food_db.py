# Banco completo de alimentos brasileiros com macros

FOOD_DB = {
    # ========== CAFÉ DA MANHÃ ==========
    "pao_frances": {"name": "Pão Francês", "category": "cafe_manha", "cal": 135, "p": 4.5, "c": 26, "g": 1.5, "portion": "1 unidade (50g)"},
    "pao_integral": {"name": "Pão Integral", "category": "cafe_manha", "cal": 120, "p": 5.0, "c": 22, "g": 2.0, "portion": "1 fatia (40g)"},
    "pao_de_queijo": {"name": "Pão de Queijo", "category": "cafe_manha", "cal": 216, "p": 5.5, "c": 25, "g": 10, "portion": "1 unidade (50g)"},
    "bolo_simples": {"name": "Bolo Simples", "category": "cafe_manha", "cal": 280, "p": 4.0, "c": 45, "g": 9, "portion": "1 fatia (80g)"},
    "bolo_fuba": {"name": "Bolo de Fubá", "category": "cafe_manha", "cal": 290, "p": 5.0, "c": 48, "g": 8, "portion": "1 fatia (80g)"},
    "sonho": {"name": "Sonho", "category": "cafe_manha", "cal": 320, "p": 6.0, "c": 42, "g": 14, "portion": "1 unidade (90g)"},
    "croissant": {"name": "Croissant", "category": "cafe_manha", "cal": 406, "p": 8.2, "c": 45.8, "g": 21, "portion": "1 unidade (90g)"},
    
    # Laticínios
    "leite_integral": {"name": "Leite Integral", "category": "cafe_manha", "cal": 61, "p": 3.2, "c": 4.8, "g": 3.3, "portion": "100ml"},
    "leite_desnatado": {"name": "Leite Desnatado", "category": "cafe_manha", "cal": 34, "p": 3.4, "c": 5.0, "g": 0.1, "portion": "100ml"},
    "leite_semilactose": {"name": "Leite Sem Lactose", "category": "cafe_manha", "cal": 58, "p": 3.3, "c": 4.9, "g": 3.0, "portion": "100ml"},
    "iogurte_natural": {"name": "Iogurte Natural", "category": "cafe_manha", "cal": 61, "p": 3.5, "c": 4.7, "g": 3.3, "portion": "100g"},
    "iogurte_desnatado": {"name": "Iogurte Desnatado", "category": "cafe_manha", "cal": 50, "p": 3.8, "c": 6.0, "g": 0.5, "portion": "100g"},
    "queijo_minas": {"name": "Queijo Minas Frescal", "category": "cafe_manha", "cal": 262, "p": 18.0, "c": 2.5, "g": 20, "portion": "100g"},
    "queijo_prato": {"name": "Queijo Prato", "category": "cafe_manha", "cal": 356, "p": 25.0, "c": 1.5, "g": 28, "portion": "100g"},
    "queijo_mussarela": {"name": "Queijo Mussarela", "category": "cafe_manha", "cal": 280, "p": 28, "c": 3.1, "g": 17, "portion": "100g"},
    "requeijao": {"name": "Requeijão Cremoso", "category": "cafe_manha", "cal": 316, "p": 7.0, "c": 5.0, "g": 29, "portion": "100g"},
    "manteiga": {"name": "Manteiga", "category": "cafe_manha", "cal": 717, "p": 0.9, "c": 0.1, "g": 81, "portion": "1 colher sopa (10g)"},
    "margarina": {"name": "Margarina", "category": "cafe_manha", "cal": 717, "p": 0.2, "c": 0.5, "g": 81, "portion": "1 colher sopa (10g)"},
    "geleia_mocot": {"name": "Geleia de Mocotó", "category": "cafe_manha", "cal": 260, "p": 0, "c": 65, "g": 0, "portion": "1 colher sopa (20g)"},
    "doce_leite": {"name": "Doce de Leite", "category": "cafe_manha", "cal": 320, "p": 6.0, "c": 55, "g": 9, "portion": "1 colher sopa (20g)"},
    
    # Bebidas quentes
    "cafe_preto": {"name": "Café Preto", "category": "cafe_manha", "cal": 2, "p": 0.3, "c": 0, "g": 0, "portion": "100ml"},
    "cafe_com_leite": {"name": "Café com Leite", "category": "cafe_manha", "cal": 46, "p": 2.4, "c": 4.7, "g": 1.8, "portion": "100ml"},
    "cappuccino": {"name": "Cappuccino", "category": "cafe_manha", "cal": 65, "p": 3.3, "c": 8.0, "g": 2.3, "portion": "100ml"},
    "cha_preto": {"name": "Chá Preto", "category": "cafe_manha", "cal": 1, "p": 0, "c": 0.3, "g": 0, "portion": "100ml"},
    "cha_verde": {"name": "Chá Verde", "category": "cafe_manha", "cal": 1, "p": 0, "c": 0, "g": 0, "portion": "100ml"},
    "cha_mate": {"name": "Chá Mate", "category": "cafe_manha", "cal": 1, "p": 0, "c": 0.3, "g": 0, "portion": "100ml"},
    "cha_camomila": {"name": "Chá de Camomila", "category": "cafe_manha", "cal": 1, "p": 0, "c": 0.2, "g": 0, "portion": "100ml"},
    "achocolatado": {"name": "Achocolatado", "category": "cafe_manha", "cal": 380, "p": 4.0, "c": 78, "g": 6, "portion": "100g"},
    "nescau": {"name": "Nescau", "category": "cafe_manha", "cal": 380, "p": 4.0, "c": 78, "g": 6, "portion": "1 colher sopa (15g)"},
    "toddy": {"name": "Toddy", "category": "cafe_manha", "cal": 376, "p": 4.5, "c": 76, "g": 5.5, "portion": "1 colher sopa (15g)"},
    
    # Frutas
    "banana_prata": {"name": "Banana Prata", "category": "cafe_manha", "cal": 89, "p": 1.1, "c": 23, "g": 0.3, "portion": "1 unidade (80g)"},
    "banana_nanica": {"name": "Banana Nanica", "category": "cafe_manha", "cal": 88, "p": 1.0, "c": 23, "g": 0.2, "portion": "1 unidade (90g)"},
    "banana_maca": {"name": "Banana Maçã", "category": "cafe_manha", "cal": 86, "p": 1.2, "c": 22, "g": 0.3, "portion": "1 unidade (70g)"},
    "maca": {"name": "Maçã", "category": "cafe_manha", "cal": 52, "p": 0.3, "c": 14, "g": 0.2, "portion": "1 unidade (130g)"},
    "maca_fuji": {"name": "Maçã Fuji", "category": "cafe_manha", "cal": 54, "p": 0.3, "c": 14, "g": 0.2, "portion": "1 unidade (140g)"},
    "maca_gala": {"name": "Maçã Gala", "category": "cafe_manha", "cal": 52, "p": 0.3, "c": 14, "g": 0.2, "portion": "1 unidade (130g)"},
    "pera": {"name": "Pera", "category": "cafe_manha", "cal": 57, "p": 0.4, "c": 15, "g": 0.1, "portion": "1 unidade (140g)"},
    "laranja": {"name": "Laranja", "category": "cafe_manha", "cal": 47, "p": 0.9, "c": 12, "g": 0.1, "portion": "1 unidade (130g)"},
    "laranja_pera": {"name": "Laranja Pera", "category": "cafe_manha", "cal": 48, "p": 0.9, "c": 12, "g": 0.1, "portion": "1 unidade (135g)"},
    "tangerina": {"name": "Tangerina", "category": "cafe_manha", "cal": 53, "p": 0.8, "c": 13, "g": 0.3, "portion": "1 unidade (100g)"},
    "mamao": {"name": "Mamão Formosa", "category": "cafe_manha", "cal": 43, "p": 0.5, "c": 11, "g": 0.3, "portion": "1 fatia (100g)"},
    "mamao_papaia": {"name": "Mamão Papaia", "category": "cafe_manha", "cal": 45, "p": 0.5, "c": 11, "g": 0.3, "portion": "1 fatia (90g)"},
    "melancia": {"name": "Melancia", "category": "cafe_manha", "cal": 30, "p": 0.6, "c": 8, "g": 0.2, "portion": "1 fatia (100g)"},
    "melao": {"name": "Melão", "category": "cafe_manha", "cal": 34, "p": 0.8, "c": 8, "g": 0.2, "portion": "1 fatia (100g)"},
    "manga": {"name": "Manga", "category": "cafe_manha", "cal": 60, "p": 0.8, "c": 15, "g": 0.4, "portion": "1 fatia (100g)"},
    "abacaxi": {"name": "Abacaxi", "category": "cafe_manha", "cal": 50, "p": 0.5, "c": 13, "g": 0.1, "portion": "1 fatia (100g)"},
    "uva": {"name": "Uva", "category": "cafe_manha", "cal": 67, "p": 0.6, "c": 17, "g": 0.4, "portion": "1 cacho pequeno (100g)"},
    "morango": {"name": "Morango", "category": "cafe_manha", "cal": 32, "p": 0.7, "c": 8, "g": 0.3, "portion": "100g"},
    "kiwi": {"name": "Kiwi", "category": "cafe_manha", "cal": 61, "p": 1.1, "c": 15, "g": 0.5, "portion": "1 unidade (75g)"},
    "abacate": {"name": "Abacate", "category": "cafe_manha", "cal": 160, "p": 2.0, "c": 9, "g": 15, "portion": "1/2 unidade (100g)"},
    "coco": {"name": "Coco", "category": "cafe_manha", "cal": 354, "p": 3.3, "c": 15, "g": 33, "portion": "100g"},
    
    # Ovos
    "ovo_cozido": {"name": "Ovo Cozido", "category": "cafe_manha", "cal": 155, "p": 13, "c": 1.1, "g": 11, "portion": "1 unidade (100g)"},
    "ovo_frito": {"name": "Ovo Frito", "category": "cafe_manha", "cal": 196, "p": 13, "c": 1.1, "g": 15, "portion": "1 unidade (100g)"},
    "ovo_mexido": {"name": "Ovo Mexido", "category": "cafe_manha", "cal": 149, "p": 10, "c": 1.6, "g": 11, "portion": "100g"},
    "omelete": {"name": "Omelete", "category": "cafe_manha", "cal": 154, "p": 11, "c": 1.5, "g": 11, "portion": "1 unidade (100g)"},
    
    # ========== ALMOÇO/JANTAR - PROTEÍNAS ==========
    # Carnes
    "frango_grelhado": {"name": "Peito de Frango Grelhado", "category": "almoco_jantar", "cal": 165, "p": 31, "c": 0, "g": 3.6, "portion": "100g"},
    "frango_assado": {"name": "Frango Assado", "category": "almoco_jantar", "cal": 190, "p": 27, "c": 0, "g": 8, "portion": "100g"},
    "frango_coelho": {"name": "Frango à Passarinho", "category": "almoco_jantar", "cal": 240, "p": 25, "c": 0, "g": 15, "portion": "100g"},
    "frango_empanado": {"name": "Frango Empanado", "category": "almoco_jantar", "cal": 280, "p": 20, "c": 15, "g": 16, "portion": "100g"},
    "frango_xadrez": {"name": "Frango Xadrez", "category": "almoco_jantar", "cal": 220, "p": 22, "c": 12, "g": 10, "portion": "100g"},
    "frango_estrogonofe": {"name": "Estrogonofe de Frango", "category": "almoco_jantar", "cal": 240, "p": 18, "c": 8, "g": 16, "portion": "100g"},
    
    "carne_bovina_magra": {"name": "Carne Bovina Magra Grelhada", "category": "almoco_jantar", "cal": 190, "p": 26, "c": 0, "g": 9, "portion": "100g"},
    "carne_bovina_gorda": {"name": "Carne Bovina (Picanha)", "category": "almoco_jantar", "cal": 290, "p": 24, "c": 0, "g": 21, "portion": "100g"},
    "bife_milanesa": {"name": "Bife à Milanesa", "category": "almoco_jantar", "cal": 290, "p": 22, "c": 12, "g": 18, "portion": "100g"},
    "bife_parmegiana": {"name": "Bife à Parmegiana", "category": "almoco_jantar", "cal": 320, "p": 24, "c": 10, "g": 21, "portion": "100g"},
    "carne_moida": {"name": "Carne Moída Refogada", "category": "almoco_jantar", "cal": 250, "p": 20, "c": 5, "g": 17, "portion": "100g"},
    "carne_seca": {"name": "Carne Seca", "category": "almoco_jantar", "cal": 290, "p": 35, "c": 0, "g": 16, "portion": "100g"},
    "linguica": {"name": "Linguiça", "category": "almoco_jantar", "cal": 310, "p": 14, "c": 2, "g": 27, "portion": "100g"},
    "salsicha": {"name": "Salsicha", "category": "almoco_jantar", "cal": 280, "p": 10, "c": 4, "g": 25, "portion": "1 unidade (80g)"},
    
    "peixe_grelhado": {"name": "Peixe Grelhado", "category": "almoco_jantar", "cal": 120, "p": 24, "c": 0, "g": 2.5, "portion": "100g"},
    "peixe_frito": {"name": "Peixe Frito", "category": "almoco_jantar", "cal": 230, "p": 20, "c": 8, "g": 13, "portion": "100g"},
    "peixe_assado": {"name": "Peixe Assado", "category": "almoco_jantar", "cal": 140, "p": 25, "c": 0, "g": 4, "portion": "100g"},
    "peixe_empanado": {"name": "Peixe Empanado", "category": "almoco_jantar", "cal": 250, "p": 18, "c": 15, "g": 14, "portion": "100g"},
    "tilapia": {"name": "Tilápia Grelhada", "category": "almoco_jantar", "cal": 128, "p": 26, "c": 0, "g": 2.7, "portion": "100g"},
    "salmão": {"name": "Salmão Grelhado", "category": "almoco_jantar", "cal": 208, "p": 20, "c": 0, "g": 13, "portion": "100g"},
    "atum": {"name": "Atum em Lata", "category": "almoco_jantar", "cal": 132, "p": 28, "c": 0, "g": 1.3, "portion": "100g"},
    "sardinha": {"name": "Sardinha em Lata", "category": "almoco_jantar", "cal": 208, "p": 25, "c": 0, "g": 11, "portion": "100g"},
    "bacalhau": {"name": "Bacalhau", "category": "almoco_jantar", "cal": 105, "p": 23, "c": 0, "g": 0.9, "portion": "100g"},
    
    "camarao": {"name": "Camarão", "category": "almoco_jantar", "cal": 99, "p": 24, "c": 0.2, "g": 0.3, "portion": "100g"},
    "camarao_empanado": {"name": "Camarão Empanado", "category": "almoco_jantar", "cal": 240, "p": 18, "c": 15, "g": 13, "portion": "100g"},
    "camarao_alho_oleo": {"name": "Camarão ao Alho e Óleo", "category": "almoco_jantar", "cal": 180, "p": 22, "c": 5, "g": 8, "portion": "100g"},
    
    # Grãos e Carboidratos
    "arroz_branco": {"name": "Arroz Branco", "category": "almoco_jantar", "cal": 130, "p": 2.5, "c": 28, "g": 0.3, "portion": "100g"},
    "arroz_integral": {"name": "Arroz Integral", "category": "almoco_jantar", "cal": 124, "p": 2.6, "c": 26, "g": 1.0, "portion": "100g"},
    "arroz_7graos": {"name": "Arroz 7 Grãos", "category": "almoco_jantar", "cal": 135, "p": 3.5, "c": 27, "g": 1.5, "portion": "100g"},
    "arroz_carreteiro": {"name": "Arroz Carreteiro", "category": "almoco_jantar", "cal": 180, "p": 6, "c": 28, "g": 5, "portion": "100g"},
    "arroz_a_grega": {"name": "Arroz à Grega", "category": "almoco_jantar", "cal": 160, "p": 4, "c": 30, "g": 3, "portion": "100g"},
    
    "feijao_preto": {"name": "Feijão Preto", "category": "almoco_jantar", "cal": 77, "p": 4.5, "c": 14, "g": 0.5, "portion": "100g"},
    "feijao_carioca": {"name": "Feijão Carioca", "category": "almoco_jantar", "cal": 76, "p": 4.8, "c": 13, "g": 0.5, "portion": "100g"},
    "feijao_branco": {"name": "Feijão Branco", "category": "almoco_jantar", "cal": 93, "p": 6, "c": 17, "g": 0.4, "portion": "100g"},
    "feijao_fradinho": {"name": "Feijão Fradinho", "category": "almoco_jantar", "cal": 116, "p": 7.5, "c": 20, "g": 0.6, "portion": "100g"},
    "feijao_tropeiro": {"name": "Feijão Tropeiro", "category": "almoco_jantar", "cal": 180, "p": 8, "c": 18, "g": 9, "portion": "100g"},
    
    "macarrao_espaguete": {"name": "Macarrão Espaguete", "category": "almoco_jantar", "cal": 158, "p": 5.8, "c": 31, "g": 0.9, "portion": "100g"},
    "macarrao_parafuso": {"name": "Macarrão Parafuso", "category": "almoco_jantar", "cal": 160, "p": 5.5, "c": 32, "g": 1.0, "portion": "100g"},
    "macarrao_integral": {"name": "Macarrão Integral", "category": "almoco_jantar", "cal": 140, "p": 6.5, "c": 28, "g": 1.5, "portion": "100g"},
    "lasanha": {"name": "Lasanha", "category": "almoco_jantar", "cal": 220, "p": 10, "c": 25, "g": 9, "portion": "100g"},
    "nhoque": {"name": "Nhoque", "category": "almoco_jantar", "cal": 140, "p": 4, "c": 28, "g": 1.5, "portion": "100g"},
    "ravioli": {"name": "Ravióli", "category": "almoco_jantar", "cal": 180, "p": 7, "c": 28, "g": 5, "portion": "100g"},
    
    "batata_inglesa": {"name": "Batata Inglesa", "category": "almoco_jantar", "cal": 77, "p": 2, "c": 17, "g": 0.1, "portion": "100g"},
    "batata_frita": {"name": "Batata Frita", "category": "almoco_jantar", "cal": 312, "p": 3.4, "c": 41, "g": 15, "portion": "100g"},
    "batata_assada": {"name": "Batata Assada", "category": "almoco_jantar", "cal": 93, "p": 2.5, "c": 21, "g": 0.1, "portion": "100g"},
    "batata_sauté": {"name": "Batata Sauté", "category": "almoco_jantar", "cal": 120, "p": 2, "c": 18, "g": 5, "portion": "100g"},
    "batata_doce": {"name": "Batata Doce", "category": "almoco_jantar", "cal": 86, "p": 1.6, "c": 20, "g": 0.1, "portion": "100g"},
    "batata_doce_assada": {"name": "Batata Doce Assada", "category": "almoco_jantar", "cal": 90, "p": 1.8, "c": 21, "g": 0.1, "portion": "100g"},
    
    "mandioca": {"name": "Mandioca Cozida", "category": "almoco_jantar", "cal": 112, "p": 1.4, "c": 27, "g": 0.3, "portion": "100g"},
    "mandioca_frita": {"name": "Mandioca Frita", "category": "almoco_jantar", "cal": 280, "p": 2, "c": 38, "g": 14, "portion": "100g"},
    "inhame": {"name": "Inhame", "category": "almoco_jantar", "cal": 112, "p": 1.5, "c": 27, "g": 0.2, "portion": "100g"},
    "cará": {"name": "Cará", "category": "almoco_jantar", "cal": 118, "p": 1.8, "c": 28, "g": 0.2, "portion": "100g"},
    
    "farofa": {"name": "Farofa", "category": "almoco_jantar", "cal": 466, "p": 4, "c": 75, "g": 16, "portion": "100g"},
    "farofa_bacon": {"name": "Farofa com Bacon", "category": "almoco_jantar", "cal": 520, "p": 8, "c": 68, "g": 24, "portion": "100g"},
    "angu": {"name": "Angu", "category": "almoco_jantar", "cal": 95, "p": 2.2, "c": 20, "g": 0.8, "portion": "100g"},
    "polenta": {"name": "Polenta", "category": "almoco_jantar", "cal": 100, "p": 2.5, "c": 21, "g": 0.5, "portion": "100g"},
    "polenta_frita": {"name": "Polenta Frita", "category": "almoco_jantar", "cal": 180, "p": 3, "c": 24, "g": 8, "portion": "100g"},
    
    # Saladas e Legumes
    "alface": {"name": "Alface", "category": "almoco_jantar", "cal": 15, "p": 1.4, "c": 2.9, "g": 0.2, "portion": "100g"},
    "rúcula": {"name": "Rúcula", "category": "almoco_jantar", "cal": 25, "p": 2.6, "c": 3.7, "g": 0.7, "portion": "100g"},
    "agriao": {"name": "Agrião", "category": "almoco_jantar", "cal": 11, "p": 2.3, "c": 1.3, "g": 0.1, "portion": "100g"},
    "espinafre": {"name": "Espinafre", "category": "almoco_jantar", "cal": 23, "p": 2.9, "c": 3.6, "g": 0.4, "portion": "100g"},
    "couve": {"name": "Couve", "category": "almoco_jantar", "cal": 28, "p": 2.5, "c": 5.6, "g": 0.4, "portion": "100g"},
    "repolho": {"name": "Repolho", "category": "almoco_jantar", "cal": 25, "p": 1.3, "c": 5.8, "g": 0.1, "portion": "100g"},
    "tomate": {"name": "Tomate", "category": "almoco_jantar", "cal": 18, "p": 0.9, "c": 3.9, "g": 0.2, "portion": "100g"},
    "pepino": {"name": "Pepino", "category": "almoco_jantar", "cal": 15, "p": 0.7, "c": 3.6, "g": 0.1, "portion": "100g"},
    "cenoura": {"name": "Cenoura", "category": "almoco_jantar", "cal": 41, "p": 0.9, "c": 10, "g": 0.2, "portion": "100g"},
    "beterraba": {"name": "Beterraba", "category": "almoco_jantar", "cal": 43, "p": 1.6, "c": 10, "g": 0.2, "portion": "100g"},
    "chuchu": {"name": "Chuchu", "category": "almoco_jantar", "cal": 19, "p": 0.8, "c": 4.5, "g": 0.1, "portion": "100g"},
    "abobrinha": {"name": "Abobrinha", "category": "almoco_jantar", "cal": 17, "p": 1.2, "c": 3.1, "g": 0.3, "portion": "100g"},
    "berinjela": {"name": "Berinjela", "category": "almoco_jantar", "cal": 25, "p": 1, "c": 5.9, "g": 0.2, "portion": "100g"},
    "abobora": {"name": "Abóbora", "category": "almoco_jantar", "cal": 26, "p": 1, "c": 6.5, "g": 0.1, "portion": "100g"},
    "brócolis": {"name": "Brócolis", "category": "almoco_jantar", "cal": 34, "p": 2.8, "c": 7, "g": 0.4, "portion": "100g"},
    "couve_flor": {"name": "Couve-Flor", "category": "almoco_jantar", "cal": 25, "p": 1.9, "c": 5, "g": 0.3, "portion": "100g"},
    "vagem": {"name": "Vagem", "category": "almoco_jantar", "cal": 31, "p": 1.8, "c": 7, "g": 0.2, "portion": "100g"},
    "ervilha": {"name": "Ervilha", "category": "almoco_jantar", "cal": 81, "p": 5.4, "c": 14, "g": 0.4, "portion": "100g"},
    "milho": {"name": "Milho Verde", "category": "almoco_jantar", "cal": 86, "p": 3.2, "c": 19, "g": 1.2, "portion": "100g"},
    "palmito": {"name": "Palmito", "category": "almoco_jantar", "cal": 28, "p": 2.5, "c": 5.5, "g": 0.2, "portion": "100g"},
    
    # Bebidas
    "agua": {"name": "Água", "category": "almoco_jantar", "cal": 0, "p": 0, "c": 0, "g": 0, "portion": "200ml"},
    "agua_com_gas": {"name": "Água com Gás", "category": "almoco_jantar", "cal": 0, "p": 0, "c": 0, "g": 0, "portion": "200ml"},
    "suco_laranja": {"name": "Suco de Laranja", "category": "almoco_jantar", "cal": 45, "p": 0.7, "c": 10, "g": 0.2, "portion": "200ml"},
    "suco_limao": {"name": "Suco de Limão", "category": "almoco_jantar", "cal": 22, "p": 0.4, "c": 7, "g": 0.1, "portion": "200ml"},
    "suco_maracuja": {"name": "Suco de Maracujá", "category": "almoco_jantar", "cal": 52, "p": 1, "c": 12, "g": 0.3, "portion": "200ml"},
    "suco_abacaxi": {"name": "Suco de Abacaxi", "category": "almoco_jantar", "cal": 40, "p": 0.4, "c": 10, "g": 0.1, "portion": "200ml"},
    "suco_manga": {"name": "Suco de Manga", "category": "almoco_jantar", "cal": 60, "p": 0.4, "c": 15, "g": 0.2, "portion": "200ml"},
    "suco_uva": {"name": "Suco de Uva", "category": "almoco_jantar", "cal": 60, "p": 0.4, "c": 15, "g": 0.1, "portion": "200ml"},
    "refrigerante_coca": {"name": "Refrigerante Coca-Cola", "category": "almoco_jantar", "cal": 37, "p": 0, "c": 10, "g": 0, "portion": "200ml"},
    "refrigerante_guarana": {"name": "Refrigerante Guaraná", "category": "almoco_jantar", "cal": 35, "p": 0, "c": 9, "g": 0, "portion": "200ml"},
    "refrigerante_sprite": {"name": "Refrigerante Sprite", "category": "almoco_jantar", "cal": 38, "p": 0, "c": 10, "g": 0, "portion": "200ml"},
    "refri_zero": {"name": "Refrigerante Zero", "category": "almoco_jantar", "cal": 0, "p": 0, "c": 0, "g": 0, "portion": "200ml"},
    "cerveja": {"name": "Cerveja", "category": "almoco_jantar", "cal": 43, "p": 0.5, "c": 3.6, "g": 0, "portion": "200ml"},
    "vinho_tinto": {"name": "Vinho Tinto", "category": "almoco_jantar", "cal": 85, "p": 0.1, "c": 2.6, "g": 0, "portion": "100ml"},
    "vinho_branco": {"name": "Vinho Branco", "category": "almoco_jantar", "cal": 82, "p": 0.1, "c": 2.6, "g": 0, "portion": "100ml"},
    
    # ========== LANCHES ==========
    "sanduiche_natural": {"name": "Sanduíche Natural", "category": "lanche", "cal": 280, "p": 12, "c": 35, "g": 10, "portion": "1 unidade (150g)"},
    "sanduiche_misto_quente": {"name": "Misto Quente", "category": "lanche", "cal": 320, "p": 15, "c": 30, "g": 16, "portion": "1 unidade (150g)"},
    "sanduiche_bauru": {"name": "Bauru", "category": "lanche", "cal": 380, "p": 18, "c": 35, "g": 20, "portion": "1 unidade (180g)"},
    "sanduiche_x_tudo": {"name": "X-Tudo", "category": "lanche", "cal": 650, "p": 28, "c": 55, "g": 35, "portion": "1 unidade (300g)"},
    "sanduiche_x_burger": {"name": "X-Burger", "category": "lanche", "cal": 450, "p": 20, "c": 45, "g": 22, "portion": "1 unidade (250g)"},
    "sanduiche_x_salada": {"name": "X-Salada", "category": "lanche", "cal": 520, "p": 22, "c": 48, "g": 26, "portion": "1 unidade (270g)"},
    "sanduiche_x_egg": {"name": "X-Egg", "category": "lanche", "cal": 550, "p": 24, "c": 50, "g": 28, "portion": "1 unidade (280g)"},
    "sanduiche_x_bacon": {"name": "X-Bacon", "category": "lanche", "cal": 680, "p": 30, "c": 55, "g": 38, "portion": "1 unidade (320g)"},
    "cachorro_quente": {"name": "Cachorro Quente", "category": "lanche", "cal": 290, "p": 10, "c": 35, "g": 12, "portion": "1 unidade (200g)"},
    "hot_dog": {"name": "Hot Dog Completo", "category": "lanche", "cal": 380, "p": 12, "c": 42, "g": 18, "portion": "1 unidade (250g)"},
    
    "pizza_mussarela": {"name": "Pizza de Mussarela", "category": "lanche", "cal": 266, "p": 11, "c": 33, "g": 10, "portion": "1 fatia (100g)"},
    "pizza_calabresa": {"name": "Pizza de Calabresa", "category": "lanche", "cal": 285, "p": 12, "c": 32, "g": 12, "portion": "1 fatia (100g)"},
    "pizza_portuguesa": {"name": "Pizza Portuguesa", "category": "lanche", "cal": 275, "p": 13, "c": 33, "g": 10, "portion": "1 fatia (100g)"},
    "pizza_frango": {"name": "Pizza de Frango", "category": "lanche", "cal": 270, "p": 14, "c": 32, "g": 9, "portion": "1 fatia (100g)"},
    "pizza_margherita": {"name": "Pizza Margherita", "category": "lanche", "cal": 260, "p": 11, "c": 33, "g": 9, "portion": "1 fatia (100g)"},
    
    "hamburguer_artesanal": {"name": "Hambúrguer Artesanal", "category": "lanche", "cal": 290, "p": 20, "c": 2, "g": 22, "portion": "1 unidade (120g)"},
    "hamburguer_mcdonalds": {"name": "Hambúrguer McDonald's", "category": "lanche", "cal": 250, "p": 12, "c": 30, "g": 9, "portion": "1 unidade (110g)"},
    "big_mac": {"name": "Big Mac", "category": "lanche", "cal": 550, "p": 25, "c": 46, "g": 30, "portion": "1 unidade (220g)"},
    "mc_chicken": {"name": "McChicken", "category": "lanche", "cal": 400, "p": 14, "c": 46, "g": 18, "portion": "1 unidade (180g)"},
    "mc_nuggets": {"name": "McNuggets (6 un)", "category": "lanche", "cal": 270, "p": 14, "c": 17, "g": 17, "portion": "6 unidades (95g)"},
    
    "batata_frita_mcdonalds": {"name": "Batata Frita McDonald's (M)", "category": "lanche", "cal": 320, "p": 4, "c": 42, "g": 15, "portion": "1 porção (117g)"},
    "batata_frita_burger_king": {"name": "Batata Frita Burger King (M)", "category": "lanche", "cal": 340, "p": 4, "c": 44, "g": 16, "portion": "1 porção (125g)"},
    
    "coxinha": {"name": "Coxinha", "category": "lanche", "cal": 250, "p": 8, "c": 28, "g": 12, "portion": "1 unidade (100g)"},
    "kibe": {"name": "Kibe", "category": "lanche", "cal": 220, "p": 10, "c": 26, "g": 9, "portion": "1 unidade (90g)"},
    "empada": {"name": "Empada", "category": "lanche", "cal": 280, "p": 6, "c": 28, "g": 16, "portion": "1 unidade (90g)"},
    "pastel_carne": {"name": "Pastel de Carne", "category": "lanche", "cal": 290, "p": 10, "c": 32, "g": 14, "portion": "1 unidade (120g)"},
    "pastel_queijo": {"name": "Pastel de Queijo", "category": "lanche", "cal": 310, "p": 11, "c": 33, "g": 15, "portion": "1 unidade (120g)"},
    "esfiha_carne": {"name": "Esfiha de Carne", "category": "lanche", "cal": 240, "p": 10, "c": 30, "g": 9, "portion": "1 unidade (90g)"},
    "esfiha_queijo": {"name": "Esfiha de Queijo", "category": "lanche", "cal": 260, "p": 11, "c": 31, "g": 10, "portion": "1 unidade (90g)"},
    "esfiha_aberta": {"name": "Esfiha Aberta", "category": "lanche", "cal": 220, "p": 9, "c": 28, "g": 8, "portion": "1 unidade (85g)"},
    
    "pao_de_queijo": {"name": "Pão de Queijo", "category": "lanche", "cal": 216, "p": 5.5, "c": 25, "g": 10, "portion": "1 unidade (50g)"},
    "chipa": {"name": "Chipa", "category": "lanche", "cal": 320, "p": 9, "c": 38, "g": 15, "portion": "1 unidade (80g)"},
    
    "salgadinho_doritos": {"name": "Doritos", "category": "lanche", "cal": 536, "p": 6, "c": 60, "g": 30, "portion": "100g"},
    "salgadinho_ruffles": {"name": "Ruffles", "category": "lanche", "cal": 536, "p": 6, "c": 53, "g": 34, "portion": "100g"},
    "salgadinho_fandangos": {"name": "Fandangos", "category": "lanche", "cal": 520, "p": 7, "c": 62, "g": 28, "portion": "100g"},
    "salgadinho_cheetos": {"name": "Cheetos", "category": "lanche", "cal": 530, "p": 7, "c": 58, "g": 30, "portion": "100g"},
    "salgadinho_pringles": {"name": "Pringles", "category": "lanche", "cal": 536, "p": 5, "c": 53, "g": 34, "portion": "100g"},
    
    "amendoim": {"name": "Amendoim", "category": "lanche", "cal": 567, "p": 26, "c": 16, "g": 49, "portion": "100g"},
    "castanha_caju": {"name": "Castanha de Caju", "category": "lanche", "cal": 553, "p": 18, "c": 30, "g": 44, "portion": "100g"},
    "amendoa": {"name": "Amêndoa", "category": "lanche", "cal": 579, "p": 21, "c": 22, "g": 50, "portion": "100g"},
    "nozes": {"name": "Nozes", "category": "lanche", "cal": 654, "p": 15, "c": 14, "g": 65, "portion": "100g"},
    "avela": {"name": "Avelã", "category": "lanche", "cal": 628, "p": 15, "c": 17, "g": 61, "portion": "100g"},
    
    "barra_cereal": {"name": "Barra de Cereal", "category": "lanche", "cal": 380, "p": 8, "c": 60, "g": 12, "portion": "1 unidade (30g)"},
    "barra_proteica": {"name": "Barra Proteica", "category": "lanche", "cal": 200, "p": 20, "c": 15, "g": 7, "portion": "1 unidade (50g)"},
    "whey_protein": {"name": "Whey Protein", "category": "lanche", "cal": 120, "p": 24, "c": 3, "g": 1, "portion": "1 scoop (30g)"},
    
    "chocolate_ao_leite": {"name": "Chocolate ao Leite", "category": "lanche", "cal": 535, "p": 8, "c": 59, "g": 30, "portion": "100g"},
    "chocolate_amargo": {"name": "Chocolate Amargo 70%", "category": "lanche", "cal": 598, "p": 8, "c": 46, "g": 43, "portion": "100g"},
    "chocolate_branco": {"name": "Chocolate Branco", "category": "lanche", "cal": 539, "p": 6, "c": 62, "g": 30, "portion": "100g"},
    "sonho_de_valsa": {"name": "Sonho de Valsa", "category": "lanche", "cal": 530, "p": 6, "c": 55, "g": 32, "portion": "100g"},
    "kitkat": {"name": "KitKat", "category": "lanche", "cal": 518, "p": 6, "c": 62, "g": 28, "portion": "100g"},
    "snickers": {"name": "Snickers", "category": "lanche", "cal": 488, "p": 9, "c": 57, "g": 24, "portion": "100g"},
    "twix": {"name": "Twix", "category": "lanche", "cal": 480, "p": 6, "c": 63, "g": 22, "portion": "100g"},
    "m&m": {"name": "M&M's", "category": "lanche", "cal": 480, "p": 6, "c": 72, "g": 18, "portion": "100g"},
    
    "bolo_chocolate": {"name": "Bolo de Chocolate", "category": "lanche", "cal": 370, "p": 5, "c": 55, "g": 15, "portion": "1 fatia (100g)"},
    "bolo_cenoura": {"name": "Bolo de Cenoura", "category": "lanche", "cal": 340, "p": 5, "c": 52, "g": 13, "portion": "1 fatia (100g)"},
    "brigadeiro": {"name": "Brigadeiro", "category": "lanche", "cal": 380, "p": 5, "c": 55, "g": 16, "portion": "1 unidade (30g)"},
    "beijinho": {"name": "Beijinho", "category": "lanche", "cal": 360, "p": 4, "c": 52, "g": 15, "portion": "1 unidade (30g)"},
    "cajuzinho": {"name": "Cajuzinho", "category": "lanche", "cal": 420, "p": 8, "c": 50, "g": 20, "portion": "1 unidade (30g)"},
    "doce_leite": {"name": "Doce de Leite", "category": "lanche", "cal": 320, "p": 6, "c": 55, "g": 9, "portion": "1 colher sopa (20g)"},
    "geleia_mocot": {"name": "Geleia de Mocotó", "category": "lanche", "cal": 260, "p": 0, "c": 65, "g": 0, "portion": "1 colher sopa (20g)"},
    
    "sorvete_creme": {"name": "Sorvete de Creme", "category": "lanche", "cal": 207, "p": 3.5, "c": 24, "g": 11, "portion": "100g"},
    "sorvete_chocolate": {"name": "Sorvete de Chocolate", "category": "lanche", "cal": 216, "p": 3.8, "c": 28, "g": 10, "portion": "100g"},
    "sorvete_morango": {"name": "Sorvete de Morango", "category": "lanche", "cal": 192, "p": 3.2, "c": 26, "g": 8, "portion": "100g"},
    "sorvete_flocos": {"name": "Sorvete de Flocos", "category": "lanche", "cal": 210, "p": 3.6, "c": 26, "g": 10, "portion": "100g"},
    "picole_fruta": {"name": "Picolé de Fruta", "category": "lanche", "cal": 80, "p": 0.5, "c": 20, "g": 0.2, "portion": "1 unidade (80g)"},
    "picole_creme": {"name": "Picolé de Creme", "category": "lanche", "cal": 150, "p": 2.5, "c": 22, "g": 6, "portion": "1 unidade (80g)"},
    
    # ========== CEIA ==========
    "cha_camomila_ceia": {"name": "Chá de Camomila", "category": "ceia", "cal": 1, "p": 0, "c": 0.2, "g": 0, "portion": "200ml"},
    "cha_cidreira": {"name": "Chá de Cidreira", "category": "ceia", "cal": 1, "p": 0, "c": 0.3, "g": 0, "portion": "200ml"},
    "cha_erva_doce": {"name": "Chá de Erva Doce", "category": "ceia", "cal": 1, "p": 0, "c": 0.2, "g": 0, "portion": "200ml"},
    "cha_hortela": {"name": "Chá de Hortelã", "category": "ceia", "cal": 1, "p": 0, "c": 0.2, "g": 0, "portion": "200ml"},
    "leite_morno": {"name": "Leite Morno", "category": "ceia", "cal": 61, "p": 3.2, "c": 4.8, "g": 3.3, "portion": "200ml"},
    "leite_mel": {"name": "Leite com Mel", "category": "ceia", "cal": 95, "p": 3.5, "c": 16, "g": 3.3, "portion": "200ml"},
    "aveia": {"name": "Aveia em Flocos", "category": "ceia", "cal": 389, "p": 17, "c": 66, "g": 7, "portion": "100g"},
    "granola": {"name": "Granola", "category": "ceia", "cal": 470, "p": 10, "c": 64, "g": 20, "portion": "100g"},
    "musli": {"name": "Muesli", "category": "ceia", "cal": 350, "p": 10, "c": 60, "g": 7, "portion": "100g"},
    "fruta_seca": {"name": "Frutas Secas", "category": "ceia", "cal": 340, "p": 3, "c": 80, "g": 1, "portion": "100g"},
}

# Combos pré-definidos
COMBOS = {
    "pf_tradicional": {
        "name": "PF Tradicional",
        "items": ["arroz_branco", "feijao_carioca", "frango_grelhado", "salada_mista"],
        "description": "Arroz, feijão, frango e salada"
    },
    "cafe_manha_completo": {
        "name": "Café da Manhã Completo",
        "items": ["pao_frances", "manteiga", "cafe_com_leite", "ovo_cozido", "fruta_mista"],
        "description": "Pão, café, ovo e fruta"
    },
    "lanche_rapido": {
        "name": "Lanche Rápido",
        "items": ["sanduiche_natural", "suco_laranja"],
        "description": "Sanduíche natural e suco"
    },
}

# Função para busca inteligente
def buscar_alimento(termo: str) -> list:
    """Busca alimentos por nome (case insensitive)"""
    termo = termo.lower().strip()
    if not termo:
        return []
    
    resultados = []
    for key, value in FOOD_DB.items():
        if termo in value["name"].lower():
            resultados.append({
                "key": key,
                "name": value["name"],
                "cal": value["cal"],
                "category": value.get("category", "geral")
            })
    
    return sorted(resultados, key=lambda x: x["name"])[:10]  # Retorna top 10
