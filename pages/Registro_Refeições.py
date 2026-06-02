import streamlit as st
from datetime import datetime
from core.nutrition import NutritionService
from utils.food_db import FOOD_DB, COMBOS

def render_meals(nutrition: NutritionService, user: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.header("🍴 Registro Alimentar")
    col1, col2 = st.columns([5, 3])
    
    with col1:
        tab1, tab2 = st.tabs(["Alimento Individual", "Combos Prontos"])
        with tab1:
            food_items = list(FOOD_DB.keys())
            selected = st.selectbox("Selecione o Alimento", food_items, format_func=lambda x: f"{FOOD_DB[x]['name']} ({FOOD_DB[x]['portion']}) — {FOOD_DB[x]['cal']} kcal")
            quantity = st.number_input("Quantidade (Fator multiplicador)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
            meal_time = st.time_input("Horário do registro", value=datetime.now().time())
            
            if st.button("Inserir no Registro", use_container_width=True, type="primary"):
                ok, name, calories = nutrition.register_food(selected, quantity, meal_time.strftime("%H:%M"))
                if ok: 
                    st.success(f"{name} adicionado com sucesso! (+{calories} kcal)")
                    st.rerun()
        with tab2:
            for combo_id, combo in COMBOS.items():
                with st.container():
                    st.markdown(f"**{combo['name']}**")
                    items_str = ", ".join([FOOD_DB[i]['name'] for i in combo['items']])
                    st.caption(f"Componentes: {items_str}")
                    if st.button("Registrar Combo Completo", key=f"combo_{combo_id}"):
                        ok, name, calories = nutrition.register_combo(combo_id)
                        if ok: 
                            st.success(f"Combo {name} registrado! (+{calories} kcal)")
                            st.rerun()
                    st.markdown("---")
    with col2:
        st.markdown("### 📸 Comprovação por Foto")
        photo = st.camera_input("Capturar imagem da refeição")
        if photo: 
            st.success("Foto vinculada temporariamente ao registro atual.")
    st.markdown('</div>', unsafe_allow_html=True)
