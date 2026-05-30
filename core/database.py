from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import streamlit as st
from supabase import create_client, Client

from models.state import BehavioralState

logger = logging.getLogger(__name__)
DEFAULT_TZ = timezone.utc


def _parse_metadata(raw) -> Dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse metadata: {raw[:60]}...")
    return {}


@st.cache_data(ttl=120)
def _cached_load_state(user_id: str, client_key: str) -> Optional[Dict]:
    if not st.session_state.get("_supabase"):
        return None
    result = (
        st.session_state._supabase.table("behavioral_state")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None


@st.cache_data(ttl=300)
def _cached_load_events(user_id: str, client_key: str, limit: int = 200) -> List[Dict]:
    if not st.session_state.get("_supabase"):
        return []
    result = (
        st.session_state._supabase.table("behavioral_events")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)        .execute()
    )
    events = [
        {
            "event_type": row["event_type"],
            "created_at_utc": row["created_at"],
            "metadata": _parse_metadata(row.get("metadata")),
        }
        for row in (result.data or [])
    ]
    return sorted(events, key=lambda x: x["created_at_utc"])


class SupabaseRepository:
    def __init__(self):
        self._client_key = hashlib.md5(
            (st.secrets.get("SUPABASE_URL", "demo") or "demo").encode()
        ).hexdigest()

    @property
    def _client(self) -> Optional[Client]:
        return st.session_state.get("_supabase")

    def load_state(self, user_id: str) -> Optional[BehavioralState]:
        if user_id == "demo-user" or not self._client:
            return None
        data = _cached_load_state(user_id, self._client_key)
        if not data:
            return None
        return BehavioralState(
            schema_version=data.get("schema_version", "1.0.0"),
            user_id=data["user_id"],
            consistency_score=data["consistency_score"],
            current_streak=data["current_streak"],
            longest_streak=data["longest_streak"],
            total_checkins=data["total_checkins"],
            last_checkin_utc=data.get("last_checkin_utc"),
            current_level=data["current_level"],
            unlocked_achievements=data.get("unlocked_achievements", []),
            psychological_mode=data.get("psychological_mode", "normal"),
            emotion_history=data.get("emotion_history", []),
            behavioral_memory=data.get("behavioral_memory", {}),
            risk_score=data.get("risk_score", 0.0),
            last_updated_utc=data.get("last_updated_utc", ""),
        )

    def load_events(self, user_id: str, limit: int = 200) -> List[Dict]:
        if user_id == "demo-user" or not self._client:
            return []
        return _cached_load_events(user_id, self._client_key, limit)
    def save_state(self, state: BehavioralState) -> bool:
        if state.user_id == "demo-user" or not self._client:
            return False
        try:
            state.last_updated_utc = datetime.now(DEFAULT_TZ).isoformat()
            self._client.table("behavioral_state").upsert(
                state.to_persist_dict(), on_conflict="user_id"
            ).execute()
            _cached_load_state.clear()
            _cached_load_events.clear()
            return True
        except Exception as e:
            logger.error(f"save_state failed: {e}")
            return False

    def log_event(self, user_id: str, event_type: str, metadata: Dict) -> bool:
        if user_id == "demo-user" or not self._client:
            return False
        try:
            self._client.table("behavioral_events").insert({
                "user_id": user_id,
                "event_type": event_type,
                "metadata": json.dumps(metadata, ensure_ascii=False),
                "created_at": datetime.now(DEFAULT_TZ).isoformat(),
            }).execute()
            _cached_load_events.clear()
            return True
        except Exception as e:
            logger.error(f"log_event failed: {e}")
            return False