import streamlit as st
from components import section_header

def render_profile(services: dict, user: dict):
    section_header("Perfil e Metas", "Gerencie seus dados e assinatura.", "")
    
    with st.form("perfil_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", value=user.get("name", ""))
            st.text_input("Email", value=user.get("email", ""), disabled=True)
            idade = st.number_input("Idade", 10, 110, int(user.get("age", 30)))
            altura = st.number_input("Altura (cm)", 100, 250, int(user.get("height", 170)))
        with col2:
            peso = st.number_input("Peso Atual (kg)", 30.0, 250.0, float(user.get("current_weight", 70.0)))
            meta = st.number_input("Meta de Peso (kg)", 30.0, 250.0, float(user.get("goal_weight", 70.0)))
            objetivo = st.selectbox("Objetivo", ["lose", "maintain", "gain"], 
                index=["lose", "maintain", "gain"].index(user.get("goal", "lose")),
                format_func=lambda x: {"lose": "Emagrecer", "maintain": "Manter", "gain": "Ganhar Massa"}[x])
            atividade = st.selectbox("Nível de Atividade", ["sedentary", "light", "moderate", "active"],
                index=["sedentary", "light", "moderate", "active"].index(user.get("activity_level", "moderate")),
                format_func=lambda x: {"sedentary": "Sedentário", "light": "Leve", "moderate": "Moderado", "active": "Ativo"}[x])
        
        if st.form_submit_button("💾 Salvar Perfil", type="primary", use_container_width=True):
            dados = {"name": nome, "current_weight": peso, "height": altura, 
                     "age": idade, "goal_weight": meta, "goal": objetivo, "activity_level": atividade}
            user.update(dados)
            services["db"].update_profile(dados)
            st.session_state.user = user
            st.success("✅ Perfil atualizado! Cálculos recalibrados.")
            st.rerun()

    st.markdown("---")
    section_header("Assinatura", "Desbloqueie o potencial máximo.", "👑")
    plano_atual = user.get("plan", "free")
    
    if plano_atual != "free":
        st.success(f"Você é um assinante **{plano_atual.upper()}**. Obrigado pelo apoio!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="border: 2px solid #0891b2; border-radius: 12px; padding: 1.5rem; text-align: center;">
                <h3 style="color: #0891b2;">👑 PRO</h3>
                <div style="font-size: 2rem; font-weight: bold;">R$ 29,90<span style="font-size: 1rem;">/mês</span></div>
                <ul style="text-align: left; list-style: none; padding: 0;">
                    <li>✅ Análises avançadas</li>
                    <li>✅ Relatórios PDF</li>
                    <li>✅ Suporte prioritário</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Assinar PRO", use_container_width=True, type="primary"):
                # Em produção: services["payment"].create_checkout_link("pro", user["email"])
                user["plan"] = "pro"
                st.session_state.user = user
                services["db"].update_profile({"plan": "pro"})
                st.success("Plano PRO ativado (Modo Sandbox)!")
                st.rerun()
