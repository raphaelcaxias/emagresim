# -*- coding: utf-8 -*-
"""
EmagreSim v13.0 - Com criação de conta, gráficos e layout responsivo
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from supabase import create_client, Client
import random

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÕES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Conectar ao Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["CHAVE_SUPABASE"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.warning("Modo offline - usando dados de demonstração")

# -----------------------------------------------------------------------------
# 2. CORES E TEMAS
# -----------------------------------------------------------------------------
if "tema" not in st.session_state:
    st.session_state.tema = "claro"

def get_tema():
    if st.session_state.tema == "claro":
        return {
            "bg": "#F8F9FA", "surface": "#FFFFFF", "card": "#FFFFFF",
            "primary": "#FF4D00", "text": "#1A1A1A", "text_muted": "#6B7280",
            "border": "rgba(0,0,0,0.08)", "shadow": "0 4px 12px rgba(0,0,0,0.05)"
        }
    else:
        return {
            "bg": "#0F172A", "surface": "#1E293B", "card": "#1E293B",
            "primary": "#FF4D00", "text": "#F8FAFC", "text_muted": "#94A3B8",
            "border": "rgba(255,255,255,0.08)", "shadow": "0 4px 12px rgba(0,0,0,0.2)"
        }

def aplicar_css():
    C = get_tema()
    css = f"""
    <style>
    .stApp {{ background: {C['bg']} !important; }}
    
    .card, .kpi-card {{
        background: {C['card']};
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid {C['border']};
        box-shadow: {C['shadow']};
        transition: all 0.3s ease;
    }}
    
    .card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }}
    
    .kpi-label {{ font-size: 0.7rem; color: {C['text_muted']}; text-transform: uppercase; }}
    .kpi-value {{ font-size: 1.8rem; font-weight: 800; color: {C['primary']}; }}
    
    h1, h2, h3 {{ color: {C['text']} !important; }}
    
    .stButton > button {{
        border-radius: 40px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }}
    .stButton > button:hover {{ transform: translateY(-2px); }}
    
    #MainMenu, header, footer, .stDeployButton {{ display: none; }}
    
    @media (max-width: 768px) {{
        .kpi-value {{ font-size: 1.3rem; }}
        .card {{ padding: 1rem; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------------
def criar_conta_simulada(nome, email, senha, idade, altura, peso, meta_peso, sexo):
    """Simula criação de conta (modo offline/demo)"""
    st.session_state["usuario"] = {
        "nome": nome, "email": email, "idade": idade,
        "altura": altura, "peso_atual": peso, "peso_meta": meta_peso, "sexo": sexo,
        "is_premium": False, "criado_em": date.today().isoformat()
    }
    return True

def login_simulado(email, senha):
    """Simula login com conta demo"""
    if email == "demo@emagresim.com" and senha == "demo123":
        st.session_state["usuario"] = {
            "nome": "Usuário Demo", "email": email, "idade": 30,
            "altura": 1.75, "peso_atual": 80.0, "peso_meta": 70.0,
            "sexo": "M", "is_premium": False
        }
        return True
    return False

def gerar_grafico_peso(pesos: list, meta: float):
    """Gera gráfico de evolução de peso"""
    if not pesos:
        # Dados simulados
        datas = [date.today() - timedelta(days=x) for x in range(30, -1, -1)]
        pesos_sim = [88 - i * 0.15 + random.uniform(-0.5, 0.5) for i in range(31)]
        df = pd.DataFrame({"data": datas, "peso": pesos_sim})
    else:
        df = pd.DataFrame(pesos)
        df["data"] = pd.to_datetime(df["data"])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["data"], y=df["peso"],
        mode="lines+markers", name="Peso",
        line=dict(color="#FF4D00", width=3),
        marker=dict(size=6, color="#FF4D00"),
        fill="tozeroy", fillcolor="rgba(255,77,0,0.1)"
    ))
    fig.add_hline(y=meta, line_dash="dash", line_color="#22C55E", 
                  annotation_text=f"Meta: {meta}kg", annotation_font_color="#22C55E")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Data", yaxis_title="Peso (kg)",
        height=350, margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# -----------------------------------------------------------------------------
# 4. PÁGINA DE CRIAÇÃO DE CONTA (COMPLETA)
# -----------------------------------------------------------------------------
def pagina_criar_conta():
    C = get_tema()
    st.markdown("<h1 style='text-align:center;'>🔥 Criar Conta</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_criar_conta"):
            nome = st.text_input("Nome completo", placeholder="Seu nome")
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            confirmar_senha = st.text_input("Confirmar senha", type="password", placeholder="••••••••")
            
            st.markdown("---")
            st.markdown("### 📊 Dados pessoais")
            
            col_a, col_b = st.columns(2)
            with col_a:
                idade = st.number_input("Idade", 18, 100, 30)
                altura = st.number_input("Altura (m)", 1.40, 2.50, 1.75, 0.01)
            with col_b:
                peso = st.number_input("Peso atual (kg)", 30.0, 300.0, 80.0, 0.1)
                meta_peso = st.number_input("Meta de peso (kg)", 40.0, 200.0, 70.0, 0.5)
            
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
            sexo_code = "M" if sexo == "Masculino" else "F"
            
            if st.form_submit_button("🔥 Criar minha conta", use_container_width=True):
                if not nome or not email or not senha:
                    st.error("Preencha todos os campos")
                elif senha != confirmar_senha:
                    st.error("As senhas não coincidem")
                else:
                    criar_conta_simulada(nome, email, senha, idade, altura, peso, meta_peso, sexo_code)
                    st.success("✅ Conta criada com sucesso!")
                    st.balloons()
                    st.query_params["pagina"] = "dashboard"
                    st.rerun()
        
        st.markdown("---")
        if st.button("← Voltar para login", use_container_width=True):
            st.query_params.clear()
            st.rerun()

# -----------------------------------------------------------------------------
# 5. PÁGINA DASHBOARD (COM GRÁFICOS)
# -----------------------------------------------------------------------------
def pagina_dashboard():
    C = get_tema()
    usuario = st.session_state.get("usuario", {})
    
    if not usuario:
        st.warning("Nenhum usuário logado. Faça login ou crie uma conta.")
        if st.button("Ir para login"):
            st.query_params.clear()
            st.rerun()
        return
    
    st.markdown(f"<h1>📊 Olá, {usuario.get('nome', 'Usuário')}!</h1>", unsafe_allow_html=True)
    
    # KPIs em grid responsivo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        imc = usuario["peso_atual"] / (usuario["altura"] ** 2)
        st.metric("Peso Atual", f"{usuario['peso_atual']:.1f} kg", f"Meta: {usuario['peso_meta']:.0f} kg")
    with col2:
        st.metric("IMC", f"{imc:.1f}", "Obesidade" if imc > 30 else "Sobrepeso" if imc > 25 else "Normal")
    with col3:
        tmb = (10 * usuario["peso_atual"]) + (6.25 * usuario["altura"] * 100) - (5 * usuario["idade"])
        tmb = tmb + 5 if usuario.get("sexo") == "M" else tmb - 161
        st.metric("TMB", f"{int(tmb)} kcal", "Basal")
    with col4:
        plano = "Premium ⭐" if usuario.get("is_premium") else "Grátis"
        st.metric("Plano", plano)
    
    # Gráfico de evolução
    st.markdown("### 📈 Evolução do Peso")
    fig = gerar_grafico_peso([], usuario["peso_meta"])
    st.plotly_chart(fig, use_container_width=True)
    
    # Previsão
    kg_restantes = usuario["peso_atual"] - usuario["peso_meta"]
    if kg_restantes > 0:
        ritmo = 0.5
        semanas = kg_restantes / ritmo
        data_estimada = date.today() + timedelta(days=int(semanas * 7))
        st.info(f"📅 **Previsão:** No ritmo de -{ritmo}kg/semana, você atinge sua meta em **{data_estimada.strftime('%d/%m/%Y')}**")
    
    # Recomendações
    with st.expander("💡 Recomendações Personalizadas", expanded=False):
        st.markdown(f"""
        - 🥩 **Proteína:** Priorize {int(usuario['peso_atual'] * 1.6)}g/dia
        - 💧 **Hidratação:** Beba 3L de água por dia
        - 🚶 **Movimento:** Caminhada leve 30min, 5x por semana
        """)
    
    # Botão de logout
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

# -----------------------------------------------------------------------------
# 6. PÁGINA DEMONSTRAÇÃO (ADRIANO)
# -----------------------------------------------------------------------------
def pagina_demo():
    C = get_tema()
    st.markdown("<h1>🧪 Modo Demonstração - Adriano</h1>", unsafe_allow_html=True)
    
    if st.button("← Voltar para o início", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    
    adriano = {"nome": "Adriano", "idade": 39, "altura": 1.75, "peso_atual": 144.0, "peso_meta": 90.0, "sexo": "M"}
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        imc = adriano["peso_atual"] / (adriano["altura"] ** 2)
        st.metric("Peso Atual", f"{adriano['peso_atual']:.1f} kg", f"Meta: {adriano['peso_meta']:.0f} kg")
        st.metric("IMC", f"{imc:.1f}", "Obesidade Grave (Grau III)")
    with col2:
        tmb = (10 * adriano["peso_atual"]) + (6.25 * adriano["altura"] * 100) - (5 * adriano["idade"]) + 5
        st.metric("TMB", f"{int(tmb)} kcal/dia")
        st.metric("Meta calórica", f"{int(tmb - 500)} kcal/dia")
    with col3:
        st.metric("Idade", f"{adriano['idade']} anos")
        st.metric("Altura", f"{adriano['altura']:.2f} m")
    
    # Gráfico
    st.markdown("### 📈 Projeção de Emagrecimento")
    fig = gerar_grafico_peso([], adriano["peso_meta"])
    st.plotly_chart(fig, use_container_width=True)
    
    # Previsão
    kg_restantes = adriano["peso_atual"] - adriano["peso_meta"]
    ritmo = 0.8
    semanas = kg_restantes / ritmo
    data_estimada = date.today() + timedelta(days=int(semanas * 7))
    st.info(f"📅 No ritmo de -{ritmo}kg/semana, você chega em {adriano['peso_meta']:.0f} kg em **{data_estimada.strftime('%d/%m/%Y')}**")
    
    # Recomendações
    with st.expander("💡 Recomendações", expanded=True):
        st.markdown("""
        - 🥩 **Proteína:** Priorize 2g/kg (≈288g/dia)
        - 💧 **Hidratação:** Beba 3L de água por dia
        - 🚶 **Movimento:** Caminhada leve 30min, 5x por semana
        - ⚠️ **Aviso:** Consulte um médico antes de começar
        """)
    
    # Metas
    st.markdown("### 📊 Metas Intermediárias")
    metas = [
        ("Obesidade Grau I (IMC 35)", 35 * (adriano["altura"] ** 2)),
        ("Sobrepeso (IMC 30)", 30 * (adriano["altura"] ** 2)),
        ("Saudável (IMC 25)", 25 * (adriano["altura"] ** 2)),
    ]
    for nome, peso_meta in metas:
        kg_faltam = adriano["peso_atual"] - peso_meta
        if kg_faltam > 0:
            st.write(f"- **{nome}:** perder {kg_faltam:.0f} kg (chegar a {peso_meta:.0f} kg)")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔥 Criar minha conta", use_container_width=True):
            st.query_params["pagina"] = "criar_conta"
            st.rerun()
    with col_b2:
        if st.button("📊 Ver Demo", use_container_width=True):
            st.query_params["pagina"] = "dashboard"
            st.rerun()

# -----------------------------------------------------------------------------
# 7. PÁGINA LOGIN
# -----------------------------------------------------------------------------
def pagina_login():
    st.markdown("<h1 style='text-align:center;'>🔥 EmagreSim</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com", value="demo@emagresim.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••", value="demo123")
            if st.form_submit_button("Entrar", use_container_width=True):
                if login_simulado(email, senha):
                    st.success("✅ Login realizado!")
                    st.query_params["pagina"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos. Use demo@emagresim.com / demo123")
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Criar conta", use_container_width=True):
                st.query_params["pagina"] = "criar_conta"
                st.rerun()
        with col_b:
            if st.button("🧪 Modo demonstração", use_container_width=True):
                st.query_params["pagina"] = "demo"
                st.rerun()

# -----------------------------------------------------------------------------
# 8. MAIN
# -----------------------------------------------------------------------------
def main():
    aplicar_css()
    
    pagina = st.query_params.get("pagina", "login")
    
    if pagina == "demo":
        pagina_demo()
    elif pagina == "criar_conta":
        pagina_criar_conta()
    elif pagina == "dashboard":
        pagina_dashboard()
    else:
        pagina_login()

if __name__ == "__main__":
    main()
