import streamlit as st
import pandas as pd
from datetime import date
from core.database import SupabaseDB
from core.services import UserService
from core.psychology import PsychologyEngine

st.set_page_config(
    page_title="EmagreSim - Sua Jornada Fitness", 
    page_icon="🍽️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS PROFISSIONAL - Layout Fitness Moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo Gradiente - Tons de Verde/Azul (Saúde e Energia) */
    .main {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        min-height: 100vh;
    }
    
    /* Cards com Glassmorphism */
    .stAlert, .stInfo, .stSuccess, .stWarning {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Métricas Estilo Dashboard */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 2px solid #e9ecef;
    }
    
    [data-testid="stMetricValue"] {
        color: #11998e;
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
    
    /* Botões Modernos - Verde Energia */
    .stButton > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(17, 153, 142, 0.4);
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
        border-color: #11998e;
        box-shadow: 0 0 0 3px rgba(17, 153, 142, 0.1);
    }
    
    /* Títulos */
    h1 {
        color: white;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
        text-align: center;
    }
    
    h2, h3 {
        color: #2d3748;
        font-weight: 600;
    }
    
    /* Barra de Progresso */
    .stProgress > div > div {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        border-radius: 10px;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main > div {
        animation: fadeIn 0.5s ease-in;
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
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🍽️ EmagreSim")
    st.subheader("Sua jornada fitness começa aqui")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        with tab1:
            st.markdown("### 👋 Bem-vindo de volta!")
            email = st.text_input("Email", placeholder="seu@email.com", label_visibility="collapsed")
            pwd = st.text_input("Senha", type="password", placeholder="Sua senha", label_visibility="collapsed")
            
            if st.button("Entrar", use_container_width=True):
                if email and pwd:
                    res = db.sign_in(email, pwd)
                    if res["success"]: 
                        st.balloons()
                        st.rerun()
                    else: 
                        st.error(f"Erro: {res.get('error', 'Email ou senha incorretos')}")
                else:
                    st.warning("Preencha todos os campos")

        with tab2:
            st.markdown("### 🚀 Nova Conta")
            new_email = st.text_input("Email", key="reg_email", placeholder="seu@email.com", label_visibility="collapsed")
            new_pwd = st.text_input("Senha", key="reg_pwd", type="password", placeholder="Mín. 6 caracteres", label_visibility="collapsed")
            new_user = st.text_input("Nome de Usuário", key="reg_user", placeholder="Seu apelido", label_visibility="collapsed")
            
            if st.button("Criar Conta", use_container_width=True):
                if new_email and new_pwd and new_user:
                    if len(new_pwd) >= 6:
                        res = db.sign_up(new_email, new_pwd, new_user)
                        if res["success"]: 
                            st.success("✅ Conta criada! Faça login.")
                            st.balloons()
                        else: 
                            st.error(f"Erro: {res['error']}")
                    else:
                        st.warning("Senha deve ter pelo menos 6 caracteres")
                else:
                    st.warning("Preencha todos os campos")

else:
    # USUÁRIO LOGADO
    with st.sidebar:
        st.title("🍽️ EmagreSim")
        st.markdown("---")
        
        profile = db.get_profile()
        if profile:
            st.metric(label="🏆 Nível", value=profile.get('level', 1))
            st.metric(label="⚡ XP", value=profile.get('experience', 0))
            st.metric(label="⚖️ Peso", value=f"{profile.get('current_weight_kg', 0)} kg")
        
        st.markdown("---")
        page = st.radio(
            "Navegação",
            ["📊 Dashboard", "🍴 Refeições", "📈 Histórico", "👤 Perfil"],
            label_visibility="collapsed"
        )
        st.session_state.page = page
        
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            db.sign_out()
            st.rerun()

    # CONTEÚDO PRINCIPAL
    if profile:
        if st.session_state.page == "📊 Dashboard":
            st.title("📊 Dashboard")
            st.markdown(f"**Bem-vindo de volta, {profile.get('username', 'Herói')}!** 💪")
            st.markdown("---")
            
            # Métricas
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("⚡ XP Total", profile.get('experience', 0))
            c2.metric("⚖️ Peso Atual", f"{profile.get('current_weight_kg', 0)} kg")
            c3.metric("🔥 Sequência", f"{profile.get('streak_days', 0)} dias")
            c4.metric("🎯 Meta", f"{profile.get('goal_weight_kg', 0)} kg")
            
            # Progresso de Nível
            st.markdown("### 🎯 Progresso para o Próximo Nível")
            level = profile.get('level', 1)
            xp_needed = int(100 * (level ** 1.5))
            xp_current = profile.get('experience', 0)
            progress = min(xp_current / xp_needed, 1.0) if xp_needed > 0 else 0
            st.progress(progress)
            st.caption(f"{xp_current} / {xp_needed} XP necessários")
            
            st.markdown("---")
            
            # Motivação e Refeições
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"💭 **Motivação:** {psychology.get_daily_motivation()}")
            
            with col2:
                st.warning(f"💡 **Dica:** {psychology.get_tip()}")
            
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
                
        elif st.session_state.page == "🍴 Refeições":
            st.title("🍴 Registrar Refeição")
            
            with st.form("meal_form", clear_on_submit=False):
                col1, col2 = st.columns(2)
                with col1:
                    tipo = st.selectbox("Tipo de Refeição", ["cafe", "almoco", "jantar", "lanche"], 
                                      format_func=lambda x: {"cafe": "☕ Café da Manhã", "almoco": "🍽️ Almoço", 
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
                                "meal_type": tipo, 
                                "food_name": nome, 
                                "calories": cal, 
                                "proteins": prot
                            })
                            if res.get("success"):
                                st.balloons()
                                st.success(f"🎉 +{res.get('xp', 0)} XP ganhos!")
                                if res.get("leveled_up"): 
                                    st.toast(f"🏆 LEVEL UP! Você alcançou o nível {res.get('level')}", icon="🎉")
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
                        st.metric("Variação", f"{diff:.1f} kg")
                
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
                if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                    with st.spinner("Salvando..."):
                        db.update_profile({"age": idade, "height_cm": altura, "goal_weight_kg": meta})
                        if abs(peso - profile.get("current_weight_kg", 0)) > 0.01:
                            res = user_service.update_weight(peso)
                            st.info(res.get("message", "Peso atualizado"))
                        st.success("✅ Perfil atualizado com sucesso!")
                        st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.9);'>EmagreSim v2.0 | Transformando vidas através da saúde 🍎</p>", unsafe_allow_html=True)
