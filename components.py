import streamlit as st

def card_metric(valor, label, icon="📊", cor="#0891b2"):
    """Card de métrica padronizado."""
    st.markdown(f"""
    <div class="data-card">
        <div class="data-value" style="color:{cor}">{valor}</div>
        <div class="data-label">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)

def progress_bar(percent, cor="auto"):
    """Barra de progresso estilizada."""
    if cor == "auto":
        cor = "#10b981" if percent <= 100 else "#ef4444"
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width:{max(0, min(100, percent))}%; background:{cor}"></div>
    </div>
    """, unsafe_allow_html=True)

def empty_state(icon, mensagem, dica=""):
    """Estado vazio reutilizável para falta de dados."""
    st.markdown(f"""
    <div style="text-align:center; padding:2rem; color:#94a3b8; background:#f8fafc; border-radius:12px; margin:1rem 0;">
        <div style="font-size:3rem; margin-bottom:0.5rem;">{icon}</div>
        <p style="margin:0; font-weight:600;">{mensagem}</p>
        {f'<p style="font-size:0.85rem; margin-top:0.5rem; color:#64748b;">{dica}</p>' if dica else ''}
    </div>
    """, unsafe_allow_html=True)

def section_header(titulo, subtitulo="", emoji=""):
    """Cabeçalho de seção padronizado."""
    st.markdown(f"""
    <div style="margin-bottom:1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.5rem;">
        <h2 style="margin:0; color:#1e293b;">{emoji} {titulo}</h2>
        {f'<p style="color:#64748b; margin:0.25rem 0 0 0;">{subtitulo}</p>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)
