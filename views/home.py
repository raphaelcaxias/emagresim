import streamlit as st
from components import card_metric, progress_bar, section_header
from utils.safe_data import get_daily_summary_safe, get_streak_safe

def render_home(services: dict, user: dict):
    # Onboarding Forçado (Fase 3)
    required_fields = ["current_weight", "height", "age", "goal_weight"]
    missing_fields = [f for f in required_fields if user.get(f) is None]
    
    if missing_fields:
        st.warning("⚠️ Complete seu perfil para uma experiência personalizada!")
        if st.button("Completar Perfil Agora", use_container_width=True, type="primary"):
            st.session_state.page = "profile"
            st.rerun()
        return

    section_header(f"Bem-vindo(a), {user.get('name', 'Usuário')}!", "Vamos analisar seu progresso de hoje.", "👋")
    
    summary = get_daily_summary_safe(services["nutrition"])
    streak = get_streak_safe(services["gamification"])
    
    w = user.get("current_weight") or 70.0
    goal = user.get("goal_weight") or 65.0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: card_metric(f"{summary.get('calories', 0)}", "Calorias Hoje", "")
    with col2: card_metric(f"{streak}", "Dias Seguidos", "🔥", "#f59e0b")
    with col3: card_metric(f"{w:.1f} kg", "Peso Atual", "⚖️", "#10b981")
    with col4: card_metric(f"{w - goal:+.1f} kg", "Para a Meta", "", "#8b5cf6")

    # Meta Diária
    tmb = services["nutrition"].calculate_tmb(w, user.get("height", 170), user.get("age", 30))
    meta = services["nutrition"].calculate_daily_goal(tmb, user.get("activity_level", "moderate"), user.get("goal", "lose"))
    percent = min(100, int((summary['calories'] / meta) * 100)) if meta > 0 else 0
    
    st.markdown(f"**Meta diária:** {meta} kcal ({percent}% consumido)")
    progress_bar(percent)

    # Ações Rápidas
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🍴 Registrar Refeição", use_container_width=True, type="primary"):
            st.session_state.page = "meals"
            st.rerun()
    with col2:
        if st.button("⚖️ Registrar Peso", use_container_width=True):
            st.session_state.page = "weight"
            st.rerun()
    with col3:
        if st.button("📊 Ver Dashboard Completo", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
