# app.py - EmagreSim v15.0 COMPLETO COM AVATAR INTERATIVO
import streamlit as st
import random
from datetime import datetime
import time

# -----------------------------------------------------------------------------
# TENTAR IMPORTAR AVATAR (COM FALLBACK)
# -----------------------------------------------------------------------------
try:
    from avatar_maker import tela_avatar, mostrar_avatar, celebrar_meta, modo_apoio
    AVATAR_DISPONIVEL = True
except ImportError:
    AVATAR_DISPONIVEL = False
    
    # Funções fallback simplificadas
    def tela_avatar():
        st.markdown("<h1 style='text-align:center;'>🎨 Escolha seu Avatar</h1>", unsafe_allow_html=True)
        genero = st.radio("Seu gênero", ["Masculino", "Feminino"], horizontal=True)
        
        if genero == "Masculino":
            avatares = [("João", "👨"), ("Carlos", "🧔"), ("Pedro", "👦")]
        else:
            avatares = [("Maria", "👩"), ("Ana", "👧"), ("Julia", "💁")]
        
        cols = st.columns(3)
        for i, (nome, emoji) in enumerate(avatares):
            with cols[i]:
                st.markdown(f'<div style="background: #4A90D9; width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto;"><span style="font-size: 3rem;">{emoji}</span></div>', unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center;'><b>{nome}</b></p>", unsafe_allow_html=True)
                if st.button(f"Escolher {nome}", key=f"fb_{i}", use_container_width=True):
                    st.session_state["avatar_data"] = {"nome": nome, "emoji": emoji, "cor": "#4A90D9"}
                    st.session_state["avatar_humor"] = "normal"
                    st.session_state["pagina"] = "criar_conta"
                    st.rerun()
    
    def mostrar_avatar():
        if "avatar_data" in st.session_state:
            avatar = st.session_state["avatar_data"]
            st.markdown(f'<div style="font-size: 4rem; text-align: center;">{avatar["emoji"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size: 3rem; text-align: center;">🔥</div>', unsafe_allow_html=True)
    
    def celebrar_meta():
        st.balloons()
        st.toast("🎉 PARABÉNS! Você atingiu sua meta! 🎉", icon="🏆")
        time.sleep(2)
    
    def modo_apoio():
        st.toast("💙 Você não está sozinho. Um dia de cada vez.", icon="🤗")
        time.sleep(2)

# Configuração da página
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🔥",
    layout="wide",
)

# -----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------------
def calcular_imc(peso, altura):
    return peso / (altura ** 2)

def classificar_imc(imc):
    if imc < 18.5: return "Abaixo do peso"
    if imc < 25: return "Saudável"
    if imc < 30: return "Sobrepeso"
    if imc < 35: return "Obesidade Grau I"
    if imc < 40: return "Obesidade Grau II"
    return "Obesidade Grau III"

def mensagem_bom_dia():
    hora = datetime.now().hour
    if hora < 12:
        return "🌅 Bom dia! Hoje é um novo começo."
    elif hora < 18:
        return "🌤️ Boa tarde! Continue firme."
    return "🌙 Boa noite! Amanhã é outro dia."

