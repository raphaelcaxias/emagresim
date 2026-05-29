import streamlit as st
import pandas as pd
from datetime import date
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine

st.set_page_config(
    page_title="EmagreSim - Sua Jornada Fitness", 
    page_icon="⚔️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS PROFISSIONAL - Design System Moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo com gradiente profissional */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Cards com Glassmorphism */
    .stAlert, .stInfo, .stSuccess, .stWarning, .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 1.5rem;
    }
    
    /* Métricas estilo Dashboard */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 2px solid #e9ecef;
        transition: transform 0.2s;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
    }
    
    [data-testid="stMetricValue"] {
        color: #667eea;
        font-weight: 700;
        font-size: 2rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6c757d;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Botões Modernos */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Inputs Modernos */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar Profissional */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Títulos */
    h1 {
        color: white;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
    }
    
    h2, h3 {
        color: #2d3748;
        font-weight: 600;
    }
    
    /* Barra de Progresso Estilizada */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Tabs Modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main > div {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Badges de Nível */
    .level-badge {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(251, 191, 36, 0.3);
    }
    
    /* Cards de Refeições */
    .meal-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização
@st.cache_resource
def init_services():
    db = SupabaseDB()
    return db, UserService(db), PsychologyEngine()

db, user_service, psychology = init_services()

# Estado
if "user" not in st.session_state: 
    st.session_state.user = None
if "page" not in st.session_state: 
    st.session_state.page = "Dashboard"
if "today_date" not in st.session_state:
    st.session_state.today_date = str(date.today())

# TELA DE LOGIN
if not st.session_state.user:
    # Header
    col_logo, col_space = st.columns([1, 3])
    with col_logo:
        st.markdown("<h1>⚔️ EmagreSim</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: white; font-size: 1.2rem; margin-bottom: 2rem;'>Transforme sua dieta em um RPG épico!</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Conteúdo principal
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.15); padding: 2.5rem; border-radius: 20px; color: white; backdrop-filter: blur(10px);'>
            <h2 style='color: white; margin-bottom: 1.5rem;'>🎮 Como funciona:</h2>
            <div style='line-height: 2.5; font-size: 1.1rem;'>
                <div style='margin: 1rem 0;'>✅ <strong>Registre refeições</strong> e ganhe XP</div>
                <div style='margin: 1rem 0;'>📈 <strong>Suba de nível</strong> com consistência</div>
                <div style='margin: 1rem 0;'>🏆 <strong>Desbloqueie conquistas</strong> épicas</div>
                <div style='margin: 1rem 0;'>📊 <strong>Acompanhe</strong> sua evolução</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        with tab1:
            st.markdown("### Bem-vindo de volta!")
            email = st.text_input("Email", key="login_email", placeholder="seu@email.com", label_visibility="collapsed")
            pwd = st.text_input("Senha", type="password", key="login_pwd", placeholder="••••••••", label_visibility="collapsed")
            
            if st.button("Entrar na Jornada", type="primary"):
                if email and pwd:
                    res = db.sign_in(email, pwd)
                    if res["success"]: 
                        st.balloons()
                        st.rerun()
                    else: 
                        st.error("Email ou senha incorretos")
                else:
                    st.warning("Preencha todos os campos")
        
        with tab2:
            st.markdown("### Comece sua transformação!")
            new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com", label_visibility="collapsed")
            new_pwd = st.text_input("Senha", type="password", key="reg_pwd", placeholder="Mínimo 6 caracteres", label_visibility="collapsed")
            new_user = st.text_input("Nome de Usuário", key="reg_user", placeholder="Como quer ser chamado?", label_visibility="collapsed")
            
            if st.button("Criar Conta Grátis", type="primary"):
                if new_email and new_pwd and new_user:
                    if len(new_pwd) >= 6:
                        res = db.sign_up(new_email, new_pwd, new_user)
                        if res["success"]: 
                            st.success("✅ Conta criada! Faça login.")
                            st.balloons()
                        else: 
                            st.error(f"Erro: {res['error']}")
                    else:
                        st.error("Senha deve ter pelo menos 6 caracteres")
                else:
                    st.warning("Preencha todos os campos")

else:
    # USUÁRIO LOGADO
    profile = db.get_profile()
    
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #667eea;'>⚔️ EmagreSim</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Info do usuário
        st.markdown(f"**👤 {st.session_state.user.get('user_metadata', {}).get('username', 'Herói')}**")
        if profile:
            st.markdown(f"<div class='level-badge'>Nível {profile['level']}</div>", unsafe_allow_html=True)
            st.progress(min(profile["experience"] / int(100 * (profile['level'] ** 1.5)), 1.0))
            st.caption(f"{profile['experience']} XP")
        
        st.markdown("---")
        
        # Menu
        menu = st.radio(
            "Navegação",
            ["📊 Dashboard", "🍽️ Refeições", "📈 Histórico", "👤 Perfil"],
            label_visibility="collapsed"
        )
        st.session_state.page = menu
        
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            db.sign_out()
            st.rerun()

    # CONTEÚDO PRINCIPAL
    if profile:
        if st.session_state.page == "📊 Dashboard":
            st.title("📊 Dashboard")
            st.markdown(f"**Bem-vindo de volta, {profile.get('username', 'Herói')}!**")
            st.markdown("---")
            
            # Métricas
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("⚡ XP Total", f"{profile['experience']}")
            c2.metric("⚖️ Peso Atual", f"{profile.get('current_weight_kg', 0)} kg")
            c3.metric("🔥 Sequência", f"{profile.get('streak_days', 0)} dias")
            c4.metric("🎯 Meta", f"{profile.get('goal_weight_kg', 0)} kg")
            
            # Progresso de Nível
            st.markdown("### 🎮 Progresso para o Próximo Nível")
            xp_needed = int(100 * (profile['level'] ** 1.5))
            progress = min(profile["experience"] / xp_needed, 1.0)
            st.progress(progress)
            st.caption(f"{profile['experience']} / {xp_needed} XP necessários")
            
            st.markdown("---")
            
            # Motivação e Refeições
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"💭 **Motivação do dia:** {psychology.get_daily_motivation()}")
            
            with col2:
                st.warning(f"💡 **Dica:** {psychology.get_tip()}")
            
            st.markdown("### 🍽️ Refeições de Hoje")
            meals = db.get_daily_meals()
            if meals:
                total_cal = sum(m['calories'] for m in meals)
                st.markdown(f"**Total: {total_cal} kcal**")
                for m in meals:
                    st.markdown(f"""
                    <div class='meal-card'>
                        <strong>{m['food_name']}</strong><br>
                        {m['calories']} kcal • {m['proteins']}g proteína • {m['meal_type']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📝 Nenhuma refeição registrada hoje. Vá em 'Refeições' para começar!")
                
        elif st.session_state.page == "🍽️ Refeições":
            st.title("🍽️ Registrar Refeição")
            
            with st.form("meal_form", clear_on_submit=False):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Tipo de Refeição", ["cafe", "almoco", "jantar", "lanche"], 
                                      format_func=lambda x: {"cafe": "☕ Café da Manhã", "almoco": "️ Almoço", 
                                                             "jantar": "🌙 Jantar", "lanche": "🍎 Lanche"}[x])
                    nome = st.text_input("Nome do Alimento", placeholder="Ex: Arroz com frango e salada")
                with col2:
                    cal = st.number_input("Calorias", min_value=0, max_value=2000, value=350, step=10)
                    prot = st.number_input("Proteínas (g)", min_value=0.0, max_value=200.0, value=15.0, step=0.5)
                
                submitted = st.form_submit_button("✅ Registrar Refeição", type="primary", use_container_width=True)
                
                if submitted:
                    if nome:
                        with st.spinner("Registrando..."):
                            res = user_service.register_meal({
                                "meal_type": tipo, 
                                "food_name": nome, 
                                "calories": cal, 
                                "proteins": prot
                            })
                            if res.get("success"):
                                st.balloons()
                                st.success(f"🎉 +{res['xp']} XP ganhos!")
                                if res.get("leveled_up"): 
                                    st.toast(f"🏆 LEVEL UP! Você alcançou o nível {res['level']}", icon="🎉")
                                st.rerun()
                            else:
                                st.error("Erro ao registrar refeição")
                    else:
                        st.warning("Por favor, digite o nome do alimento")
                        
        elif st.session_state.page == "📈 Histórico":
            st.title("📈 Histórico de Peso")
            logs = db.get_weight_history(90)
            if logs:
                df = pd.DataFrame(logs)
                df["recorded_at"] = pd.to_datetime(df["recorded_at"]).dt.date
                df = df.sort_values("recorded_at", ascending=False)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.line_chart(df.set_index("recorded_at")["weight_kg"])
                with col2:
                    st.metric("Último Peso", f"{df.iloc[0]['weight_kg']} kg")
                    if len(df) > 1:
                        diff = df.iloc[-1]['weight_kg'] - df.iloc[0]['weight_kg']
                        st.metric("Variação", f"{diff:.1f} kg", delta=f"{diff:.1f}" if diff < 0 else None)
                
                st.markdown("### Registros")
                st.dataframe(df[["recorded_at", "weight_kg"]].rename(columns={"recorded_at": "Data", "weight_kg": "Peso (kg)"}), use_container_width=True)
            else:
                st.info("📝 Registre seu peso em 'Perfil' para ver o histórico.")
                
        elif st.session_state.page == "👤 Perfil":
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
                if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                    with st.spinner("Salvando..."):
                        db.update_profile({"age": idade, "height_cm": altura, "goal_weight_kg": meta})
                        if abs(peso - profile.get("current_weight_kg", 0)) > 0.01:
                            res = user_service.update_weight(peso)
                            st.info(res.get("message", "Peso atualizado"))
                        st.success("✅ Perfil atualizado com sucesso!")
                        st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.9);'>EmagreSim v2.0 | Transformando vidas através da gamificação ⚔️</p>", unsafe_allow_html=True)
