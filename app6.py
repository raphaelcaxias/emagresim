# -*- coding: utf-8 -*-
"""
EmagreSim v10.0 - Com Supabase
Autenticação real (Google + Email) + Banco de dados completo
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase import create_client, Client
import bcrypt

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Conectar ao Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase. Verifique o arquivo .streamlit/secrets.toml")
    st.stop()

# -----------------------------------------------------------------------------
# 2. CORES E TEMAS
# -----------------------------------------------------------------------------
if "tema" not in st.session_state:
    st.session_state.tema = "auto"

def get_tema():
    if st.session_state.tema == "claro":
        return {"bg": "#F5F5F0", "surface": "#FFFFFF", "card": "#FFFFFF", "primary": "#FF4D00", "text": "#1A1A1A", "text_muted": "#666666", "border": "rgba(0,0,0,0.08)"}
    elif st.session_state.tema == "escuro":
        return {"bg": "#0D0D0D", "surface": "#1A1A1A", "card": "#1E1E1E", "primary": "#FF4D00", "text": "#FFFFFF", "text_muted": "#A0A0A0", "border": "rgba(255,255,255,0.06)"}
    else:
        hora = datetime.now().hour
        if hora < 6 or hora > 18:
            return {"bg": "#0D0D0D", "surface": "#1A1A1A", "card": "#1E1E1E", "primary": "#FF4D00", "text": "#FFFFFF", "text_muted": "#A0A0A0", "border": "rgba(255,255,255,0.06)"}
        else:
            return {"bg": "#F5F5F0", "surface": "#FFFFFF", "card": "#FFFFFF", "primary": "#FF4D00", "text": "#1A1A1A", "text_muted": "#666666", "border": "rgba(0,0,0,0.08)"}

def aplicar_css():
    C = get_tema()
    css = f"""
    <style>
    .stApp, .stApp > header {{ background: {C['bg']} !important; }}
    section[data-testid="stSidebar"] {{ background: {C['surface']} !important; border-right: 1px solid {C['border']} !important; }}
    .es-card, .kpi-card {{ background: {C['card']}; border-radius: 20px; padding: 20px; margin-bottom: 20px; border: 1px solid {C['border']}; }}
    .kpi-label {{ font-size: 0.7rem; color: {C['text_muted']}; text-transform: uppercase; }}
    .kpi-value {{ font-size: 2rem; font-weight: 800; color: {C['text']}; }}
    .kpi-badge {{ background: rgba(255,77,0,0.15); color: {C['primary']}; border-radius: 20px; padding: 4px 10px; font-size: 0.7rem; }}
    .prog-track {{ background: rgba(0,0,0,0.1); border-radius: 99px; height: 6px; }}
    .prog-fill {{ height: 100%; border-radius: 99px; background: {C['primary']}; transition: width 0.5s; }}
    .insight-box {{ background: rgba(255,77,0,0.08); border-left: 3px solid {C['primary']}; padding: 12px; border-radius: 12px; margin: 8px 0; }}
    #MainMenu, header, footer, .stDeployButton {{ display: none; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. FUNÇÕES DE AUTENTICAÇÃO
# -----------------------------------------------------------------------------
def fazer_login(email: str, senha: str):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        return response.user
    except Exception as e:
        st.error(f"Email ou senha inválidos")
        return None

def fazer_login_google():
    # Google OAuth - redireciona para URL do Supabase
    try:
        redirect_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to=http://localhost:8501"
        st.markdown(f'<a href="{redirect_url}" target="_blank">Clique aqui para fazer login com Google</a>', unsafe_allow_html=True)
        return None
    except Exception as e:
        st.error(f"Erro no login com Google: {e}")
        return None

def criar_conta(email: str, senha: str, nome: str, idade: int, altura: float, peso: float, meta_peso: float, sexo: str):
    try:
        # Criar usuário no Auth
        response = supabase.auth.sign_up({"email": email, "password": senha})
        if response.user:
            user_id = response.user.id
            # Inserir perfil na tabela users
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "name": nome,
                "age": idade,
                "height": altura,
                "current_weight": peso,
                "target_weight": meta_peso,
                "sex": sexo,
                "is_premium": False
            }).execute()
            # Inserir meta inicial
            supabase.table("user_goals").insert({
                "user_id": user_id,
                "target_weight": meta_peso,
                "monthly_goal_kg": 2.0
            }).execute()
            return response.user
    except Exception as e:
        st.error(f"Erro ao criar conta: {e}")
        return None

