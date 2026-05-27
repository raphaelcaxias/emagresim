# app.py - EmagreSim v17.0 (Correções Imediatas)
# Meta mensal | Avatar simbólico | Cadastro simples | Sem rótulos
import streamlit as st
import random
from datetime import datetime, timedelta, date
import time

st.set_page_config(
    page_title="EmagreSim | Recomeço",
    page_icon="🌅",
    layout="wide",
)

# =============================================================================
# DOMÍNIO (Lógica pura, sem UI)
# =============================================================================

def calcular_imc(peso, altura):
    """Calcula IMC como referência, sem julgamento"""
    if altura <= 0:
        return 0
    return peso / (altura ** 2)

def normalizar_altura(valor):
    """Converte 175 para 1.75 automaticamente"""
    try:
        altura = float(str(valor).replace(",", "."))
        if altura > 3:  # Provavelmente está em centímetros
            altura = altura / 100
        return round(altura, 2)
    except:
        return 1.75

def classificar_imc_referencia(imc):
    """Apenas referência, sem rótulo de 'obesidade'"""
    if imc < 18.5:
        return "abaixo da faixa de referência"
    elif imc < 25:
        return "dentro da faixa de referência"
    elif imc < 30:
        return "acima da faixa de referência"
    else:
        return "acima da faixa de referência"

def calcular_avatar(progresso_mensal):
    """Avatar simbólico que evolui com o progresso"""
    if progresso_mensal >= 100:
        return {"simbolo": "🏆", "nome": "Conquista", "mensagem": "Meta do mês alcançada! 🎉"}
    elif progresso_mensal >= 75:
        return {"simbolo": "⚡", "nome": "Energia", "mensagem": "Você está no caminho! Continue!"}
    elif progresso_mensal >= 50:
        return {"simbolo": "🌱", "nome": "Crescimento", "mensagem": "Meio do mês. Continue firme."}
    elif progresso_mensal >= 25:
        return {"simbolo": "🔥", "nome": "Transformação", "mensagem": "Primeiros resultados aparecendo!"}
    else:
        return {"simbolo": "🌅", "nome": "Despertar", "mensagem": "Todo recomeço é uma semente."}

def calcular_streak(historico_pesos):
    """Calcula sequência de dias consecutivos com registro"""
    if not historico_pesos:
        return 0
    streak = 0
    hoje = date.today()
    for i in range(len(historico_pesos)):
        data_registro = datetime.fromisoformat(historico_pesos[i]["data"]).date()
        if data_registro == hoje - timedelta(days=i):
            streak += 1
        else:
            break
    return streak

def mensagem_bom_dia():
    hora = datetime.now().hour
    if hora < 12:
        return "🌅 Bom dia! Hoje é um novo começo."
    elif hora < 18:
        return "🌤️ Boa tarde! Continue firme."
    return "🌙 Boa noite! Amanhã é outro dia."

def get_dica_dia(usuario):
    """Dica contextual baseada no comportamento"""
    if usuario.get("ultimo_registro") and usuario["ultimo_registro"] < date.today() - timedelta(days=2):
        return "💡 Recomeçar também é progresso. Registre seu peso hoje."
    elif usuario.get("streak", 0) >= 5:
        return "💡 Você está há 5+ dias registrando. Isso é consistência real!"
    else:
        dicas = [
            "💡 Beba um copo de água antes de cada refeição.",
            "💡 Durma 7-8h por noite para regular os hormônios.",
            "💡 Pequenos passos todos os dias > grandes mudanças uma vez.",
            "💡 O peso oscila naturalmente. Olhe a tendência, não o dia.",
        ]
        return random.choice(dicas)

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

# =============================================================================
# PÁGINAS
# =============================================================================

