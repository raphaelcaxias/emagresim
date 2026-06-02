import streamlit as st
from core.payment import PaymentService

def render_profile(payment: PaymentService, user: dict):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.header("👤 Definições de Perfil")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome de Exibição", value=user.get("name", ""))
            st.text_input("Identificador / Email", value=user.get("email", ""), disabled=True)
        with col2:
            weight = st.number_input("Peso Atual de Referência (kg)", min_value=30.0, max_value=250.0, value=float(user.get("current_weight") or 70.0))
            height = st.number_input("Altura total (cm)", min_value=100, max_value=250, value=int(user.get("height") or 170))
            age = st.number_input("Idade Cronológica", min_value=10, max_value=110, value=int(user.get("age") or 30))
            
        goal = st.selectbox("Objetivo Biológico Principal", ["lose", "maintain", "gain"], format_func=lambda x: {"lose": "Emagrecimento / Déficit", "maintain": "Manutenção TDEE", "gain": "Hipertrofia / Superávit"}[x])
        activity = st.selectbox("Taxa de Atividade Diária", ["sedentary", "light", "moderate", "active"], format_func=lambda x: {"sedentary": "Sedentário (Trabalho Sentado)", "light": "Atividade Leve (1-2x semana)", "moderate": "Moderadamente Ativo (3-5x semana)", "active": "Altamente Ativo (Diário)"}[x])
        
        if st.form_submit_button("Atualizar Configurações de Saúde", use_container_width=True, type="primary"):
            updated_fields = {"name": name, "current_weight": weight, "height": height, "age": age, "goal": goal, "activity_level": activity}
            user.update(updated_fields)
            st.session_state.user = user
            st.success("Métricas recalculadas e salvas com sucesso!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("💳 Planos de Assinatura")
    if user.get("plan") != "free":
        st.success(f"Assinatura Ativa: Nível [{user.get('plan').upper()}] habilitado com sucesso.")
        return
        
    plans = {
        "pro": {"name": "Pro", "price": 29.90, "features": ["Análises avançadas", "Relatórios completos", "Foco em Metas"]},
        "lifetime": {"name": "Vitalício", "price": 497.00, "features": ["Todos os recursos", "Acesso permanente para sempre"]}
    }

    cols = st.columns(2)
    for idx, (plan_key, plan) in enumerate(plans.items()):
        with cols[idx]:
            st.markdown(f'<div style="border:1px solid #0891b2;border-radius:12px;padding:1.5rem;text-align:center;background:#f8fafc;"><h3>{plan["name"]}</h3><div style="font-size:1.75rem;font-weight:700;color:#0891b2;margin:0.5rem 0;">R$ {plan["price"]:.2f}</div></div>', unsafe_allow_html=True)
            for feat in plan['features']: st.markdown(f"🔹 {feat}")
            if st.button(f"Ativar Plano {plan['name']}", key=f"pay_{plan_key}", use_container_width=True, type="primary"):
                user["plan"] = plan_key
                st.session_state.user = user
                st.success("Plano habilitado em ambiente Sandbox com Sucesso!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
