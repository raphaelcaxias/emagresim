# -*- coding: utf-8 -*-
"""
EmagreSim v12.0 - Com Supabase (Tema Claro Padrão)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase import create_client, Client
import random
from streamlit_confetti import confetti

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
    SUPABASE_KEY = st.secrets["CHAVE_SUPABASE"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase. Verifique as secrets no Streamlit Cloud.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. CORES E TEMAS (Claro como padrão)
# -----------------------------------------------------------------------------
if "tema" not in st.session_state:
    st.session_state.tema = "claro"  # Agora começa no claro!

def get_tema():
    if st.session_state.tema == "claro":
        return {"bg": "#F5F5F0", "surface": "#FFFFFF", "card": "#FFFFFF", "primary": "#FF4D00", "text": "#1A1A1A", "text_muted": "#666666", "border": "rgba(0,0,0,0.08)"}
    else:
        return {"bg": "#0D0D0D", "surface": "#1A1A1A", "card": "#1E1E1E", "primary": "#FF4D00", "text": "#FFFFFF", "text_muted": "#A0A0A0", "border": "rgba(255,255,255,0.06)"}

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
    .comparison-card {{ background: {C['surface']}; border-radius: 16px; padding: 16px; margin: 8px 0; border: 1px solid {C['border']}; }}
    .comparison-value {{ font-size: 1.5rem; font-weight: 800; color: {C['primary']}; }}
    .comparison-label {{ font-size: 0.7rem; color: {C['text_muted']}; text-transform: uppercase; }}
    .back-button {{ background: transparent; border: 1px solid {C['primary']}; color: {C['primary']}; padding: 8px 16px; border-radius: 20px; cursor: pointer; margin-bottom: 20px; }}
    #MainMenu, header, footer, .stDeployButton {{ display: none; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. DESAFIOS SEMANAIS
# -----------------------------------------------------------------------------
DESAFIOS = [
    {"nome": "💧 Hidratação", "descricao": "Beba 2L de água por 5 dias", "meta": 5, "xp": 100},
    {"nome": "🥚 Proteína", "descricao": "Registre proteína em todas as refeições por 3 dias", "meta": 3, "xp": 150},
    {"nome": "🚶 Movimento", "descricao": "Caminhe 30min por dia durante 4 dias", "meta": 4, "xp": 120},
    {"nome": "😴 Sono", "descricao": "Durma 7h+ por 5 dias", "meta": 5, "xp": 100},
    {"nome": "🍽️ Sem pular", "descricao": "Registre 3 refeições/dia por 4 dias", "meta": 4, "xp": 130},
    {"nome": "🥗 Salada", "descricao": "Inclua salada no almoço por 3 dias", "meta": 3, "xp": 80},
]

def get_desafio_semanal():
    semana = datetime.now().isocalendar()[1]
    return DESAFIOS[semana % len(DESAFIOS)]

# -----------------------------------------------------------------------------
# 4. FUNÇÕES DE AUTENTICAÇÃO E DADOS
# -----------------------------------------------------------------------------
def fazer_login(email: str, senha: str):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        return response.user
    except:
        st.error("Email ou senha inválidos")
        return None

def criar_conta(email: str, senha: str, nome: str, idade: int, altura: float, peso: float, meta_peso: float, sexo: str):
    try:
        response = supabase.auth.sign_up({"email": email, "password": senha})
        if response.user:
            user_id = response.user.id
            supabase.table("users").insert({
                "id": user_id, "email": email, "name": nome, "age": idade,
                "height": altura, "current_weight": peso, "target_weight": meta_peso,
                "sex": sexo, "is_premium": False
            }).execute()
            supabase.table("user_goals").insert({
                "user_id": user_id, "target_weight": meta_peso, "monthly_goal_kg": 2.0
            }).execute()
            return response.user
    except Exception as e:
        st.error(f"Erro ao criar conta: {e}")
        return None

def carregar_usuario(user_id: str):
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except:
        return None

def registrar_peso(user_id: str, peso: float, data_registro: str):
    try:
        existing = supabase.table("weight_logs").select("*").eq("user_id", user_id).eq("date", data_registro).execute()
        if existing.data:
            supabase.table("weight_logs").update({"weight": peso}).eq("user_id", user_id).eq("date", data_registro).execute()
        else:
            supabase.table("weight_logs").insert({"user_id": user_id, "date": data_registro, "weight": peso}).execute()
        supabase.table("users").update({"current_weight": peso}).eq("id", user_id).execute()
        return True
    except:
        return False

def registrar_refeicao(user_id: str, data_registro: str, hour: str, meal_type: str, food_name: str, calories: int):
    try:
        supabase.table("food_logs").insert({
            "user_id": user_id, "date": data_registro, "hour": hour, "meal_type": meal_type,
            "food_name": food_name, "calories": calories
        }).execute()
        return True
    except:
        return False

def registrar_humor(user_id: str, data_registro: str, humor: str, consistencia: int):
    try:
        existing = supabase.table("checkin_logs").select("*").eq("user_id", user_id).eq("date", data_registro).execute()
        if existing.data:
            supabase.table("checkin_logs").update({"humor": humor, "consistency_score": consistencia}).eq("user_id", user_id).eq("date", data_registro).execute()
        else:
            supabase.table("checkin_logs").insert({"user_id": user_id, "date": data_registro, "humor": humor, "consistency_score": consistencia}).execute()
        return True
    except:
        return False

def carregar_pesos(user_id: str, dias: int = 90):
    try:
        data_limite = (date.today() - timedelta(days=dias)).isoformat()
        result = supabase.table("weight_logs").select("*").eq("user_id", user_id).gte("date", data_limite).order("date").execute()
        return result.data
    except:
        return []

def carregar_refeicoes(user_id: str, dias: int = 7):
    try:
        data_limite = (date.today() - timedelta(days=dias)).isoformat()
        result = supabase.table("food_logs").select("*").eq("user_id", user_id).gte("date", data_limite).order("date").execute()
        return result.data
    except:
        return []

def carregar_ranking():
    try:
        result = supabase.rpc('get_weekly_ranking').execute()
        return result.data
    except:
        return []

def calcular_previsao_meta(peso_atual: float, peso_meta: float, ritmo_semanal: float):
    if ritmo_semanal <= 0:
        return None
    kg_restantes = max(peso_atual - peso_meta, 0)
    semanas_restantes = kg_restantes / ritmo_semanal
    data_estimada = date.today() + timedelta(days=int(semanas_restantes * 7))
    return data_estimada

def calcular_ritmo_semanal(pesos: list):
    if len(pesos) < 14:
        return 0
    pesos_df = pd.DataFrame(pesos)
    pesos_df["date"] = pd.to_datetime(pesos_df["date"])
    pesos_df = pesos_df.sort_values("date")
    peso_inicio = pesos_df.iloc[-14]["weight"]
    peso_fim = pesos_df.iloc[-1]["weight"]
    diferenca = peso_fim - peso_inicio
    return round(diferenca / 2, 2)

def comparar_30_dias(pesos: list):
    if len(pesos) < 30:
        return None
    pesos_df = pd.DataFrame(pesos)
    pesos_df["date"] = pd.to_datetime(pesos_df["date"])
    pesos_df = pesos_df.sort_values("date")
    peso_atual = pesos_df.iloc[-1]["weight"]
    peso_30d = pesos_df.iloc[-30]["weight"]
    diferenca = peso_atual - peso_30d
    return {"peso_anterior": peso_30d, "peso_atual": peso_atual, "diferenca": diferenca}

# -----------------------------------------------------------------------------
# 5. PÁGINAS
# -----------------------------------------------------------------------------
def pagina_demo():
    C = get_tema()
    st.markdown("<h1>🧪 Modo Demonstração - Adriano</h1>", unsafe_allow_html=True)
    
    if st.button("← Voltar para o início"):
        st.query_params.clear()
        st.rerun()
    
    adriano = {"name": "Adriano", "age": 39, "height": 1.75, "current_weight": 144.0, "target_weight": 90.0, "sex": "M"}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        imc = adriano["current_weight"] / (adriano["height"] ** 2)
        st.metric("Peso Atual", f"{adriano['current_weight']:.1f} kg", f"Meta: {adriano['target_weight']:.0f} kg")
        st.metric("IMC", f"{imc:.1f}", "Obesidade Grave (Grau III)" if imc >= 40 else "Obesidade Grau II" if imc >= 35 else "Obesidade Grau I")
    with col2:
        tmb = (10 * adriano["current_weight"]) + (6.25 * adriano["height"] * 100) - (5 * adriano["age"]) + 5
        st.metric("TMB", f"{int(tmb)} kcal/dia")
        st.metric("Meta calórica", f"{int(tmb - 500)} kcal/dia")
    with col3:
        st.metric("Idade", f"{adriano['age']} anos")
        st.metric("Altura", f"{adriano['height']:.2f} m")
    
    st.markdown("### 📈 Projeção Realista")
    ritmo = 0.8
    data_estimada = calcular_previsao_meta(adriano["current_weight"], adriano["target_weight"], ritmo)
    if data_estimada:
        st.info(f"🔥 No ritmo de **-{ritmo}kg/semana**, você chega em {adriano['target_weight']:.0f} kg em **{data_estimada.strftime('%d/%m/%Y')}**")
    
    st.markdown("### 💡 Recomendações Personalizadas")
    st.markdown("""
    - 🥩 **Proteína:** Priorize 2g/kg (≈288g/dia) – ovos, frango, carne magra
    - 💧 **Hidratação:** Beba 3L de água por dia (6 garrafas de 500ml)
    - 🚶 **Movimento:** Caminhada leve 30min, 5x por semana
    - ⚠️ **Aviso importante:** Consulte um médico antes de iniciar qualquer programa de emagrecimento
    """)
    
    st.markdown("### 📊 Quanto falta para cada meta")
    metas = [
        ("Obesidade Grau I (IMC 35)", 35 * (adriano["height"] ** 2), adriano["current_weight"] - 35 * (adriano["height"] ** 2)),
        ("Sobrepeso (IMC 30)", 30 * (adriano["height"] ** 2), adriano["current_weight"] - 30 * (adriano["height"] ** 2)),
        ("Saudável (IMC 25)", 25 * (adriano["height"] ** 2), adriano["current_weight"] - 25 * (adriano["height"] ** 2)),
    ]
    for nome, peso_meta, kg_faltam in metas:
        if kg_faltam > 0:
            st.write(f"- {nome}: perder **{kg_faltam:.0f} kg** (chegar a {peso_meta:.0f} kg)")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔥 Criar minha conta", use_container_width=True):
            st.query_params["pagina"] = "criar_conta"
            st.rerun()
    with col_b2:
        if st.button("📊 Ver ranking", use_container_width=True):
            st.query_params["pagina"] = "ranking"
            st.rerun()

def pagina_dashboard(user):
    C = get_tema()
    st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)
    
    pesos = carregar_pesos(user["id"])
    refeicoes = carregar_refeicoes(user["id"])
    hoje = date.today().isoformat()
    refeicoes_hoje = [r for r in refeicoes if r["date"] == hoje]
    calorias_hoje = sum(r["calories"] for r in refeicoes_hoje)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Peso Atual", f"{user['current_weight']:.1f} kg", f"Meta: {user['target_weight']:.0f} kg")
    with col2:
        imc = user["current_weight"] / (user["height"] ** 2)
        class_imc = "Obesidade Grave" if imc >= 40 else "Obesidade GII" if imc >= 35 else "Obesidade GI" if imc >= 30 else "Sobrepeso" if imc >= 25 else "Saudável"
        st.metric("IMC", f"{imc:.1f}", class_imc)
    with col3:
        st.metric("Calorias Hoje", f"{calorias_hoje} kcal", f"{len(refeicoes_hoje)} refeições")
    with col4:
        plano = "Premium ⭐" if user.get("is_premium") else "Grátis"
        st.metric("Plano", plano)
    
    comparacao = comparar_30_dias(pesos)
    if comparacao:
        cor = "#22C55E" if comparacao['diferenca'] < 0 else "#EF4444"
        st.markdown(f"""
        <div class="comparison-card">
            <div class="comparison-label">📊 VOCÊ HÁ 30 DIAS vs HOJE</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div><span class="comparison-value">{comparacao['peso_anterior']:.1f} kg</span><br>Há 30 dias</div>
                <div style="font-size: 2rem;">→</div>
                <div><span class="comparison-value">{comparacao['peso_atual']:.1f} kg</span><br>Hoje</div>
                <div><span class="comparison-value" style="color: {cor};">{comparacao['diferenca']:+.1f} kg</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if pesos:
        df = pd.DataFrame(pesos)
        df["date"] = pd.to_datetime(df["date"])
        fig = px.line(df, x="date", y="weight", title="Evolução do Peso")
        fig.update_layout(paper_bgcolor=C['card'], plot_bgcolor=C['card'], font_color=C['text'])
        st.plotly_chart(fig, use_container_width=True)
    
    ritmo = calcular_ritmo_semanal(pesos)
    if ritmo != 0:
        data_estimada = calcular_previsao_meta(user["current_weight"], user["target_weight"], abs(ritmo))
        if data_estimada:
            st.info(f"📅 **Previsão:** No seu ritmo atual ({abs(ritmo):.1f}kg/semana), você atingirá sua meta em **{data_estimada.strftime('%d/%m/%Y')}**")
    
    desafio = get_desafio_semanal()
    with st.expander("🏆 Desafio da Semana"):
        st.markdown(f"**{desafio['nome']}** – {desafio['descricao']} ⚡ +{desafio['xp']} XP")
    
    if st.button("🔍 Como foi meu dia hoje?", use_container_width=True):
        tmb = (10 * user["current_weight"]) + (6.25 * user["height"] * 100) - (5 * user["age"]) + (5 if user.get("sex") == "M" else -161)
        meta_calorica = int(tmb - 500)
        positivos, melhorias = [], []
        if calorias_hoje <= meta_calorica:
            positivos.append(f"✅ Calorias dentro da meta ({calorias_hoje}/{meta_calorica} kcal)")
        else:
            melhorias.append(f"⚠️ Calorias acima da meta em {calorias_hoje - meta_calorica} kcal")
        
        proteinas_sugeridas = int(user["current_weight"] * 1.6)
        melhorias.append(f"🥩 Proteína sugerida: {proteinas_sugeridas}g/dia")
        
        st.markdown(f'<div class="insight-box">{"".join(positivos)}{"".join(melhorias)}</div>', unsafe_allow_html=True)
    
    ranking = carregar_ranking()
    if ranking:
        st.markdown("### 🏆 Ranking Semanal")
        for i, row in enumerate(ranking[:5]):
            medalha = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}º"
            st.write(f"{medalha} **{row['user_name']}** – {row['points']} pontos")

