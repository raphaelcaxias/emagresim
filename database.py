# database.py
import streamlit as st

# Supabase desativado para mock (comente as linhas abaixo se for usar depois)
# from supabase import create_client, Client

def conectar_supabase():
    """Mock - implementar depois com st.secrets"""
    return None

def criar_usuario(dados):
    st.session_state["usuario"] = dados
    return True

def get_usuario():
    return st.session_state.get("usuario", None)

def salvar_peso(usuario_id, peso, data):
    """Mock - implementar depois"""
    return True

def salvar_refeicao(usuario_id, refeicao):
    """Mock - implementar depois"""
    return True

def get_ranking():
    """Mock - retorna ranking de exemplo"""
    return [
        {"nome": "Adriano", "pontos": 1250, "avatar": "🔥"},
        {"nome": "Mariana", "pontos": 980, "avatar": "💪"},
        {"nome": "Lucas", "pontos": 720, "avatar": "🏃"},
        {"nome": "Carla", "pontos": 540, "avatar": "🧘"},
        {"nome": "Pedro", "pontos": 310, "avatar": "🚴"},
    ]
