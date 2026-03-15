"""SQLite database for entries (local metadata only, memories stored in EverMemOS)."""

import sqlite3
from pathlib import Path
from app.models import Entry

DB_PATH = Path(__file__).parent.parent / "data" / "reunite.db"


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_type TEXT NOT NULL,
            name TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            birth_date TEXT DEFAULT '',
            missing_date TEXT DEFAULT '',
            location TEXT DEFAULT '',
            physical_features TEXT DEFAULT '',
            description TEXT DEFAULT '',
            contact TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def insert_entry(entry: Entry) -> int:
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO entries (entry_type, name, gender, birth_date, missing_date,
           location, physical_features, description, contact)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            entry.entry_type,
            entry.name,
            entry.gender,
            entry.birth_date,
            entry.missing_date,
            entry.location,
            entry.physical_features,
            entry.description,
            entry.contact,
        ),
    )
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()
    return entry_id


def get_all_entries(entry_type: str | None = None) -> list[Entry]:
    conn = get_db()
    if entry_type:
        rows = conn.execute(
            "SELECT * FROM entries WHERE entry_type = ? ORDER BY created_at DESC",
            (entry_type,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM entries ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [_row_to_entry(r) for r in rows]


def get_entry(entry_id: int) -> Entry | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return _row_to_entry(row) if row else None


def update_entry(entry_id: int, **fields) -> bool:
    """Update specific fields of an existing entry."""
    if not fields:
        return False
    allowed = {"name", "gender", "birth_date", "missing_date", "location",
               "physical_features", "description", "contact"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return False
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [entry_id]
    conn = get_db()
    conn.execute(f"UPDATE entries SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return True


def _row_to_entry(row: sqlite3.Row) -> Entry:
    return Entry(
        id=row["id"],
        entry_type=row["entry_type"],
        name=row["name"],
        gender=row["gender"],
        birth_date=row["birth_date"],
        missing_date=row["missing_date"],
        location=row["location"],
        physical_features=row["physical_features"],
        description=row["description"],
        contact=row["contact"],
        created_at=row["created_at"],
    )
