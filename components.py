import streamlit as st

def card_metric(valor, label, icon="📊", cor="#0891b2"):
    """Card de métrica reutilizável"""
    st.markdown(f"""
    <div class="data-card">
        <div class="data-value" style="color:{cor}">{valor}</div>
        <div class="data-label">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)

def progress_bar(percent, cor="auto"):
    """Barra de progresso estilizada"""
    if cor == "auto":
        cor = "#10b981" if percent <= 100 else "#ef4444"
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width:{percent}%;background:{cor}"></div>
    </div>
    """, unsafe_allow_html=True)

def empty_state(icon, mensagem, dica=""):
    """Estado vazio elegante"""
    st.markdown(f"""
    <div style="text-align:center;padding:2rem;color:#94a3b8;">
        <div style="font-size:3rem;margin-bottom:0.5rem;">{icon}</div>
        <p style="margin:0;">{mensagem}</p>
        {f'<p style="font-size:0.85rem;margin-top:0.5rem;">{dica}</p>' if dica else ''}
    </div>
    """, unsafe_allow_html=True)

def section_header(titulo, subtitulo="", emoji=""):
    """Cabeçalho de seção"""
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <h2 style="margin:0;">{emoji} {titulo}</h2>
        {f'<p style="color:#64748b;margin:0.25rem 0 0 0;">{subtitulo}</p>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)

def info_box(mensagem, tipo="info"):
    """Caixa de informação estilizada"""
    cores = {
        "info": "#0891b2",
        "sucesso": "#10b981",
        "alerta": "#f59e0b",
        "erro": "#ef4444"
    }
    cor = cores.get(tipo, cores["info"])
    st.markdown(f"""
    <div style="background:{cor}15;border-left:4px solid {cor};padding:0.75rem 1rem;border-radius:8px;margin:1rem 0;">
        {mensagem}
    </div>
    """, unsafe_allow_html=True)