from __future__ import annotations
import logging
from datetime import datetime, timezone

import streamlit as st
from supabase import create_client

from core.database import SupabaseRepository
from core.services import process_checkin, AuthService
from utils.analytics import BehavioralEngine
from models.state import BehavioralState
from views import render_dashboard, render_checkin_form

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEFAULT_TZ = timezone.utc

st.set_page_config(
    page_title="EmagreSim • Aderência",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def _init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("CHAVE_SUPABASE")
        if not url or not key:
            logger.warning("Supabase credentials missing. Running in demo mode.")
            return None
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Supabase init failed: {e}")
        return None


def main():
    # Inicializa recursos
    AuthService.initialize_session(st.session_state)
    if "_supabase" not in st.session_state:
        st.session_state._supabase = _init_supabase()

    user_id = AuthService.get_current_user_id(st.session_state)
    is_demo = AuthService.is_demo_mode(user_id)

    repo = SupabaseRepository()
    state = repo.load_state(user_id) or BehavioralState(user_id=user_id)
    events = repo.load_events(user_id, limit=100)

    # Calcula métricas
    patterns = BehavioralEngine.detect_patterns(events)
    risk_score = BehavioralEngine.calculate_risk_score(events)

    # Formulário de Check-in
    def handle_checkin(emotion, actions, reflection):
        new_state = process_checkin(repo, user_id, emotion, actions, reflection)
        # Atualiza estado local para re-render imediato
        for field in ["consistency_score", "current_streak", "risk_score"]:
            setattr(state, field, getattr(new_state, field))

    render_checkin_form(is_demo, handle_checkin)

    # Dashboard
    render_dashboard(state, patterns, risk_score)

    # Footer
    st.markdown("---")
    mode_label = "🧪 Demo" if is_demo else "🔐 Autenticado"
    st.caption(
        f"EmagreSim • {mode_label} • UTC: {datetime.now(DEFAULT_TZ).strftime('%H:%M')}"
    )


if __name__ == "__main__":
    main()