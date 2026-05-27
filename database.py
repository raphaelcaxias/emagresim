# database.py
import streamlit as st
from supabase import create_client, Client

def conectar_supabase():
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["CHAVE_SUPABASE"]
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

# Funções para usuário (mock enquanto não usa banco real)
def criar_usuario(dados):
    st.session_state["usuario"] = dados
    return True

def get_usuario():
    return st.session_state.get("usuario", None)

def salvar_peso(usuario_id, peso, data):
    # Mock - implementar depois
    return True

def salvar_refeicao(usuario_id, refeicao):
    # Mock
    return True

def get_ranking():
    # Mock
    return [
        {"nome": "Adriano", "pontos": 1250, "avatar": "??"},
        {"nome": "Mariana", "pontos": 980, "avatar": "??"},
        {"nome": "Lucas", "pontos": 720, "avatar": "??"},
    ]