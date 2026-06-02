import streamlit as st
from datetime import datetime
from components import section_header, empty_state
from utils.food_db import FOOD_DB, buscar_alimento

def render_meals(services: dict, user: dict):
    section_header("Registro Alimentar", f"{datetime.now().strftime('%d/%m/%Y')}", "🍽️")
    
    # Fluxo por Período (Requisito Fase 2)
    col1, col2 = st.columns([2, 1])
    with col1:
        periodo = st.selectbox("Qual refeição você vai registrar?", 
            ["☕ Café da Manhã", "🍴 Almoço", "🌙 Jantar", "🥪 Lanche da Tarde", "🌃 Ceia"])
    
    mapeamento = {
        " Café da Manhã": "cafe_manha", "🍴 Almoço": "almoco_jantar", 
        "🌙 Jantar": "almoco_jantar", "🥪 Lanche da Tarde": "lanche", "🌃 Ceia": "ceia"
    }
    categoria = mapeamento[periodo]

    # Busca Inteligente (Requisito Fase 2)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        termo = st.text_input("🔍 Buscar alimento...", placeholder="Ex: arroz, frango...")
    
    food_key = None
    if termo:
        resultados = buscar_alimento(termo)
        if resultados:
            opcoes = {f"{r['name']} ({r['cal']} kcal)": r['key'] for r in resultados}
            selecionado = st.selectbox("Resultados da busca:", list(opcoes.keys()))
            food_key = opcoes[selecionado]
        else:
            st.warning("Nenhum alimento encontrado.")
    else:
        # Fallback para categoria
        alimentos_cat = {k: v for k, v in FOOD_DB.items() if v.get("category") == categoria}
        if alimentos_cat:
            opcoes = {f"{v['name']} ({v['cal']} kcal)": k for k, v in alimentos_cat.items()}
            selecionado = st.selectbox(f"Ou escolha de {periodo}:", list(opcoes.keys()))
            food_key = opcoes[selecionado]

    # Campos Contextuais e Horário Automático
    col1, col2, col3 = st.columns(3)
    with col1:
        qtd = st.number_input("Quantidade (x)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    with col2:
        hora = st.time_input("Horário", value=datetime.now().time())
    with col3:
        # Campos contextuais para Almoço/Jantar
        observacoes = ""
        if categoria == "almoco_jantar":
            observacoes = st.text_area("Obs (Opcional)", placeholder="Ex: Grelhado, sem sal...")

    # Ação de Registro
    if st.button("✅ Registrar Refeição", type="primary", use_container_width=True):
        if food_key:
            ok, nome, cal = services["nutrition"].register_food(food_key, qtd, hora.strftime("%H:%M"))
            if ok:
                st.success(f"✅ {nome} registrado! (+{cal * qtd:.0f} kcal)")
                st.rerun()
        else:
            st.error("Selecione um alimento primeiro.")

    # Histórico Diário
    st.markdown("---")
    section_header("Refeições de Hoje", "", "📋")
    summary = services["nutrition"].get_daily_summary()
    
    if summary.get('meals'):
        for i, meal in enumerate(summary['meals']):
            st.markdown(f"• **{meal.get('meal_time', '--:--')}** - {meal.get('food', '?')} ({meal.get('calories', 0)} kcal)")
    else:
        empty_state("️", "Nenhuma refeição registrada hoje", "Use o seletor acima para começar.")
