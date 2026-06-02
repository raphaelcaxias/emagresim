import streamlit as st
from core.database import AppDatabase
from components import card_metric

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

db = AppDatabase()
user = st.session_state.user

st.title("👤 Perfil")

with st.form("perfil_form"):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome", value=user.get("name", ""))
        email = st.text_input("Email", value=user.get("email", ""), disabled=True)
        idade = st.number_input("Idade", 10, 110, int(user.get("age", 30)))
    with col2:
        peso = st.number_input("Peso (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)))
        altura = st.number_input("Altura (cm)", 100, 250, int(user.get("height", 170)))
        meta = st.number_input("Meta (kg)", 30.0, 250.0, float(user.get("goal_weight", 70.0)))
    
    objetivo = st.selectbox("Objetivo", ["lose", "maintain", "gain"],
                           index=["lose", "maintain", "gain"].index(user.get("goal", "lose")),
                           format_func=lambda x: {"lose": "Emagrecer", "maintain": "Manter", "gain": "Ganhar massa"}[x])
    atividade = st.selectbox("Atividade", ["sedentary", "light", "moderate", "active"],
                            index=["sedentary", "light", "moderate", "active"].index(user.get("activity_level", "moderate")),
                            format_func=lambda x: {"sedentary": "Sedentário", "light": "Leve", "moderate": "Moderado", "active": "Ativo"}[x])
    
    if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
        dados = {
            "name": nome, "current_weight": peso, "height": altura,
            "age": idade, "goal_weight": meta, "goal": objetivo, "activity_level": atividade
        }
        user.update(dados)
        db.update_profile(dados)
        st.session_state.user = user
        st.success("Perfil atualizado!")
        st.rerun()

st.markdown("---")
st.subheader("💳 Plano Atual")
plano = user.get("plan", "free")
st.markdown(f"Você está no plano **{plano.upper()}**")

if plano == "free":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Plano Pro** - R$ 29,90/mês")
        if st.button("Assinar Pro", use_container_width=True):
            user["plan"] = "pro"
            st.session_state.user = user
            db.update_profile({"plan": "pro"})
            st.success("Plano Pro ativado!")
            st.rerun()
    with col2:
        st.markdown("**Vitalício** - R$ 497,00")
        if st.button("Assinar Vitalício", use_container_width=True):
            user["plan"] = "lifetime"
            st.session_state.user = user
            db.update_profile({"plan": "lifetime"})
            st.success("Plano Vitalício ativado!")
            st.rerun()
