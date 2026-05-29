# app.py - EmagreSim v27.0 (Unificado com Design System Slate+Amber)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from supabase import create_client

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================
st.set_page_config(
    page_title="EmagreSim",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# SUPABASE (opcional, fallback para demo)
# ============================================================================
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["CHAVE_SUPABASE"]
        return create_client(url, key)
    except:
        return None

supabase = get_supabase()

# ============================================================================
# DESIGN SYSTEM – SLATE + AMBER (dark, profissional)
# ============================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:        #0F1117;
    --surface:   #181C27;
    --surface2:  #1E2333;
    --border:    #2A3050;
    --amber:     #F59E0B;
    --amber-dim: #92610A;
    --teal:      #14B8A6;
    --red:       #F87171;
    --text:      #E2E8F0;
    --muted:     #64748B;
    --success:   #34D399;
    --font:      'DM Sans', sans-serif;
    --display:   'DM Serif Display', serif;
    --radius:    14px;
    --radius-sm: 8px;
}

html, body, [data-testid="stAppViewContainer"], section.main {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}

[data-testid="stSidebar"] { display: none !important; }
#MainMenu, header, footer, .stDeployButton { display: none !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* Top bar */
.topbar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 14px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    position: sticky;
    top: 0;
    z-index: 100;
}
.logo { font-family: var(--display); font-size: 1.5rem; color: var(--text); }
.logo em { font-style: normal; color: var(--amber); }
.user-badge {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.8rem;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 8px;
}
.user-badge strong { color: var(--text); }

/* Nav pills */
.stButton > button {
    background: var(--surface) !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: var(--font) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 8px 0 !important;
    transition: all .18s ease !important;
}
.stButton > button:hover {
    background: var(--surface2) !important;
    color: var(--amber) !important;
    border-color: var(--amber-dim) !important;
    transform: translateY(-1px);
}

/* Hero card */
.hero-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 32px;
    display: flex;
    align-items: center;
    gap: 24px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-card::before {
    content: '';
    position: absolute;
    right: -40px; top: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(245,158,11,.08) 0%, transparent 70%);
    border-radius: 50%;
}
.avatar {
    width: 72px; height: 72px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--amber-dim), var(--amber));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    flex-shrink: 0;
}
.hero-text h2 { font-family: var(--display); font-size: 1.7rem; color: var(--text); }
.hero-text p { font-size: 0.9rem; color: var(--muted); margin-top: 4px; }

/* KPI grid */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 20px; }
.kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 18px;
    position: relative;
    overflow: hidden;
}
.kpi::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-amber::after  { background: var(--amber); }
.kpi-teal::after   { background: var(--teal); }
.kpi-red::after    { background: var(--red); }
.kpi-green::after  { background: var(--success); }
.kpi-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
.kpi-value { font-size: 1.7rem; font-weight: 700; color: var(--text); line-height: 1; }
.kpi-delta { font-size: 0.8rem; margin-top: 4px; }
.delta-pos { color: var(--success); }
.delta-neg { color: var(--red); }
.delta-neu { color: var(--muted); }

/* Progress bar */
.prog-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 20px; }
.prog-header { display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--muted); margin-bottom: 10px; }
.prog-track { background: var(--surface2); border-radius: 999px; height: 10px; overflow: hidden; }
.prog-fill { background: linear-gradient(90deg, var(--amber-dim), var(--amber)); height: 100%; border-radius: 999px; transition: width .6s ease; }

/* IMC badge */
.imc-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.imc-normal { background: rgba(52,211,153,.15); color: var(--success); }
.imc-low    { background: rgba(248,113,113,.15); color: var(--red); }
.imc-high   { background: rgba(245,158,11,.15); color: var(--amber); }
.imc-very-high { background: rgba(248,113,113,.2); color: var(--red); }

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 20px;
}
.card-title {
    font-family: var(--display);
    font-size: 1.1rem;
    color: var(--text);
    margin-bottom: 18px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
}

