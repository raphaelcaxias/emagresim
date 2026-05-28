# app.py - EmagreSim v19.0 (MVP completo com Supabase)
# Funcionalidades: Login, registro, peso, refeições com foto, meta mensal, avatar simbólico
# Database: Supabase (Auth + Storage + Tables)
# Deploy: Streamlit Cloud

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
from supabase import create_client
import time
import json

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
# 2. CONEXÃO SUPABASE (com fallback para diferentes nomes de secrets)
# =============================================================================
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    
    # Tenta diferentes nomes para a chave (prioriza CHAVE_SUPABASE)
    if "CHAVE_SUPABASE" in st.secrets:
        supabase_key = st.secrets["CHAVE_SUPABASE"]
    elif "SUPABASE_KEY" in st.secrets:
        supabase_key = st.secrets["SUPABASE_KEY"]
    elif "supabase_key" in st.secrets:
        supabase_key = st.secrets["supabase_key"]
    else:
        st.error("❌ Nenhuma chave do Supabase encontrada nas secrets. Use CHAVE_SUPABASE ou SUPABASE_KEY.")
        st.stop()
    
    supabase = create_client(supabase_url, supabase_key)
    
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {e}")
    st.info("Verifique se as secrets estão configuradas corretamente no Streamlit Cloud.")
    st.stop()

# =============================================================================
# 3. FUNÇÕES AUXILIARES (DOMÍNIO)
# =============================================================================
def normalizar_altura(valor):
    """Converte 175 → 1.75 automaticamente"""
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
    """Retorna avatar e mensagem baseado no progresso da meta mensal"""
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
# 4. FUNÇÕES DE ACESSO AO SUPABASE (COM CACHE)
# =============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def carregar_usuario(user_id):
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Erro ao carregar usuário: {e}")
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
    except Exception as e:
        st.error(f"Erro ao carregar histórico de pesos: {e}")
        return []

@st.cache_data(ttl=60, show_spinner=False)
def carregar_refeicoes(user_id, limite=30):
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