def pagina_registrar(user):
    st.markdown("<h1>✏️ Registrar</h1>", unsafe_allow_html=True)
    hoje = date.today().isoformat()
    
    tab1, tab2, tab3 = st.tabs(["🍽️ Refeição", "⚖️ Peso", "😊 Humor"])
    
    with tab1:
        with st.form("form_refeicao"):
            col1, col2 = st.columns(2)
            with col1:
                meal_type = st.selectbox("Tipo", ["Café da manhã", "Almoço", "Jantar", "Lanche", "Pré-treino", "Pós-treino", "Ceia"])
                hour = st.time_input("Horário", datetime.now().time())
            with col2:
                food_name = st.text_input("O que comeu?")
                calories = st.number_input("Calorias (kcal)", 0, 2000, 300, 50)
            if st.form_submit_button("Salvar Refeição"):
                if food_name:
                    registrar_refeicao(user["id"], hoje, hour.strftime("%H:%M:%S"), meal_type, food_name, calories)
                    st.toast(f"✅ {meal_type} registrado!", icon="🍽️")
                    st.rerun()
    
    with tab2:
        with st.form("form_peso"):
            peso = st.number_input("Peso (kg)", 30.0, 300.0, user["current_weight"], 0.1)
            if st.form_submit_button("Salvar Peso"):
                registrar_peso(user["id"], peso, hoje)
                st.toast("✅ Peso registrado!", icon="⚖️")
                if abs(peso - user["target_weight"]) <= 2:
                    confetti()
                st.rerun()
    
    with tab3:
        with st.form("form_humor"):
            humor = st.selectbox("Como você está se sentindo?", ["Motivado 🚀", "Cansado 😴", "Determinado 💪", "Focado 🎯", "Ansioso 😰", "Frustrado 😞", "Orgulhoso 🏆"])
            consistencia = st.slider("Consistência hoje (0-100)", 0, 100, 70)
            if st.form_submit_button("Salvar Humor"):
                registrar_humor(user["id"], hoje, humor, consistencia)
                st.toast("✅ Humor registrado!", icon="😊")
                st.rerun()

