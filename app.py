# app.py - EmagreSim v25.0 (Modo Demonstração Completo em Português)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import random

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA & ESTILIZAÇÃO CUSTOMIZADA (CSS CORAL & TEAL)
# =============================================================================
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Injeção de CSS para layout moderno, tipografia limpa e paleta Coral/Teal
st.markdown("""
<style>
    /* Importação de Fonte Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAFA;
        color: #2D3748;
    }
    
    /* Topbar Customizada */
    .topbar {
        background: linear-gradient(135deg, #008080 0%, #005A5A 100%);
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 0 0 16px 16px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0, 128, 128, 0.15);
    }
    .topbar-logo {
        color: #FFFFFF;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .topbar-logo span {
        color: #FF6F61;
    }
    .topbar-user {
        color: #E2E8F0;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Hero Card com Anel de Avatar */
    .hero-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        display: flex;
        align-items: center;
        gap: 24px;
        margin-bottom: 25px;
        border-left: 6px solid #FF6F61;
    }
    .avatar-container {
        position: relative;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: white;
        padding: 4px;
        border: 4px solid #008080; /* Anel Teal */
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 2.2rem;
        box-shadow: 0 4px 10px rgba(0, 128, 128, 0.2);
    }
    .hero-text h2 {
        margin: 0;
        color: #1A202C;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .hero-text p {
        margin: 4px 0 0 0;
        color: #718096;
        font-size: 1rem;
    }

    /* Customização de Cards de Métricas e Bordas Coloridas */
    div[data-testid="stMetric"] {
        background-color: white !important;
        border-radius: 12px !important;
        padding: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }
    /* Cores de Destaque nas Métricas via seletores de coluna */
    .metric-coral div[data-testid="stMetric"] { border-top: 4px solid #FF6F61; }
    .metric-teal div[data-testid="stMetric"] { border-top: 4px solid #008080; }
    .metric-blue div[data-testid="stMetric"] { border-top: 4px solid #3182CE; }
    .metric-orange div[data-testid="stMetric"] { border-top: 4px solid #DD6B20; }

    /* Cards de Seção */
    .section-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Bloco de Apoio Emocional Side-by-Side */
    .apoio-card {
        background: #FFF5F5;
        border: 1px solid #FED7D7;
        border-radius: 12px;
        padding: 16px;
        height: 100%;
    }
    .dica-card {
        background: #EBF8FA;
        border: 1px solid #E2F8FA;
        border-radius: 12px;
        padding: 16px;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ESTADO DA SESSÃO (INTERATIVIDADE EM TEMPO REAL)
# =============================================================================
if "peso_atual" not in st.session_state:
    st.session_state.peso_atual = 105.8
if "habitos" not in st.session_state:
    st.session_state.habitos = {
        "💧 Água (2L+)": True,
        "🥗 Salada no Almoço": False,
        "🚶 8k Passos": True,
        "😴 7h+ Sono": False
    }
if "refeicoes" not in st.session_state:
    st.session_state.refeicoes = [
        {"hora": "08:00", "tipo": "Café da manhã", "desc": "Ovos mexidos, café sem açúcar e mamão", "cal": 320},
        {"hora": "12:30", "tipo": "Almoço", "desc": "Arroz integral, feijão, patinho grelhado e salada verde", "cal": 580},
        {"hora": "16:00", "tipo": "Lanche", "desc": "Iogurte natural desnatado com whey e aveia", "cal": 240}
    ]

# =============================================================================
# FUNÇÕES AUXILIARES LÓGICAS
# =============================================================================
def calcular_imc(peso, altura):
    return peso / (altura ** 2) if altura > 0 else 0

def get_avatar_info(percentual):
    if percentual >= 100: return "🏆", "Meta batida! Você é gigante!"
    if percentual >= 75:  return "⚡", "Reta final! Ritmo acelerado."
    if percentual >= 50:  return "🌱", "Metade do caminho concluída. Siga firme!"
    if percentual >= 25:  return "🔥", "Evolução visível! Não para agora."
    return "🌅", "Foco no processo. Cada escolha conta!"

# =============================================================================
# 1. TOPBAR COM LOGO PRÓPRIA
# =============================================================================
st.markdown(f"""
<div class="topbar">
    <div class="topbar-logo">🌱 Emagre<span>Sim</span></div>
    <div class="topbar-user">👤 Modo Demonstração &nbsp;|&nbsp; <b>Adriano</b> (39 anos)</div>
</div>
""", unsafe_allow_html=True)

# Dados Base Fixos
ALTURA = 1.75
PESO_INICIAL_MES = 108.0
META_MENSAL_KG = 3.0

# Cálculos reativos baseados no Session State
delta_mensal = PESO_INICIAL_MES - st.session_state.peso_atual
percentual_meta = min(100.0, max(0.0, (delta_mensal / META_MENSAL_KG) * 100))
avatar_emoji, avatar_msg = get_avatar_info(percentual_meta)
imc_atual = calcular_imc(st.session_state.peso_atual, ALTURA)

# =============================================================================
# 2. HERO CARD COM ANEL DE AVATAR
# =============================================================================
st.markdown(f"""
<div class="hero-card">
    <div class="avatar-container">{avatar_emoji}</div>
    <div class="hero-text">
        <h2>Bem-vindo de volta, Adriano!</h2>
        <p>🎯 {avatar_msg}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# 3. METRICAS EM GRID DE 4 CARDS (COM ACENTOS COLORIDOS VIA CSS)
# =============================================================================
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown('<div class="metric-coral">', unsafe_allow_html=True)
    st.metric("⚖️ Peso Atual", f"{st.session_state.peso_atual:.1f} kg", f"-{delta_mensal:.1f} kg no mês")
    st.markdown('</div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="metric-teal">', unsafe_allow_html=True)
    st.metric("📊 IMC Reativo", f"{imc_atual:.1f}", "Faixa ideal: 18.5 - 24.9")
    st.markdown('</div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="metric-blue">', unsafe_allow_html=True)
    st.metric("🎯 Meta do Mês", f"{META_MENSAL_KG:.1f} kg", f"{percentual_meta:.1f}% concluído")
    st.markdown('</div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="metric-orange">', unsafe_allow_html=True)
    st.metric("🔥 Consistência", "14 Dias", "Sequência ativa!")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout Principal splitado em 2 Colunas (Dashboard Esquerda / Entradas Direita)
col_esq, col_dir = st.columns([2, 1], gap="large")

with col_esq:
    # =============================================================================
    # 4. GRÁFICO DE LINHA ESTILIZADO (PALETA TEAL/CORAL)
    # =============================================================================
    st.markdown('<div class="section-card"><div class="section-title">📈 Curva de Evolução do Peso</div>', unsafe_allow_html=True)
    datas = [date.today() - timedelta(days=i) for i in range(15, -1, -1)]
    pesos_historico = [108.0 - (i * 0.15) + random.uniform(-0.1, 0.1) for i in range(15)] + [st.session_state.peso_atual]
    df_pesos = pd.DataFrame({"Data": datas, "Peso (kg)": pesos_historico})
    
    fig = px.line(df_pesos, x="Data", y="Peso (kg)", markers=True)
    fig.update_traces(line=dict(color="#008080", width=3), marker=dict(size=8, color="#FF6F61"))
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        height=260,
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#F0F0F0', tickformat="%d/%m"),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # =============================================================================
    # 5. GRID DE REFEIÇÕES DO DIA
    # =============================================================================
    st.markdown('<div class="section-card"><div class="section-title">🍽️ Linha do Tempo Alimentar</div>', unsafe_allow_html=True)
    
    ref_cols = st.columns(3)
    for idx, ref in enumerate(st.session_state.refeicoes):
        with ref_cols[idx % 3]:
            st.markdown(f"""
            <div style="background: #F7FAFC; border-left: 3px solid #008080; padding: 12px; border-radius: 8px; height: 100%;">
                <span style="font-size: 0.8rem; color: #718096; font-weight: 600;">{ref['hora']} - {ref['tipo']}</span>
                <p style="margin: 4px 0; font-size: 0.9rem; font-weight: 500;">{ref['desc']}</p>
                <span style="font-size: 0.85rem; color: #FF6F61; font-weight: 600;">🔥 {ref['cal']} kcal</span>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

with col_dir:
    # =============================================================================
    # 6. FORMULÁRIO DINÂMICO DE PESO REATIVO
    # =============================================================================
    st.markdown('<div class="section-card"><div class="section-title">⚖️ Atualizar Peso Atual</div>', unsafe_allow_html=True)
    
    novo_peso = st.number_input(
        "Registre sua pesagem de hoje (kg):", 
        min_value=40.0, max_value=200.0, 
        value=st.session_state.peso_atual, 
        step=0.1
    )
    
    if novo_peso != st.session_state.peso_atual:
        st.session_state.peso_atual = novo_peso
        st.toast(f"Peso atualizado para {novo_peso}kg! Calculando novas métricas...", icon="⚖️")
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

    # =============================================================================
    # 7. HÁBITOS CLICÁVEIS COM FEEDBACK EM TEMPO REAL (CHECKBOXES ESTILIZADAS)
    # =============================================================================
    st.markdown('<div class="section-card"><div class="section-title">🎯 Metas Diárias (Clique para mudar)</div>', unsafe_allow_html=True)
    
    habitos_concluidos = 0
    for habito, status in st.session_state.habitos.items():
        # Checkbox nativo que atua diretamente modificando o dicionário de estados
        novo_status = st.checkbox(habito, value=status, key=f"hab_{habito}")
        if novo_status != status:
            st.session_state.habitos[habito] = novo_status
            if novo_status:
                st.toast(f"Parabéns! Você concluiu: {habito}", icon="✅")
            st.rerun()
        if novo_status:
            habitos_concluidos += 1
            
    # Barra de Progresso de Hábitos Integrada
    pct_habitos = habitos_concluidos / len(st.session_state.habitos)
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.progress(pct_habitos, text=f"Hábitos do dia: {habitos_concluidos}/{len(st.session_state.habitos)}")
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 8. BARRAS DE PROGRESSO SEPARADAS POR CATEGORIA
# =============================================================================
st.markdown('<div class="section-card"><div class="section-title">📊 Visão Geral de Metas</div>', unsafe_allow_html=True)
c_prog1, c_prog2, c_prog3 = st.columns(3)
with c_prog1:
    st.progress(percentual_meta / 100, text=f"Metas de Peso Mensal: {percentual_meta:.1f}%")
with c_prog2:
    st.progress(pct_habitos, text=f"Consistência Rotineira Diária: {pct_habitos*100:.0f}%")
with c_prog3:
    # Simulação calórica diária baseado no log alimentício
    total_cal = sum(r['cal'] for r in st.session_state.refeicoes)
    meta_cal = 2000
    st.progress(min(1.0, total_cal/meta_cal), text=f"Orçamento Calórico Consumido: {total_cal}/{meta_cal} kcal")
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# 9. LADO A LADO: DICA DO DIA & APOIO EMOCIONAL
# =============================================================================
col_dica, col_apoio = st.columns(2)

with col_dica:
    st.markdown("""
    <div class="dica-card">
        <h4 style="margin: 0 0 8px 0; color: #008080;">💡 Dica Saudável do Dia</h4>
        <p style="margin: 0; font-size: 0.95rem; color: #2D3748; line-height: 1.5;">
            "Mastigue devagar: o sistema digestivo demora cerca de 20 minutos para enviar os sinais de saciedade total ao cérebro. Aproveite a refeição!"
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_apoio:
    st.markdown("""
    <div class="apoio-card">
        <h4 style="margin: 0 0 8px 0; color: #E53E3E;">🫂 Suporte & Acolhimento</h4>
        <p style="margin: 0; font-size: 0.95rem; color: #2D3748; line-height: 1.5;">
            "Dias difíceis e oscilações no peso fazem parte de jornadas reais. Não se julgue por ontem, foque no próximo pequeno passo certo que você pode dar agora."
        </p>
    </div>
    """, unsafe_allow_html=True)

# Rodapé informativo fixado de forma limpa
st.markdown("""
<br><hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 20px 0;">
<div style="text-align: center; color: #A0AEC0; font-size: 0.85rem;">
    📌 EmagreSim v25.0 • Desenvolvido com foco em psicologia comportamental e usabilidade transparente.
</div>
""", unsafe_allow_html=True)
