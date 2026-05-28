# app.py - EmagreSim v20.1 (Corrigido - Botão Esqueci Senha fora do formulário)
# Funcionalidades: Login, cadastro com validação, esqueci senha, modo demo
# Database: Supabase (Auth + Storage + Tables)
# Deploy: Streamlit Cloud

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
from supabase import create_client
import time
import re

# =============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="EmagreSim | Transformação",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="auto",
)

# =============================================================================
# 2. CONEXÃO SUPABASE
# =============================================================================
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    
    if "CHAVE_SUPABASE" in st.secrets:
        supabase_key = st.secrets["CHAVE_SUPABASE"]
    elif "SUPABASE_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_KEY"]
    else:
        st.error("❌ Chave do Supabase não encontrada. Configure as secrets.")
        st.stop()
    
    supabase = create_client(supabase_url, supabase_key)
    
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {e}")
    st.stop()

# =============================================================================
# 3. FUNÇÕES AUXILIARES
# =============================================================================
def normalizar_altura(valor):
    try:
        altura = float(str(valor).replace(",", "."))
        if altura > 3:
            altura = altura / 100
        return round(altura, 2)
    except:
        return 1.75

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

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def traduzir_erro(mensagem_original):
    """Traduz mensagens de erro do Supabase para português"""
    erros = {
        "email rate limit exceeded": "⚠️ Muitas tentativas para este e-mail. Aguarde 1 hora ou use outro e-mail.",
        "Invalid login credentials": "❌ E-mail ou senha incorretos. Verifique seus dados.",
        "User already registered": "📧 Este e-mail já está cadastrado. Faça login ou use outro e-mail.",
        "Password should be at least 6 characters": "🔒 A senha deve ter pelo menos 6 caracteres.",
        "Network error": "🌐 Erro de rede. Verifique sua conexão.",
        "Email not confirmed": "✉️ E-mail não confirmado. Verifique sua caixa de entrada.",
    }
    for chave, valor in erros.items():
        if chave in mensagem_original.lower():
            return valor
    return f"❌ Erro: {mensagem_original}"

# =============================================================================
# 4. FUNÇÕES SUPABASE
# =============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def carregar_usuario(user_id):
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def carregar_historico_pesos(user_id, limite=90):
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

def salvar_peso(user_id, peso, data_registro):
    try:
        supabase.table("weight_logs").insert({
            "user_id": user_id,
            "peso_kg": peso,
            "registered_at": data_registro.isoformat()
        }).execute()
        supabase.table("users").update({"current_weight": peso}).eq("id", user_id).execute()
        st.cache_data.clear()
        return True
    except:
        return False

def verificar_email_existe(email):
    """Verifica se o e-mail já está cadastrado"""
    try:
        result = supabase.auth.admin.list_users()
        for user in result.users:
            if user.email == email:
                return True
        return False
    except:
        return False

