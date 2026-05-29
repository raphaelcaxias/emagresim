import streamlit as st
import pandas as pd

def render_dashboard(db, user_service, psychology, profile):
    st.title("📊 Dashboard")
    st.markdown(f"**Bem-vindo de volta, {profile.get('username', 'Herói')}!** 💪")
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚡ XP Total", profile.get('experience', 0))
    c2.metric("️ Peso Atual", f"{profile.get('current_weight_kg', 0)} kg")
    c3.metric("🔥 Sequência", f"{profile.get('streak_days', 0)} dias")
    c4.metric("🎯 Meta", f"{profile.get('goal_weight_kg', 0)} kg")
    
    st.markdown("### 🎯 Progresso para o Próximo Nível")
    level = profile.get('level', 1)
    xp_needed = int(100 * (level ** 1.5))
    xp_current = profile.get('experience', 0)
    progress = min(xp_current / xp_needed, 1.0) if xp_needed > 0 else 0
    st.progress(progress)
    st.caption(f"{xp_current} / {xp_needed} XP necessários")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1: st.info(f"💭 **Motivação:** {psychology.get_daily_motivation()}")
    with col2: st.warning(f"💡 **Dica:** {psychology.get_tip()}")
    
    st.markdown("### 🍴 Refeições de Hoje")
    meals = db.get_daily_meals()
    if meals:
        total_cal = sum(m.get('calories', 0) for m in meals)
        st.markdown(f"**Total: {total_cal} kcal**")
        for m in meals:
            st.markdown(f"""
            <div style='background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #11998e;'>
                <strong>{m.get('food_name', 'Sem nome')}</strong><br>
                {m.get('calories', 0)} kcal • {m.get('proteins', 0)}g proteína • {m.get('meal_type', '')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📝 Nenhuma refeição registrada hoje. Vá em 'Refeições' para começar!")

def render_refeicoes(db, user_service):
    st.title("🍴 Registrar Refeição")
    
    with st.form("meal_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Refeição", ["cafe", "almoco", "jantar", "lanche"], 
                              format_func=lambda x: {"cafe": "☕ Café", "almoco": "️ Almoço", 
                                                     "jantar": "🌙 Jantar", "lanche": "🍎 Lanche"}[x])
            nome = st.text_input("Nome do Alimento", placeholder="Ex: Arroz com frango e salada")
        with col2:
            cal = st.number_input("Calorias", min_value=0, max_value=2000, value=350, step=10)
            prot = st.number_input("Proteínas (g)", min_value=0.0, max_value=200.0, value=15.0, step=0.5)
        
        submitted = st.form_submit_button("✅ Registrar Refeição", use_container_width=True)
        
        if submitted:
            if nome:
                with st.spinner("Registrando..."):
                    res = user_service.register_meal({
                        "meal_type": tipo, "food_name": nome, "calories": cal, "proteins": prot
                    })
                    if res.get("success"):
                        st.balloons()
                        st.success(f"🎉 +{res.get('xp', 0)} XP ganhos!")
                        if res.get("leveled_up"): 
                            st.toast(f"🏆 LEVEL UP! Nível {res.get('level')}", icon="🎉")
                        st.rerun()
                    else: st.error("Erro ao registrar refeição")
            else: st.warning("Digite o nome do alimento")

def render_historico(db):
    st.title(" Histórico de Peso")
    logs = db.get_weight_history(90)
    if logs:
        df = pd.DataFrame(logs)
        df["recorded_at"] = pd.to_datetime(df["recorded_at"]).dt.date
        df = df.sort_values("recorded_at", ascending=False)
        
        col1, col2 = st.columns([3, 1])
        with col1: st.line_chart(df.set_index("recorded_at")["weight_kg"])
        with col2:
            st.metric("Último Peso", f"{df.iloc[0]['weight_kg']} kg")
            if len(df) > 1:
                diff = df.iloc[-1]['weight_kg'] - df.iloc[0]['weight_kg']
                st.metric("Variação", f"{diff:.1f} kg")
        
        st.markdown("### Registros")
        st.dataframe(df[["recorded_at", "weight_kg"]].rename(columns={"recorded_at": "Data", "weight_kg": "Peso (kg)"}), use_container_width=True)
    else:
        st.info(" Registre seu peso em 'Perfil' para ver o histórico.")

def render_perfil(db, user_service, profile):
    st.title("👤 Meu Perfil")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Informações Pessoais")
            idade = st.number_input("Idade", min_value=0, max_value=120, value=profile.get("age") or 25)
            peso = st.number_input("Peso Atual (kg)", min_value=0.0, max_value=300.0, 
                                 value=float(profile.get("current_weight_kg") or 70.0), step=0.1)
        with col2:
            st.subheader("Metas")
            altura = st.number_input("Altura (cm)", min_value=0, max_value=250, value=profile.get("height_cm") or 170)
            meta = st.number_input("Peso Meta (kg)", min_value=0.0, max_value=300.0, 
                                 value=float(profile.get("goal_weight_kg") or 65.0), step=0.1)
        
        st.markdown("---")
        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
            with st.spinner("Salvando..."):
                db.update_profile({"age": idade, "height_cm": altura, "goal_weight_kg": meta})
                if abs(peso - profile.get("current_weight_kg", 0)) > 0.01:
                    res = user_service.update_weight(peso)
                    st.info(res.get("message", "Peso atualizado"))
                st.success("✅ Perfil atualizado com sucesso!")
                st.rerun()
