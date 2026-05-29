# services/storage.py
import sqlite3
import json
from typing import Optional, List
from pathlib import Path
from models.state import AppState, Meal, EmotionEntry, WeightEntry, PointLog

DB_PATH = Path(__file__).parent.parent / "emagresim.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                calories INTEGER NOT NULL,
                has_photo INTEGER DEFAULT 0,
                time TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emotion TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                reflection TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS points_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                points INTEGER NOT NULL,
                source TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)


def save_state(state: AppState) -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM meals")
            conn.execute("DELETE FROM emotions")
            conn.execute("DELETE FROM weights")
            conn.execute("DELETE FROM points_log")

            for meal in state.meals_history:
                conn.execute(
                    "INSERT INTO meals (date, type, description, calories, has_photo, time) VALUES (?,?,?,?,?,?)",
                    (meal.date, meal.type, meal.description, meal.calories, 1 if meal.has_photo else 0, meal.time)
                )

            for emo in state.emotion_history:
                conn.execute(
                    "INSERT INTO emotions (emotion, timestamp, reflection) VALUES (?,?,?)",
                    (emo.emotion, emo.timestamp, emo.reflection)
                )

            for w in state.weight_history:
                conn.execute(
                    "INSERT INTO weights (weight, date) VALUES (?,?)",
                    (w.weight, w.date)
                )

            for p in state.points_log:
                conn.execute(
                    "INSERT INTO points_log (points, source, date) VALUES (?,?,?)",
                    (p.points, p.source, p.date)
                )

            state_dict = {
                "nome": state.nome, "sexo": state.sexo, "idade": state.idade,
                "altura": state.altura, "objetivo": state.objetivo, "nivel_atividade": state.nivel_atividade,
                "peso_atual": state.peso_atual, "peso_meta": state.peso_meta, "peso_inicio": state.peso_inicio,
                "total_points": state.total_points, "streak": state.streak, "longest_streak": state.longest_streak,
                "total_checkins": state.total_checkins, "last_checkin": state.last_checkin or "",
                "is_premium": state.is_premium
            }
            conn.execute(
                "INSERT OR REPLACE INTO app_state (key, value) VALUES (?,?)",
                ("state", json.dumps(state_dict))
            )
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False


def load_state() -> Optional[AppState]:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT value FROM app_state WHERE key = 'state'")
            row = cursor.fetchone()
            if not row:
                return None

            state_dict = json.loads(row[0])

            meals = []
            for row in conn.execute("SELECT date, type, description, calories, has_photo, time FROM meals ORDER BY id"):
                meals.append(Meal(
                    date=row[0], type=row[1], description=row[2],
                    calories=row[3], has_photo=bool(row[4]), time=row[5]
                ))

            emotions = []
            for row in conn.execute("SELECT emotion, timestamp, reflection FROM emotions ORDER BY id"):
                emotions.append(EmotionEntry(emotion=row[0], timestamp=row[1], reflection=row[2] or ""))

            weights = []
            for row in conn.execute("SELECT weight, date FROM weights ORDER BY id"):
                weights.append(WeightEntry(weight=row[0], date=row[1]))

            points_log = []
            for row in conn.execute("SELECT points, source, date FROM points_log ORDER BY id"):
                points_log.append(PointLog(points=row[0], source=row[1], date=row[2]))

            return AppState(
                nome=state_dict.get("nome", "Atleta"),
                sexo=state_dict.get("sexo", "M"),
                idade=state_dict.get("idade", 28),
                altura=state_dict.get("altura", 1.72),
                objetivo=state_dict.get("objetivo", "emagrecer"),
                nivel_atividade=state_dict.get("nivel_atividade", "moderado"),
                peso_atual=state_dict.get("peso_atual", 82.0),
                peso_meta=state_dict.get("peso_meta", 72.0),
                peso_inicio=state_dict.get("peso_inicio", 82.0),
                total_points=state_dict.get("total_points", 0),
                streak=state_dict.get("streak", 0),
                longest_streak=state_dict.get("longest_streak", 0),
                total_checkins=state_dict.get("total_checkins", 0),
                last_checkin=state_dict.get("last_checkin") or None,
                is_premium=state_dict.get("is_premium", False),
                meals_history=meals,
                emotion_history=emotions,
                weight_history=weights,
                points_log=points_log,
            )
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        return None