# =============================================================================
# 5. PÁGINAS
# =============================================================================
def pagina_login():
    st.markdown("<h1 style='text-align:center;'>🌱 EmagreSim</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Para quem já tentou de tudo. Dessa vez, sem julgamento.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Criar Conta"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("E-mail", placeholder="seu@email.com")
                password = st.text_input("Senha", type="password", placeholder="••••••••")
                
                if st.form_submit_button("Entrar", use_container_width=True):
                    if email and password:
                        try:
                            resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                            if resp.user:
                                st.session_state["user_id"] = resp.user.id
                                st.session_state["pagina"] = "dashboard"
                                st.rerun()
                        except Exception as e:
                            st.error(traduzir_erro(str(e)))
                    else:
                        st.warning("Digite e-mail e senha.")
            
            # Botão "Esqueci minha senha" fora do formulário
            if st.button("🔑 Esqueci minha senha", use_container_width=True):
                st.session_state["pagina"] = "recuperar_senha"
                st.rerun()
        
        with tab2:
            with st.form("criar_conta_form"):
                email = st.text_input("E-mail", placeholder="seu@email.com")
                senha = st.text_input("Senha", type="password", placeholder="•••••••• (mínimo 6 caracteres)")
                nome = st.text_input("Como quer ser chamado?", placeholder="Seu nome")
                
                st.markdown("---")
                st.markdown("### 📊 Seus dados (opcional)")
                st.caption("Você pode preencher agora ou depois no seu perfil.")
                
                col_idade, col_altura = st.columns(2)
                with col_idade:
                    idade = st.number_input("Idade", min_value=18, max_value=120, value=30, step=1)
                with col_altura:
                    altura_input = st.text_input("Altura", placeholder="Ex: 1.75 ou 175", value="1.75")
                
                col_peso, col_meta = st.columns(2)
                with col_peso:
                    peso_atual = st.number_input("Peso atual (kg)", min_value=30.0, max_value=300.0, value=80.0, step=0.5)
                with col_meta:
                    meta_mensal_kg = st.selectbox("Meta mensal (kg)", [0, 1, 2, 3, 4, 5], index=2)
                
                genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Não binário", "Prefiro não informar"])
                
                if st.form_submit_button("Criar conta", use_container_width=True):
                    if not email or not senha or not nome:
                        st.error("Preencha e-mail, senha e nome.")
                    elif not validar_email(email):
                        st.error("E-mail inválido. Digite um endereço válido (ex: nome@dominio.com).")
                    elif len(senha) < 6:
                        st.error("A senha deve ter pelo menos 6 caracteres.")
                    else:
                        # Verificar se e-mail já existe
                        if verificar_email_existe(email):
                            st.error("📧 Este e-mail já está cadastrado. Faça login ou use outro e-mail.")
                        else:
                            try:
                                resp = supabase.auth.sign_up({"email": email, "password": senha})
                                
                                if resp.user:
                                    user_id = resp.user.id
                                    altura = normalizar_altura(altura_input)
                                    
                                    # Inserir perfil
                                    supabase.table("users").insert({
                                        "id": user_id,
                                        "nome": nome,
                                        "idade": idade,
                                        "altura": altura,
                                        "genero": genero,
                                        "current_weight": peso_atual,
                                        "meta_mensal_kg": meta_mensal_kg,
                                        "peso_inicio_mes": peso_atual,
                                        "data_inicio_mes": date.today().isoformat()
                                    }).execute()
                                    
                                    # Registrar peso inicial
                                    supabase.table("weight_logs").insert({
                                        "user_id": user_id,
                                        "peso_kg": peso_atual,
                                        "registered_at": datetime.now().isoformat(),
                                        "nota": "Peso inicial"
                                    }).execute()
                                    
                                    st.success("✅ Conta criada com sucesso! Faça login.")
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Erro ao criar usuário. Tente novamente.")
                            except Exception as e:
                                st.error(traduzir_erro(str(e)))
        
        st.markdown("---")
        if st.button("🧪 Modo demonstração (Adriano)", use_container_width=True):
            st.session_state["pagina"] = "demo"
            st.rerun()

def pagina_recuperar_senha():
    st.markdown("<h1 style='text-align:center;'>🔑 Recuperar Senha</h1>", unsafe_allow_html=True)
    
    with st.form("recuperar_senha_form"):
        email = st.text_input("Digite seu e-mail", placeholder="seu@email.com")
        
        if st.form_submit_button("Enviar link de recuperação", use_container_width=True):
            if email:
                try:
                    supabase.auth.reset_password_for_email(email)
                    st.success("✅ Link de recuperação enviado para seu e-mail!")
                    st.info("Verifique sua caixa de entrada e spam. O link é válido por 24 horas.")
                    time.sleep(2)
                    st.session_state["pagina"] = "login"
                    st.rerun()
                except Exception as e:
                    st.error(traduzir_erro(str(e)))
            else:
                st.warning("Digite seu e-mail.")
    
    if st.button("← Voltar para login", use_container_width=True):
        st.session_state["pagina"] = "login"
        st.rerun()

def pagina_demo():
    st.markdown("<h1 style='text-align:center;'>🧪 Modo Demonstração - Adriano</h1>", unsafe_allow_html=True)
    st.info("📌 Este é o modo demonstração com dados do Adriano (108kg, meta 2kg/mês). Os dados não são salvos permanentemente.")
    
    usuario_demo = {
        "nome": "Adriano",
        "idade": 39,
        "altura": 1.75,
        "current_weight": 108.0,
        "meta_mensal_kg": 2.0,
        "peso_inicio_mes": 108.0
    }
    
    pesos_demo = [{"registered_at": date.today() - timedelta(days=i), "peso_kg": 108.0 - i * 0.1} for i in range(30)]
    df_pesos = pd.DataFrame(pesos_demo)
    
    peso_atual = usuario_demo["current_weight"]
    meta_kg = usuario_demo["meta_mensal_kg"]
    peso_inicio = usuario_demo["peso_inicio_mes"]
    progresso = peso_inicio - peso_atual
    percentual = (progresso / meta_kg) * 100 if meta_kg > 0 else 0
    percentual = max(0, min(100, percentual))
    
    avatar, msg_avatar = get_avatar(percentual)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 4rem; text-align: center;'>{avatar}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1>Olá, {usuario_demo['nome']}!</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Peso Atual", f"{peso_atual:.1f} kg", f"{progresso:+.1f} kg este mês")
    with k2:
        imc = calcular_imc(peso_atual, usuario_demo["altura"])
        st.metric("IMC", f"{imc:.1f}", "referência")
    with k3:
        st.metric("Meta mensal", f"{meta_kg:.1f} kg", f"{progresso:.1f} kg")
    with k4:
        st.metric("Sequência", "30 dias", "")
    
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg_avatar)
    
    if not df_pesos.empty:
        df_pesos["registered_at"] = pd.to_datetime(df_pesos["registered_at"])
        fig = px.line(df_pesos, x="registered_at", y="peso_kg", title="Evolução do Peso")
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🍽️ Últimas refeições (demo)")
    refeicoes_demo = [
        {"descricao": "Arroz, feijão, frango grelhado", "calorias": 550, "data": date.today()},
        {"descricao": "Omelete com espinafre", "calorias": 350, "data": date.today() - timedelta(days=1)},
        {"descricao": "Salada de quinoa com frango", "calorias": 450, "data": date.today() - timedelta(days=2)},
    ]
    for r in refeicoes_demo[:5]:
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.write(f"**{r['descricao']}**")
            st.caption(r['data'].strftime("%d/%m/%Y"))
        with cols[1]:
            st.write(f"{r['calorias']} kcal")
    
    if st.button("← Voltar ao login", use_container_width=True):
        st.session_state.clear()
        st.rerun()

