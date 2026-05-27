# utils.py
import streamlit as st
import random
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import pandas as pd

from config import RECEITAS, CONQUISTAS

def calcular_imc(peso, altura):
    return peso / (altura ** 2)

def classificar_imc(imc):
    if imc < 18.5: return "Abaixo do peso"
    if imc < 25: return "Saudável"
    if imc < 30: return "Sobrepeso"
    if imc < 35: return "Obesidade Grau I"
    if imc < 40: return "Obesidade Grau II"
    return "Obesidade Grau III"

def calcular_tmb(peso, altura, idade, sexo):
    altura_cm = altura * 100
    tmb = (10 * peso) + (6.25 * altura_cm) - (5 * idade)
    return tmb + 5 if sexo == "M" else tmb - 161

def gerar_grafico_peso(historico, meta):
    fig = go.Figure()
    
    if historico:
        df = pd.DataFrame(historico)
        fig.add_trace(go.Scatter(
            x=df["data"], y=df["peso"],
            mode="lines+markers", name="Peso",
            line=dict(color="#FF4D00", width=3),
            marker=dict(size=6),
            fill="tozeroy", fillcolor="rgba(255,77,0,0.1)"
        ))
    else:
        # Dados simulados
        datas = [date.today() - timedelta(days=x) for x in range(30, -1, -1)]
        pesos = [85 - i * 0.15 + random.uniform(-0.5, 0.5) for i in range(31)]
        fig.add_trace(go.Scatter(
            x=datas, y=pesos,
            mode="lines+markers", name="Peso",
            line=dict(color="#FF4D00", width=3),
            fill="tozeroy", fillcolor="rgba(255,77,0,0.1)"
        ))
    
    fig.add_hline(y=meta, line_dash="dash", line_color="#22C55E",
                  annotation_text=f"Meta: {meta}kg", annotation_font_color="#22C55E")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Data", yaxis_title="Peso (kg)",
        height=350, margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def previsao_meta(peso_atual, peso_meta, ritmo=0.5):
    if peso_atual <= peso_meta:
        return None
    kg_restantes = peso_atual - peso_meta
    semanas = kg_restantes / ritmo
    return date.today() + timedelta(days=int(semanas * 7))

def receita_do_dia():
    return random.choice(RECEITAS)

def mensagem_bom_dia():
    hora = datetime.now().hour
    if hora < 12:
        return "?? Bom dia! Hoje é um novo começo."
    elif hora < 18:
        return "??? Boa tarde! Continue firme."
    return "?? Boa noite! Amanhã é outro dia."

def badge_desbloqueada(conquista_key):
    if "conquistas" not in st.session_state:
        st.session_state.conquistas = []
    
    for c in CONQUISTAS:
        if c["key"] == conquista_key and conquista_key not in st.session_state.conquistas:
            st.session_state.conquistas.append(conquista_key)
            return True
    return False

def progresso_meta_diaria(calorias_consumidas, meta_calorica):
    if meta_calorica <= 0:
        return 0
    return min(100, (calorias_consumidas / meta_calorica) * 100)