def pagina_login():
    st.markdown("<h1 style='text-align:center;'>🌅 EmagreSim</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Sua jornada de transformação começa aqui.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com", value="demo@emagresim.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••", value="demo123")
            if st.form_submit_button("Entrar", use_container_width=True):
                if email == "demo@emagresim.com" and senha == "demo123":
                    # Dados do Adriano (apenas para demo)
                    st.session_state.usuario = {
                        "nome": "Adriano",
                        "email": email,
                        "idade": 39,
                        "altura": 1.75,
                        "peso_atual": 115.0,
                        "meta_mensal_kg": 2.0,
                        "peso_inicio_mes": 115.0,
                        "data_inicio_mes": date.today().isoformat(),
                        "historico_pesos": [{"data": date.today().isoformat(), "peso": 115.0}],
                        "streak": 0,
                        "ultimo_registro": date.today()
                    }
                    st.session_state.pagina = "dashboard"
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos. Use demo@emagresim.com / demo123")
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Criar conta", use_container_width=True):
                st.session_state.pagina = "criar_conta"
                st.rerun()
        with col_b:
            if st.button("🧪 Modo demonstração", use_container_width=True):
                st.session_state.usuario = {
                    "nome": "Adriano",
                    "email": "demo@emagresim.com",
                    "idade": 39,
                    "altura": 1.75,
                    "peso_atual": 115.0,
                    "meta_mensal_kg": 2.0,
                    "peso_inicio_mes": 115.0,
                    "data_inicio_mes": date.today().isoformat(),
                    "historico_pesos": [{"data": date.today().isoformat(), "peso": 115.0}],
                    "streak": 0,
                    "ultimo_registro": date.today()
                }
                st.session_state.pagina = "dashboard"
                st.rerun()

