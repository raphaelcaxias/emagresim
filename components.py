import streamlit as st

def card_metric(valor, label, icon="📊", cor="#0891b2"):
    st.markdown(f"""
    <div class="data-card">
        <div class="data-value" style="color:{cor}">{valor}</div>
        <div class="data-label">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)

def progress_bar(percent, cor="auto"):
    if cor == "auto":
        cor = "#10b981" if percent <= 100 else "#ef4444"
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width:{percent}%;background:{cor}"></div>
    </div>
    """, unsafe_allow_html=True)

def empty_state(icon, mensagem, dica=""):
    st.markdown(f"""
    <div style="text-align:center;padding:2rem;color:#94a3b8;">
        <div style="font-size:3rem;margin-bottom:0.5rem;">{icon}</div>
        <p style="margin:0;">{mensagem}</p>
        {f'<p style="font-size:0.85rem;margin-top:0.5rem;">{dica}</p>' if dica else ''}
    </div>
    """, unsafe_allow_html=True)