def salvar_peso(user_id, peso, data_registro):
    try:
        supabase.table("weight_logs").insert({
            "user_id": user_id,
            "peso_kg": peso,
            "registered_at": data_registro.isoformat()
        }).execute()
        # Atualizar current_weight na tabela users
        supabase.table("users").update({"current_weight": peso}).eq("id", user_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar peso: {e}")
        return False

def salvar_refeicao(user_id, descricao, calorias, foto_url, data_registro):
    try:
        supabase.table("food_logs").insert({
            "user_id": user_id,
            "descricao": descricao,
            "calorias": calorias,
            "foto_url": foto_url,
            "registered_at": data_registro.isoformat()
        }).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar refeição: {e}")
        return False

def salvar_foto(file, user_id):
    """Salva foto no Supabase Storage e retorna URL pública"""
    try:
        file_ext = file.name.split(".")[-1]
        file_path = f"{user_id}/{datetime.now().timestamp()}.{file_ext}"
        supabase.storage.from_("fotos").upload(file_path, file.getvalue())
        # Torna público e obtém URL
        supabase.storage.from_("fotos").update_public(file_path, {"public": True})
        url = supabase.storage.from_("fotos").get_public_url(file_path)
        return url
    except Exception as e:
        st.error(f"Erro ao salvar foto: {e}")
        return None

# =============================================================================
# 5. PÁGINAS DO APP
# =============================================================================
def pagina_login():
    st.markdown("<h1 style='text-align:center;'>🌱 EmagreSim</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Para quem já tentou de tudo. Dessa vez, sem julgamento.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com", value="demo@emagresim.com")
            password = st.text_input("Senha", type="password", placeholder="••••••••", value="demo123")
            if st.form_submit_button("Entrar", use_container_width=True):
                try:
                    resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if resp.user:
                        st.session_state["user_id"] = resp.user.id
                        st.session_state["pagina"] = "dashboard"
                        st.rerun()
                except Exception as e:
                    st.error("Email ou senha inválidos. Use demo@emagresim.com / demo123")
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Criar conta", use_container_width=True):
                st.session_state["pagina"] = "criar_conta"
                st.rerun()
        with col_b:
            if st.button("🧪 Modo demonstração", use_container_width=True):
                try:
                    supabase.auth.sign_up({"email": "demo@emagresim.com", "password": "demo123"})
                    time.sleep(1)
                    resp = supabase.auth.sign_in_with_password({"email": "demo@emagresim.com", "password": "demo123"})
                    st.session_state["user_id"] = resp.user.id
                    st.session_state["pagina"] = "dashboard"
                    st.rerun()
                except:
                    st.info("Modo demonstração disponível após criar conta. Clique em 'Criar conta' primeiro.")

def pagina_criar_conta():
    st.markdown("<h1 style='text-align:center;'>🌱 Criar Conta</h1>", unsafe_allow_html=True)
    
    with st.form("criar_conta_form"):
        email = st.text_input("E-mail *", placeholder="seu@email.com")
        senha = st.text_input("Senha *", type="password", placeholder="••••••••")
        nome = st.text_input("Como quer ser chamado? *", placeholder="Seu nome")
        
        st.markdown("---")
        st.markdown("### 📊 Seus dados (opcional agora)")
        st.caption("Você pode preencher depois. Isso nos ajuda a personalizar sua experiência.")
        
        idade = st.number_input("Idade", min_value=18, max_value=120, value=30, step=1)
        altura_input = st.text_input("Altura", placeholder="Ex: 1.75 ou 175", value="1.75")
        peso_atual = st.number_input("Peso atual (kg)", min_value=30.0, max_value=300.0, value=80.0, step=0.5)
        meta_mensal_kg = st.selectbox("Quanto quer perder/ganhar este mês? (kg)", [0, 1, 2, 3, 4, 5], index=2)
        genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Não binário", "Prefiro não informar"])
        
        if st.form_submit_button("Criar conta", use_container_width=True):
            if email and senha and nome:
                try:
                    # Criar usuário no Auth
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
                        salvar_peso(user_id, peso_atual, date.today())
                        st.success("✅ Conta criada com sucesso! Faça login.")
                        st.session_state["pagina"] = "login"
                        st.rerun()
                    else:
                        st.error("Erro ao criar usuário. Tente outro e-mail.")
                except Exception as e:
                    st.error(f"Erro: {e}. Tente outro e-mail.")
            else:
                st.error("Preencha e-mail, senha e nome.")
    
    if st.button("← Voltar", use_container_width=True):
        st.session_state["pagina"] = "login"
        st.rerun()

def pagina_dashboard():
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.session_state["pagina"] = "login"
        st.rerun()
        return

    # Carregar dados do usuário
    user = carregar_usuario(user_id)
    if not user:
        st.error("Usuário não encontrado. Faça login novamente.")
        if st.button("Voltar ao login"):
            st.session_state.clear()
            st.rerun()
        return

    # Carregar histórico de peso
    pesos = carregar_historico_pesos(user_id)
    df_pesos = pd.DataFrame(pesos) if pesos else pd.DataFrame()

    # Meta mensal
    peso_inicio = user.get("peso_inicio_mes", user["current_weight"])
    meta_kg = user.get("meta_mensal_kg", 2)
    peso_atual = user["current_weight"]
    progresso = peso_inicio - peso_atual
    percentual = (progresso / meta_kg) * 100 if meta_kg > 0 else 0
    percentual = max(0, min(100, percentual))

    # Avatar
    avatar, msg_avatar = get_avatar(percentual)

    # Layout do dashboard
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<div style='font-size: 4rem; text-align: center;'>{avatar}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1>Olá, {user['nome']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p>{mensagem_bom_dia()}</p>", unsafe_allow_html=True)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Peso Atual", f"{peso_atual:.1f} kg", f"{progresso:+.1f} kg este mês")
    with k2:
        imc = calcular_imc(peso_atual, user.get("altura", 1.75))
        st.metric("IMC", f"{imc:.1f}", "referência")
    with k3:
        st.metric("Meta mensal", f"{meta_kg:.1f} kg", f"{progresso:.1f} kg alcançados")
    with k4:
        st.metric("Registros", f"{len(pesos)} dias", "")

    # Barra de progresso da meta mensal
    st.markdown(f"**📅 Progresso da meta mensal**")
    st.progress(percentual / 100, text=f"{progresso:.1f} kg / {meta_kg:.1f} kg")
    st.caption(msg_avatar)

    # Gráfico de evolução de peso
    if not df_pesos.empty:
        df_pesos["registered_at"] = pd.to_datetime(df_pesos["registered_at"])
        fig = px.line(df_pesos, x="registered_at", y="peso_kg", 
                      title="Evolução do Peso",
                      labels={"registered_at": "Data", "peso_kg": "Peso (kg)"},
                      line_shape="linear")
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Registro rápido de peso
    with st.expander("⚖️ Registrar peso hoje"):
        novo_peso = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=peso_atual, step=0.1)
        if st.button("✅ Salvar peso", use_container_width=True):
            if salvar_peso(user_id, novo_peso, date.today()):
                st.success("Peso registrado!")
                time.sleep(1)
                st.rerun()

    # Registro de refeição com foto
    with st.expander("🍽️ Registrar refeição"):
        descricao = st.text_input("O que você comeu?")
        calorias = st.number_input("Calorias (kcal)", min_value=0, max_value=2000, value=300, step=50)
        foto = st.camera_input("Tirar foto do prato (opcional)")
        if st.button("✅ Salvar refeição", use_container_width=True):
            if descricao:
                foto_url = None
                if foto:
                    foto_url = salvar_foto(foto, user_id)
                if salvar_refeicao(user_id, descricao, calorias, foto_url, datetime.now()):
                    st.success("Refeição registrada!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("Digite uma descrição da refeição.")

    # Histórico de refeições
    refeicoes = carregar_refeicoes(user_id)
    if refeicoes:
        st.markdown("### 🍽️ Últimas refeições")
        for r in refeicoes[:5]:
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write(f"**{r['descricao']}**")
                data_str = r['registered_at'][:10] if r['registered_at'] else ""
                st.caption(data_str)
            with cols[1]:
                st.write(f"{r['calorias']} kcal")
            with cols[2]:
                if r.get('foto_url'):
                    st.image(r['foto_url'], width=60)
        if len(refeicoes) > 5:
            st.caption("Mostrando as últimas 5 refeições.")
    else:
        st.info("Nenhuma refeição registrada ainda.")

    # Apoio emocional (hover, sem botão agressivo)
    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); border-radius: 20px; padding: 15px; text-align: center; margin: 15px 0;">
        <span style="font-size: 1.2rem;">🫂</span>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">Dias difíceis acontecem. Você não está sozinho.</p>
        <p style="font-size: 0.7rem; color: #888;">(passe o mouse para apoio)</p>
    </div>
    """, unsafe_allow_html=True)

    # Botão sair
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
    elif pagina == "criar_conta":
        pagina_criar_conta()
    elif pagina == "dashboard":
        pagina_dashboard()
    else:
        pagina_login()

if __name__ == "__main__":
    main()
