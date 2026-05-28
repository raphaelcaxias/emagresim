# app.py
import streamlit as st
from datetime import datetime, timedelta
import random

# Configuração da página
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CORES (definidas aqui para evitar importação circular)
# =============================================================================
CORES = {
    "primary": "#FF6F61",
    "secondary": "#008080",
    "background": "#FAFAFA",
    "text": "#2D3748",
    "text_light": "#718096",
    "success": "#22C55E",
    "warning": "#FBBF24",
    "danger": "#EF4444",
}

# =============================================================================
# INICIALIZAR ESTADO DA SESSÃO
# =============================================================================
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "dashboard"
if "peso_atual" not in st.session_state:
    st.session_state["peso_atual"] = 105.8
if "refeicoes" not in st.session_state:
    st.session_state["refeicoes"] = []
if "historico_pesos" not in st.session_state:
    datas = [datetime.now() - timedelta(days=i) for i in range(30, -1, -1)]
    pesos = [108.0 - (i * 0.08) + random.uniform(-0.3, 0.3) for i in range(31)]
    st.session_state.historico_pesos = list(zip(datas, pesos))
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "demo-user"

# =============================================================================
# CSS GLOBAL
# =============================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', sans-serif;
    background-color: {CORES["background"]};
    color: {CORES["text"]};
}}

