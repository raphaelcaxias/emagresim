from __future__ import annotations
import logging
from datetime import datetime, timezone

import streamlit as st
from supabase import create_client

from core.database import SupabaseRepository
from core.services import process_checkin, AuthService, load_user_state
from utils.analytics import BehavioralEngine
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

_APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; }
    [data-testid="stMetric"] {
        background: white; padding: 1.2rem; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center;
    }
    [data-testid="stMetricValue"] { color: #2d3436; font-weight: 700; font-size: 1.8rem; }
    [data-testid="stMetricLabel"] { color: #636e72; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
    .stButton > button {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white; border: none; border-radius: 10px; font-weight: 600; width: 100%;
    }
    .stInfo, .stSuccess { border-radius: 12px !important; }
</style>
"""
st.markdown(_APP_CSS, unsafe_allow_html=True)


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


def main() -> None:
    AuthService.initialize_session(st.session_state)

    if "_supabase" not in st.session_state:
        st.session_state._supabase = _init_supabase()

    user_id = AuthService.get_current_user_id(st.session_state)
    is_demo = AuthService.is_demo_mode(user_id)

    repo = SupabaseRepository()
    state = load_user_state(repo, user_id)
    events = repo.load_events(user_id, limit=100)

    patterns = BehavioralEngine.detect_patterns(events)
    risk_score = BehavioralEngine.calculate_risk_score(events)

    def handle_checkin(emotion, actions, reflection):
        new_state = process_checkin(repo, user_id, emotion, actions, reflection)
        state.consistency_score = new_state.consistency_score
        state.current_streak = new_state.current_streak
        state.risk_score = new_state.risk_score
        state.current_level = new_state.current_level
        state.unlocked_achievements = new_state.unlocked_achievements
        state.emotion_history = new_state.emotion_history
        state.psychological_mode = new_state.psychological_mode

    render_checkin_form(is_demo, handle_checkin)
    render_dashboard(state, patterns, risk_score)

    st.markdown("---")
    mode_label = "🧪 Demo" if is_demo else "🔐 Autenticado"
    st.caption(f"EmagreSim v33.0 • {mode_label} • UTC: {datetime.now(DEFAULT_TZ).strftime('%H:%M')}")


if __name__ == "__main__":
    main()