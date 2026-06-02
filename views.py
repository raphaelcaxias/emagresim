import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
import random
from utils.food_db import FOOD_DB, COMBOS

__all__ = [
    "load_css", "render_login", "render_onboarding", "render_dashboard",
    "render_meals", "render_weight", "render_behavior", "render_subscription"
]

def load_css():
    try:
        with open('assets/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception:
        pass

def render_login(db):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💪 EmagreSim</h1>
        <p style="color: #6b7280;">Transforme sua jornada de emagrecimento em um jogo!</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
    
    with tab1:
        login_email = st.text_input("Email", key="login_email", placeholder="seu@email.com")
        login_password = st.text_input("Senha", type="password", key="login_pass", placeholder="••••••••")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Entrar", use_container_width=True, type="primary"):
                users = st.session_state.mock_db.get("users", {})
                if login_email in users and users[login_email].get("password") == login_password:
                    st.session_state.user = {**users[login_email], "onboarded": False, "plan": "free"}
                    st.toast(f"Bem-vindo de volta, {users[login_email].get('name')}! 🎉", icon="👋")
                    st.rerun()
                else:
                    st.error("❌ Email ou senha incorretos")
        
        with col2:
            if st.button("🎮 Modo Demo", use_container_width=True):
                if "demo@emagresim.com" not in st.session_state.mock_db["users"]:                    st.session_state.mock_db["users"]["demo@emagresim.com"] = {
                        "password": "demo123", "name": "Usuário Demo", "email": "demo@emagresim.com", "is_demo": True
                    }
                
                st.session_state.user = {
                    "email": "demo@emagresim.com",
                    "name": "Usuário Demo",
                    "is_demo": True,
                    "onboarded": False,
                    "plan": "free"
                }
                st.toast("Modo demo ativado! Explore o app livremente 🎮", icon="🎉")
                st.rerun()
    
    with tab2:
        new_name = st.text_input("Nome completo", key="reg_name", placeholder="Seu nome")
        new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com")
        new_password = st.text_input("Senha", type="password", key="reg_pass", placeholder="••••••••")
        confirm_password = st.text_input("Confirmar senha", type="password", key="reg_confirm", placeholder="••••••••")
        
        if st.button("📝 Cadastrar", use_container_width=True, type="primary"):
            if not all([new_name, new_email, new_password]):
                st.error("❌ Preencha todos os campos")
            elif new_password != confirm_password:
                st.error("❌ Senhas não conferem")
            else:
                users = st.session_state.mock_db.get("users", {})
                email_key = new_email.lower().strip()
                if email_key in users:
                    st.error("❌ Email já cadastrado")
                else:
                    users[email_key] = {
                        "password": new_password,
                        "name": new_name,
                        "email": email_key,
                        "is_demo": False
                    }
                    st.session_state.mock_db["users"] = users
                    st.toast("Conta criada com sucesso! Faça login 📝", icon="✅")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_onboarding(nutrition, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h2>👋 Vamos começar!</h2>
        <p style="color: #6b7280;">Algumas informações para personalizar sua experiência</p>    </div>
    """, unsafe_allow_html=True)
    
    weight = st.number_input("⚖️ Peso atual (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
    height = st.number_input("📏 Altura (cm)", min_value=100, max_value=250, value=170, step=1)
    age = st.number_input("🎂 Idade", min_value=15, max_value=120, value=30, step=1)
    goal = st.number_input("🎯 Peso desejado (kg)", min_value=30.0, max_value=300.0, value=65.0, step=0.5)
    
    if st.button("🚀 Iniciar Jornada", use_container_width=True, type="primary"):
        user.update({
            "weight": weight, "height": height, "age": age,
            "goal_weight": goal, "onboarded": True, "tdee": 2000
        })
        st.session_state.user = user
        st.toast("Bem-vindo ao EmagreSim! Sua jornada começa agora 🎉", icon="🌟")
        st.balloons()
        return True
    return False

def render_dashboard(nutrition, behavior, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    hora = datetime.now().hour
    saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"
    
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="margin: 0;">📊 Dashboard</h1>
        <p style="color: #6b7280; margin: 0;">{saudacao}, {user.get('name', 'Usuário')}! 👋</p>
    </div>
    """, unsafe_allow_html=True)
    
    data = nutrition.get_daily_summary()
    streak = behavior.calculate_streak()
    goal_cal = user.get("tdee", 2000)
    
    user["streak_display"] = streak
    st.session_state.user = user
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        percent = min(100, int((data['cal'] / goal_cal) * 100))
        st.markdown(f"""
        <div style="background: white; border-radius: 16px; padding: 1rem; text-align: center; border: 1px solid #e5e7eb;">
            <div style="font-size: 1.75rem; font-weight: 700; color: #667eea;">{data['cal']} <span style="font-size: 0.9rem;">/ {goal_cal}</span></div>
            <div style="font-size: 0.75rem; color: #6b7280;">🔥 Calorias</div>
            <div style="background: #e5e7eb; border-radius: 9999px; height: 0.5rem; margin-top: 0.5rem;">
                <div style="background: linear-gradient(90deg, #667eea, #764ba2); width: {percent}%; height: 100%; border-radius: 9999px;"></div>
            </div>        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; border-radius: 16px; padding: 1rem; text-align: center; border: 1px solid #e5e7eb;">
            <div style="font-size: 1.75rem; font-weight: 700; color: #667eea;">{data['count']}</div>
            <div style="font-size: 0.75rem; color: #6b7280;">🍽️ Refeições hoje</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        streak_emoji = "🔥" if streak > 0 else "🌱"
        st.markdown(f"""
        <div style="background: white; border-radius: 16px; padding: 1rem; text-align: center; border: 1px solid #e5e7eb;">
            <div style="font-size: 1.75rem; font-weight: 700; color: #667eea;">{streak_emoji} {streak}</div>
            <div style="font-size: 0.75rem; color: #6b7280;">Dias de sequência</div>
        </div>
        """, unsafe_allow_html=True)
    
    msg = behavior.get_motivation_message(streak, data['cal'], goal_cal)
    st.info(f"✨ {msg}")
    
    weekly = nutrition.get_weekly_summary()
    if not weekly.empty:
        st.subheader("📈 Evolução da Semana")
        fig = px.line(weekly, x='date', y='calories', markers=True, title="Calorias por dia")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=40, b=10),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if data['meals']:
        st.subheader("🍽️ Últimas Refeições")
        cols = st.columns(min(3, len(data['meals'])))
        for idx, meal in enumerate(data['meals'][-3:]):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="background: #f8f9fa; border-radius: 12px; padding: 0.75rem; text-align: center;">
                    <strong>{meal.get('food', '?')}</strong><br>
                    <span style="color: #667eea; font-weight: 600;">{meal.get('cal', 0)} kcal</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_meals(nutrition, behavior, user):    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("🍴 Registrar Refeição")
    
    data = nutrition.get_daily_summary()
    goal_cal = user.get("tdee", 2000)
    percent = min(100, int((data['cal'] / goal_cal) * 100))
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span>Progresso do dia</span>
            <span>{data['cal']} / {goal_cal} kcal</span>
        </div>
        <div style="background: #e5e7eb; border-radius: 9999px; height: 0.5rem; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #667eea, #764ba2); width: {percent}%; height: 100%; border-radius: 9999px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Alimento", "🍽️ Combo Rápido"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Buscar alimento", placeholder="Digite...", key="search_food")
            food_items = list(FOOD_DB.keys())
            
            if search:
                food_items = [f for f in food_items if search.lower() in FOOD_DB[f]['name'].lower()]
            
            if not food_items:
                st.warning("Nenhum alimento encontrado com esse termo.")
                selected_food = None
            else:
                selected_food = st.selectbox(
                    "Selecione",
                    food_items,
                    format_func=lambda x: f"{FOOD_DB[x]['name']} - {FOOD_DB[x]['cal']} kcal"
                )
        
        with col2:
            st.markdown("###")
            qty = st.number_input("Quantidade", min_value=0.5, max_value=3.0, value=1.0, step=0.5)
        
        if selected_food and st.button("✅ Registrar", use_container_width=True, type="primary"):
            ok, name, cal = nutrition.register_food(selected_food, qty, "Hábito")
            if ok:
                st.toast(f"{name} adicionado! +{cal} kcal", icon="🍽️")
                st.rerun()
        with tab2:
        st.markdown("### 🚀 Combos Rápidos")
        cols = st.columns(3)
        for idx, (combo_id, combo) in enumerate(COMBOS.items()):
            with cols[idx]:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 0.75rem; text-align: center; border: 1px solid #e5e7eb;">
                    <h4 style="margin: 0 0 0.25rem 0;">{combo['name']}</h4>
                    <p style="font-size: 0.7rem; color: #6b7280; margin: 0;">
                        {', '.join([FOOD_DB[item]['name'].split()[0] for item in combo['items']])}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Usar", key=f"combo_{combo_id}", use_container_width=True):
                    total_cal = 0
                    for item in combo['items']:
                        ok, name, cal = nutrition.register_food(item, 1, "Hábito")
                        if ok: total_cal += cal
                    st.toast(f"{combo['name']} registrado! +{total_cal} kcal", icon="🍽️")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_weight(nutrition, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("⚖️ Acompanhamento de Peso")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("### Registrar hoje")
        current = user.get("weight", 70.0)
        new_weight = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=float(current), step=0.1)
        if st.button("💾 Salvar", use_container_width=True, type="primary"):
            nutrition.db.save_weight({"val": new_weight, "record_date": str(date.today())})
            user["weight"] = new_weight
            st.session_state.user = user
            st.toast(f"Peso atualizado: {new_weight}kg", icon="⚖️")
            st.rerun()
    
    with col2:
        weights_df = nutrition.db.get_weights(days=30)
        if not weights_df.empty:
            date_col = 'record_date' if 'record_date' in weights_df.columns else 'date'
            weights_df[date_col] = pd.to_datetime(weights_df[date_col])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=weights_df[date_col],
                y=weights_df['val'],                mode='lines+markers',
                name='Peso',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8, color='#764ba2')
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=30, b=10),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Registre seu peso para ver o gráfico de evolução")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_behavior(behavior, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("🧠 Meu Perfil")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👤 Informações")
        st.write(f"**Nome:** {user.get('name', '—')}")
        st.write(f"**Email:** {user.get('email', '—')}")
        st.write(f"**Plano:** {'👑 PRO' if user.get('plan') != 'free' else '🎁 GRÁTIS'}")
    with col2:
        st.markdown("### ⚡ Stats")
        st.write(f"**Peso atual:** {user.get('weight', '—')} kg")
        st.write(f"**Meta:** {user.get('goal_weight', '—')} kg")
    
    st.markdown("---")
    st.subheader("🏆 Conquistas")
    achievements = behavior.db.get_achievements()
    if achievements:
        cols = st.columns(3)
        for idx, ach in enumerate(achievements):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.5rem;">🏅</div>
                    <div style="font-weight: 600; font-size: 0.8rem;">{ach.get('title', 'Conquista')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🏆 Complete seus primeiros registros para desbloquear conquistas!")
    
    st.markdown("---")
    st.subheader("💡 Dicas para você")    tips = [
        "🥗 Experimente preparar marmitas no domingo",
        "💧 Beba 2L de água por dia",
        "📱 Registre refeições no mesmo horário",
        "🎯 Metas pequenas são mais sustentáveis"
    ]
    st.info(f"✨ {random.choice(tips)}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_subscription(payment, user):
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("💳 Upgrade de Plano")
    
    if user.get("plan") == "pro":
        st.success("🎉 Você já é assinante PRO!")
        return
    
    cols = st.columns(3)
    plans = [
        {"name": "Start", "price": "R$ 19,90", "features": ["📊 Gráficos", "🍴 Refeições"]},
        {"name": "Pro", "price": "R$ 39,90", "features": ["✨ Tudo do Start", "🤖 IA Comportamental", "🏆 Conquistas extras"]},
        {"name": "Vitalício", "price": "R$ 297", "features": ["🚀 Todos os recursos", "🌟 Suporte vitalício"]}
    ]
    
    for idx, plan in enumerate(plans):
        with cols[idx]:
            is_pro = idx == 1
            border = "2px solid #f59e0b" if is_pro else "1px solid #e5e7eb"
            st.markdown(f"""
            <div style="border: {border}; border-radius: 20px; padding: 1.5rem; text-align: center;">
                <h3>{plan['name']}</h3>
                <div style="font-size: 1.5rem; font-weight: bold; margin: 1rem 0;">{plan['price']}</div>
            """, unsafe_allow_html=True)
            for feature in plan['features']:
                st.markdown(f"✅ {feature}")
            if st.button(f"Escolher {plan['name']}", key=f"plan_{idx}", use_container_width=True):
                if is_pro:
                    user["plan"] = "pro"
                    st.session_state.user = user
                    st.toast("Plano Pro ativado! 🎉", icon="👑")
                    st.rerun()
                else:
                    st.info("🚧 Em desenvolvimento - experimente o Pro!")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)