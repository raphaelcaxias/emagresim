# app.py - EmagreSim v25.0 (Modo Demonstração Completo em Português)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import locale

# Tentar configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'portuguese')
    except:
        pass  # mantém padrão

st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="auto",
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

def formatar_data_brasil(data):
    return data.strftime("%d/%m/%Y")

# =============================================================================
# REGISTRO DE REFEIÇÕES
# =============================================================================
def registrar_refeicao():
    """Interface para registrar refeição com foto"""
    with st.expander("🍽️ Registrar refeição", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            tipo = st.selectbox("Tipo de refeição", [
                "Café da manhã", "Almoço", "Jantar", "Lanche", "Pré-treino", "Pós-treino"
            ])
            descricao = st.text_area("O que você comeu?", placeholder="Ex: Arroz, feijão, frango grelhado, salada")
            calorias = st.number_input("Calorias (kcal)", min_value=0, max_value=2000, value=400, step=50)
            
            if st.button("✅ Salvar refeição", use_container_width=True):
                if descricao:
                    st.success(f"🍽️ {tipo} registrado! +{calorias} kcal")
                    st.balloons()
                else:
                    st.warning("Digite uma descrição da refeição.")
        
        with col2:
            st.markdown("### 📸 Tire uma foto")
            st.caption("Fotografar o prato ajuda na consciência alimentar.")
            foto = st.camera_input("Tirar foto do prato")
            if foto:
                st.image(foto, width=150, caption="Sua refeição")

# =============================================================================
# PÁGINA PRINCIPAL (MODO DEMONSTRAÇÃO)
# =============================================================================
def pagina_demo():
    st.markdown("<h1 style='text-align:center;'>🌱 EmagreSim</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Para quem já tentou de tudo. Dessa vez, sem julgamento.</p>", unsafe_allow_html=True)
    
    # Dados do Adriano (exemplo)
    usuario = {
        "nome": "Adriano",
        "idade": 39,
        "altura": 1.75,
        "current_weight": 108.0,
        "meta_mensal_kg": 2.0,
        "peso_inicio_mes": 108.0
    }
    
    # Simular histórico de peso (30 dias)
    datas = [date.today() - timedelta(days=i) for i in range(30, -1, -1)]
    pesos_simulados = [108.0 - i * 0.1 for i in range(31)]
    
    df_pesos = pd.DataFrame({
        "data": datas,
        "peso": pesos_simulados
    })
    
    peso_atual = usuario["current_weight"]
    meta_kg = usuario["meta_mensal_kg"]
    progresso = usuario["peso_inicio_mes"] - peso_atual
    percentual = min(100, max(0, (progresso / meta_kg) * 100)) if meta_kg > 0 else 0
    
    avatar, msg = get_avatar(percentual)
    
    # Avatar e saudação
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 4rem; text-align: center;'>{avatar}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1>Olá, {usuario['nome']}!</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("⚖️ Peso Atual", f"{peso_atual:.1f} kg", f"{progresso:+.1f} kg este mês")
    with k2:
        imc = calcular_imc(peso_atual, usuario["altura"])
        st.metric("📊 IMC", f"{imc:.1f}", "referência (18.5-25 é saudável)")
    with k3:
        st.metric("🎯 Meta mensal", f"{meta_kg:.1f} kg", f"{progresso:.1f} kg conquistados")
    with k4:
        st.metric("📅 Sequência", "30 dias", "🔥 consistência")
    
    # Barra de progresso
    st.markdown(f"**📅 Progresso da meta mensal**")
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg)
    
    # Gráfico de evolução (em português)
    st.markdown("### 📈 Evolução do Peso")
    
    fig = px.line(
        df_pesos, 
        x="data", 
        y="peso",
        title="",
        labels={"data": "Data", "peso": "Peso (kg)"}
    )
    fig.update_traces(line=dict(color="#FF4D00", width=3), marker=dict(size=4))
    fig.update_layout(
        height=400,
        xaxis_title="Data",
        yaxis_title="Peso (kg)",
        xaxis=dict(
            tickformat="%d/%m",
            gridcolor='lightgray'
        ),
        yaxis=dict(
            gridcolor='lightgray'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Registrar peso
    with st.expander("⚖️ Registrar peso hoje", expanded=False):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            novo_peso = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=peso_atual, step=0.1)
        with col_p2:
            st.markdown(" ")
            if st.button("✅ Salvar", use_container_width=True):
                st.success(f"✅ Peso registrado: {novo_peso:.1f} kg")
                if novo_peso <= usuario["meta_mensal_kg"]:
                    st.balloons()
    
    # Registrar refeição
    registrar_refeicao()
    
    # Apoio emocional
    with st.expander("🫂 Preciso de apoio", expanded=False):
        st.markdown("""
        <div style="background: rgba(255,77,0,0.1); border-radius: 20px; padding: 20px; text-align: center;">
            <span style="font-size: 2rem;">💙</span>
            <p style="font-size: 1rem; margin-top: 10px;">Dias difíceis acontecem. Você não está sozinho.</p>
            <p style="font-size: 0.85rem;">Um dia de cada vez. Recomeçar também é progresso.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Desafio da semana
    with st.expander("🏆 Desafio da Semana", expanded=False):
        desafios = [
            "💧 Beba 2L de água por 5 dias",
            "🥚 Registre proteína em todas as refeições",
            "🚶 Caminhe 30min por dia durante 4 dias",
            "😴 Durma 7h+ por 5 dias",
            "🍎 Coma uma fruta em todas as refeições"
        ]
        import random
        desafio = random.choice(desafios)
        st.markdown(f"**{desafio}** ⚡ +100 XP")
        st.progress(0.3, text="Progresso: 2/5 dias")
    
    # Dica do dia
    with st.expander("💡 Dica do dia", expanded=False):
        dicas = [
            "Beba um copo de água antes de cada refeição.",
            "Durma 7-8h por noite para regular os hormônios.",
            "Inclua proteína em todas as refeições para mais saciedade.",
            "Não pule o café da manhã – ele ativa seu metabolismo.",
            "Faça pequenas caminhadas após as refeições.",
            "Mastigue devagar – seu cérebro leva 20min para perceber saciedade."
        ]
        st.info(random.choice(dicas))
    
    # Rodapé informativo
    st.markdown("---")
    st.caption("📌 Modo demonstração com dados do Adriano. Para criar sua conta, entre em contato com o administrador.")

# =============================================================================
# MAIN
# =============================================================================
def main():
    pagina_demo()

if __name__ == "__main__":
    main()
