import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
from utils.calculations import AnalyticsEngine

# ==========================================
# 1. TELA DE ONBOARDING
# ==========================================
def render_onboarding(db, profile):
    st.title("👋 Bem-vindo! Configure seu Perfil")
    st.caption("Precisamos destes dados para calcular suas metas e análises.")
    
    with st.form("onboarding"):
        c1, c2 = st.columns(2)
        with c1:
            dob = st.date_input("Data de Nascimento", value=datetime(1990, 1, 1))
            age = (datetime.today() - datetime.combine(dob, datetime.min.time())).days // 365
            st.number_input("Idade (calculada)", value=age, disabled=True)
            height = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170)
            gender = st.radio("Gênero", ["M", "F", "Other"])
        
        with c2:
            current_w = st.number_input("Peso Atual (kg)", min_value=30.0, max_value=300.0, value=70.0)
            goal_w = st.number_input("Peso Meta (kg)", min_value=30.0, max_value=300.0, value=65.0)
            
            st.markdown("📏 **Circunferência Abdominal**")
            st.markdown("_Coloque a fita na altura do umbigo._")
            waist = st.number_input("Abdômen (cm)", min_value=40.0, max_value=200.0, value=80.0)
            
            activity = st.selectbox("Nível de Atividade", ["Sedentario", "Leve", "Moderado", "Intenso"])
            goal = st.selectbox("Objetivo", ["Perder Peso", "Ganhar Massa", "Manter", "Saude"])

        if st.form_submit_button("✅ Salvar e Iniciar Jornada"):
            db.update_profile({
                "date_of_birth": dob.isoformat(), "age": age, "height_cm": height, "gender": gender,
                "current_weight_kg": current_w, "goal_weight_kg": goal_w, "activity_level": activity,
                "goal_type": goal, "is_onboarding_complete": True
            })
            return True
    return False

# ==========================================
# 2. DASHBOARD ANALÍTICO
# ==========================================
def render_dashboard(db, profile, is_demo):
    st.title("📊 Painel de Controle")
    
    # Header com KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(" Nível", profile.get("level", 1))
    c2.metric("⚡ XP", profile.get("experience", 0))
    c3.metric("⚖️ Peso", f"{profile.get('current_weight_kg', 0)} kg")
    c4.metric(" Streak", f"{profile.get('streak_days', 0)} dias")
    
    st.divider()
    
    # Análise Principal (Peso)
    st.subheader(" Evolução do Peso")
    
    if is_demo:
        # Dados Fake para Demo
        dates = pd.date_range(end=date.today(), periods=30).strftime('%Y-%m-%d').tolist()
        weights = [80.0 - (i*0.1) for i in range(30)] # Perda gradual
        df = pd.DataFrame({"log_date": dates, "weight_kg": weights})
    else:
        logs = db.get_logs_history(30)
        df = pd.DataFrame(logs)
    
    if not df.empty:
        fig = px.line(df, x="log_date", y="weight_kg", markers=True, title="Últimos 30 Dias")
        fig.update_layout(xaxis_title="Data", yaxis_title="Peso (kg)", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registre seu peso diariamente para ver o gráfico!")

    # Gráficos Secundários (Correlações)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💧 Hidratação vs Humor")
        # Simulação visual
        fig_bar = px.bar(
            x=["Seg", "Ter", "Qua", "Qui", "Sex"],
            y=[2.0, 1.5, 3.0, 2.2, 2.8],
            color=["Baixo", "Médio", "Alto", "Alto", "Alto"],
            title="Água vs Humor (Exemplo)",
            labels={'x':'Dia da Semana', 'y':'Litros'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader(" Medidas Corporais")
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[profile.get("current_weight_kg", 70), profile.get("height_cm", 170)/2, 80, 30, 50],
            theta=['Peso', 'Altura/2', 'Abdômen', 'Sono', 'Energia'],
            fill='toself', name='Atual'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig_radar, use_container_width=True)

# ==========================================
# 3. REGISTRO DIÁRIO
# ==========================================
def render_daily_log(db):
    st.title("📝 Registro do Dia")
    st.caption(f"Data: {date.today().strftime('%d/%m/%Y')}")
    
    # Verifica se já existe log de hoje
    existing_log = db.get_daily_log()
    
    with st.form("daily_log"):
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("⚖️ **Medidas**")
            weight = st.number_input("Peso (kg)", value=existing_log["weight_kg"] if existing_log else None)
            waist = st.number_input("Abdômen (cm)", value=existing_log["waist_cm"] if existing_log else None)
            
            st.markdown("🏃 **Atividade**")
            steps = st.number_input("Passos", step=100, value=existing_log["steps"] if existing_log else 0)
            exercise = st.number_input("Minutos de Exercício", value=existing_log["exercise_minutes"] if existing_log else 0)

        with c2:
            st.markdown("💧 **Hidratação & Sono**")
            water = st.slider("Água (Litros)", 0.0, 5.0, existing_log["water_intake_liters"] if existing_log else 1.5, 0.1)
            sleep = st.slider("Sono (Horas)", 0.0, 12.0, existing_log["sleep_hours"] if existing_log else 7.0, 0.5)
            
            st.markdown("😊 **Bem-estar**")
            mood = st.selectbox("Humor", ["Feliz", "Neutro", "Triste", "Ansioso", "Cansado"], index=0)
            stress = st.slider("Estresse (1-10)", 1, 10, existing_log["stress_level"] if existing_log else 5)

        if st.form_submit_button("💾 Salvar Registro"):
            log_data = {
                "log_date": date.today().isoformat(),
                "weight_kg": weight, "waist_cm": waist,
                "water_intake_liters": water, "sleep_hours": sleep,
                "mood": mood, "stress_level": stress,
                "steps": steps, "exercise_minutes": exercise
            }
            success = db.save_daily_log(log_data)
            if success: st.success("✅ Registro salvo com sucesso!"); st.balloons()
            else: st.error("Erro ao salvar.")

# ==========================================
# 4. PERFIL
# ==========================================
def render_profile(db, profile):
    st.title("👤 Meu Perfil")
    
    # Métricas Calculadas
    bmi = AnalyticsEngine.calculate_bmi(profile.get("current_weight_kg"), profile.get("height_cm"))
    cat, icon = AnalyticsEngine.get_bmi_category(bmi)
    tmb = AnalyticsEngine.calculate_tmb(profile.get("current_weight_kg"), profile.get("height_cm"), profile.get("age"), profile.get("gender"), profile.get("activity_level"))
    
    st.markdown(f"### 📊 Seus Números")
    c1, c2, c3 = st.columns(3)
    c1.metric(f"IMC {icon}", f"{bmi}", f"{cat}")
    c2.metric("TMB", f"{tmb} kcal", "Gasto em repouso")
    c3.metric("Meta", f"{profile.get('goal_weight_kg', 0)} kg")
    
    st.divider()
    
    with st.form("profile_update"):
        st.markdown("### ⚙️ Configurações")
        new_goal = st.number_input("Nova Meta de Peso", value=profile.get("goal_weight_kg"))
        new_act = st.selectbox("Nível de Atividade", ["Sedentario", "Leve", "Moderado", "Intenso"], index=["Sedentario", "Leve", "Moderado", "Intenso"].index(profile.get("activity_level")))
        
        if st.form_submit_button("Atualizar Perfil"):
            db.update_profile({"goal_weight_kg": new_goal, "activity_level": new_act})
            st.success("Perfil atualizado!")
            st.rerun()
