import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from utils.food_db import FOOD_DB, COMBOS

# Para garantir que o app.py consiga importar a função de CSS
__all__ = ["load_css", "render_onboarding", "render_dashboard", "render_meals", "render_weight", "render_behavior", "render_subscription"]

def load_css():
    try:
        with open('assets/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass

def render_onboarding(nutrition, user):
    load_css()
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <h1 style="font-size: 3rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                💪 EmagreSim
            </h1>
            <p style="color: #6b7280; margin-top: 1rem;">Transforme sua jornada de emagrecimento em um jogo!</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="modern-card" style="background: linear-gradient(135deg, #667eea, #764ba2);">', unsafe_allow_html=True)
        st.markdown("### 📊 Dados Iniciais")
        weight = st.number_input("Peso atual (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
        height = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170, step=1)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="modern-card" style="background: linear-gradient(135deg, #f093fb, #f5576c);">', unsafe_allow_html=True)
        st.markdown("### 🎯 Objetivos")
        age = st.number_input("Idade", min_value=10, max_value=120, value=30, step=1)
        goal = st.number_input("Peso desejado (kg)", min_value=30.0, max_value=300.0, value=65.0, step=0.5)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    if weight and height:
        bmi = weight / ((height/100) ** 2)
        if bmi < 18.5: bmi_status, bmi_color = "Abaixo do peso", "#3498db"
        elif bmi < 25: bmi_status, bmi_color = "Peso normal", "#2ecc71"
        elif bmi < 30: bmi_status, bmi_color = "Sobrepeso", "#f39c12"
        else: bmi_status, bmi_color = "Obesidade", "#e74c3c"
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 16px;">
                <h4>Seu IMC: <span style="color: {bmi_color}; font-weight: bold;">{bmi:.1f}</span></h4>
                <p>{bmi_status}</p>
            </div>
            """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Começar Jornada", use_container_width=True):
            user["weight"] = weight; user["height"] = height; user["age"] = age
            user["goal_weight"] = goal; user["onboarded"] = True
            st.session_state.user = user
            return True
    st.markdown('</div>', unsafe_allow_html=True)
    return False

def render_dashboard(nutrition, behavior, user):
    load_css()
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    plan_badge = " PRO" if user.get("plan") != "free" else "🎁 GRÁTIS"
    plan_color = "#f59e0b" if user.get("plan") != "free" else "#6b7280"
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h1 style="margin: 0;">📊 Dashboard</h1>
        <span style="background: {plan_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px;">{plan_badge}</span>
    </div>
    """, unsafe_allow_html=True)
    
    today_data = nutrition.get_daily_summary()
    streak = behavior.calculate_streak()
    weekly_df = nutrition.get_weekly_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{today_data['cal']}</div><div class="metric-label">🔥 Calorias hoje</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{today_data['count']}</div><div class="metric-label">🍽️ Refeições</div></div>""", unsafe_allow_html=True)
    with col3:
        emoji = "" if streak > 0 else ""
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{emoji} {streak}</div><div class="metric-label">Dias de sequência</div></div>""", unsafe_allow_html=True)
    with col4:
        meta_perda = max(0, user.get("goal_weight", user.get("weight", 70)) - user.get("weight", 70))
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{meta_perda:.1f} kg</div><div class="metric-label"> Faltam para meta</div></div>""", unsafe_allow_html=True)
    
    goal_cal = 2000
    msg = behavior.get_motivation_message(streak, today_data['cal'], goal_cal)
    st.info(f"✨ {msg}")
    
    if not weekly_df.empty:
        st.subheader("📈 Evolução Semanal")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weekly_df['date'], y=weekly_df['calories'], mode='lines+markers', name='Calorias', line=dict(color='#667eea', width=3), marker=dict(size=8, color='#764ba2')))
        fig.update_layout(plot_bgcolor='white', xaxis_title="Data", yaxis_title="Calorias (kcal)", hovermode='x unified', height=400)
        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("💡 Insights Personalizados")
    meals = nutrition.db.get_meals(days=30)
    insights = behavior.get_insights(meals)
    for insight in insights:
        st.markdown(f"- {insight}")
    
    if today_data['meals']:
        st.subheader("🍽️ Últimas Refeições")
        for meal in today_data['meals'][-5:]:
            emotion_icon = "😊" if meal.get("emotion") == "Hábito" else "😟" if meal.get("emotion") == "Ansiedade" else "🍽️"
            st.markdown(f"""<div style="background: #f8f9fa; border-radius: 12px; padding: 0.75rem; margin-bottom: 0.5rem;"><b>{emotion_icon} {meal['food']}</b> - {meal['cal']} kcal <span style="color: #6b7280; font-size: 0.875rem;">({meal.get('emotion', 'Hábito')})</span></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_meals(nutrition, behavior, user):
    load_css()
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title(" Registrar Refeição")
    today_data = nutrition.get_daily_summary()
    meta_cal = 2000
    percent = min(100, int((today_data['cal'] / meta_cal) * 100))
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>Progresso de hoje</span>
            <span>{today_data['cal']} / {meta_cal} kcal ({percent}%)</span>
        </div>
        <div class="progress-container"><div class="progress-bar" style="width: {percent}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Alimentos", "🍽️ Combos", "📊 Análise"])
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            food_items = list(FOOD_DB.keys())
            food_display = {k: f"{v['name']} - {v['cal']} kcal | P:{v['p']}g" for k, v in FOOD_DB.items()}
            selected_food = st.selectbox("🍎 Escolha o alimento", food_items, format_func=lambda x: food_display[x])
            qty = st.slider("Quantidade", 0.5, 3.0, 1.0, 0.5, help="Ex: 1 = porção padrão, 0.5 = meia porção")
            emotion = st.selectbox("🎭 Como você estava se sentindo?", ["Hábito", "Fome", "Ansiedade", "Tédio", "Felicidade", "Estresse"], help="Isso nos ajuda a entender seus padrões alimentares")
            if st.button("✅ Registrar Refeição", use_container_width=True):
                success, name, calories = nutrition.register_food(selected_food, qty, emotion)
                if success:
                    st.success(f"🍽️ {name} registrado! +{calories} kcal")
                    st.balloons()
                    st.rerun()
        with col2:
            st.markdown("""<div class="modern-card" style="background: linear-gradient(135deg, #43e97b, #38f9d7);"><h4>💡 Dica Rápida</h4><p style="font-size: 0.875rem;">Use os combos prontos para refeições completas e economizar tempo!</p></div>""", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("🍽️ Combos Prontos")
        st.markdown("""<p style="color: #6b7280; margin-bottom: 1rem;">Refeições pré-montadas baseadas em hábitos brasileiros</p>""", unsafe_allow_html=True)
        combo_list = list(COMBOS.keys())
        cols = st.columns(len(combo_list))
        for idx, combo_id in enumerate(combo_list):
            combo = COMBOS[combo_id]
            with cols[idx]:
                st.markdown(f"""<div class="metric-card" style="height: 100%;"><h4>{combo['name']}</h4><p style="font-size: 0.75rem; color: #6b7280;">{', '.join([FOOD_DB[item]['name'] for item in combo['items']])}</p></div>""", unsafe_allow_html=True)
                if st.button(f"Usar {combo['name']}", key=f"combo_{combo_id}"):
                    success, name, calories = nutrition.register_combo(combo_id, "Hábito")
                    if success:
                        st.success(f"️ {name} registrado! +{calories} kcal")
                        st.balloons()
                        st.rerun()
    with tab3:
        st.subheader("📊 Análise Comportamental")
        meals = nutrition.db.get_meals(days=30)
        if meals:
            emotions = {}
            for m in meals:
                emo = m.get("emotion", "Não informado")
                emotions[emo] = emotions.get(emo, 0) + 1
            if emotions:
                fig = px.pie(values=list(emotions.values()), names=list(emotions.keys()), title="Distribuição por Estado Emocional", color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Registre mais refeições para ver análises detalhadas!")
    st.markdown('</div>', unsafe_allow_html=True)

def render_weight(nutrition, user):
    load_css()
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("⚖️ Acompanhamento de Peso")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="modern-card" style="background: linear-gradient(135deg, #4facfe, #00f2fe);"><h3>Registrar Peso</h3></div>""", unsafe_allow_html=True)
        current_weight = user.get("weight", 70.0)
        new_weight = st.number_input("Peso atual (kg)", min_value=30.0, max_value=300.0, value=float(current_weight), step=0.1)
        notes = st.text_area("Observações (opcional)", placeholder="Ex: Pós-treino, manhã, etc...")
        if st.button(" Salvar Registro", use_container_width=True):
            nutrition.db.save_weight({"val": new_weight, "date": str(date.today()), "notes": notes})
            user["weight"] = new_weight
            st.session_state.user = user
            st.success("Peso registrado com sucesso!")
            st.rerun()
    with col2:
        st.markdown("""<div class="modern-card" style="background: linear-gradient(135deg, #fa709a, #fee140);"><h3>📊 Histórico</h3></div>""", unsafe_allow_html=True)
        weights_df = nutrition.db.get_weights(days=30)
        if not weights_df.empty:
            initial = weights_df.iloc[0]['val']
            current = weights_df.iloc[-1]['val']
            change = current - initial
            col_a, col_b = st.columns(2)
            with col_a: st.metric("Peso inicial", f"{initial:.1f} kg")
            with col_b: st.metric("Peso atual", f"{current:.1f} kg", delta=f"{change:+.1f} kg", delta_color="inverse")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=weights_df['date'], y=weights_df['val'], mode='lines+markers', name='Peso', line=dict(color='#667eea', width=3), marker=dict(size=8, color='#764ba2')))
            fig.update_layout(title="Evolução do Peso", plot_bgcolor='white', xaxis_title="Data", yaxis_title="Peso (kg)", height=300)
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("📋 Ver todos os registros"):
                st.dataframe(weights_df.sort_values('date', ascending=False), use_container_width=True)
        else:
            st.info("Nenhum registro de peso ainda. Comece registrando seu peso hoje!")
    st.markdown('</div>', unsafe_allow_html=True)

def render_behavior(behavior, user):
    load_css()
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("🧠 Perfil Comportamental")
    st.subheader("🏆 Conquistas")
    achievements = behavior.db.get_achievements()
    if achievements:
        cols = st.columns(3)
        for idx, ach in enumerate(achievements):
            with cols[idx % 3]:
                st.markdown(f"""<div class="metric-card"><div style="font-size: 2rem;">🎖️</div><div style="font-weight: 600;">{ach['title']}</div><div style="font-size: 0.75rem; color: #6b7280;">{ach['date']}</div></div>""", unsafe_allow_html=True)
    else:
        st.info("Complete desafios para desbloquear conquistas!")
    st.subheader("📊 Estatísticas de Consistência")
    meals = behavior.db.get_meals(days=90)
    total_days = len(set(m.get("date") for m in meals if m.get("date")))
    streak = behavior.calculate_streak(meals)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{total_days}</div><div class="metric-label">Dias ativos</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">🔥 {streak}</div><div class="metric-label">Maior sequência</div></div>""", unsafe_allow_html=True)
    with col3:
        consistency = (total_days / 90) * 100 if total_days > 0 else 0
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{consistency:.0f}%</div><div class="metric-label">Consistência (90 dias)</div></div>""", unsafe_allow_html=True)
    st.subheader("💡 Dicas para você")
    import random
    tips = [" Experimente preparar marmitas no domingo", " Beba um copo d'água antes de cada refeição", "📱 Use o app sempre no mesmo horário", "🎯 Comece com pequenas metas alcançáveis", "😴 Durma bem - isso afeta diretamente a fome"]
    st.info(f"✨ {random.choice(tips)}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_subscription(payment, user):
    load_css()
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("💳 Upgrade de Plano")
    if user.get("plan") == "pro":
        st.success("🎉 Você já é assinante PRO! Obrigado por apoiar o EmagreSim.")
        return
    st.markdown("""<p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">Desbloqueie recursos exclusivos e acelere seus resultados!</p>""", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, (key, plan) in enumerate(payment.PLANS.items()):
        with cols[idx]:
            is_pro = key != "start"
            border_color = "#f59e0b" if is_pro else "#e5e7eb"
            st.markdown(f"""<div style="border: 2px solid {border_color}; border-radius: 20px; padding: 1.5rem; text-align: center; height: 100%;"><h3>{plan['name']}</h3><div style="font-size: 2rem; font-weight: bold; margin: 1rem 0;">R$ {plan['price']:.2f}</div><div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1rem;">{'/mês' if plan.get('monthly', True) else 'único'}</div>""", unsafe_allow_html=True)
            for feature in plan['features']:
                st.markdown(f"✅ {feature}")
            if st.button(f"Assinar {plan['name']}", key=f"plan_{key}", use_container_width=True):
                link = payment.create_preference(key, user["id"])
                if link:
                    if "DEMO" in link:
                        st.success("🎉 Modo Demo: Assinatura ativada!")
                        user["plan"] = "pro"
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.markdown(f"[🔗 Ir para o pagamento]({link})")
                        st.info("Após o pagamento, você será redirecionado automaticamente.")
            st.markdown('</div>', unsafe_allow_html=True)
    with st.expander("❓ Dúvidas frequentes"):
        st.markdown("""**Como funciona o período de teste?** > Oferecemos 7 dias de teste grátis do Plano Pro! **Posso cancelar a qualquer momento?** > Sim, você pode cancelar diretamente no Mercado Pago. **O que acontece se eu cancelar?** > Você mantém acesso até o fim do período já pago.""")
    payment_id = st.query_params.get("payment_id")
    status = st.query_params.get("collection_status")
    if payment_id:
        if payment.process_return(user, payment_id, status):
            st.success("✅ Pagamento confirmado! Seu plano foi atualizado.")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