# -----------------------------------------------------------------------------
# PÁGINA LOGIN
# -----------------------------------------------------------------------------
def pagina_login():
    st.markdown("<h1 style='text-align:center;'>🔥 EmagreSim</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com", value="demo@emagresim.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••", value="demo123")
            if st.form_submit_button("Entrar", use_container_width=True):
                if email == "demo@emagresim.com" and senha == "demo123":
                    st.session_state["usuario"] = {
                        "nome": "Adriano", "email": email,
                        "idade": 39, "altura": 1.75, "peso_atual": 144.0, "peso_meta": 90.0,
                        "sexo": "M"
                    }
                    st.session_state["pagina"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos. Use demo@emagresim.com / demo123")
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Criar conta", use_container_width=True):
                st.session_state["pagina"] = "avatar"
                st.rerun()
        with col_b:
            if st.button("🧪 Modo demonstração", use_container_width=True):
                st.session_state["usuario"] = {
                    "nome": "Adriano", "email": "demo@emagresim.com",
                    "idade": 39, "altura": 1.75, "peso_atual": 144.0, "peso_meta": 90.0,
                    "sexo": "M"
                }
                st.session_state["pagina"] = "dashboard"
                st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA CRIAR CONTA
# -----------------------------------------------------------------------------
def pagina_criar_conta():
    st.markdown("<h1 style='text-align:center;'>🔥 Criar Conta</h1>", unsafe_allow_html=True)
    
    if "avatar_data" in st.session_state:
        col1, col2 = st.columns([1, 2])
        with col1:
            mostrar_avatar()
            if st.button("🎨 Editar Avatar", use_container_width=True):
                st.session_state["pagina"] = "avatar"
                st.rerun()
        with col2:
            with st.form("form_criar_conta"):
                nome = st.text_input("Nome completo")
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    idade = st.number_input("Idade", 18, 100, 30)
                    altura = st.number_input("Altura (m)", 1.40, 2.50, 1.75, 0.01)
                with col_b:
                    peso = st.number_input("Peso atual (kg)", 30.0, 300.0, 80.0, 0.1)
                    meta_peso = st.number_input("Meta de peso (kg)", 40.0, 200.0, 70.0, 0.5)
                
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
                
                if st.form_submit_button("🔥 Criar minha conta", use_container_width=True):
                    if nome and email and senha:
                        st.session_state["usuario"] = {
                            "nome": nome, "email": email, "idade": idade,
                            "altura": altura, "peso_atual": peso, "peso_meta": meta_peso,
                            "sexo": "M" if sexo == "Masculino" else "F"
                        }
                        st.success(f"✅ Conta criada com sucesso, {nome}!")
                        st.balloons()
                        st.session_state["pagina"] = "dashboard"
                        st.rerun()
    else:
        st.info("🎨 Primeiro, crie seu avatar!")
        if st.button("Criar Avatar", use_container_width=True):
            st.session_state["pagina"] = "avatar"
            st.rerun()
    
    if st.button("← Voltar", use_container_width=True):
        st.session_state["pagina"] = "login"
        st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA DASHBOARD
# -----------------------------------------------------------------------------
def pagina_dashboard():
    usuario = st.session_state.get("usuario", None)
    if not usuario:
        st.warning("Nenhum usuário logado")
        if st.button("Voltar"):
            st.session_state["pagina"] = "login"
            st.rerun()
        return
    
    # Cabeçalho com avatar
    col_avatar, col_titulo = st.columns([1, 3])
    with col_avatar:
        mostrar_avatar()
    with col_titulo:
        st.markdown(f"<h1>Olá, {usuario['nome']}!</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)
    
    # Botão de apoio emocional
    col_apoio1, col_apoio2 = st.columns([3, 1])
    with col_apoio2:
        if st.button("😔 Estou para baixo", use_container_width=True):
            modo_apoio()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        imc = calcular_imc(usuario["peso_atual"], usuario["altura"])
        st.metric("Peso Atual", f"{usuario['peso_atual']:.1f} kg", f"Meta: {usuario['peso_meta']:.0f} kg")
    with col2:
        st.metric("IMC", f"{imc:.1f}", classificar_imc(imc))
    with col3:
        st.metric("Idade", f"{usuario['idade']} anos")
    with col4:
        st.metric("Plano", "Grátis")
    
    # Previsão
    kg_restantes = usuario["peso_atual"] - usuario["peso_meta"]
    if kg_restantes > 0:
        st.info(f"📅 **Previsão:** Faltam {kg_restantes:.0f} kg para atingir sua meta!")
    
    # Simular registro de peso
    with st.expander("⚖️ Registrar Peso Hoje", expanded=False):
        peso_hoje = st.number_input("Peso atual (kg)", 30.0, 300.0, usuario["peso_atual"], 0.1)
        if st.button("Salvar Peso", use_container_width=True):
            usuario["peso_atual"] = peso_hoje
            st.success(f"✅ Peso registrado: {peso_hoje:.1f} kg")
            if peso_hoje <= usuario["peso_meta"]:
                celebrar_meta()
            st.rerun()
    
    # Desafio da semana
    with st.expander("🏆 Desafio da Semana", expanded=True):
        desafios = [
            ("💧 Beba 2L de água por 5 dias", 100),
            ("🥚 Registre proteína em todas as refeições", 150),
            ("🚶 Caminhe 30min por dia durante 4 dias", 120),
            ("😴 Durma 7h+ por 5 dias", 100),
        ]
        desafio, xp = random.choice(desafios)
        st.markdown(f"**{desafio}** ⚡ +{xp} XP")
        st.progress(0.3, text="Progresso: 2/5 dias")
    
    # Dica do dia
    with st.expander("💡 Dica do dia", expanded=False):
        dicas = [
            "Beba um copo de água antes de cada refeição.",
            "Durma 7-8h por noite para regular os hormônios.",
            "Inclua proteína em todas as refeições para mais saciedade.",
            "Não pule o café da manhã – ele ativa seu metabolismo.",
            "Faça pequenas caminhadas após as refeições.",
        ]
        st.info(random.choice(dicas))
    
    # Botão sair
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.clear()
        st.session_state["pagina"] = "login"
        st.rerun()

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "login"
    
    pagina = st.session_state["pagina"]
    
    if pagina == "login":
        pagina_login()
    elif pagina == "avatar":
        tela_avatar()
    elif pagina == "criar_conta":
        pagina_criar_conta()
    elif pagina == "dashboard":
        pagina_dashboard()
    else:
        pagina_login()

if __name__ == "__main__":
    main()
