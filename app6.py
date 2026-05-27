# -*- coding: utf-8 -*-
"""
EmagreSim v11.0 - Com Supabase
- Previsão de meta com data
- Comparação "você vs você há 30 dias"
- Desafios semanais
- Modo escuro automático (baseado no horário)
- Confetes e celebração visual
- Registro de refeições com horário
- Feedback sob demanda
- Dia do lixo
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase import create_client, Client
import uuid
import random
from streamlit_confetti import confetti  # pip install streamlit-confetti

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
# 2. CORES E TEMAS (com automático por horário)
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
    .comparison-card {{ background: {C['surface']}; border-radius: 16px; padding: 16px; margin: 8px 0; border: 1px solid {C['border']}; }}
    .comparison-value {{ font-size: 1.5rem; font-weight: 800; color: {C['primary']}; }}
    .comparison-label {{ font-size: 0.7rem; color: {C['text_muted']}; text-transform: uppercase; }}
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
    """Retorna o desafio baseado na semana do ano"""
    semana = datetime.now().isocalendar()[1]
    return DESAFIOS[semana % len(DESAFIOS)]

# -----------------------------------------------------------------------------
# 4. FUNÇÕES DE AUTENTICAÇÃO E DADOS
# -----------------------------------------------------------------------------
def fazer_login(email: str, senha: str):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        return response.user
    except Exception as e:
        st.error(f"Email ou senha inválidos")
        return None

def criar_conta(email: str, senha: str, nome: str, idade: int, altura: float, peso: float, meta_peso: float, sexo: str):
    try:
        response = supabase.auth.sign_up({"email": email, "password": senha})
        if response.user:
            user_id = response.user.id
            supabase.table("users").insert({
                "id": user_id, "email": email, "name": nome, "age": idade,
                "height": altura, "current_weight": peso, "target_weight": meta_peso, "sex": sexo, "is_premium": False
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
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
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
    except Exception as e:
        return False

def registrar_refeicao(user_id: str, data_registro: str, hour: str, meal_type: str, food_name: str, calories: int, is_cheat_day: bool = False):
    try:
        supabase.table("food_logs").insert({
            "user_id": user_id, "date": data_registro, "hour": hour, "meal_type": meal_type,
            "food_name": food_name, "calories": calories
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar refeição: {e}")
        return False

def registrar_humor(user_id: str, data_registro: str, humor: str, consistencia: int):
    try:
        existing = supabase.table("checkin_logs").select("*").eq("user_id", user_id).eq("date", data_registro).execute()
        if existing.data:
            supabase.table("checkin_logs").update({"humor": humor, "consistency_score": consistencia}).eq("user_id", user_id).eq("date", data_registro).execute()
        else:
            supabase.table("checkin_logs").insert({"user_id": user_id, "date": data_registro, "humor": humor, "consistency_score": consistencia}).execute()
        return True
    except Exception as e:
        return False

def carregar_pesos(user_id: str, dias: int = 90):
    try:
        data_limite = (date.today() - timedelta(days=dias)).isoformat()
        result = supabase.table("weight_logs").select("*").eq("user_id", user_id).gte("date", data_limite).order("date").execute()
        return result.data
    except Exception as e:
        return []

def carregar_refeicoes(user_id: str, dias: int = 7):
    try:
        data_limite = (date.today() - timedelta(days=dias)).isoformat()
        result = supabase.table("food_logs").select("*").eq("user_id", user_id).gte("date", data_limite).order("date").execute()
        return result.data
    except Exception as e:
        return []

def carregar_ranking():
    try:
        result = supabase.rpc('get_weekly_ranking').execute()
        return result.data
    except Exception as e:
        return []

def calcular_previsao_meta(peso_atual: float, peso_meta: float, ritmo_semanal: float):
    """Calcula data estimada para atingir a meta baseado no ritmo atual"""
    if ritmo_semanal <= 0:
        return None
    kg_restantes = peso_atual - peso_meta
    semanas_restantes = kg_restantes / ritmo_semanal
    data_estimada = date.today() + timedelta(days=int(semanas_restantes * 7))
    return data_estimada

def calcular_ritmo_semanal(pesos: list):
    """Calcula ritmo médio de perda/ganho de peso por semana"""
    if len(pesos) < 14:
        return 0
    pesos_df = pd.DataFrame(pesos)
    pesos_df["date"] = pd.to_datetime(pesos_df["date"])
    pesos_df = pesos_df.sort_values("date")
    if len(pesos_df) >= 14:
        peso_inicio = pesos_df.iloc[-14]["weight"]
        peso_fim = pesos_df.iloc[-1]["weight"]
        diferenca = peso_fim - peso_inicio
        semanas = 2
        return round(diferenca / semanas, 2)
    return 0

def comparar_30_dias(pesos: list):
    """Compara peso atual com peso há 30 dias"""
    if len(pesos) < 30:
        return None
    pesos_df = pd.DataFrame(pesos)
    pesos_df["date"] = pd.to_datetime(pesos_df["date"])
    pesos_df = pesos_df.sort_values("date")
    peso_atual = pesos_df.iloc[-1]["weight"]
    peso_30d = pesos_df.iloc[-30]["weight"] if len(pesos_df) >= 30 else None
    if peso_30d:
        diferenca = peso_atual - peso_30d
        return {"peso_anterior": peso_30d, "peso_atual": peso_atual, "diferenca": diferenca}
    return None

# -----------------------------------------------------------------------------
# 5. FUNÇÕES DE FEEDBACK E ANÁLISE
# -----------------------------------------------------------------------------
def analisar_feedback_diario(refeicoes_hoje: list, meta_calorica: int, proteina_meta: int):
    """Gera feedback detalhado do dia sob demanda"""
    calorias_total = sum(r["calories"] for r in refeicoes_hoje)
    pontos_positivos = []
    pontos_melhoria = []
    
    if calorias_total <= meta_calorica:
        pontos_positivos.append(f"✅ Calorias dentro da meta ({calorias_total} / {meta_calorica} kcal)")
    else:
        pontos_melhoria.append(f"⚠️ Calorias acima da meta em {calorias_total - meta_calorica} kcal")
    
    # Análise de horários
    refeicoes_tarde = [r for r in refeicoes_hoje if r.get("hour") and r["hour"] > "21:00:00"]
    if refeicoes_tarde:
        pontos_melhoria.append(f"⚠️ {len(refeicoes_tarde)} refeições após 21h. Tente jantar mais cedo.")
    
    # Verificar se pulou refeições
    tipos_esperados = ["Café da manhã", "Almoço", "Jantar"]
    tipos_registrados = [r["meal_type"] for r in refeicoes_hoje]
    faltantes = [t for t in tipos_esperados if t not in tipos_registrados]
    if faltantes:
        pontos_melhoria.append(f"⚠️ Você não registrou: {', '.join(faltantes)}")
    else:
        pontos_positivos.append("✅ Todas as refeições principais registradas!")
    
    return pontos_positivos, pontos_melhoria

# -----------------------------------------------------------------------------
# 6. PÁGINAS
# -----------------------------------------------------------------------------
def pagina_demo():
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
        st.metric("TMB", f"{int(tmb)} kcal/dia", "Para manter o peso")
        st.metric("Meta calórica", f"{int(tmb - 500)} kcal/dia", "Déficit de 500 kcal")
    with col3:
        st.metric("Idade", f"{adriano['age']} anos")
        st.metric("Altura", f"{adriano['height']:.2f} m")
    
    st.markdown("### 📈 Projeção")
    ritmo = 0.5
    data_estimada = calcular_previsao_meta(adriano["current_weight"], adriano["target_weight"], ritmo)
    if data_estimada:
        st.info(f"🔥 No ritmo de **-{ritmo}kg/semana**, você chega em {adriano['target_weight']:.0f} kg em **{data_estimada.strftime('%d/%m/%Y')}**")
    
    st.markdown("### 💡 Recomendações")
    st.markdown("""
    - 🥩 Priorize proteínas (2g/kg = ~288g/dia)
    - 💧 Beba 3L de água por dia
    - 🚶 Caminhada leve 30min, 5x semana
    - ⚠️ Consulte um médico antes de começar
    """)
    
    if st.button("🔥 Criar minha conta", use_container_width=True):
        st.query_params["pagina"] = "criar_conta"
        st.rerun()

def pagina_dashboard(user):
    C = get_tema()
    st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)
    
    # Carregar dados
    pesos = carregar_pesos(user["id"])
    refeicoes = carregar_refeicoes(user["id"])
    hoje = date.today().isoformat()
    refeicoes_hoje = [r for r in refeicoes if r["date"] == hoje]
    calorias_hoje = sum(r["calories"] for r in refeicoes_hoje)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Peso Atual", f"{user['current_weight']:.1f} kg", f"Meta: {user['target_weight']:.0f} kg")
    with col2:
        imc = user["current_weight"] / (user["height"] ** 2)
        classificacao = "Obesidade Grave" if imc >= 40 else "Obesidade G II" if imc >= 35 else "Obesidade G I" if imc >= 30 else "Sobrepeso" if imc >= 25 else "Saudável"
        st.metric("IMC", f"{imc:.1f}", classificacao)
    with col3:
        st.metric("Calorias Hoje", f"{calorias_hoje} kcal", f"{len(refeicoes_hoje)} refeições")
    with col4:
        plano = "Premium" if user.get("is_premium", False) else "Grátis"
        st.metric("Plano", plano)
    
    # Comparação com você há 30 dias
    comparacao = comparar_30_dias(pesos)
    if comparacao:
        st.markdown(f"""
        <div class="comparison-card">
            <div class="comparison-label">📊 VOCÊ HÁ 30 DIAS vs HOJE</div>
            <div style="display: flex; justify-content: space-between;">
                <div><span class="comparison-value">{comparacao['peso_anterior']:.1f} kg</span><br>Há 30 dias</div>
                <div>→</div>
                <div><span class="comparison-value">{comparacao['peso_atual']:.1f} kg</span><br>Hoje</div>
            </div>
            <div class="comparison-value" style="color: {'#22C55E' if comparacao['diferenca'] < 0 else '#EF4444'}">
                {comparacao['diferenca']:+.1f} kg
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de peso
    if pesos:
        df = pd.DataFrame(pesos)
        df["date"] = pd.to_datetime(df["date"])
        fig = px.line(df, x="date", y="weight", title="Evolução do Peso", labels={"date": "Data", "weight": "Peso (kg)"})
        fig.update_layout(paper_bgcolor=C['card'], plot_bgcolor=C['card'], font_color=C['text'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Previsão de meta
    ritmo = calcular_ritmo_semanal(pesos)
    if ritmo != 0:
        data_estimada = calcular_previsao_meta(user["current_weight"], user["target_weight"], abs(ritmo))
        if data_estimada:
            st.info(f"📅 **Previsão:** No seu ritmo atual ({ritmo:+.1f}kg/semana), você atingirá sua meta em **{data_estimada.strftime('%d/%m/%Y')}**")
    
    # Desafio semanal
    desafio = get_desafio_semanal()
    with st.expander("🏆 Desafio da Semana", expanded=False):
        st.markdown(f"**{desafio['nome']}**")
        st.markdown(f"🎯 {desafio['descricao']}")
        st.markdown(f"⚡ Recompensa: {desafio['xp']} XP")
    
    # Botão de feedback
    if st.button("🔍 Como foi meu dia hoje?", use_container_width=True):
        meta_calorica = int((10 * user["current_weight"]) + (6.25 * user["height"] * 100) - (5 * user["age"]) - 500)
        positivos, melhorias = analisar_feedback_diario(refeicoes_hoje, meta_calorica, 150)
        
        feedback_html = ""
        if positivos:
            feedback_html += "<h4>✅ Pontos positivos</h4>" + "".join(f"<p>{p}</p>" for p in positivos)
        if melhorias:
            feedback_html += "<h4>⚠️ O que pode melhorar</h4>" + "".join(f"<p>{m}</p>" for m in melhorias)
        
        if not positivos and not melhorias:
            feedback_html = "<p>Registre mais refeições para receber feedback personalizado!</p>"
        
        st.markdown(f'<div class="insight-box">{feedback_html}</div>', unsafe_allow_html=True)
    
    # Ranking
    ranking = carregar_ranking()
    if ranking:
        st.markdown("### 🏆 Ranking Semanal")
        for i, row in enumerate(ranking[:5]):
            medalha = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}º"
            st.write(f"{medalha} **{row['user_name']}** - {row['points']} pontos")

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
                is_cheat_day = st.checkbox("🍕 Dia do lixo? (não conta para o déficit)")
            with col2:
                food_name = st.text_input("O que comeu?")
                calories = st.number_input("Calorias (kcal)", 0, 2000, 300, 50)
            
            if st.form_submit_button("Salvar Refeição"):
                if food_name:
                    registrar_refeicao(user["id"], hoje, hour.strftime("%H:%M:%S"), meal_type, food_name, calories, is_cheat_day)
                    st.toast(f"✅ {meal_type} registrado! +{calories} kcal", icon="🍽️")
                    st.rerun()
    
    with tab2:
        with st.form("form_peso"):
            peso = st.number_input("Peso (kg)", 30.0, 250.0, user["current_weight"], 0.1)
            if st.form_submit_button("Salvar Peso"):
                registrar_peso(user["id"], peso, hoje)
                st.toast("✅ Peso registrado!", icon="⚖️")
                st.rerun()
    
    with tab3:
        with st.form("form_humor"):
            humor = st.selectbox("Como você está se sentindo?", ["Motivado", "Cansado", "Determinado", "Focado", "Ansioso", "Frustrado", "Orgulhoso"])
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
            altura = st.number_input("Altura (m)", 1.40, 2.20, user["height"], 0.01)
            meta_peso = st.number_input("Meta de peso (kg)", 40.0, 200.0, user["target_weight"], 0.5)
        if st.form_submit_button("Salvar Alterações"):
            try:
                supabase.table("users").update({"name": nome, "age": idade, "height": altura, "target_weight": meta_peso}).eq("id", user["id"]).execute()
                st.toast("Perfil atualizado!", icon="👤")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")

def pagina_planos():
    st.markdown("<h1>💎 Planos</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="es-card">
            <h3>🔥 GRÁTIS</h3>
            <p>R$ 0</p>
            <ul>
            <li>✅ Peso ilimitado</li>
            <li>✅ Até 8 refeições/dia</li>
            <li>✅ Histórico 30 dias</li>
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
            <li>✅ IA e toques inteligentes</li>
            <li>✅ Ranking completo</li>
            <li>✅ Exportar CSV/PDF</li>
            <li>🚫 Sem anúncios</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="es-card">
            <h3>👨‍👩‍👧‍👦 FAMÍLIA</h3>
            <p>R$ 49,90/mês</p>
            <ul>
            <li>✅ Premium para até 5 usuários</li>
            <li>✅ Ranking familiar</li>
            <li>✅ Desafios em grupo</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔥 Testar 14 dias grátis", use_container_width=True):
        st.toast("🎉 Teste grátis ativado!", icon="🎉")
        confetti()

def sidebar(user):
    C = get_tema()
    with st.sidebar:
        st.markdown(f"<h2 style='color:{C['primary']}'>🔥 EmagreSim</h2>", unsafe_allow_html=True)
        
        tema_opts = ["auto", "claro", "escuro"]
        tema_idx = tema_opts.index(st.session_state.tema)
        tema = st.radio("🎨 Tema", tema_opts, index=tema_idx, horizontal=True, label_visibility="collapsed")
        if tema != st.session_state.tema:
            st.session_state.tema = tema
            st.rerun()
        
        st.markdown("---")
        st.page_link("app.py", label="📊 Dashboard", icon="📊")
        st.page_link("app.py", label="✏️ Registrar", icon="✏️")
        st.page_link("app.py", label="👤 Perfil", icon="👤")
        st.page_link("app.py", label="💎 Planos", icon="💎")
        st.markdown("---")
        
        if st.button("🚪 Sair", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.clear()
            st.rerun()
        
        st.caption(f"Olá, {user['name']}")

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
            <p style="text-align:center;"><a href="?pagina=criar_conta">Criar conta</a></p>
            <p style="text-align:center;"><a href="?pagina=demo">🧪 Testar demonstração (Adriano)</a></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    elif pagina == "planos":
        pagina_planos()
    elif st.session_state.user is None:
        pagina_login()
    else:
        user = st.session_state.user
        sidebar(user)
        
        if pagina == "Registrar":
            pagina_registrar(user)
        elif pagina == "Perfil":
            pagina_perfil(user)
        elif pagina == "Planos":
            pagina_planos()
        else:
            pagina_dashboard(user)

if __name__ == "__main__":
    main()
