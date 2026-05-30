import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from utils.analytics import AnalyticsEngine

# ==========================================
# 1. ONBOARDING
# ==========================================
def render_onboarding(db, profile):
    st.title("👋 Complete seu Perfil")
    st.caption("Dados essenciais para análises personalizadas")
    
    with st.form("onboarding"):
        c1, c2 = st.columns(2)
        with c1:
            dob = st.date_input("Data de Nascimento", value=datetime(1990,1,1))
            age = (datetime.today() - datetime.combine(dob, datetime.min.time())).days // 365
            height = st.number_input("Altura (cm)", 100, 250, 170)
            gender = st.radio("Gênero", ["M", "F", "Outro"], horizontal=True)
        with c2:
            weight = st.number_input("Peso Atual (kg)", 30.0, 300.0, 70.0, 0.1)
            goal = st.number_input("Peso Meta (kg)", 30.0, 300.0, 65.0, 0.1)
            waist = st.number_input("Cintura (cm)", 40.0, 200.0, 80.0, 0.1)
        
        activity = st.selectbox("Nível de Atividade", ["Sedentario", "Leve", "Moderado", "Intenso"])
        goal_type = st.selectbox("Objetivo Principal", ["Perder Peso", "Ganhar Massa", "Manter", "Saude"])
        
        if st.form_submit_button("✅ Iniciar Jornada"):
            db.update_profile({
                "date_of_birth": dob.isoformat(), "age": age, "height_cm": height, "gender": gender,
                "current_weight_kg": weight, "goal_weight_kg": goal, "activity_level": activity,
                "goal_type": goal_type, "is_onboarding_complete": True
            })
            return True
    return False