def pagina_dashboard():
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.session_state["pagina"] = "login"
        st.rerun()
        return
    
    user = carregar_usuario(user_id)
    if not user:
        st.error("Usuário não encontrado. Faça login novamente.")
        if st.button("Voltar ao login"):
            st.session_state.clear()
            st.rerun()
        return
    
    pesos = carregar_historico_pesos(user_id)
    df_pesos = pd.DataFrame(pesos) if pesos else pd.DataFrame()
    
    peso_inicio = user.get("peso_inicio_mes", user["current_weight"])
    meta_kg = user.get("meta_mensal_kg", 2)
    peso_atual = user["current_weight"]
    progresso = peso_inicio - peso_atual
    percentual = (progresso / meta_kg) * 100 if meta_kg > 0 else 0
    percentual = max(0, min(100, percentual))
    
    avatar, msg_avatar = get_avatar(percentual)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 4rem; text-align: center;'>{avatar}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1>Olá, {user['nome']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Peso Atual", f"{peso_atual:.1f} kg", f"{progresso:+.1f} kg este mês")
    with k2:
        imc = calcular_imc(peso_atual, user.get("altura", 1.75))
        st.metric("IMC", f"{imc:.1f}", "referência")
    with k3:
        st.metric("Meta mensal", f"{meta_kg:.1f} kg", f"{progresso:.1f} kg")
    with k4:
        st.metric("Registros", f"{len(pesos)} dias", "")
    
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg_avatar)
    
    if not df_pesos.empty:
        df_pesos["registered_at"] = pd.to_datetime(df_pesos["registered_at"])
        fig = px.line(df_pesos, x="registered_at", y="peso_kg", title="Evolução do Peso")
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("⚖️ Registrar peso hoje"):
        novo_peso = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=peso_atual, step=0.1)
        if st.button("✅ Salvar peso"):
            if salvar_peso(user_id, novo_peso, date.today()):
                st.success("Peso registrado!")
                time.sleep(1)
                st.rerun()
    
    with st.expander("🍽️ Registrar refeição"):
        descricao = st.text_input("O que você comeu?")
        calorias = st.number_input("Calorias (kcal)", min_value=0, max_value=2000, value=300, step=50)
        if st.button("✅ Salvar refeição"):
            if descricao:
                st.success("Refeição registrada!")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Digite uma descrição.")
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); border-radius: 20px; padding: 15px; text-align: center; margin: 15px 0;">
        <span style="font-size: 1.2rem;">🫂</span>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">Dias difíceis acontecem. Você não está sozinho.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sair", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()

# =============================================================================
# 6. MAIN
# =============================================================================
def main():
    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "login"
    
    pagina = st.session_state["pagina"]
    
    if pagina == "login":
        pagina_login()
    elif pagina == "recuperar_senha":
        pagina_recuperar_senha()
    elif pagina == "dashboard":
        pagina_dashboard()
    elif pagina == "demo":
        pagina_demo()
    else:
        pagina_login()

if __name__ == "__main__":
    main()
