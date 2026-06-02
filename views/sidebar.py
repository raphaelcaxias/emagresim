import streamlit as st

def render_sidebar(services: dict):
    user = st.session_state.user
    if not user:
        return

    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #334155; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: #06b6d4;">💪 EmagreSim</h2>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #94a3b8;">v2.0 Pro</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Badge de Plano
        plan = user.get("plan", "free")
        badge_color = "#f59e0b" if plan == "pro" else "#64748b"
        st.markdown(f'<div style="background: {badge_color}20; color: {badge_color}; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: 600; margin-bottom: 1.5rem; border: 1px solid {badge_color};">👑 PLANO {plan.upper()}</div>', unsafe_allow_html=True)
        
        st.markdown(f"**👤 {user.get('name', 'Usuário')}**")
        st.caption(f"📧 {user.get('email', '')}")
        
        # Stats rápidos da sidebar
        from utils.safe_data import get_daily_summary_safe, get_streak_safe
        summary = get_daily_summary_safe(services["nutrition"])
        streak = get_streak_safe(services["gamification"])
        
        st.markdown("---")
        st.markdown("**📊 Resumo de Hoje**")
        st.metric("🔥 Calorias", f"{summary.get('calories', 0)} kcal")
        st.metric("🍽️ Refeições", summary.get('count', 0))
        st.metric("🔥 Sequência", f"{streak} dias")
        
        st.markdown("---")
        st.markdown("**🧭 Navegação**")
        
        pages = [
            (" Início", "home"),
            (" Dashboard", "dashboard"),
            (" Registro Alimentar", "meals"),
            ("⚖️ Evolução Peso", "weight"),
            ("📈 Análise e Desafios", "analysis"),
            ("👤 Perfil e Metas", "profile")
        ]
        
        for label, page_key in pages:
            btn_type = "primary" if st.session_state.page == page_key else "secondary"
            if st.button(label, use_container_width=True, type=btn_type):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()