.topbar {{
    background: linear-gradient(135deg, {CORES["secondary"]} 0%, #005A5A 100%);
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 0 0 16px 16px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0, 128, 128, 0.15);
}}
.topbar-logo {{
    color: #FFFFFF;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}}
.topbar-logo span {{ color: {CORES["primary"]}; }}
.topbar-user {{ color: #E2E8F0; font-size: 0.9rem; font-weight: 500; }}

.hero-card {{
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 25px;
    border-left: 6px solid {CORES["primary"]};
}}
.avatar-container {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: white;
    padding: 4px;
    border: 4px solid {CORES["secondary"]};
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 2.2rem;
    box-shadow: 0 4px 10px rgba(0, 128, 128, 0.2);
}}
.hero-text h2 {{ margin: 0; color: #1A202C; font-size: 1.8rem; font-weight: 700; }}
.hero-text p {{ margin: 4px 0 0 0; color: #718096; font-size: 1rem; }}

.section-card {{
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    margin-bottom: 20px;
}}
.section-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: {CORES["text"]};
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.apoio-card {{
    background: #FFF5F5;
    border: 1px solid #FED7D7;
    border-radius: 12px;
    padding: 16px;
    height: 100%;
}}
.dica-card {{
    background: #EBF8FA;
    border: 1px solid #E2F8FA;
    border-radius: 12px;
    padding: 16px;
    height: 100%;
}}

.metric-coral div[data-testid="stMetric"] {{ border-top: 4px solid {CORES["primary"]}; }}
.metric-teal div[data-testid="stMetric"] {{ border-top: 4px solid {CORES["secondary"]}; }}
.metric-blue div[data-testid="stMetric"] {{ border-top: 4px solid #3182CE; }}
.metric-orange div[data-testid="stMetric"] {{ border-top: 4px solid #DD6B20; }}

#MainMenu, header, footer, .stDeployButton {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# TOPBAR
# =============================================================================
st.markdown(f"""
<div class="topbar">
    <div class="topbar-logo">🌱 Emagre<span>Sim</span></div>
    <div class="topbar-user">👤 Adriano | Modo Demo</div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# NAVEGAÇÃO
# =============================================================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state["pagina"] = "dashboard"
        st.rerun()
with col2:
    if st.button("🍽️ Refeições", use_container_width=True):
        st.session_state["pagina"] = "refeicoes"
        st.rerun()
with col3:
    if st.button("📈 Histórico", use_container_width=True):
        st.session_state["pagina"] = "historico"
        st.rerun()
with col4:
    if st.button("👤 Perfil", use_container_width=True):
        st.session_state["pagina"] = "perfil"
        st.rerun()

# =============================================================================
# FUNÇÕES AUXILIARES (para evitar importação circular)
# =============================================================================
def mensagem_bom_dia():
    from datetime import datetime
    hora = datetime.now().hour
    if hora < 12:
        return "🌅 Bom dia! Hoje é um novo começo."
    elif hora < 18:
        return "🌤️ Boa tarde! Continue firme."
    return "🌙 Boa noite! Amanhã é outro dia."

def calcular_avatar(percentual):
    if percentual >= 100:
        return "🏆", "Conquista! Você atingiu sua meta mensal!"
    elif percentual >= 75:
        return "⚡", "Quase lá! Continue firme."
    elif percentual >= 50:
        return "🌱", "Metade do caminho. Você está evoluindo."
    elif percentual >= 25:
        return "🔥", "Primeiros resultados! Continue assim."
    else:
        return "🌅", "Todo recomeço é uma semente. Confie no processo."

def calcular_imc(peso, altura):
    if altura <= 0:
        return 0
    return peso / (altura ** 2)

# =============================================================================
# PÁGINAS (definidas aqui para manter tudo em um arquivo)
# =============================================================================
def pagina_dashboard():
    usuario = {
        "nome": "Adriano",
        "altura": 1.75,
        "current_weight": st.session_state.get("peso_atual", 105.8),
        "meta_mensal_kg": 3.0,
        "peso_inicio_mes": 108.0
    }
    
    peso_atual = usuario["current_weight"]
    meta_kg = usuario["meta_mensal_kg"]
    progresso = usuario["peso_inicio_mes"] - peso_atual
    percentual = min(100, max(0, (progresso / meta_kg) * 100)) if meta_kg > 0 else 0
    avatar, msg_avatar = calcular_avatar(percentual)
    imc = calcular_imc(peso_atual, usuario["altura"])
    
    st.markdown(f"""
    <div class="hero-card">
        <div class="avatar-container">{avatar}</div>
        <div class="hero-text">
            <h2>Bem-vindo de volta, {usuario['nome']}!</h2>
            <p>🎯 {msg_avatar}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown('<div class="metric-coral">', unsafe_allow_html=True)
        st.metric("⚖️ Peso Atual", f"{peso_atual:.1f} kg", f"-{progresso:.1f} kg no mês")
        st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="metric-teal">', unsafe_allow_html=True)
        st.metric("📊 IMC", f"{imc:.1f}", "Referência 18.5 - 24.9")
        st.markdown('</div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="metric-blue">', unsafe_allow_html=True)
        st.metric("🎯 Meta do Mês", f"{meta_kg:.1f} kg", f"{percentual:.1f}% concluído")
        st.markdown('</div>', unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="metric-orange">', unsafe_allow_html=True)
        st.metric("🔥 Consistência", "14 Dias", "Sequência ativa!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg_avatar)
    
    st.info(mensagem_bom_dia())
    
    with st.expander("⚖️ Registrar peso hoje"):
        novo_peso = st.number_input("Peso (kg)", 40.0, 200.0, peso_atual, 0.1)
        if st.button("Salvar"):
            st.session_state["peso_atual"] = novo_peso
            st.success(f"✅ Peso registrado: {novo_peso:.1f} kg")
            st.rerun()
    
    col_apoio, col_dica = st.columns(2)
    with col_apoio:
        st.markdown("""
        <div class="apoio-card">
            <h4 style="margin: 0 0 8px 0; color: #E53E3E;">🫂 Suporte & Acolhimento</h4>
            <p style="margin: 0; font-size: 0.95rem;">"Dias difíceis e oscilações no peso fazem parte de jornadas reais. Não se julgue por ontem, foque no próximo passo certo."</p>
        </div>
        """, unsafe_allow_html=True)
    with col_dica:
        dicas = ["Mastigue devagar", "Beba água antes das refeições", "Durma 7-8h por noite"]
        st.markdown(f"""
        <div class="dica-card">
            <h4 style="margin: 0 0 8px 0; color: #008080;">💡 Dica do Dia</h4>
            <p style="margin: 0; font-size: 0.95rem;">"{random.choice(dicas)}"</p>
        </div>
        """, unsafe_allow_html=True)

def pagina_refeicoes():
    st.markdown('<div class="section-card"><div class="section-title">🍽️ Minhas Refeições</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Adicionar refeição", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", ["Café da manhã", "Almoço", "Jantar", "Lanche", "Pré-treino", "Pós-treino"])
            hora = st.time_input("Horário", datetime.now().time())
            descricao = st.text_area("O que comeu?", placeholder="Ex: Arroz, feijão, frango")
        with col2:
            calorias = st.number_input("Calorias (kcal)", 0, 2000, 400, 50)
            foto = st.camera_input("Tirar foto (opcional)")
        if st.button("✅ Salvar", use_container_width=True):
            if descricao:
                st.session_state.refeicoes.append({
                    "hora": hora.strftime("%H:%M"), "tipo": tipo,
                    "descricao": descricao, "calorias": calorias, "foto": foto
                })
                st.success("Refeição registrada!")
                st.rerun()
            else:
                st.warning("Digite uma descrição")
    
    if st.session_state.refeicoes:
        for ref in reversed(st.session_state.refeicoes[-10:]):
            st.markdown(f"""
            <div style="background:#F7FAFC; border-left:3px solid #008080; padding:12px; border-radius:8px; margin-bottom:12px;">
                <span style="font-size:0.75rem; color:#718096;">{ref['hora']} - {ref['tipo']}</span>
                <p style="margin:4px 0; font-size:0.9rem;">{ref['descricao']}</p>
                <span style="font-size:0.85rem; color:#FF6F61;">🔥 {ref['calorias']} kcal</span>
            </div>
            """, unsafe_allow_html=True)
        total = sum(r["calorias"] for r in st.session_state.refeicoes)
        st.markdown(f"<div style='background:#00808010; padding:15px; border-radius:12px;'><b>📊 Resumo:</b> {len(st.session_state.refeicoes)} refeições | {total} kcal</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhuma refeição registrada ainda.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def pagina_historico():
    st.markdown('<div class="section-card"><div class="section-title">📊 Histórico e Métricas</div>', unsafe_allow_html=True)
    
    import pandas as pd
    import plotly.express as px
    
    df = pd.DataFrame(st.session_state.historico_pesos, columns=["data", "peso"])
    df["data"] = pd.to_datetime(df["data"])
    
    fig = px.line(df, x="data", y="peso", markers=True, labels={"data": "Data", "peso": "Peso (kg)"})
    fig.update_traces(line=dict(color="#008080", width=3), marker=dict(size=6, color="#FF6F61"))
    fig.update_layout(height=350, plot_bgcolor='white', xaxis=dict(tickformat="%d/%m"))
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    peso_inicial = st.session_state.historico_pesos[0][1]
    peso_atual = st.session_state.historico_pesos[-1][1]
    with col1: st.metric("Peso inicial", f"{peso_inicial:.1f} kg")
    with col2: st.metric("Peso atual", f"{peso_atual:.1f} kg", f"{peso_atual - peso_inicial:+.1f} kg")
    with col3: st.metric("Melhor", f"{min(p[1] for p in st.session_state.historico_pesos):.1f} kg")
    with col4: st.metric("Pior", f"{max(p[1] for p in st.session_state.historico_pesos):.1f} kg")
    
    if st.session_state.refeicoes:
        st.markdown("### 🍽️ Últimas refeições")
        for ref in reversed(st.session_state.refeicoes[-5:]):
            st.markdown(f"""
            <div style="background:#F7FAFC; border-left:3px solid #FF6F61; padding:10px; border-radius:8px; margin-bottom:8px;">
                <span style="font-size:0.75rem;">{ref.get('hora','--:--')} - {ref['tipo']}</span>
                <p style="margin:2px 0; font-size:0.85rem;">{ref['descricao']} - 🔥 {ref['calorias']} kcal</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def pagina_perfil():
    st.markdown('<div class="section-card"><div class="section-title">👤 Meu Perfil</div>', unsafe_allow_html=True)
    
    usuario = {"nome": "Adriano", "idade": 39, "altura": 1.75, "meta_mensal_kg": 3.0}
    
    with st.form("editar_perfil"):
        nome = st.text_input("Nome", usuario["nome"])
        idade = st.number_input("Idade", 18, 100, usuario["idade"])
        altura = st.number_input("Altura (m)", 1.40, 2.20, usuario["altura"], 0.01)
        meta = st.number_input("Meta mensal (kg)", 0.0, 10.0, usuario["meta_mensal_kg"], 0.5)
        if st.form_submit_button("Salvar"):
            st.success("Perfil atualizado (modo demo)")
    
    st.markdown("### 📸 Foto de perfil")
    st.camera_input("Tirar foto")
    
    st.markdown("---")
    st.info("📌 Modo demonstração. Dados não são salvos permanentemente.")
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# ROTEAMENTO PRINCIPAL
# =============================================================================
pagina = st.session_state["pagina"]

if pagina == "dashboard":
    pagina_dashboard()
elif pagina == "refeicoes":
    pagina_refeicoes()
elif pagina == "historico":
    pagina_historico()
elif pagina == "perfil":
    pagina_perfil()
else:
    pagina_dashboard()
