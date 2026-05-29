import streamlit as st
import pandas as pd

def render_dashboard(db, user_service, psychology, profile):
    # Header Personalizado
    st.markdown(f"### Olá, **{profile.get('username', 'Herói')}!** 👋")
    st.caption("Aqui está o resumo da sua jornada hoje.")
    st.markdown("---")
    
    # Grid de Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 Nível Atual", profile.get('level', 1))
    with col2:
        st.metric("⚡ XP Acumulado", profile.get('experience', 0))
    with col3:
        st.metric("🔥 Sequência", f"{profile.get('streak_days', 0)} dias")
    with col4:
        peso = profile.get('current_weight_kg')
        st.metric("⚖️ Peso", f"{peso if peso else '-'} kg")
    
    # Progresso
    st.markdown("### 📈 Evolução para o Próximo Nível")
    level = profile.get('level', 1)
    xp_needed = int(100 * (level ** 1.5))
    xp_current = profile.get('experience', 0)
    progress = min(xp_current / xp_needed, 1.0) if xp_needed > 0 else 0
    
    st.progress(progress)
    st.caption(f"Faltam {max(0, xp_needed - xp_current)} pontos para o nível {level + 1}")
    
    st.markdown("---")
    
    # Cards de Conteúdo (Motivação e Refeições)
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("### 💭 Motivação do Dia")
        # Card customizado
        st.markdown(f"""
        <div style='background: #e3f2fd; padding: 1.5rem; border-radius: 15px; color: #1565c0;'>
            <h4 style='margin-top:0;'>Inspiração</h4>
            <p style='margin-bottom:0;'>{psychology.get_daily_motivation()}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_b:
        st.markdown("### 💡 Dica de Saúde")
        st.markdown(f"""
        <div style='background: #fff3e0; padding: 1.5rem; border-radius: 15px; color: #e65100;'>
            <h4 style='margin-top:0;'>Dica Prática</h4>
            <p style='margin-bottom:0;'>{psychology.get_tip()}</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Refeições
    st.markdown("---")
    st.markdown("### 🍴 Refeições de Hoje")
    meals = db.get_daily_meals()
    if meals:
        total_cal = sum(m.get('calories', 0) for m in meals)
        st.info(f"🔥 Total: **{total_cal} kcal** consumidos hoje.")
        
        cols = st.columns(3)
        for i, m in enumerate(meals):
            with cols[i % 3]:
                tipo_emoji = {"cafe": "☕", "almoco": "🍽️", "jantar": "🌙", "lanche": "🍎"}.get(m.get('meal_type', ''), '🍴')
                st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 12px; border-left: 4px solid #00b894; margin-bottom: 0.5rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                    <strong>{tipo_emoji} {m.get('food_name', 'Sem nome')}</strong><br>
                    <small style='color:#666;'>{m.get('calories', 0)} kcal • {m.get('proteins', 0)}g prot.</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: white; border-radius: 15px; border: 2px dashed #dfe6e9;'>
            <p style='font-size: 1.2rem; color: #636e72;'>Nenhuma refeição registrada hoje.</p>
            <p>Vá em <b>Refeições</b> para começar! 🚀</p>
        </div>
        """, unsafe_allow_html=True)

def render_refeicoes(db, user_service):
    st.title("🍴 Registrar Refeição")
    st.markdown("Adicione o que comeu para ganhar XP e manter o controle.")
    
    with st.form("meal_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Refeição", ["cafe", "almoco", "jantar", "lanche"], 
                              format_func=lambda x: {"cafe": "☕ Café da Manhã", "almoco": "🍽️ Almoço", 
                                                     "jantar": "🌙 Jantar", "lanche": "🍎 Lanche"}[x])
            nome = st.text_input("Nome do Alimento", placeholder="Ex: Arroz com frango e salada")
        with col2:
            cal = st.number_input("Calorias", min_value=0, max_value=2000, value=350, step=10)
            prot = st.number_input("Proteínas (gramas)", min_value=0.0, max_value=200.0, value=15.0, step=0.5)
        
        submitted = st.form_submit_button("✅ Registrar Refeição")
        
        if submitted:
            if nome:
                with st.spinner("Registrando..."):
                    res = user_service.register_meal({
                        "meal_type": tipo, "food_name": nome, "calories": cal, "proteins": prot
                    })
                    if res.get("success"):
                        st.balloons()
                        st.success(f"🎉 +{res.get('xp', 0)} pontos ganhos!")
                        if res.get("leveled_up"): 
                            st.toast(f" PARABÉNS! Nível {res.get('level')}", icon="🎉")
                        st.rerun()
                    else: st.error("Erro ao registrar")
            else: st.warning("Digite o nome do alimento")

def render_historico(db):
    st.title("📈 Histórico de Peso")
    logs = db.get_weight_history(90)
    if logs:
        df = pd.DataFrame(logs)
        df["recorded_at"] = pd.to_datetime(df["recorded_at"]).dt.date
        df = df.sort_values("recorded_at", ascending=False)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Evolução Gráfica")
            st.line_chart(df.set_index("recorded_at")["weight_kg"], color="#00b894")
        with col2:
            st.markdown("### Resumo")
            st.metric("Peso Atual", f"{df.iloc[0]['weight_kg']} kg")
            if len(df) > 1:
                diff = df.iloc[-1]['weight_kg'] - df.iloc[0]['weight_kg']
                st.metric("Mudança Total", f"{diff:.1f} kg")
        
        st.markdown("### 📋 Registros Recentes")
        st.dataframe(df[["recorded_at", "weight_kg"]].rename(columns={"recorded_at": "Data", "weight_kg": "Peso (kg)"}), use_container_width=True)
    else:
        st.info("Registre seu peso em 'Perfil' para ver o histórico.")

def render_perfil(db, user_service, profile):
    st.title("👤 Meu Perfil")
    st.markdown("Mantenha seus dados atualizados para cálculos precisos.")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Informações Pessoais")
            idade = st.number_input("Idade", min_value=0, max_value=120, value=profile.get("age") or 25)
            peso = st.number_input("Peso Atual (kg)", min_value=0.0, max_value=300.0, 
                                 value=float(profile.get("current_weight_kg") or 70.0), step=0.1)
        with col2:
            st.subheader(" Metas")
            altura = st.number_input("Altura (cm)", min_value=0, max_value=250, value=profile.get("height_cm") or 170)
            meta = st.number_input("Peso Desejado (kg)", min_value=0.0, max_value=300.0, 
                                 value=float(profile.get("goal_weight_kg") or 65.0), step=0.1)
        
        if st.form_submit_button("💾 Salvar Alterações"):
            with st.spinner("Salvando..."):
                db.update_profile({"age": idade, "height_cm": altura, "goal_weight_kg": meta})
                if abs(peso - profile.get("current_weight_kg", 0)) > 0.01:
                    res = user_service.update_weight(peso)
                    st.info(res.get("message", "Peso atualizado"))
                st.success("✅ Perfil atualizado com sucesso!")
                st.rerun()
