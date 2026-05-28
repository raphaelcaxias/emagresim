# app.py - EmagreSim (Modo Demonstração Direto)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🌱",
    layout="wide",
)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================
def calcular_imc(peso, altura):
    if altura <= 0:
        return 0
    return peso / (altura ** 2)

def mensagem_bom_dia():
    hora = datetime.now().hour
    if hora < 12:
        return "🌅 Bom dia! Hoje é um novo começo."
    elif hora < 18:
        return "🌤️ Boa tarde! Continue firme."
    return "🌙 Boa noite! Amanhã é outro dia."

def get_avatar(percentual):
    if percentual >= 100:
        return "🏆", "Conquista! Você atingiu sua meta mensal!"
    elif percentual >= 75:
        return "⚡", "Quase lá! Continue firme."
    elif percentual >= 50:
        return "🌱", "Metade do caminho. Você está evoluindo."
    elif percentual >= 25:
        return "🔥", "Primeiros resultados! Continue assim."
    else:
        return "🌅", "Todo recomeço é uma semente. Confie no processo."

# =============================================================================
# PÁGINA PRINCIPAL (MODO DEMONSTRAÇÃO)
# =============================================================================
def pagina_demo():
    st.markdown("<h1 style='text-align:center;'>🌱 EmagreSim</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Para quem já tentou de tudo. Dessa vez, sem julgamento.</p>", unsafe_allow_html=True)
    
    # Dados do Adriano
    usuario = {
        "nome": "Adriano",
        "idade": 39,
        "altura": 1.75,
        "current_weight": 108.0,
        "meta_mensal_kg": 2.0,
        "peso_inicio_mes": 108.0
    }
    
    # Simular histórico de peso
    pesos = [{"registered_at": date.today() - timedelta(days=i), "peso_kg": 108.0 - i * 0.1} for i in range(30)]
    df_pesos = pd.DataFrame(pesos)
    
    peso_atual = usuario["current_weight"]
    meta_kg = usuario["meta_mensal_kg"]
    progresso = usuario["peso_inicio_mes"] - peso_atual
    percentual = min(100, max(0, (progresso / meta_kg) * 100)) if meta_kg > 0 else 0
    
    avatar, msg = get_avatar(percentual)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 4rem; text-align: center;'>{avatar}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1>Olá, {usuario['nome']}!</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Peso Atual", f"{peso_atual:.1f} kg", f"{progresso:+.1f} kg")
    with k2:
        imc = calcular_imc(peso_atual, usuario["altura"])
        st.metric("IMC", f"{imc:.1f}", "referência")
    with k3:
        st.metric("Meta mensal", f"{meta_kg:.1f} kg", f"{progresso:.1f} kg")
    with k4:
        st.metric("Sequência", "30 dias", "")
    
    # Barra de progresso
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg)
    
    # Gráfico de evolução
    if not df_pesos.empty:
        df_pesos["registered_at"] = pd.to_datetime(df_pesos["registered_at"])
        fig = px.line(df_pesos, x="registered_at", y="peso_kg", 
                      title="Evolução do Peso",
                      labels={"registered_at": "Data", "peso_kg": "Peso (kg)"})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Registrar peso (simulado)
    with st.expander("⚖️ Registrar peso hoje"):
        novo_peso = st.number_input("Peso (kg)", 30.0, 300.0, peso_atual, 0.1)
        if st.button("Salvar"):
            st.success(f"✅ Peso registrado: {novo_peso:.1f} kg")
            st.toast("Simulação: dados não são salvos permanentemente.", icon="ℹ️")
    
    # Apoio emocional
    st.markdown("""
    <div style="background: rgba(255,255,255,0.05); border-radius: 20px; padding: 15px; text-align: center; margin: 15px 0;">
        <span style="font-size: 1.2rem;">🫂</span>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">Dias difíceis acontecem. Você não está sozinho.</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN
# =============================================================================
def main():
    pagina_demo()

if __name__ == "__main__":
    main()
