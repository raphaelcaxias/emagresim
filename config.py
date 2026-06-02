import streamlit as st
import os

# Configurações da Aplicação
APP_TITLE = "EmagreSim"
APP_ICON = ""
THEME_PRIMARY_COLOR = "#0891b2"

# Verificar se está rodando no Streamlit Cloud
IS_DEPLOYED = "STREAMLIT_APP" in os.environ

# Credenciais de Demonstração
DEMO_USER_EMAIL = "demo@emagresim.com"
DEMO_USER_PASS = "demo"

# Configurações de Segurança
MIN_CALORIE_GOAL = 1200