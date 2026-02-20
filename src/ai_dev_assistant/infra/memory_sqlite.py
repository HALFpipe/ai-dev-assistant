# infra/memory_sqlite.py

import json
import sqlite3
from typing import Optional

from ai_dev_assistant.rag.memory import ConversationState, turn_from_dict, turn_to_dict
from ai_dev_assistant.tools.defaults import get_memory_db_path


def _serialize_state(state: ConversationState) -> dict:
    return {
        "summary": state["summary"],
        "recent_turns": [turn_to_dict(t) for t in state["recent_turns"]],
    }


def _deserialize_state(raw: dict) -> ConversationState:
    return {
        "summary": raw.get("summary"),
        "recent_turns": [turn_from_dict(t) for t in raw.get("recent_turns", [])],
    }


def _get_conn() -> sqlite3.Connection:
    get_memory_db_path().parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(get_memory_db_path())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            state_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


def load_conversation(conversation_id: str) -> Optional[ConversationState]:
    conn = _get_conn()
    cur = conn.execute(
        "SELECT state_json FROM conversations WHERE conversation_id = ?",
        (conversation_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    raw = json.loads(row[0])
    return _deserialize_state(raw)


def save_conversation(
    conversation_id: str,
    state: ConversationState,
) -> None:
    conn = _get_conn()

    payload = _serialize_state(state)

    conn.execute(
        """
        INSERT INTO conversations (conversation_id, state_json)
        VALUES (?, ?)
        ON CONFLICT(conversation_id)
        DO UPDATE SET
            state_json = excluded.state_json,
            updated_at = CURRENT_TIMESTAMP
        """,
        (conversation_id, json.dumps(payload)),
    )
    conn.commit()
    conn.close()
