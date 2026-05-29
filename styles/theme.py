"""
Configurações de tema para o EmagreSim
"""
import streamlit as st

class Theme:
    """Gerenciador de temas"""
    
    LIGHT_THEME = {
        "primary": "#667eea",
        "secondary": "#764ba2",
        "background": "#ffffff",
        "text": "#2c3e50"
    }
    
    DARK_THEME = {
        "primary": "#9f7aea",
        "secondary": "#6b46c0",
        "background": "#1a202c",
        "text": "#e2e8f0"
    }
    
    @staticmethod
    def apply_theme(theme_name: str = "light"):
        """Aplica o tema selecionado"""
        theme = Theme.LIGHT_THEME if theme_name == "light" else Theme.DARK_THEME
        
        st.markdown(f"""
        <style>
            :root {{
                --primary-color: {theme["primary"]};
                --secondary-color: {theme["secondary"]};
                --background-color: {theme["background"]};
                --text-color: {theme["text"]};
            }}
        </style>
        """, unsafe_allow_html=True)