def carregar_usuario(user_id: str):
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        st.error(f"Erro ao carregar usuário: {e}")
        return None

# -----------------------------------------------------------------------------
# 4. FUNÇÕES DE DADOS
# -----------------------------------------------------------------------------
def registrar_peso(user_id: str, peso: float, data_registro: str):
    try:
        # Verificar se já existe registro para esta data
        existing = supabase.table("weight_logs").select("*").eq("user_id", user_id).eq("date", data_registro).execute()
        if existing.data:
            supabase.table("weight_logs").update({"weight": peso}).eq("user_id", user_id).eq("date", data_registro).execute()
        else:
            supabase.table("weight_logs").insert({
                "user_id": user_id,
                "date": data_registro,
                "weight": peso
            }).execute()
        # Atualizar peso atual no perfil
        supabase.table("users").update({"current_weight": peso}).eq("id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar peso: {e}")
        return False

def registrar_refeicao(user_id: str, data_registro: str, meal_type: str, food_name: str, calories: int):
    try:
        supabase.table("food_logs").insert({
            "user_id": user_id,
            "date": data_registro,
            "meal_type": meal_type,
            "food_name": food_name,
            "calories": calories
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar refeição: {e}")
        return False

def registrar_humor(user_id: str, data_registro: str, humor: str, consistencia: int):
    try:
        existing = supabase.table("checkin_logs").select("*").eq("user_id", user_id).eq("date", data_registro).execute()
        if existing.data:
            supabase.table("checkin_logs").update({
                "humor": humor,
                "consistency_score": consistencia
            }).eq("user_id", user_id).eq("date", data_registro).execute()
        else:
            supabase.table("checkin_logs").insert({
                "user_id": user_id,
                "date": data_registro,
                "humor": humor,
                "consistency_score": consistencia
            }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar humor: {e}")
        return False

def carregar_pesos(user_id: str, dias: int = 30):
    try:
        data_limite = (date.today() - timedelta(days=dias)).isoformat()
        result = supabase.table("weight_logs").select("*").eq("user_id", user_id).gte("date", data_limite).order("date").execute()
        return result.data
    except Exception as e:
        return []

def carregar_refeicoes(user_id: str, data_registro: str):
    try:
        result = supabase.table("food_logs").select("*").eq("user_id", user_id).eq("date", data_registro).execute()
        return result.data
    except Exception as e:
        return []

def carregar_ranking():
    try:
        result = supabase.rpc('get_weekly_ranking').execute()
        return result.data
    except Exception as e:
        return []

# -----------------------------------------------------------------------------
# 5. PÁGINA DE LOGIN
# -----------------------------------------------------------------------------
def pagina_login():
    C = get_tema()
    st.markdown(f"""
    <div style="max-width: 400px; margin: 50px auto;">
        <h1 style="text-align:center;">🔥 EmagreSim</h1>
        <div class="es-card">
            <h3>🔐 Login</h3>
            <form action="" method="post">
                <input type="email" name="email" placeholder="E-mail" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                <input type="password" name="password" placeholder="Senha" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                <button type="submit" style="width:100%; padding:10px; background:{C['primary']}; color:white; border:none; border-radius:10px;">Entrar</button>
            </form>
            <hr>
            <button onclick="window.location.href='?login=google'" style="width:100%; padding:10px; background:#4285F4; color:white; border:none; border-radius:10px;">🔑 Entrar com Google</button>
            <hr>
            <p style="text-align:center;">Não tem conta? <a href="?pagina=criar_conta">Criar conta</a></p>
            <p style="text-align:center; margin-top:20px;"><a href="?pagina=demo">🧪 Testar demonstração (Adriano)</a></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. PÁGINA DE CRIAR CONTA
# -----------------------------------------------------------------------------
def pagina_criar_conta():
    C = get_tema()
    st.markdown(f"""
    <div style="max-width: 500px; margin: 30px auto;">
        <h1 style="text-align:center;">🔥 Criar Conta</h1>
        <div class="es-card">
            <form action="" method="post">
                <input type="text" name="nome" placeholder="Nome completo" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                <input type="email" name="email" placeholder="E-mail" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                <input type="password" name="senha" placeholder="Senha" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                <div style="display:flex; gap:10px;">
                    <input type="number" name="idade" placeholder="Idade" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                    <input type="number" step="0.01" name="altura" placeholder="Altura (m)" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                </div>
                <div style="display:flex; gap:10px;">
                    <input type="number" step="0.1" name="peso" placeholder="Peso (kg)" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                    <input type="number" step="0.1" name="meta_peso" placeholder="Meta de peso" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                </div>
                <select name="sexo" style="width:100%; padding:10px; margin:8px 0; border-radius:10px; border:1px solid {C['border']}; background:{C['surface']}; color:{C['text']};">
                    <option value="M">Masculino</option>
                    <option value="F">Feminino</option>
                </select>
                <button type="submit" style="width:100%; padding:10px; background:{C['primary']}; color:white; border:none; border-radius:10px;">Criar Conta</button>
            </form>
            <hr>
            <p style="text-align:center;"><a href="?pagina=login">← Voltar para login</a></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 7. PÁGINA DEMONSTRAÇÃO (ADRIANO)
# -----------------------------------------------------------------------------
def pagina_demo():
    st.markdown("<h1>🧪 Modo Demonstração - Adriano</h1>", unsafe_allow_html=True)
    st.info("Este é um modo de demonstração com dados de exemplo (Adriano, 144kg). Nenhum dado será salvo permanentemente.")
    
    # Dados do Adriano
    adriano = {
        "name": "Adriano",
        "age": 39,
        "height": 1.75,
        "current_weight": 144.0,
        "target_weight": 90.0,
        "sex": "M"
    }
    
    # Mostrar KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        imc = adriano["current_weight"] / (adriano["height"] ** 2)
        st.metric("Peso Atual", f"{adriano['current_weight']:.1f} kg", f"Meta: {adriano['target_weight']:.0f} kg")
        st.metric("IMC", f"{imc:.1f}", "Obesidade Grave")
    with col2:
        st.metric("Idade", f"{adriano['age']} anos")
        st.metric("Altura", f"{adriano['height']:.2f} m")
    with col3:
        st.metric("Sexo", "Masculino")
        progresso = (adriano["current_weight"] - adriano["target_weight"]) / adriano["current_weight"] * 100
        st.progress(min(progresso / 100, 1.0))
    
    st.info("💡 Para criar sua própria conta, clique em 'Sair' no menu lateral e escolha 'Criar conta'.")

# -----------------------------------------------------------------------------
# 8. PÁGINA DASHBOARD
# -----------------------------------------------------------------------------
def pagina_dashboard(user):
    C = get_tema()
    st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)
    
    # Carregar dados
    pesos = carregar_pesos(user["id"])
    hoje = date.today().isoformat()
    refeicoes_hoje = carregar_refeicoes(user["id"], hoje)
    calorias_hoje = sum(r["calories"] for r in refeicoes_hoje)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Peso Atual", f"{user['current_weight']:.1f} kg", f"Meta: {user['target_weight']:.0f} kg")
    with col2:
        imc = user["current_weight"] / (user["height"] ** 2)
        st.metric("IMC", f"{imc:.1f}")
    with col3:
        st.metric("Calorias Hoje", f"{calorias_hoje} kcal", f"{len(refeicoes_hoje)} refeições")
    with col4:
        plano = "Premium" if user.get("is_premium", False) else "Grátis"
        st.metric("Plano", plano)
    
    # Gráfico de peso
    if pesos:
        df = pd.DataFrame(pesos)
        df["date"] = pd.to_datetime(df["date"])
        fig = px.line(df, x="date", y="weight", title="Evolução do Peso", labels={"date": "Data", "weight": "Peso (kg)"})
        fig.update_layout(paper_bgcolor=C['card'], plot_bgcolor=C['card'], font_color=C['text'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Ranking
    ranking = carregar_ranking()
    if ranking:
        st.markdown("### 🏆 Ranking Semanal")
        for i, row in enumerate(ranking[:5]):
            medalha = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}º"
            st.write(f"{medalha} **{row['user_name']}** - {row['points']} pontos")

# -----------------------------------------------------------------------------
# 9. PÁGINA REGISTRAR
# -----------------------------------------------------------------------------
def pagina_registrar(user):
    st.markdown("<h1>✏️ Registrar</h1>", unsafe_allow_html=True)
    hoje = date.today().isoformat()
    
    tab1, tab2, tab3 = st.tabs(["⚖️ Peso", "🍽️ Refeição", "😊 Humor"])
    
    with tab1:
        with st.form("form_peso"):
            peso = st.number_input("Peso (kg)", 30.0, 250.0, user["current_weight"], 0.1)
            if st.form_submit_button("Salvar Peso"):
                if registrar_peso(user["id"], peso, hoje):
                    st.toast("✅ Peso registrado!", icon="⚖️")
                    st.rerun()
    
    with tab2:
        with st.form("form_refeicao"):
            col1, col2 = st.columns(2)
            with col1:
                meal_type = st.selectbox("Refeição", ["Café da manhã", "Almoço", "Jantar", "Lanche"])
                food_name = st.text_input("O que comeu?")
            with col2:
                calories = st.number_input("Calorias (kcal)", 0, 2000, 300, 50)
            if st.form_submit_button("Salvar Refeição"):
                if food_name:
                    registrar_refeicao(user["id"], hoje, meal_type, food_name, calories)
                    st.toast(f"✅ {meal_type} registrado!", icon="🍽️")
                    st.rerun()
    
    with tab3:
        with st.form("form_humor"):
            humor = st.selectbox("Como você está se sentindo?", ["Motivado", "Cansado", "Determinado", "Focado", "Ansioso", "Frustrado", "Orgulhoso"])
            consistencia = st.slider("Consistência hoje (0-100)", 0, 100, 70)
            if st.form_submit_button("Salvar Humor"):
                registrar_humor(user["id"], hoje, humor, consistencia)
                st.toast("✅ Humor registrado!", icon="😊")
                st.rerun()

# -----------------------------------------------------------------------------
# 10. PÁGINA PERFIL
# -----------------------------------------------------------------------------
def pagina_perfil(user):
    st.markdown("<h1>👤 Meu Perfil</h1>", unsafe_allow_html=True)
    
    with st.form("form_perfil"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", user["name"])
            idade = st.number_input("Idade", 18, 100, user["age"])
        with col2:
            altura = st.number_input("Altura (m)", 1.40, 2.20, user["height"], 0.01)
            meta_peso = st.number_input("Meta de peso (kg)", 40.0, 200.0, user["target_weight"], 0.5)
        
        if st.form_submit_button("Salvar Alterações"):
            try:
                supabase.table("users").update({
                    "name": nome, "age": idade, "height": altura, "target_weight": meta_peso
                }).eq("id", user["id"]).execute()
                st.toast("Perfil atualizado!", icon="👤")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")

# -----------------------------------------------------------------------------
# 11. SIDEBAR
# -----------------------------------------------------------------------------
def sidebar(user):
    C = get_tema()
    with st.sidebar:
        st.markdown(f"<h2 style='color:{C['primary']}'>🔥 EmagreSim</h2>", unsafe_allow_html=True)
        
        # Seletor de tema
        tema_opts = ["auto", "claro", "escuro"]
        tema_idx = tema_opts.index(st.session_state.tema)
        tema = st.radio("🎨 Tema", tema_opts, index=tema_idx, horizontal=True, label_visibility="collapsed")
        if tema != st.session_state.tema:
            st.session_state.tema = tema
            st.rerun()
        
        st.markdown("---")
        
        # Navegação
        st.page_link("app.py", label="📊 Dashboard", icon="📊")
        st.page_link("app.py", label="✏️ Registrar", icon="✏️")
        st.page_link("app.py", label="👤 Perfil", icon="👤")
        
        st.markdown("---")
        
        if st.button("🚪 Sair", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.clear()
            st.rerun()
        
        st.caption(f"Olá, {user['name']}")

# -----------------------------------------------------------------------------
# 12. MAIN
# -----------------------------------------------------------------------------
def main():
    aplicar_css()
    
    # Verificar se usuário está logado
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Verificar sessão atual
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            user_data = carregar_usuario(session.user.id)
            if user_data:
                st.session_state.user = user_data
    except:
        pass
    
    # Modo demonstração
    if st.query_params.get("pagina") == "demo":
        pagina_demo()
        return
    
    # Login e páginas
    if st.session_state.user is None:
        if st.query_params.get("pagina") == "criar_conta":
            pagina_criar_conta()
        else:
            pagina_login()
        return
    
    # Usuário logado
    user = st.session_state.user
    sidebar(user)
    
    # Router
    if st.query_params.get("pagina") == "Registrar":
        pagina_registrar(user)
    elif st.query_params.get("pagina") == "Perfil":
        pagina_perfil(user)
    else:
        pagina_dashboard(user)

if __name__ == "__main__":
    main()
