from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Callable, Dict, Optional

from models.state import BehavioralState, EMOTIONAL_STATES, LEVELS, ACHIEVEMENTS
from core.psychology import NarrativeEngine


def render_dashboard(
    state: BehavioralState,
    patterns: Dict,
    risk_score: float,
) -> None:
    """Render the main analytics dashboard below the check-in form."""

    # --- Greeting + companion message ---
    st.markdown(f"### {NarrativeEngine.get_greeting(state, patterns)}")

    message = NarrativeEngine.get_companion_message(state, risk_score, patterns)
    st.info(f"💬 {message}")

    micro_goal = NarrativeEngine.get_micro_goal(
        state.psychological_mode,
        risk_score,
        patterns,
        seed_context=f"goal_{state.user_id}",
    )
    st.success(f"🎯 Meta de hoje: {micro_goal}")

    # --- Key metrics ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Consistência", f"{state.consistency_score:.1f}", help="Score de 0 a 100 baseado nos últimos 30 dias")
    with col2:
        streak_icon = "🔥" if state.current_streak >= 3 else "🌱"
        st.metric(f"{streak_icon} Streak", state.current_streak, help="Dias consecutivos com check-in")
    with col3:
        lvl = LEVELS.get(state.current_level, {})
        st.metric(
            f"{lvl.get('icon', '🌟')} Nível",
            lvl.get("name", "Desconhecido"),
            help=lvl.get("desc", ""),
        )

    # --- Secondary stats row ---
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Total de Check-ins", state.total_checkins)
    with col5:
        st.metric("Maior Streak", state.longest_streak)
    with col6:
        risk_label = "🟢 Baixo" if risk_score < 30 else ("🟡 Médio" if risk_score < 60 else "🔴 Alto")
        st.metric("Risco de Abandono", risk_label, help="Calculado com base em ausências e emoções recentes")

    # --- Emotion chart ---
    if state.emotion_history:
        _render_emotion_chart(state.emotion_history[-14:])

    # --- Achievements ---
    if state.unlocked_achievements:
        st.markdown("**🏆 Conquistas Desbloqueadas**")
        cols = st.columns(min(len(state.unlocked_achievements), 5))
        for col, ach_key in zip(cols, state.unlocked_achievements):
            ach = ACHIEVEMENTS.get(ach_key, {})
            col.markdown(
                f"{ach.get('icon', '🏅')} **{ach.get('name', ach_key)}**  \n"
                f"<small>{ach.get('desc', '')}</small>",
                unsafe_allow_html=True,
            )


def _render_emotion_chart(emotion_history: list) -> None:
    """Stacked bar chart of emotional states over the last 14 days."""
    try:
        df = pd.DataFrame(emotion_history)
        df["date"] = pd.to_datetime(df["timestamp_utc"], utc=True).dt.date
        counts = df.groupby(["date", "emotion"]).size().unstack(fill_value=0)

        color_map = {emo: meta["color"] for emo, meta in EMOTIONAL_STATES.items()}
        bars = [
            go.Bar(
                name=EMOTIONAL_STATES.get(emo, {}).get("label", emo),
                x=counts.index.astype(str),
                y=counts[emo],
                marker_color=color_map.get(emo, "#636e72"),
            )
            for emo in counts.columns
        ]

        fig = go.Figure(bars)
        fig.update_layout(
            barmode="stack",
            title="Emoções (últimos 14 dias)",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        # Gracefully skip chart on data issues rather than crashing
        pass


def render_checkin_form(is_demo: bool, on_submit: Callable) -> None:
    """
    Check-in form with basic UX guardrails:
    - Reflection is optional (always was).
    - Submit is disabled in demo mode with a clear warning instead of silent failure.
    - Spinner provides feedback during the DB write.
    """
    with st.form("checkin_form", clear_on_submit=True):
        st.subheader("📝 Como você está hoje?")

        emotion = st.selectbox(
            "Estado emocional *",
            options=list(EMOTIONAL_STATES.keys()),
            format_func=lambda x: f"{EMOTIONAL_STATES[x]['icon']} {EMOTIONAL_STATES[x]['label']}",
        )

        actions = st.multiselect(
            "Ações realizadas (opcional)",
            ["Hidratei bem", "Caminhei", "Respirei fundo", "Anotei sentimentos", "Dormi bem", "Outro"],
        )

        reflection = st.text_area(
            "Reflexão rápida (opcional)",
            placeholder="Como foi hoje? O que te trouxe aqui?",
            height=80,
        )

        col_btn, col_hint = st.columns([2, 3])
        with col_btn:
            submitted = st.form_submit_button(
                "✅ Registrar Presença",
                use_container_width=True,
                disabled=is_demo,
            )
        with col_hint:
            if is_demo:
                st.caption("🧪 Modo demo — dados não são salvos. Configure o Supabase para ativar.")

        if submitted and not is_demo:
            with st.spinner("Registrando sua presença…"):
                on_submit(emotion, actions, reflection or None)
            st.success("✅ Presença registrada! Continue assim. 🌱")
            st.rerun()
