import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any


class AuthSessionStore:
    """Simple SQLite-backed store for active auth sessions."""

    def __init__(self, db_path: str = "auth_sessions.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        # Use check_same_thread=False to allow usage across FastAPI worker threads
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS active_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    user_name TEXT NOT NULL,
                    role TEXT,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create_session(self, session_id: str, user_email: str, user_name: str, role: str) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO active_sessions (
                    session_id, user_email, user_name, role, created_at, last_activity
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, user_email, user_name, role, now, now),
            )
            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT session_id, user_email, user_name, role, created_at, last_activity FROM active_sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "session_id": row[0],
                "user_email": row[1],
                "user_name": row[2],
                "role": row[3],
                "created_at": row[4],
                "last_activity": row[5],
            }

    def touch(self, session_id: str) -> None:
        now = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                "UPDATE active_sessions SET last_activity = ? WHERE session_id = ?",
                (now, session_id),
            )
            conn.commit()

    def delete(self, session_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM active_sessions WHERE session_id = ?",
                (session_id,),
            )
            conn.commit()

    def list_sessions(self) -> list:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT session_id, user_email, user_name, role, created_at, last_activity FROM active_sessions ORDER BY last_activity DESC"
            )
            rows = cur.fetchall()
            return [
                {
                    "session_id": r[0],
                    "user_email": r[1],
                    "user_name": r[2],
                    "role": r[3],
                    "created_at": r[4],
                    "last_activity": r[5],
                }
                for r in rows
            ] 