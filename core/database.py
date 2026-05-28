# core/database.py
import streamlit as st
from supabase import create_client
from typing import Optional, List, Dict
from .models import User, WeightLog, MealLog

def get_supabase():
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["CHAVE_SUPABASE"]
    return create_client(supabase_url, supabase_key)

# =============================================================================
# USUÁRIOS
# =============================================================================
def carregar_usuario(user_id: str) -> Optional[Dict]:
    supabase = get_supabase()
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except:
        return None

def criar_usuario(user_data: dict) -> bool:
    supabase = get_supabase()
    try:
        supabase.table("users").insert(user_data).execute()
        return True
    except:
        return False

def atualizar_usuario(user_id: str, updates: dict) -> bool:
    supabase = get_supabase()
    try:
        supabase.table("users").update(updates).eq("id", user_id).execute()
        return True
    except:
        return False

# =============================================================================
# PESOS
# =============================================================================
def carregar_historico_pesos(user_id: str, limite: int = 90) -> List[Dict]:
    supabase = get_supabase()
    try:
        result = supabase.table("weight_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("registered_at", desc=False)\
            .limit(limite)\
            .execute()
        return result.data
    except:
        return []

def salvar_peso(user_id: str, peso: float, data: datetime) -> bool:
    supabase = get_supabase()
    try:
        supabase.table("weight_logs").insert({
            "user_id": user_id,
            "peso_kg": peso,
            "registered_at": data.isoformat()
        }).execute()
        supabase.table("users").update({"current_weight": peso}).eq("id", user_id).execute()
        return True
    except:
        return False

# =============================================================================
# REFEIÇÕES
# =============================================================================
def carregar_refeicoes(user_id: str, limite: int = 30) -> List[Dict]:
    supabase = get_supabase()
    try:
        result = supabase.table("food_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("registered_at", desc=True)\
            .limit(limite)\
            .execute()
        return result.data
    except:
        return []
