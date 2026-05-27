# styles.py
import streamlit as st

def get_tema():
    if "tema" not in st.session_state:
        st.session_state.tema = "claro"
    
    if st.session_state.tema == "claro":
        return {
            "bg": "#F8F9FA", "surface": "#FFFFFF", "card": "#FFFFFF",
            "primary": "#FF4D00", "text": "#1A1A1A", "text_muted": "#6B7280",
            "border": "rgba(0,0,0,0.08)", "shadow": "0 4px 12px rgba(0,0,0,0.05)",
            "hover": "0 8px 24px rgba(0,0,0,0.12)"
        }
    else:
        return {
            "bg": "#0F172A", "surface": "#1E293B", "card": "#1E293B",
            "primary": "#FF4D00", "text": "#F8FAFC", "text_muted": "#94A3B8",
            "border": "rgba(255,255,255,0.08)", "shadow": "0 4px 12px rgba(0,0,0,0.2)",
            "hover": "0 8px 24px rgba(0,0,0,0.3)"
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
    
    .card:hover, .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: {C['hover']};
    }}
    
    .kpi-label {{ font-size: 0.7rem; color: {C['text_muted']}; text-transform: uppercase; }}
    .kpi-value {{ font-size: 1.8rem; font-weight: 800; color: {C['primary']}; }}
    
    h1, h2, h3 {{ color: {C['text']} !important; }}
    
    .stButton > button {{
        border-radius: 40px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }}
    .stButton > button:hover {{ transform: translateY(-2px); }}
    
    .progress-track {{ background: rgba(0,0,0,0.1); border-radius: 99px; height: 6px; overflow: hidden; }}
    .progress-fill {{ height: 100%; border-radius: 99px; background: {C['primary']}; transition: width 0.5s; }}
    
    .insight-box {{
        background: rgba(255,77,0,0.08);
        border-left: 3px solid {C['primary']};
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }}
    
    #MainMenu, header, footer, .stDeployButton {{ display: none; }}
    
    @media (max-width: 768px) {{
        .kpi-value {{ font-size: 1.3rem; }}
        .card {{ padding: 1rem; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
