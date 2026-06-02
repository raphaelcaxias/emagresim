import streamlit as st
from datetime import datetime
from core.database import AppDatabase
from core.nutrition import NutritionService
from utils.food_db import FOOD_DB, COMBOS

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

@st.cache_resource(show_spinner=False)
def init():
    db = AppDatabase()
    return db, NutritionService(db)

db, nutrition = init()
user = st.session_state.user

st.title(" Registro Alimentar")

tab1, tab2 = st.tabs(["Alimento Individual", "Combos Prontos"])

with tab1:
    col1, col2, col3 = st.columns([4, 2, 3])
    with col1:
        alimentos = list(FOOD_DB.keys())
        selected = st.selectbox("Alimento", alimentos, 
                               format_func=lambda x: f"{FOOD_DB[x]['name']} - {FOOD_DB[x]['cal']} kcal")
    with col2:
        qty = st.number_input("Qtd", 0.1, 10.0, 1.0, 0.1)
    with col3:
        hora = st.time_input("Horário", value=datetime.now().time())
    
    if st.button("✅ Registrar", type="primary", use_container_width=True):
        ok, nome, cal = nutrition.register_food(selected, qty, hora.strftime("%H:%M"))
        if ok:
            st.success(f"{nome} registrado! (+{cal} kcal)")
            st.rerun()

with tab2:
    st.markdown("Combos rápidos baseados na alimentação brasileira:")
    for cid, combo in COMBOS.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{combo['name']}**")
                itens = ", ".join([FOOD_DB[i]['name'] for i in combo['items']])
                st.caption(itens)
            with col2:
                if st.button("Usar", key=f"combo_{cid}"):
                    ok, nome, cal = nutrition.register_combo(cid)
                    if ok:
                        st.success(f"{nome} registrado! (+{cal} kcal)")
                        st.rerun()
            st.markdown("---")

# Histórico do dia
st.subheader("📋 Hoje")
summary = nutrition.get_daily_summary()
if summary['meals']:
    for m in summary['meals']:
        st.markdown(f"• **{m.get('meal_time','--:--')}** - {m.get('food','?')} ({m.get('calories',0)} kcal)")
else:
    st.info("Nenhuma refeição registrada hoje.")
