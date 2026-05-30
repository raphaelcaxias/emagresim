import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta

# CORREÇÃO: Importando do arquivo 'calculations' que você tem na pasta utils
from utils.calculations import AnalyticsEngine

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

def render_dashboard(db, profile, is_demo):
    st.title("📊 Painel de Analytics")
    
    bmi = AnalyticsEngine.calculate_bmi(profile.get("current_weight_kg"), profile.get("height_cm"))
    bmi_cat, bmi_icon = AnalyticsEngine.get_bmi_category(bmi)
    tmb = AnalyticsEngine.calculate_tmb(profile.get("current_weight_kg"), profile.get("height_cm"), 
                                        profile.get("age"), profile.get("gender"), profile.get("activity_level"))
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(" Nível", profile.get("level", 1))
    c2.metric(f"IMC {bmi_icon}", f"{bmi if bmi else '-'}", bmi_cat)
    c3.metric(" TMB", f"{int(tmb) if tmb else '-'} kcal")
    c4.metric("🔥 Streak", f"{profile.get('streak_days', 0)} dias")
    
    st.divider()
    
    if is_demo:
        logs = _generate_demo_logs()
    else:
        logs = db.get_logs_history(60)
        
    if not logs:
        st.info("📝 Registre seus dados em 'Registro do Dia' para ver os gráficos!")
        return

    df = pd.DataFrame(logs)
    df['log_date'] = pd.to_datetime(df['log_date']).dt.date
    
    st.subheader("📈 Evolução do Peso")
    weight_df = df.dropna(subset=['weight_kg']).sort_values('log_date')
    
    if len(weight_df) >= 3:
        trend = AnalyticsEngine.calculate_weight_trend(logs)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weight_df['log_date'], y=weight_df['weight_kg'],
            mode='lines+markers', name='Peso Real',
            line=dict(color='#00b894', width=3), marker=dict(size=