# ==========================================
# 2. DASHBOARD ANALYTICS (PRINCIPAL)
# ==========================================
def render_dashboard(db, profile, is_demo):
    st.title("📊 Painel de Analytics")
    
    # Header com KPIs calculados
    bmi = AnalyticsEngine.calculate_bmi(profile.get("current_weight_kg"), profile.get("height_cm"))
    bmi_cat, bmi_icon = AnalyticsEngine.get_bmi_category(bmi)
    tmb = AnalyticsEngine.calculate_tmb(profile.get("current_weight_kg"), profile.get("height_cm"), 
                                        profile.get("age"), profile.get("gender"), profile.get("activity_level"))
        c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Nível", profile.get("level", 1))
    c2.metric(f"IMC {bmi_icon}", f"{bmi if bmi else '-'}", bmi_cat)
    c3.metric("⚡ TMB", f"{tmb if tmb else '-'} kcal/dia")
    c4.metric("🔥 Streak", f"{profile.get('streak_days', 0)} dias")
    
    st.divider()
    
    # Carregar dados
    if is_demo:
        logs = _generate_demo_logs()
    else:
        logs = db.get_logs_history(60)
    
    if not logs:
        st.info("📝 Comece registrando seus dados diários em 'Registro do Dia'!")
        return
    
    df = pd.DataFrame(logs)
    df['log_date'] = pd.to_datetime(df['log_date'])
    
    # 📈 GRÁFICO 1: Evolução de Peso com Tendência
    st.subheader("📈 Evolução do Peso")
    
    weight_df = df.dropna(subset=['weight_kg']).sort_values('log_date')
    
    if len(weight_df) >= 5:
        # Calcular tendência
        trend = AnalyticsEngine.calculate_weight_trend(logs)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weight_df['log_date'], y=weight_df['weight_kg'],
            mode='lines+markers', name='Peso Registrado',
            line=dict(color='#00b894', width=3),
            marker=dict(size=6)
        ))
        
        # Linha de tendência
        if trend:
            fig.add_trace(go.Scatter(
                x=weight_df['log_date'],
                y=[trend['slope']/1000 * (d.toordinal() - weight_df['log_date'].min().toordinal()) + weight_df['weight_kg'].iloc[0] 
                   for d in weight_df['log_date']],
                mode='lines', name='Tendência',
                line=dict(color='#0984e3', width=2, dash='dash')
            ))
            
            st.caption(f"📊 Tendência: {trend['daily_change_g']}g/dia • R² = {trend['r_squared']}")
                fig.update_layout(
            xaxis_title="Data", yaxis_title="Peso (kg)",
            hovermode="x unified", height=350,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Projeção de meta
        if trend and profile.get("goal_weight_kg"):
            current = profile.get("current_weight_kg")
            goal = profile.get("goal_weight_kg")
            if trend['slope'] < 0 and current > goal:
                days_left = (current - goal) / abs(trend['slope'])
                st.success(f"🎯 No ritmo atual, você atinge sua meta em **~{int(days_left)} dias**!")
    
    else:
        st.warning("Registre pelo menos 5 dias de peso para ver a análise de tendência.")
    
    # 📊 GRÁFICO 2: Correlações
    st.subheader("🔍 Análise de Correlações")
    
    correlations = AnalyticsEngine.analyze_correlations(logs)
    
    if correlations:
        c1, c2, c3 = st.columns(3)
        
        if 'sono_energia' in correlations:
            corr = correlations['sono_energia']
            c1.metric("😴 Sono → ⚡ Energia", f"{corr['correlation']}", f"Correlação {corr['interpretation']}")
        
        if 'agua_humor' in correlations:
            corr = correlations['agua_humor']
            c2.metric("💧 Água → 😊 Humor", f"{corr['correlation']}", f"Correlação {corr['interpretation']}")
        
        if 'exercicio_estresse' in correlations:
            corr = correlations['exercicio_estresse']
            c3.metric("🏃 Exercício → 😰 Estresse", f"{corr['correlation']}", f"Correlação {corr['interpretation']}")
        
        st.caption("💡 Correlação varia de -1 (inversa) a +1 (direta). Valores próximos de 0 indicam pouca relação.")
    else:
        st.info("Registre mais dados para ver análises de correlação!")
    
    # 🔥 HEATMAP DE CONSISTÊNCIA
    st.subheader("🔥 Consistência Semanal")
    
    heatmap_data = AnalyticsEngine.generate_consistency_heatmap(logs)
    
    if heatmap_data:
        hm_df = pd.DataFrame(heatmap_data)
        hm_df['date'] = pd.to_datetime(hm_df['date'])        hm_df['week'] = hm_df['date'].dt.isocalendar().week
        hm_df['weekday'] = hm_df['date'].dt.day_name()
        
        # Pivot para formato heatmap
        pivot = hm_df.pivot_table(index='weekday', columns='week', values='count', aggfunc='max')
        
        # Ordenar dias da semana
        order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot = pivot.reindex([d for d in order if d in pivot.index])
        
        fig = px.imshow(
            pivot, 
            labels=dict(x="Semana", y="Dia", color="Atividade"),
            x=pivot.columns, y=pivot.index,
            color_continuous_scale=['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'],
            aspect="auto"
        )
        fig.update_layout(height=250, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # 📋 RESUMO ESTATÍSTICO
    st.divider()
    st.subheader("📋 Resumo Estatístico")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("##### 💧 Hidratação")
        if 'water_intake_liters' in df.columns:
            avg_water = df['water_intake_liters'].mean()
            st.metric("Média Diária", f"{avg_water:.1f} L")
            st.progress(min(avg_water / 2.5, 1.0))
            st.caption("Meta: 2.5L/dia")
    
    with c2:
        st.markdown("##### 😴 Qualidade do Sono")
        if 'sleep_hours' in df.columns:
            avg_sleep = df['sleep_hours'].mean()
            st.metric("Média Nocturna", f"{avg_sleep:.1f} h")
            st.progress(min(avg_sleep / 8.0, 1.0))
            st.caption("Recomendado: 7-8h/noite")
    
    # 🎯 INSIGHTS PERSONALIZADOS
    st.divider()
    st.subheader("💡 Insights para Você")
    
    insights = []
    
    if trend and trend['slope'] > 0 and profile.get("goal_type") == "Perder Peso":
        insights.append("⚠️ Seu peso está subindo levemente. Revise sua ingestão calórica.")    
    if 'water_intake_liters' in df.columns and df['water_intake_liters'].mean() < 2:
        insights.append("💧 Você está bebendo menos de 2L de água. A hidratação ajuda no metabolismo!")
    
    if 'sleep_hours' in df.columns and df['sleep_hours'].mean() < 7:
        insights.append("😴 Dormir bem é essencial para perda de peso. Tente aumentar para 7-8h.")
    
    if profile.get("streak_days", 0) >= 7:
        insights.append(f"🔥 Incrível! {profile['streak_days']} dias seguidos de registro. Mantenha a consistência!")
    
    if not insights:
        insights.append("✨ Continue registrando! Mais dados = insights mais precisos.")
    
    for insight in insights:
        st.info(insight)

# ==========================================
# 3. REGISTRO DIÁRIO
# ==========================================
def render_daily_log(db):
    st.title("📝 Registro do Dia")
    
    existing = db.get_daily_log()
    
    with st.form("daily_log"):
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### ⚖️ Medidas")
            weight = st.number_input("Peso (kg)", 30.0, 300.0, 
                                   existing["weight_kg"] if existing and existing.get("weight_kg") else None, 0.1)
            waist = st.number_input("Cintura (cm)", 40.0, 200.0,
                                  existing["waist_cm"] if existing and existing.get("waist_cm") else None, 0.1)
            
            st.markdown("##### 🏃 Atividade")
            steps = st.number_input("Passos", 0, 50000, 
                                  existing["steps"] if existing and existing.get("steps") else 0, 100)
            exercise = st.number_input("Exercício (min)", 0, 300,
                                     existing["exercise_minutes"] if existing and existing.get("exercise_minutes") else 0)
        
        with c2:
            st.markdown("##### 💧 Hidratação")
            water = st.slider("Água (Litros)", 0.0, 5.0,
                            existing["water_intake_liters"] if existing and existing.get("water_intake_liters") else 1.5, 0.1)
            
            st.markdown("##### 😴 Sono")
            sleep = st.slider("Horas de Sono", 0.0, 12.0,
                            existing["sleep_hours"] if existing and existing.get("sleep_hours") else 7.0, 0.5)
            sleep_q = st.select_slider("Qualidade", options=[1,2,3,4,5],
                                     value=existing["sleep_quality"] if existing and existing.get("sleep_quality") else 3)            
            st.markdown("##### 😊 Bem-estar")
            mood = st.selectbox("Humor", ["Feliz", "Neutro", "Triste", "Ansioso", "Cansado"],
                              index=0 if not existing else ["Feliz", "Neutro", "Triste", "Ansioso", "Cansado"].index(existing.get("mood", "Feliz")))
            stress = st.select_slider("Estresse (1-10)", options=list(range(1,11)),
                                    value=existing["stress_level"] if existing and existing.get("stress_level") else 5)
        
        if st.form_submit_button("💾 Salvar Registro"):
            log = {
                "log_date": date.today().isoformat(),
                "weight_kg": weight, "waist_cm": waist,
                "water_intake_liters": water, "sleep_hours": sleep, "sleep_quality": sleep_q,
                "mood": mood, "stress_level": stress,
                "steps": steps, "exercise_minutes": exercise
            }
            if db.save_daily_log(log):
                st.success("✅ Registro salvo! Seus dados alimentam as análises.")
                st.balloons()
            else:
                st.error("Erro ao salvar.")

# ==========================================
# 4. PERFIL
# ==========================================
def render_profile(db, profile):
    st.title("👤 Meu Perfil")
    
    # Métricas calculadas
    bmi = AnalyticsEngine.calculate_bmi(profile.get("current_weight_kg"), profile.get("height_cm"))
    bmi_cat, bmi_icon = AnalyticsEngine.get_bmi_category(bmi)
    tmb = AnalyticsEngine.calculate_tmb(profile.get("current_weight_kg"), profile.get("height_cm"),
                                       profile.get("age"), profile.get("gender"), profile.get("activity_level"))
    
    c1, c2, c3 = st.columns(3)
    c1.metric(f"IMC {bmi_icon}", f"{bmi if bmi else '-'}", bmi_cat)
    c2.metric("🔥 TMB", f"{tmb if tmb else '-'} kcal", "Gasto em repouso")
    c3.metric("🎯 Meta", f"{profile.get('goal_weight_kg', '-')} kg")
    
    st.divider()
    
    with st.form("profile_update"):
        st.markdown("##### ⚙️ Atualizar Dados")
        c1, c2 = st.columns(2)
        with c1:
            new_weight = st.number_input("Peso Atual (kg)", 30.0, 300.0, 
                                       float(profile.get("current_weight_kg") or 70), 0.1)
            new_goal = st.number_input("Peso Meta (kg)", 30.0, 300.0,
                                     float(profile.get("goal_weight_kg") or 65), 0.1)
        with c2:
            new_activity = st.selectbox("Nível de Atividade",                                       ["Sedentario", "Leve", "Moderado", "Intenso"],
                                      index=["Sedentario", "Leve", "Moderado", "Intenso"].index(
                                          profile.get("activity_level", "Sedentario")))
            new_goal_type = st.selectbox("Objetivo", 
                                       ["Perder Peso", "Ganhar Massa", "Manter", "Saude"],
                                       index=["Perder Peso", "Ganhar Massa", "Manter", "Saude"].index(
                                           profile.get("goal_type", "Perder Peso")))
        
        if st.form_submit_button("💾 Atualizar Perfil"):
            db.update_profile({
                "current_weight_kg": new_weight, "goal_weight_kg": new_goal,
                "activity_level": new_activity, "goal_type": new_goal_type
            })
            st.success("Perfil atualizado! As análises serão recalculadas.")
            st.rerun()

# ==========================================
# DADOS DEMO (Para demonstração)
# ==========================================
def _generate_demo_logs():
    """Gera 30 dias de dados realistas para demonstração"""
    import random
    logs = []
    base_date = date.today()
    
    for i in range(30):
        day = base_date - timedelta(days=29-i)
        # Peso decrescente com variação
        weight = 78.0 - (i * 0.05) + random.uniform(-0.2, 0.2)
        
        logs.append({
            "log_date": day.isoformat(),
            "weight_kg": round(weight, 1),
            "waist_cm": round(92 - (i * 0.1) + random.uniform(-0.5, 0.5), 1),
            "water_intake_liters": round(random.uniform(1.5, 3.0), 1),
            "sleep_hours": round(random.uniform(6, 9), 1),
            "sleep_quality": random.randint(3, 5),
            "energy_level": random.randint(5, 10),
            "stress_level": random.randint(2, 6),
            "mood": random.choice(["Feliz", "Neutro", "Feliz", "Feliz", "Neutro"]),
            "steps": random.randint(3000, 12000),
            "exercise_minutes": random.choice([0, 0, 0, 30, 45, 60])
        })
    
    return logs