def pagina_perfil(user):
    st.markdown("<h1>👤 Meu Perfil</h1>", unsafe_allow_html=True)
    with st.form("form_perfil"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", user["name"])
            idade = st.number_input("Idade", 18, 100, user["age"])
        with col2:
            altura = st.number_input("Altura (m)", 1.40, 2.50, user["height"], 0.01)
            meta_peso = st.number_input("Meta de peso (kg)", 40.0, 200.0, user["target_weight"], 0.5)
        if st.form_submit_button("Salvar Alterações"):
            supabase.table("users").update({"name": nome, "age": idade, "height": altura, "target_weight": meta_peso}).eq("id", user["id"]).execute()
            st.toast("Perfil atualizado!", icon="👤")
            st.rerun()

def pagina_planos():
    st.markdown("<h1>💎 Planos</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="es-card">
            <h3>🔥 GRÁTIS</h3>
            <p>R$ 0</p>
            <ul>
            <li>✅ Peso ilimitado</li>
            <li>✅ Até 8 refeições/dia</li>
            <li>✅ Histórico 30 dias</li>
            <li>✅ 1 dieta disponível</li>
            <li>📢 Anúncios leves</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="es-card">
            <h3>💎 PREMIUM</h3>
            <p>R$ 19,90/mês</p>
            <ul>
            <li>✅ Tudo do grátis</li>
            <li>✅ Refeições ilimitadas</li>
            <li>✅ Histórico completo</li>
            <li>✅ 10 dietas</li>
            <li>✅ IA e toques inteligentes</li>
            <li>✅ Ranking completo</li>
            <li>✅ Exportar CSV/PDF</li>
            <li>🚫 Sem anúncios</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔥 Testar 14 dias grátis", use_container_width=True):
        st.toast("🎉 Teste grátis ativado! Aproveite todos os recursos premium.", icon="🎉")
        confetti()

def sidebar(user):
    C = get_tema()
    with st.sidebar:
        st.markdown(f"<h2 style='color:{C['primary']}'>🔥 EmagreSim</h2>", unsafe_allow_html=True)
        
        tema_opts = ["claro", "escuro"]
        tema_idx = tema_opts.index(st.session_state.tema)
        tema = st.radio("🎨 Tema", tema_opts, index=tema_idx, horizontal=True, label_visibility="collapsed")
        if tema != st.session_state.tema:
            st.session_state.tema = tema
            st.rerun()
        
        st.markdown("---")
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.query_params["pagina"] = "dashboard"
            st.rerun()
        if st.button("✏️ Registrar", use_container_width=True):
            st.query_params["pagina"] = "Registrar"
            st.rerun()
        if st.button("👤 Perfil", use_container_width=True):
            st.query_params["pagina"] = "Perfil"
            st.rerun()
        if st.button("💎 Planos", use_container_width=True):
            st.query_params["pagina"] = "Planos"
            st.rerun()
        if st.button("🏆 Ranking", use_container_width=True):
            st.query_params["pagina"] = "ranking"
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.clear()
            st.rerun()
        
        st.caption(f"Olá, {user['name']}")

def pagina_login():
    C = get_tema()
    with st.form("login_form"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", use_container_width=True):
            user = fazer_login(email, senha)
            if user:
                st.session_state.user = carregar_usuario(user.id)
                st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Criar conta", use_container_width=True):
            st.query_params["pagina"] = "criar_conta"
            st.rerun()
    with col2:
        if st.button("🧪 Modo demonstração", use_container_width=True):
            st.query_params["pagina"] = "demo"
            st.rerun()

def pagina_criar_conta():
    with st.form("criar_conta_form"):
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        col1, col2 = st.columns(2)
        with col1:
            idade = st.number_input("Idade", 18, 100, 30)
            altura = st.number_input("Altura (m)", 1.40, 2.50, 1.75, 0.01)
        with col2:
            peso = st.number_input("Peso atual (kg)", 30.0, 300.0, 80.0, 0.1)
            meta_peso = st.number_input("Meta de peso (kg)", 40.0, 200.0, 70.0, 0.5)
        sexo = st.selectbox("Sexo", ["M", "F"])
        if st.form_submit_button("Criar Conta", use_container_width=True):
            user = criar_conta(email, senha, nome, idade, altura, peso, meta_peso, sexo)
            if user:
                st.success("✅ Conta criada! Faça login.")
                st.query_params.clear()
                st.rerun()
    
    if st.button("← Voltar para login"):
        st.query_params.clear()
        st.rerun()

def pagina_ranking():
    st.markdown("<h1>🏆 Ranking Semanal</h1>", unsafe_allow_html=True)
    ranking = carregar_ranking()
    if ranking:
        for i, row in enumerate(ranking[:20]):
            medalha = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}º"
            st.write(f"{medalha} **{row['user_name']}** – {row['points']} pontos")
    else:
        st.info("Nenhum ponto registrado esta semana. Registre suas atividades para aparecer no ranking!")
    
    if st.button("← Voltar"):
        st.query_params["pagina"] = "dashboard"
        st.rerun()

# -----------------------------------------------------------------------------
# 6. MAIN
# -----------------------------------------------------------------------------
def main():
    aplicar_css()
    
    if "user" not in st.session_state:
        st.session_state.user = None
    
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            user_data = carregar_usuario(session.user.id)
            if user_data:
                st.session_state.user = user_data
    except:
        pass
    
    pagina = st.query_params.get("pagina", "login")
    
    if pagina == "demo":
        pagina_demo()
    elif pagina == "criar_conta":
        pagina_criar_conta()
    elif pagina == "ranking":
        pagina_ranking()
    elif st.session_state.user is None:
        pagina_login()
    else:
        if pagina not in ["Registrar", "Perfil", "Planos", "dashboard", "ranking"]:
            st.query_params["pagina"] = "dashboard"
            pagina = "dashboard"
        
        sidebar(st.session_state.user)
        
        if pagina == "Registrar":
            pagina_registrar(st.session_state.user)
        elif pagina == "Perfil":
            pagina_perfil(st.session_state.user)
        elif pagina == "Planos":
            pagina_planos()
        elif pagina == "ranking":
            pagina_ranking()
        else:
            pagina_dashboard(st.session_state.user)

if __name__ == "__main__":
    main()
