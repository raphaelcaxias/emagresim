from __future__ import annotations
import hashlib
import random as _random_module
from datetime import datetime, timezone
from typing import Dict, List

from models.state import BehavioralState

DEFAULT_TZ = timezone.utc


class NarrativeEngine:
    @staticmethod
    def _seeded_choice(choices: List[str], seed_suffix: str) -> str:
        digest = hashlib.md5(f"42:{seed_suffix}".encode()).hexdigest()
        rng = _random_module.Random(int(digest[:8], 16))
        return rng.choice(choices)

    @classmethod
    def get_greeting(cls, state: BehavioralState, patterns: Dict) -> str:
        hour = datetime.now(DEFAULT_TZ).hour
        if hour < 12:
            period = "Bom dia"
        elif hour < 18:
            period = "Boa tarde"
        else:
            period = "Boa noite"

        mode_labels = {
            "normal": "🌿 Equilíbrio",
            "survival": "🛡️ Sobrevivência",
            "returning": "🔄 Reencontro",
            "stable": "⚓ Constância",
        }
        memory = ""
        return_data = patterns.get("return_pattern")
        if return_data and return_data.get("count", 0) >= 2:
            memory = " Você já voltou outras vezes — isso mostra resiliência."
        elif patterns.get("risky_hours"):
            hrs = ", ".join(f"{h}:00" for h in patterns["risky_hours"][:2])
            memory = f" Horários de atenção: {hrs}."

        label = mode_labels.get(state.psychological_mode, "Equilíbrio")
        return f"{period}. Modo {label}.{memory}"

    @classmethod
    def get_companion_message(cls, state: BehavioralState, risk_score: float, patterns: Dict) -> str:
        mode = state.psychological_mode
        if mode == "survival":
            return "Hoje o objetivo é só se manter presente. Nada além disso importa."
        if mode == "returning":
            return "Você voltou. Isso importa mais do que qualquer streak ou número."
        if risk_score > 70:
            return f"Você está há {state.current_streak} dias consistente. Cuidado com o cansaço emocional."
        if state.current_streak >= 7:
            return f"{state.current_streak} dias seguidos. Isso é presença real."
        if (patterns.get("return_pattern") or {}).get("count", 0) >= 1:
            return "Você já mostrou que consegue retornar. Confie no seu processo."
        return "Sua presença hoje já é um ato de cuidado. Um dia de cada vez."

    @classmethod
    def get_micro_goal(cls, mode: str, risk: float, patterns: Dict, seed_context: str = "microgoal") -> str:
        if mode == "survival":
            choices = ["Hoje só abra o app.", "Beba um copo d'água agora.", "Registre como você está se sentindo."]
        elif mode == "returning":
            choices = ["Registre uma refeição hoje.", "Não tente compensar o tempo perdido.", "Olhe para o que você já conquistou."]
        elif risk > 70:
            choices = ["Descanse. Amanhã será mais leve.", "Respire fundo três vezes antes de qualquer decisão."]
        elif patterns.get("risky_hours"):
            h = patterns["risky_hours"][0]
            choices = [f"Seu horário de atenção é às {h}:00. Programe um lembrete suave.", f"Às {h}:00, pause e respire antes de decidir."]
        else:
            choices = ["Registre seu estado emocional.", "Faça uma refeição consciente.", "Anote uma coisa que você fez bem hoje."]
        return cls._seeded_choice(choices, seed_context)