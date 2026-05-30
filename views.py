import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone

from models.state import BehavioralState, LEVELS, ACHIEVEMENTS, EMOTIONAL_STATES
from core.psychology import NarrativeEngine


def render_dashboard(state: BehavioralState, patterns: Dict, risk_score: float) -> None:
    st.markdown(f"### {NarrativeEngine.get_greeting(state, patterns)}")

    message = NarrativeEngine.get_companion_message(state, risk_score, patterns)
    st.info(f"💬 {message}")

    micro_goal = NarrativeEngine.get_micro_goal(
        state.psychological_mode, risk_score, patterns,
        seed_context=f"goal_{state.user_id}",
    )
    st.success(f"🎯 Meta de hoje: {micro_goal}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Consistência", f"{state.consistency_score:.1f}")
    with col2:
        icon = "🔥" if state.current_streak >= 3 else "🌱"
        st.metric(f"{icon} Streak", state.current_streak)
    with col3:
        lvl = LEVELS.get(state.current_level, {})
        st.metric(f"{lvl.get('icon', '🌟')} Nível", lvl.get("name", "Desconhecido"))

    if state.emotion_history:
        df = pd.DataFrame(state.emotion_history[-14:])
        df["date"] = pd.to_datetime(df["timestamp_utc"]).dt.date
        counts = df.groupby(["date", "emotion"]).size().unstack(fill_value=0)
        fig = go.Figure(
            [go.Bar(name=emo, x=counts.index, y=counts[emo]) for emo in counts.columns]
        )
        fig.update_layout(barmode="stack", title="Emoções (14 dias)", height=300)
        st.plotly_chart(fig, use_container_width=True)

    if state.unlocked_achievements:
        st.markdown("**🏆 Conquistas**")
        cols = st.columns(min(len(state.unlocked_achievements), 5))
        for col, key in zip(cols, state.unlocked_achievements):
            ach = ACHIEVEMENTS.get(key, {})
            col.markdown(f"{ach.get('icon', '🏅')} **{ach.get('name', key)}**")


def render_checkin_form(is_demo: bool, on_submit) -> None:
    with st.form("checkin_form", clear_on_submit=True):
        st.subheader("📝 Como você está hoje?")
        emotion = st.selectbox(
            "Estado emocional",
            options=list(EMOTIONAL_STATES.keys()),
            format_func=lambda x: f"{EMOTIONAL_STATES[x]['icon']} {EMOTIONAL_STATES[x]['label']}",
        )
        actions = st.multiselect(
            "Ações realizadas",
            ["Hidratei", "Caminhei", "Respirei fundo", "Anotei sentimentos", "Outro"],
        )
        reflection = st.text_area("Reflexão rápida (opcional)", height=70)
        submitted = st.form_submit_button("✅ Registrar Presença")

        if submitted and not is_demo:
            with st.spinner("Registrando…"):
                on_submit(emotion, actions, reflection)
                st.success("Presença registrada! 🌱")