def pagina_criar_conta():
    st.markdown("<h1 style='text-align:center;'>🌅 Criar Conta</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Só precisamos de algumas informações para começar.</p>", unsafe_allow_html=True)
    
    with st.form("form_criar_conta"):
        nome = st.text_input("Nome", placeholder="Como você quer ser chamado?")
        email = st.text_input("E-mail", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        
        st.markdown("---")
        st.markdown("### 📊 Completar perfil (opcional agora)")
        st.caption("Você pode preencher depois. Isso só nos ajuda a personalizar.")
        
        idade = st.number_input("Idade", min_value=18, max_value=120, value=30, step=1)
        altura_input = st.text_input("Altura", placeholder="Ex: 1.75 ou 175", value="1.75")
        peso = st.number_input("Peso atual (kg)", min_value=30.0, max_value=300.0, value=80.0, step=0.5)
        
        objetivo = st.selectbox(
            "Seu objetivo este mês",
            options=["🌱 Emagrecer (perder peso de forma saudável)",
                     "💪 Ganhar massa muscular",
                     "⚖️ Manter o peso (saúde e bem-estar)"],
            help="Isso define sua meta mensal."
        )
        
        genero = st.selectbox(
            "Gênero",
            options=["Masculino", "Feminino", "Não binário", "Prefiro não informar"],
            help="Para personalizar os cálculos."
        )
        
        if st.form_submit_button("🔥 Criar minha conta", use_container_width=True):
            if nome and email and senha:
                altura = normalizar_altura(altura_input)
                
                # Define meta mensal baseada no objetivo
                if "Emagrecer" in objetivo:
                    meta_mensal_kg = 2.0
                elif "Ganhar" in objetivo:
                    meta_mensal_kg = 1.0
                else:
                    meta_mensal_kg = 0.0
                
                st.session_state.usuario = {
                    "nome": nome,
                    "email": email,
                    "idade": idade,
                    "altura": altura,
                    "peso_atual": peso,
                    "meta_mensal_kg": meta_mensal_kg,
                    "peso_inicio_mes": peso,
                    "data_inicio_mes": date.today().isoformat(),
                    "historico_pesos": [{"data": date.today().isoformat(), "peso": peso}],
                    "objetivo": objetivo,
                    "genero": genero,
                    "streak": 1,
                    "ultimo_registro": date.today()
                }
                st.success(f"✅ Conta criada, {nome}!")
                st.balloons()
                st.session_state.pagina = "dashboard"
                st.rerun()
            else:
                st.error("Preencha nome, email e senha.")
    
    if st.button("← Voltar", use_container_width=True):
        st.session_state.pagina = "login"
        st.rerun()

def pagina_dashboard():
    usuario = st.session_state.usuario
    if not usuario:
        st.warning("Nenhum usuário logado")
        if st.button("Voltar"):
            st.session_state.pagina = "login"
            st.rerun()
        return
    
    # Cálculos do mês
    peso_atual = usuario["peso_atual"]
    peso_inicio = usuario.get("peso_inicio_mes", peso_atual)
    meta_mensal = usuario.get("meta_mensal_kg", 2.0)
    progresso_kg = peso_inicio - peso_atual
    progresso_percentual = min(100, max(0, (progresso_kg / meta_mensal) * 100)) if meta_mensal > 0 else 0
    
    # Atualizar streak
    hoje = date.today()
    if usuario.get("ultimo_registro") == hoje - timedelta(days=1):
        usuario["streak"] = usuario.get("streak", 0) + 1
    elif usuario.get("ultimo_registro") != hoje:
        usuario["streak"] = 1
    usuario["ultimo_registro"] = hoje
    
    # Avatar baseado no progresso
    avatar = calcular_avatar(progresso_percentual)
    
    # Cabeçalho
    col_avatar, col_titulo = st.columns([1, 3])
    with col_avatar:
        st.markdown(f'<div style="font-size: 4rem; text-align: center;">{avatar["simbolo"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; font-size: 0.8rem;">{avatar["nome"]}</p>', unsafe_allow_html=True)
    with col_titulo:
        st.markdown(f"<h1>Olá, {usuario['nome']}!</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)
    
    # Streak
    if usuario.get("streak", 0) >= 3:
        st.success(f"🔥 Você está há {usuario['streak']} dias seguidos registrando! Isso é consistência real.")
    
    # KPIs (sem rótulos ofensivos)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Peso Atual", f"{peso_atual:.1f} kg", f"{progresso_kg:+.1f} kg este mês")
    with col2:
        imc = calcular_imc(peso_atual, usuario["altura"])
        st.metric("IMC", f"{imc:.1f}", classificar_imc_referencia(imc))
    with col3:
        st.metric("Meta do Mês", f"{meta_mensal:.1f} kg", f"{progresso_kg:.1f} kg conquistados")
    with col4:
        st.metric("Sequência", f"{usuario.get('streak', 0)} dias", "registrando")
    
    # Barra de progresso mensal
    st.markdown(f"**📅 Progresso da meta mensal**")
    st.progress(progresso_percentual / 100, text=f"{progresso_kg:.1f}kg / {meta_mensal:.1f}kg")
    st.caption(f"{avatar['mensagem']}")
    
    # Registrar peso
    with st.expander("⚖️ Registrar Peso Hoje", expanded=False):
        peso_hoje = st.number_input("Peso atual (kg)", 30.0, 300.0, peso_atual, 0.1)
        if st.button("✅ Salvar Peso", use_container_width=True):
            usuario["peso_atual"] = peso_hoje
            usuario["historico_pesos"].append({"data": date.today().isoformat(), "peso": peso_hoje})
            
            # Verificar se atingiu a meta
            novo_progresso = usuario["peso_inicio_mes"] - peso_hoje
            if meta_mensal > 0 and novo_progresso >= meta_mensal:
                st.balloons()
                st.toast("🎉 META DO MÊS ALCANÇADA! 🎉", icon="🏆")
                st.audio(None)  # placeholder para som se quiser
            
            st.success(f"✅ Peso registrado: {peso_hoje:.1f} kg")
            st.rerun()
    
    # Apoio emocional (hover, não botão)
    st.markdown("""
    <div style="background: rgba(255,255,255,0.05); border-radius: 20px; padding: 15px; text-align: center; margin: 15px 0;">
        <span style="font-size: 1.2rem;">🫂</span>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">Dias difíceis acontecem. Você não está sozinho.</p>
        <p style="font-size: 0.7rem; color: #888;">(passe o mouse para apoio)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Desafio da semana
    with st.expander("🏆 Desafio da Semana", expanded=True):
        desafios = [
            "💧 Beba 2L de água por 5 dias",
            "🥚 Registre proteína em todas as refeições",
            "🚶 Caminhe 30min por dia durante 4 dias",
            "😴 Durma 7h+ por 5 dias",
        ]
        desafio = random.choice(desafios)
        st.markdown(f"**{desafio}** ⚡ +100 XP")
        st.progress(0.3, text="Progresso: 2/5 dias")
    
    # Dica do dia
    with st.expander("💡 Dica do dia", expanded=False):
        st.info(get_dica_dia(usuario))
    
    # Sair
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.clear()
        st.session_state.pagina = "login"
        st.rerun()

# =============================================================================
# MAIN
# =============================================================================

def main():
    if st.session_state.pagina == "login":
        pagina_login()
    elif st.session_state.pagina == "criar_conta":
        pagina_criar_conta()
    elif st.session_state.pagina == "dashboard":
        pagina_dashboard()
    else:
        pagina_login()

if __name__ == "__main__":
    main()
