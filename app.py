# app.py - VERSÃO COMPLETA SEM AVATAR_MAKER
import streamlit as st
import random
from datetime import datetime

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
# PÁGINA AVATAR (SIMPLES, SEM ARQUIVO EXTERNO)
# -----------------------------------------------------------------------------
def tela_avatar():
    st.markdown("<h1 style='text-align:center;'>🎨 Crie seu Avatar</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        genero = st.selectbox("Gênero", ["Masculino", "Feminino"])
        estilo = st.selectbox("Estilo", ["🔥 Energético", "💪 Forte", "🧘 Calmo", "🏃 Veloz", "😊 Feliz", "🤔 Pensativo"])
        cor_principal = st.color_picker("Cor principal", "#FF4D00")
        cor_fundo = st.color_picker("Cor de fundo", "#1A1A1A")
        
        if st.button("🎲 Criar aleatório", use_container_width=True):
            estilos = ["🔥 Energético", "💪 Forte", "🧘 Calmo", "🏃 Veloz", "😊 Feliz", "🤔 Pensativo"]
            estilo = random.choice(estilos)
            cor_principal = random.choice(["#FF4D00", "#22C55E", "#3B82F6", "#8B5CF6", "#F59E0B", "#EF4444"])
            st.rerun()
    
    with col2:
        # Avatar SVG simples
        emoji = estilo[0]
        svg = f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" rx="20" fill="{cor_fundo}"/>
            <circle cx="100" cy="95" r="60" fill="{cor_principal}" stroke="white" stroke-width="3"/>
            <circle cx="75" cy="85" r="8" fill="white"/>
            <circle cx="125" cy="85" r="8" fill="white"/>
            <circle cx="77" cy="85" r="4" fill="black"/>
            <circle cx="127" cy="85" r="4" fill="black"/>
            <path d="M 80 115 Q 100 130 120 115" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
            <text x="100" y="175" text-anchor="middle" font-size="40" fill="white">{emoji}</text>
        </svg>'''
        st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
        
        st.download_button("⬇️ Baixar Avatar (SVG)", svg, "meu_avatar.svg", "image/svg+xml", use_container_width=True)
    
    st.markdown("---")
    if st.button("✅ Salvar Avatar e Continuar", use_container_width=True):
        st.session_state["avatar_svg"] = svg
        st.session_state["avatar_estilo"] = estilo
        st.session_state["pagina"] = "criar_conta"
        st.rerun()

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
                        "sexo": "M", "avatar": "🔥"
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
                    "sexo": "M", "avatar": "🔥"
                }
                st.session_state["pagina"] = "dashboard"
                st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA CRIAR CONTA
# -----------------------------------------------------------------------------
def pagina_criar_conta():
    st.markdown("<h1 style='text-align:center;'>🔥 Criar Conta</h1>", unsafe_allow_html=True)
    
    # Mostrar avatar se já foi criado
    if "avatar_svg" in st.session_state:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f'<div style="display: flex; justify-content: center;">{st.session_state["avatar_svg"]}</div>', unsafe_allow_html=True)
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
                            "sexo": "M" if sexo == "Masculino" else "F",
                            "avatar": st.session_state.get("avatar_svg", "🔥")
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
    
    st.markdown(f"<h1>Olá, {usuario['nome']}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)
    
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
    
    # Desafio da semana
    with st.expander("🏆 Desafio da Semana", expanded=True):
        st.markdown("💧 **Hidratação** – Beba 2L de água por 5 dias ⚡ +100 XP")
        st.progress(0.3, text="Progresso: 2/5 dias")
    
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
