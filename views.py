import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

# Import seguro
try:
    from utils.analytics import AnalyticsEngine
except ImportError:
    st.error("Erro: utils/analytics.py não encontrado ou com erro.")
    st.stop()

# ==========================================
# 1. ONBOARDING (Tela de Cadastro Completo)
# ==========================================
def render_onboarding(db, profile):
    st.title("👋 Complete seu Perfil")
    st.caption("Precisamos destes dados para calcular suas metas e análises.")
    
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
# 2. DASHBOARD ANALYTICS
# ==========================================
def render_dashboard(db, profile, is_demo):
    st.title(" Painel de Analytics")
        # KPIs
    bmi = AnalyticsEngine.calculate_bmi(profile.get("current_weight_kg"), profile.get("height_cm"))
    bmi_cat, bmi_icon = AnalyticsEngine.get_bmi_category(bmi)
    tmb = AnalyticsEngine.calculate_tmb(profile.get("current_weight_kg"), profile.get("height_cm"), 
                                        profile.get("age"), profile.get("gender"), profile.get("activity_level"))
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Nível", profile.get("level", 1))
    c2.metric(f"IMC {bmi_icon}", f"{bmi if bmi else '-'}", bmi_cat)
    c3.metric("🔥 TMB", f"{int(tmb) if tmb else '-'} kcal")
    c4.metric(" Streak", f"{profile.get('streak_days', 0)} dias")
    
    st.divider()
    
    # Dados
    if is_demo:
        logs = _generate_demo_logs()
    else:
        logs = db.get_logs_history(60)
        
    if not logs:
        st.info("📝 Registre seus dados em 'Registro do Dia' para ver os gráficos!")
        return

    df = pd.DataFrame(logs)
    df['log_date'] = pd.to_datetime(df['log_date']).dt.date
    
    # Gráfico de Peso
    st.subheader("📈 Evolução do Peso")
    weight_df = df.dropna(subset=['weight_kg']).sort_values('log_date')
    
    if len(weight_df) >= 3:
        trend = AnalyticsEngine.calculate_weight_trend(logs)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weight_df['log_date'], y=weight_df['weight_kg'],
            mode='lines+markers', name='Peso Real',
            line=dict(color='#00b894', width=3), marker=dict(size=6)
        ))
        
        if trend:
            fig.add_trace(go.Scatter(
                x=weight_df['log_date'],
                y=[trend['slope'] * (d.toordinal() - weight_df['log_date'].min().toordinal()) + weight_df['weight_kg'].iloc[0] 
                   for d in weight_df['log_date']],
                mode='lines', name='Tendência', line=dict(color='#0984e3', dash='dash')
            ))
            st.caption(f"📊 Tendência: {trend['trend_text']} (R² = {trend['r_squared']})")
                fig.update_layout(xaxis_title="Data", yaxis_title="Peso (kg)", height=300, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Registre mais dias de peso para ver a tendência.")

    # Heatmap de Consistência
    st.subheader(" Consistência de Registro")
    heatmap_data = []
    today = date.today()
    
    for i in range(28):
        check_date = today - timedelta(days=i)
        count = len(df[df['log_date'] == check_date])
        heatmap_data.append({'date': check_date, 'count': count})
        
    hm_df = pd.DataFrame(heatmap_data)
    hm_df['weekday'] = hm_df['date'].dt.day_name()
    hm_df['week'] = hm_df['date'].dt.isocalendar().week
    
    pivot = hm_df.pivot_table(index='weekday', columns='week', values='count', aggfunc='sum').fillna(0)
    week_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = pivot.reindex(week_order)
    
    fig_heat = px.imshow(pivot, aspect="auto", color_continuous_scale="Viridis", labels=dict(x="Semana", y="Dia", color="Registros"))
    fig_heat.update_xaxes(side="top")
    st.plotly_chart(fig_heat, use_container_width=True)

    # Métricas de Estilo de Vida
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        avg_sleep = df['sleep_hours'].mean() if 'sleep_hours' in df.columns else 0
        st.metric("😴 Sono Médio", f"{avg_sleep:.1f}h")
        st.progress(min(avg_sleep / 8.0, 1.0))
    with c2:
        avg_water = df['water_intake_liters'].mean() if 'water_intake_liters' in df.columns else 0
        st.metric("💧 Água Média", f"{avg_water:.1f}L")
        st.progress(min(avg_water / 2.5, 1.0))

# ==========================================
# 3. REGISTRO DIÁRIO
# ==========================================
def render_daily_log(db):
    st.title("📝 Registro do Dia")
    existing = db.get_daily_log()
    
    with st.form("daily_form"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ⚖️ Medidas")            weight = st.number_input("Peso (kg)", 30.0, 300.0, float(existing.get("weight_kg", 0)) if existing else 0.0, 0.1)
            waist = st.number_input("Cintura (cm)", 40.0, 200.0, float(existing.get("waist_cm", 0)) if existing else 0.0, 0.1)
            st.markdown("####  Atividade")
            steps = st.number_input("Passos", 0, 50000, int(existing.get("steps", 0)) if existing else 0)
            exercise = st.number_input("Minutos de Exercício", 0, 300, int(existing.get("exercise_minutes", 0)) if existing else 0)
        with c2:
            st.markdown("#### 💧 Estilo de Vida")
            water = st.slider("Água (Litros)", 0.0, 5.0, float(existing.get("water_intake_liters", 1.5)) if existing else 1.5, 0.1)
            sleep = st.slider("Sono (Horas)", 0.0, 12.0, float(existing.get("sleep_hours", 7.0)) if existing else 7.0, 0.5)
            st.markdown("####  Humor")
            mood = st.selectbox("Humor", ["Feliz", "Neutro", "Triste", "Ansioso", "Cansado"])
            stress = st.slider("Estresse (1-10)", 1, 10, int(existing.get("stress_level", 5)) if existing else 5)
        
        if st.form_submit_button(" Salvar Registro"):
            log = {
                "log_date": date.today().isoformat(),
                "weight_kg": weight, "waist_cm": waist,
                "water_intake_liters": water, "sleep_hours": sleep,
                "mood": mood, "stress_level": stress,
                "steps": steps, "exercise_minutes": exercise
            }
            if db.save_daily_log(log):
                st.success("✅ Salvo com sucesso!")
                st.balloons()
            else:
                st.error("Erro ao salvar.")

# ==========================================
# 4. PERFIL
# ==========================================
def render_profile(db, profile):
    st.title("👤 Meu Perfil")
    bmi = AnalyticsEngine.calculate_bmi(profile.get("current_weight_kg"), profile.get("height_cm"))
    bmi_cat, _ = AnalyticsEngine.get_bmi_category(bmi)
    st.info(f"Seu IMC é **{bmi}** ({bmi_cat})")
    
    with st.form("profile_update"):
        c1, c2 = st.columns(2)
        with c1:
            new_weight = st.number_input("Peso Atual (kg)", value=float(profile.get("current_weight_kg", 70)), step=0.1)
            new_goal = st.number_input("Meta de Peso (kg)", value=float(profile.get("goal_weight_kg", 65)), step=0.1)
        with c2:
            new_act = st.selectbox("Atividade", ["Sedentario", "Leve", "Moderado", "Intenso"], 
                                 index=["Sedentario", "Leve", "Moderado", "Intenso"].index(profile.get("activity_level", "Sedentario")))
            new_goal_type = st.selectbox("Objetivo", ["Perder Peso", "Ganhar Massa", "Manter", "Saude"],
                                       index=["Perder Peso", "Ganhar Massa", "Manter", "Saude"].index(profile.get("goal_type", "Perder Peso")))
            
        if st.form_submit_button("Atualizar"):
            db.update_profile({
                "current_weight_kg": new_weight, "goal_weight_kg": new_goal,                "activity_level": new_act, "goal_type": new_goal_type
            })
            st.success("Perfil atualizado!")
            st.rerun()

# ==========================================
# DADOS DEMO
# ==========================================
def _generate_demo_logs():
    logs = []
    base = date.today()
    for i in range(30):
        day = base - timedelta(days=29-i)
        logs.append({
            "log_date": day.isoformat(),
            "weight_kg": 80.0 - (i * 0.1),
            "waist_cm": 90 - (i * 0.05),
            "water_intake_liters": 2.0,
            "sleep_hours": 7.5,
            "mood": "Feliz",
            "stress_level": 4,
            "steps": 5000,
            "exercise_minutes": 30
        })
    return logs