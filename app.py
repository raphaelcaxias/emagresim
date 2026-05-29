# app.py — EmagreSim v37.0
import streamlit as st
from datetime import datetime, date
import random

from styles.theme import CSS
from models.state import AppState, Meal, EmotionEntry, WeightEntry, PointLog
from core.calculations import calc_meta_calorica, calc_imc
from core.psychology import (
    calculate_risk_score, get_psychological_mode, get_micro_goal,
    get_companion_message, get_memory_line
)
from core.gamification import (
    get_level, get_next_level, level_progress,
    calculate_meal_points, calculate_streak_bonus
)
from services.storage import init_db, save_state, load_state

st.set_page_config(
    page_title="EmagreSim",
    page_icon="🌱",
    layout="centered",
)
st.markdown(CSS, unsafe_allow_html=True)


# ── Inicialização ──────────────────────────────────────────────────────────────

init_db()

if "state" not in st.session_state:
    loaded = load_state()
    st.session_state.state = loaded if loaded else AppState()

S: AppState = st.session_state.state


def auto_save() -> None:
    save_state(S)


# ── Componentes de UI ──────────────────────────────────────────────────────────

def progress_bar(label: str, value_str: str, pct: float, variant: str = "primary") -> None:
    """Barra de progresso com label e porcentagem."""
    colors = {
        "primary": "#2dce89",
        "warning": "#f0b429",
    }
    color = colors.get(variant, colors["primary"])
    pct_clamped = max(0.0, min(100.0, pct))
    st.markdown(
        f"""
        <div style="margin: 10px 0;">
          <div style="display: flex; justify-content: space-between;
                      font-size: 0.75rem; color: #7d8590; margin-bottom: 5px;">
            <span>{label}</span><span>{value_str}</span>
          </div>
          <div style="background: #21262d; border-radius: 20px;
                      height: 6px; overflow: hidden;">
            <div style="width: {pct_clamped}%; height: 100%;
                        border-radius: 20px; background: {color};
                        transition: width 0.3s ease;"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(content: str, border_color: str = "#30363d") -> None:
    st.markdown(
        f"""
        <div style="background: #161b22; border-radius: 12px;
                    padding: 14px 18px; margin-bottom: 16px;
                    border-left: 3px solid {border_color};">
          {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Header ─────────────────────────────────────────────────────────────────────

level = get_level(S.total_points)
next_level = get_next_level(S.total_points)
hora = datetime.now().hour
saudacao = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")
mode = get_psychological_mode(S)

primeiro_nome = S.nome.split()[0]

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-eyebrow">{saudacao}, {primeiro_nome}</div>
      <div class="hero-name">{level['desc']}</div>
      <div style="display: inline-flex; gap: 8px; align-items: center;
                  background: rgba(45,206,137,0.08);
                  border: 1px solid #1a7d52; border-radius: 24px;
                  padding: 5px 14px; margin-top: 12px; font-size: 0.85rem;">
        <span style="color:#2dce89;">{level['icon']} {level['name']}</span>
        <span style="color:#484f58;">·</span>
        <span style="color:#7d8590;">⭐ {S.total_points} pts</span>
        <span style="color:#484f58;">·</span>
        <span style="color:#7d8590;">🔥 {S.streak} dias</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Companion — só aparece se tiver algo concreto a dizer
companion_msg = get_companion_message(S, mode)
memory_line = get_memory_line(S)

if companion_msg:
    memory_html = (
        f'<div style="font-size:0.75rem; color:#484f58; margin-top:8px;">🧠 {memory_line}</div>'
        if memory_line else ""
    )
    st.markdown(
        f"""
        <div class="companion-card">
          <div style="font-size:0.68rem; color:#2dce89;
                      text-transform:uppercase; margin-bottom:6px; letter-spacing:0.5px;">
            companion
          </div>
          <div class="companion-text">"{companion_msg}"</div>
          {memory_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# Aviso de baixo ritmo — sem dramatização
if mode == "low_momentum":
    info_card(
        content="""
          <div style="font-size:0.8rem; color:#7d8590; text-transform:uppercase;
                      margin-bottom:4px; letter-spacing:0.4px;">ritmo baixo</div>
          <div style="font-size:0.9rem;">
            Você está em uma fase mais difícil. Um registro já conta como progresso.
          </div>
        """,
        border_color="#484f58",
    )

# Meta contextual — ancorada ao comportamento, não ao mood
micro_goal = get_micro_goal(mode)
if micro_goal:
    info_card(
        content=f"""
          <div style="font-size:0.68rem; color:#f0b429;
                      text-transform:uppercase; margin-bottom:4px; letter-spacing:0.4px;">
            meta de hoje
          </div>
          <div style="font-size:0.9rem;">{micro_goal}</div>
        """,
        border_color="#f0b429",
    )


# ── Métricas principais ────────────────────────────────────────────────────────

meta_cal = calc_meta_calorica(S)
cal_hoje = S.today_calories()
diff_peso = round(S.peso_inicio - S.peso_atual, 1)
diff_str = f"−{diff_peso} kg" if diff_peso >= 0 else f"+{abs(diff_peso)} kg"

st.markdown(
    f"""
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-num green">{cal_hoje}</div>
        <div class="stat-label">kcal hoje</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{meta_cal}</div>
        <div class="stat-label">meta diária</div>
      </div>
      <div class="stat-card">
        <div class="stat-num gold">{diff_str}</div>
        <div class="stat-label">variação total</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

pct_cal = (cal_hoje / meta_cal * 100) if meta_cal > 0 else 0
progress_bar(
    label=f"{cal_hoje} / {meta_cal} kcal",
    value_str=f"{int(pct_cal)}%",
    pct=pct_cal,
    variant="primary",
)
progress_bar(
    label=f"{level['icon']} {level['name']}",
    value_str=f"próximo: {next_level['name']}",
    pct=level_progress(S.total_points),
    variant="warning",
)


# ── Tabs ───────────────────────────────────────────────────────────────────────

tabs = st.tabs(["Nutrição", "Peso", "Histórico", "Configurações"])


# ── Tab: Nutrição ──────────────────────────────────────────────────────────────

with tabs[0]:
    st.markdown('<div class="section-title">Refeições de hoje</div>', unsafe_allow_html=True)

    refeicoes_hoje = S.today_meals()

    if refeicoes_hoje:
        ICONES = {"cafe": "☀️", "almoco": "🥗", "lanche": "🍎", "jantar": "🌙"}
        LABELS = {"cafe": "café da manhã", "almoco": "almoço", "lanche": "lanche", "jantar": "jantar"}

        for m in refeicoes_hoje:
            icone = ICONES.get(m.type, "🍽️")
            label = LABELS.get(m.type, m.type)
            foto_badge = (
                ' <span style="background:rgba(240,180,41,0.12); color:#c99a00;'
                '       border-radius:4px; padding:1px 6px; font-size:0.65rem;">foto</span>'
                if m.has_photo else ""
            )
            st.markdown(
                f"""
                <div class="meal-item">
                  <div>
                    <div style="font-size:0.7rem; color:#2dce89; margin-bottom:2px;">
                      {icone} {label}{foto_badge}
                    </div>
                    <div style="font-size:0.9rem;">{m.description}</div>
                    <div style="font-size:0.7rem; color:#484f58; margin-top:2px;">{m.time}</div>
                  </div>
                  <div class="meal-kcal">
                    {m.calories}<br>
                    <span style="font-size:0.65rem; color:#7d8590;">kcal</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="empty-state">
              <div class="icon">🥗</div>
              <div class="msg">Nenhuma refeição registrada hoje.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    CALORIAS_PADRAO = {"cafe": 350, "almoco": 600, "lanche": 200, "jantar": 500}

    with st.expander("Registrar refeição", expanded=not refeicoes_hoje):
        with st.form("form_refeicao"):
            col1, col2 = st.columns(2)

            with col1:
                tipo = st.selectbox(
                    "Momento",
                    options=list(CALORIAS_PADRAO.keys()),
                    format_func=lambda x: {
                        "cafe": "Café da manhã",
                        "almoco": "Almoço",
                        "lanche": "Lanche",
                        "jantar": "Jantar",
                    }[x],
                )

            with col2:
                calorias = st.number_input(
                    "Calorias estimadas",
                    min_value=0,
                    max_value=2000,
                    value=CALORIAS_PADRAO[tipo],
                    step=25,
                )

            descricao = st.text_area(
                "O que você comeu?",
                placeholder="Ex: arroz integral, frango grelhado, brócolis",
            )
            foto = st.camera_input("Foto do prato (opcional)")

            if st.form_submit_button("Salvar refeição", use_container_width=True):
                if descricao.strip():
                    refeicao = Meal(
                        date=S.today_str(),
                        type=tipo,
                        description=descricao.strip(),
                        calories=calorias,
                        has_photo=foto is not None,
                    )
                    S.meals_history.append(refeicao)
                    pts = calculate_meal_points(refeicao)
                    S.total_points += pts
                    S.points_log.append(PointLog(points=pts, source="meal", date=S.today_str()))
                    auto_save()
                    st.toast(f"Refeição salva · +{pts} pontos", icon="✅")
                    st.rerun()
                else:
                    st.warning("Descreva o que você comeu.")


# ── Tab: Peso ──────────────────────────────────────────────────────────────────

with tabs[1]:
    st.markdown('<div class="section-title">Registro de peso</div>', unsafe_allow_html=True)

    with st.form("form_peso"):
        col1, col2 = st.columns(2)

        with col1:
            peso_novo = st.number_input(
                "Peso atual (kg)", min_value=30.0, max_value=250.0,
                value=S.peso_atual, step=0.1,
            )
        with col2:
            peso_meta = st.number_input(
                "Meta (kg)", min_value=30.0, max_value=250.0,
                value=S.peso_meta, step=0.1,
            )

        if st.form_submit_button("Registrar peso", use_container_width=True):
            S.peso_atual = peso_novo
            S.peso_meta = peso_meta
            S.weight_history.append(WeightEntry(weight=peso_novo, date=S.today_str()))
            S.total_points += 10
            S.points_log.append(PointLog(points=10, source="weight", date=S.today_str()))
            auto_save()
            st.toast("Peso registrado · +10 pontos", icon="⚖️")
            st.rerun()

    imc = calc_imc(S.peso_atual, S.altura)
    col1, col2, col3 = st.columns(3)
    col1.metric("IMC", f"{imc:.1f}")
    col2.metric("Perdidos", f"{max(0.0, S.peso_inicio - S.peso_atual):.1f} kg")
    col3.metric("Faltam", f"{max(0.0, S.peso_atual - S.peso_meta):.1f} kg")


# ── Tab: Histórico ─────────────────────────────────────────────────────────────

with tabs[2]:
    st.markdown('<div class="section-title">Padrão emocional</div>', unsafe_allow_html=True)

    if S.emotion_history:
        from collections import Counter
        import plotly.graph_objects as go

        contagem = Counter(e.emotion for e in S.emotion_history)
        fig = go.Figure(
            go.Bar(
                x=list(contagem.keys()),
                y=list(contagem.values()),
                marker_color="#2dce89",
                hovertemplate="%{x}: %{y} registros<extra></extra>",
            )
        )
        fig.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#7d8590", size=12),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#21262d"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Faça check-ins para visualizar seu padrão emocional ao longo do tempo.")


# ── Tab: Configurações ─────────────────────────────────────────────────────────

with tabs[3]:
    st.markdown('<div class="section-title">Seu perfil</div>', unsafe_allow_html=True)

    with st.form("form_perfil"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome completo", value=S.nome)
            idade = st.number_input("Idade", min_value=16, max_value=100, value=S.idade)
            sexo = st.selectbox("Sexo biológico", ["M", "F"], index=0 if S.sexo == "M" else 1)

        with col2:
            altura = st.number_input(
                "Altura (m)", min_value=1.40, max_value=2.40,
                value=S.altura, step=0.01,
            )
            objetivo = st.selectbox(
                "Objetivo",
                options=["emagrecer", "ganhar_massa", "manter"],
                format_func=lambda x: {
                    "emagrecer": "Reduzir gordura corporal",
                    "ganhar_massa": "Ganhar massa muscular",
                    "manter": "Manter peso atual",
                }[x],
            )
            atividade = st.selectbox(
                "Nível de atividade",
                options=["sedentario", "leve", "moderado", "intenso", "extremo"],
                format_func=lambda x: {
                    "sedentario": "Sedentário (sem exercício)",
                    "leve": "Leve (1–3x por semana)",
                    "moderado": "Moderado (3–5x por semana)",
                    "intenso": "Intenso (6–7x por semana)",
                    "extremo": "Muito intenso (2x por dia)",
                }[x],
            )

        if st.form_submit_button("Salvar configurações", use_container_width=True):
            S.nome = nome
            S.idade = idade
            S.sexo = sexo
            S.altura = altura
            S.objetivo = objetivo
            S.nivel_atividade = atividade
            auto_save()
            st.toast("Configurações salvas", icon="✅")
            st.rerun()


# ── Check-in emocional ─────────────────────────────────────────────────────────

st.markdown(
    "<hr style='border:0; border-top:1px solid #21262d; margin:28px 0;'>",
    unsafe_allow_html=True,
)
st.markdown('<div class="section-title">Como você está agora?</div>', unsafe_allow_html=True)

EMOCOES = {
    "motivado": "✨",
    "confiante": "💪",
    "neutro": "😐",
    "ansioso": "😰",
    "cansado": "😔",
    "frustrado": "😞",
}

colunas = st.columns(len(EMOCOES))
emocao_selecionada = None

for i, (chave, icone) in enumerate(EMOCOES.items()):
    with colunas[i]:
        if st.button(f"{icone}\n{chave}", key=f"emo_{chave}", use_container_width=True):
            emocao_selecionada = chave

if emocao_selecionada:
    reflexao = st.text_area(
        "Aconteceu algo que influenciou como você comeu hoje? (opcional)",
        placeholder="Contexto ajuda o sistema a entender seus padrões.",
        height=70,
        label_visibility="visible",
    )

    with st.form("form_checkin"):
        if st.form_submit_button("Confirmar check-in", use_container_width=True):
            hoje = date.today()

            if S.last_checkin:
                gap = (hoje - date.fromisoformat(S.last_checkin)).days
                if gap == 1:
                    S.streak += 1
                elif gap == 0:
                    pass  # Já fez check-in hoje
                else:
                    S.streak = 1
            else:
                S.streak = 1

            S.longest_streak = max(S.longest_streak, S.streak)
            S.total_checkins += 1
            S.last_checkin = S.today_str()
            S.emotion_history.append(
                EmotionEntry(
                    emotion=emocao_selecionada,
                    timestamp=datetime.now().isoformat(),
                    reflection=reflexao,
                )
            )

            pts = 10 + calculate_streak_bonus(S.streak)
            S.total_points += pts
            S.points_log.append(PointLog(points=pts, source="checkin", date=S.today_str()))
            auto_save()

            if S.streak > 0 and S.streak % 7 == 0:
                st.balloons()
                st.toast(f"{S.streak} dias seguidos. Consistência real.", icon="🔥")
            else:
                st.toast(f"Check-in registrado · +{pts} pontos", icon="✅")

            st.rerun()


# ── Footer ─────────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div style="text-align:center; padding:40px 0 16px;
                font-size:0.7rem; color:#484f58;">
      {S.streak} dias consecutivos · {S.total_points} pontos acumulados
    </div>
    """,
    unsafe_allow_html=True,
)