/* Meal row */
.meal-row {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px 16px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: border-color .18s;
}
.meal-row:hover { border-color: var(--amber-dim); }
.meal-info .meal-type { font-size: 0.75rem; color: var(--amber); font-weight: 600; text-transform: uppercase; letter-spacing: .06em; }
.meal-info .meal-desc { font-size: 0.9rem; color: var(--text); margin-top: 2px; }
.meal-info .meal-time { font-size: 0.75rem; color: var(--muted); }
.meal-kcal { font-size: 0.95rem; font-weight: 700; color: var(--teal); }

/* Info boxes */
.info-box {
    border-radius: var(--radius-sm);
    padding: 16px;
    font-size: 0.87rem;
    line-height: 1.5;
}
.info-support { background: rgba(20,184,166,.07); border: 1px solid rgba(20,184,166,.2); color: var(--teal); }
.info-tip     { background: rgba(245,158,11,.07); border: 1px solid rgba(245,158,11,.2); color: var(--amber); }
.info-label   { font-weight: 700; margin-bottom: 4px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .07em; }

/* Overrides */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font) !important;
}
div[data-testid="stExpander"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
div[data-testid="stExpander"] summary { color: var(--amber) !important; font-weight: 500 !important; }
[data-testid="stProgress"] > div > div { background: var(--amber) !important; }
.stAlert { background: var(--surface2) !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: var(--radius-sm) !important; }
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ============================================================================
# INICIALIZAÇÃO DO ESTADO
# ============================================================================
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "demo-user"
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "dashboard"

uid = st.session_state["user_id"]

# Carregar dados do Supabase (se não for demo)
if uid != "demo-user" and supabase:
    try:
        user_data = supabase.table("users").select("*").eq("id", uid).execute()
        if user_data.data:
            u = user_data.data[0]
            st.session_state["current_weight"] = u.get("current_weight", 80.0)
            st.session_state["meta_mensal_kg"] = u.get("meta_mensal_kg", 2.0)
            st.session_state["peso_inicio_mes"] = u.get("peso_inicio_mes", 80.0)
            st.session_state["altura"] = u.get("altura", 1.70)
            st.session_state["nome"] = u.get("nome", "Usuário")
            st.session_state["idade"] = u.get("idade", 30)
            # Histórico de pesos
            hist = supabase.table("weight_logs").select("registered_at, peso_kg").eq("user_id", uid).order("registered_at").execute()
            if hist.data:
                st.session_state["historico_pesos"] = [(h["registered_at"], h["peso_kg"]) for h in hist.data]
            else:
                st.session_state["historico_pesos"] = []
            # Refeições
            refs = supabase.table("food_logs").select("registered_at, meal_type, description, calories").eq("user_id", uid).order("registered_at", desc=True).execute()
            if refs.data:
                st.session_state["refeicoes"] = [
                    {"hora": (r.get("registered_at") or "")[11:16] or "12:00",
                     "tipo": r["meal_type"], "descricao": r["description"], "calorias": r["calories"], "foto": None}
                    for r in refs.data
                ]
    except Exception as e:
        pass

# Modo demo (valores padrão)
if uid == "demo-user":
    defaults = {
        "current_weight": 105.8, "meta_mensal_kg": 3.0, "peso_inicio_mes": 108.0,
        "altura": 1.75, "nome": "Adriano", "idade": 39, "refeicoes": []
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)
    if "historico_pesos" not in st.session_state or not st.session_state["historico_pesos"]:
        datas = [datetime.now() - timedelta(days=i) for i in range(30, -1, -1)]
        pesos = [108.0 - i * 0.08 + random.uniform(-0.3, 0.3) for i in range(31)]
        st.session_state["historico_pesos"] = list(zip(datas, pesos))

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================
def saudacao():
    h = datetime.now().hour
    if h < 12: return "Bom dia"
    if h < 18: return "Boa tarde"
    return "Boa noite"

def imc_info(peso, altura):
    if altura <= 0: return 0, "", ""
    imc = peso / altura ** 2
    if imc < 18.5:   return imc, "Abaixo do peso", "imc-low"
    elif imc < 25.0: return imc, "Peso normal", "imc-normal"
    elif imc < 30.0: return imc, "Sobrepeso", "imc-high"
    else:            return imc, "Obesidade", "imc-very-high"

def avatar_emoji(pct):
    if pct >= 100: return "🏆"
    if pct >= 75:  return "⚡"
    if pct >= 50:  return "🌱"
    if pct >= 25:  return "🔥"
    return "🌅"

def salvar_peso_db(peso):
    if uid != "demo-user" and supabase:
        try:
            supabase.table("weight_logs").insert({"user_id": uid, "peso_kg": round(peso,1), "registered_at": datetime.now().isoformat()}).execute()
            supabase.table("users").update({"current_weight": round(peso,1)}).eq("id", uid).execute()
        except:
            pass

def salvar_refeicao_db(ref):
    if uid != "demo-user" and supabase:
        try:
            supabase.table("food_logs").insert({
                "user_id": uid, "date": datetime.now().date().isoformat(),
                "meal_type": ref["tipo"], "description": ref["descricao"],
                "calories": ref["calorias"], "registered_at": datetime.now().isoformat()
            }).execute()
        except:
            pass

# ============================================================================
# TOPBAR
# ============================================================================
modo = "Demo" if uid == "demo-user" else "Premium"
st.markdown(f"""
<div class="topbar">
    <div class="logo">Emagre<em>Sim</em></div>
    <div class="user-badge">
        <span>👤</span>
        <strong>{st.session_state.get('nome','Usuário')}</strong>
        <span>·</span>
        <span>{modo}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# NAVEGAÇÃO
# ============================================================================
nav_cols = st.columns(4)
nav_items = [("📊 Dashboard","dashboard"), ("🍽️ Refeições","refeicoes"), ("📈 Histórico","historico"), ("👤 Perfil","perfil")]
for col, (label, key) in zip(nav_cols, nav_items):
    with col:
        if st.button(label, use_container_width=True, key=f"nav_{key}"):
            st.session_state["pagina"] = key
            st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ============================================================================
# PÁGINA DASHBOARD
# ============================================================================
def pagina_dashboard():
    peso   = st.session_state["current_weight"]
    meta   = st.session_state["meta_mensal_kg"]
    inicio = st.session_state["peso_inicio_mes"]
    prog   = max(0, inicio - peso)
    pct    = min(100, (prog / meta) * 100) if meta > 0 else 0
    imc, imc_cat, imc_cls = imc_info(peso, st.session_state.get("altura",1.70))
    emoji  = avatar_emoji(pct)
    msgs = {100:"Meta mensal alcançada — incrível!",75:"Quase lá, continue firme.",
            50:"Metade do caminho. Você está evoluindo.",25:"Primeiros resultados visíveis!",
            0:"Todo recomeço é uma semente. Confie no processo."}
    msg = next(v for k,v in sorted(msgs.items(), reverse=True) if pct >= k)

    st.markdown(f"""
    <div class="hero-card">
        <div class="avatar">{emoji}</div>
        <div class="hero-text">
            <h2>{saudacao()}, {st.session_state.get('nome','Usuário')}.</h2>
            <p>{msg}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    delta_peso = f"-{prog:.1f} kg" if prog >= 0 else f"+{abs(prog):.1f} kg"
    delta_cls  = "delta-pos" if prog >= 0 else "delta-neg"
    restante   = max(0, meta - prog)
    n_ref      = len(st.session_state.get("refeicoes", []))

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi kpi-amber">
            <div class="kpi-label">⚖️ Peso atual</div>
            <div class="kpi-value">{peso:.1f} <span style="font-size:.9rem;font-weight:400">kg</span></div>
            <div class="kpi-delta {delta_cls}">{delta_peso} vs. início do mês</div>
        </div>
        <div class="kpi kpi-teal">
            <div class="kpi-label">📊 IMC</div>
            <div class="kpi-value">{imc:.1f}</div>
            <div class="kpi-delta"><span class="imc-badge {imc_cls}">{imc_cat}</span></div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">🎯 Meta mensal</div>
            <div class="kpi-value">{meta:.1f} <span style="font-size:.9rem;font-weight:400">kg</span></div>
            <div class="kpi-delta delta-neu">{pct:.0f}% concluído · faltam {restante:.1f} kg</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">🍽️ Refeições hoje</div>
            <div class="kpi-value">{n_ref}</div>
            <div class="kpi-delta delta-neu">registradas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="prog-wrap">
        <div class="prog-header">
            <span>Progresso mensal</span>
            <span style="color:var(--amber);font-weight:600">{prog:.1f} kg / {meta:.1f} kg</span>
        </div>
        <div class="prog-track"><div class="prog-fill" style="width:{pct:.1f}%"></div></div>
        <div style="font-size:.75rem;color:var(--muted);margin-top:8px">{pct:.1f}% da meta concluída</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚖️ Registrar novo peso"):
        novo = st.number_input("Peso (kg)", 40.0, 200.0, peso, 0.1, key="input_peso")
        if st.button("Salvar peso", key="btn_peso"):
            st.session_state["current_weight"] = novo
            if uid != "demo-user":
                salvar_peso_db(novo)
            st.success(f"✓ {novo:.1f} kg registrado")
            st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="info-box info-support">
            <div class="info-label">🫂 Apoio</div>
            Dias difíceis fazem parte. O que importa é continuar. Você não está sozinho nessa jornada.
        </div>""", unsafe_allow_html=True)
    with c2:
        dicas = [
            "Mastigue devagar — a saciedade leva ~20 min para chegar.",
            "Beba 1 copo d'água antes de cada refeição principal.",
            "Prefira proteínas no café da manhã para controlar a fome.",
            "Durma 7–8h: cortisol elevado sabota o emagrecimento.",
            "Planeje as refeições da semana no domingo.",
            "Não pule refeições — o risco de compulsão aumenta.",
            "Tempere com ervas e especiarias para reduzir o sal.",
        ]
        st.markdown(f"""
        <div class="info-box info-tip">
            <div class="info-label">💡 Dica do dia</div>
            {random.choice(dicas)}
        </div>""", unsafe_allow_html=True)

# ============================================================================
# PÁGINA REFEIÇÕES
# ============================================================================
TIPOS = ["Café da manhã","Almoço","Jantar","Lanche","Pré-treino","Pós-treino"]
KCAL_REF = 2000

def pagina_refeicoes():
    refeicoes = st.session_state.get("refeicoes", [])
    total_kcal = sum(r["calorias"] for r in refeicoes)
    pct_kcal   = min(100, total_kcal / KCAL_REF * 100)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🍽️ Refeições do dia</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="prog-wrap" style="margin-bottom:20px">
        <div class="prog-header">
            <span>Calorias consumidas</span>
            <span style="color:var(--teal);font-weight:600">{total_kcal} / {KCAL_REF} kcal</span>
        </div>
        <div class="prog-track">
            <div class="prog-fill" style="width:{pct_kcal:.1f}%;background:linear-gradient(90deg,#0d7970,var(--teal))"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("➕ Adicionar refeição"):
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo", TIPOS, key="ref_tipo")
            desc = st.text_area("Descrição", placeholder="Ex: Frango grelhado, arroz integral, salada", key="ref_desc")
        with c2:
            kcal = st.number_input("Calorias (kcal)", 0, 3000, 400, 50, key="ref_kcal")
            hora = st.time_input("Horário", datetime.now().time(), key="ref_hora")
        if st.button("✅ Salvar refeição", key="btn_salvar_ref"):
            if desc.strip():
                nova = {"hora": hora.strftime("%H:%M"), "tipo": tipo,
                        "descricao": desc.strip(), "calorias": kcal, "foto": None}
                if uid != "demo-user":
                    salvar_refeicao_db(nova)
                st.session_state["refeicoes"].append(nova)
                st.success("Refeição registrada!")
                st.rerun()
            else:
                st.warning("Informe a descrição da refeição.")

    if refeicoes:
        for ref in reversed(refeicoes[-15:]):
            st.markdown(f"""
            <div class="meal-row">
                <div class="meal-info">
                    <div class="meal-type">{ref['tipo']}</div>
                    <div class="meal-desc">{ref['descricao']}</div>
                    <div class="meal-time">{ref.get('hora','--:--')}</div>
                </div>
                <div class="meal-kcal">{ref['calorias']} kcal</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:var(--muted);font-size:.9rem;text-align:center;padding:24px'>Nenhuma refeição registrada hoje.</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PÁGINA HISTÓRICO
# ============================================================================
def pagina_historico():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 Histórico de peso</div>', unsafe_allow_html=True)

    hist = st.session_state.get("historico_pesos", [])
    if not hist:
        st.info("Nenhum dado de peso registrado ainda.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    df = pd.DataFrame(hist, columns=["data", "peso"])
    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values("data")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["data"], y=df["peso"],
        mode="lines+markers",
        line=dict(color="#F59E0B", width=2.5),
        marker=dict(color="#F59E0B", size=6, line=dict(color="#0F1117", width=2)),
        fill="tozeroy",
        fillcolor="rgba(245,158,11,0.06)",
        hovertemplate="<b>%{y:.1f} kg</b><br>%{x|%d/%m/%Y}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#181C27", plot_bgcolor="#181C27",
        font=dict(family="DM Sans", color="#64748B"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickformat="%d/%m", gridcolor="#2A3050", tickfont=dict(color="#64748B")),
        yaxis=dict(gridcolor="#2A3050", tickfont=dict(color="#64748B")),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    pesos = df["peso"].tolist()
    c1, c2, c3, c4 = st.columns(4)
    delta_total = pesos[-1] - pesos[0]
    delta_cls = "delta-pos" if delta_total <= 0 else "delta-neg"
    delta_sym = "↓" if delta_total <= 0 else "↑"

    c1.metric("Início", f"{pesos[0]:.1f} kg")
    c2.metric("Atual", f"{pesos[-1]:.1f} kg", f"{delta_sym} {abs(delta_total):.1f} kg total")
    c3.metric("Menor peso", f"{min(pesos):.1f} kg")
    c4.metric("Maior peso", f"{max(pesos):.1f} kg")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PÁGINA PERFIL
# ============================================================================
def pagina_perfil():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">👤 Meu Perfil</div>', unsafe_allow_html=True)

    with st.form("perfil_form"):
        c1, c2 = st.columns(2)
        with c1:
            nome   = st.text_input("Nome", st.session_state.get("nome","Usuário"))
            altura = st.number_input("Altura (m)", 1.40, 2.20, float(st.session_state.get("altura", 1.70)), 0.01)
        with c2:
            idade  = st.number_input("Idade", 10, 100, int(st.session_state.get("idade", 30)))
            meta   = st.number_input("Meta mensal de perda (kg)", 0.5, 10.0, float(st.session_state.get("meta_mensal_kg", 2.0)), 0.5)

        peso_inicio = st.number_input("Peso no início do mês (kg)", 40.0, 200.0,
            float(st.session_state.get("peso_inicio_mes", st.session_state.get("current_weight", 80.0))), 0.1,
            help="Referência para calcular o progresso mensal.")

        if st.form_submit_button("💾 Salvar perfil"):
            st.session_state.update({"nome": nome, "altura": altura, "idade": idade,
                                     "meta_mensal_kg": meta, "peso_inicio_mes": peso_inicio})
            st.success("Perfil atualizado!")
            st.rerun()

    imc, cat, cls = imc_info(st.session_state.get("current_weight",80), st.session_state.get("altura",1.70))
    st.markdown(f"""
    <div class="info-box info-tip" style="margin-top:16px">
        <div class="info-label">📊 Seu IMC atual</div>
        <b style="font-size:1.4rem">{imc:.1f}</b>
        &nbsp;<span class="imc-badge {cls}">{cat}</span>
        <p style="margin-top:8px;font-size:.82rem;color:var(--muted)">Referência OMS: &lt;18.5 abaixo do peso · 18.5–24.9 normal · 25–29.9 sobrepeso · ≥30 obesidade</p>
    </div>""", unsafe_allow_html=True)

    if uid == "demo-user":
        st.markdown('<p style="font-size:.8rem;color:var(--muted);margin-top:16px">⚠️ Modo demo — dados não persistem entre sessões.</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# ROTEAMENTO
# ============================================================================
paginas = {
    "dashboard":  pagina_dashboard,
    "refeicoes":  pagina_refeicoes,
    "historico":  pagina_historico,
    "perfil":     pagina_perfil,
}
paginas.get(st.session_state["pagina"], pagina_dashboard)()