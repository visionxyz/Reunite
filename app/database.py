"""SQLite database for entries (local metadata only, memories stored in EverOS)."""

import os
import secrets
import sqlite3
import string
from pathlib import Path
from app.models import Entry

_PUBLIC_ID_ALPHA = string.ascii_letters + string.digits  # 62 chars
_PUBLIC_ID_LEN = 9  # ~53 bits entropy, ample for tens of thousands of entries


def _generate_public_id() -> str:
    """Opaque, non-sequential, URL-safe id like 'rnt_a8X3kp9Qe'."""
    return "rnt_" + "".join(secrets.choice(_PUBLIC_ID_ALPHA) for _ in range(_PUBLIC_ID_LEN))

# Use /tmp on Vercel (ephemeral), local data/ dir otherwise
if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/reunite.db")
else:
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
            public_id TEXT UNIQUE,
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
    # Migration: legacy Chinese enum values -> English canonical form.
    # No-op once converted; safe to run on every startup.
    conn.execute("UPDATE entries SET entry_type='parent_seeking' WHERE entry_type='家寻宝贝'")
    conn.execute("UPDATE entries SET entry_type='child_seeking'  WHERE entry_type='宝贝寻家'")
    conn.execute("UPDATE entries SET gender='male'    WHERE gender='男'")
    conn.execute("UPDATE entries SET gender='female'  WHERE gender='女'")
    conn.execute("UPDATE entries SET gender='unknown' WHERE gender='未知'")
    # Migration: pre-existing schemas may not have public_id; add it idempotently.
    cols = {row[1] for row in conn.execute("PRAGMA table_info(entries)").fetchall()}
    if "public_id" not in cols:
        conn.execute("ALTER TABLE entries ADD COLUMN public_id TEXT")
    # Backfill any rows missing a public_id
    rows = conn.execute(
        "SELECT id FROM entries WHERE public_id IS NULL OR public_id = ''"
    ).fetchall()
    for row in rows:
        # Retry on the (astronomically unlikely) collision
        for _ in range(5):
            try:
                conn.execute(
                    "UPDATE entries SET public_id = ? WHERE id = ?",
                    (_generate_public_id(), row[0]),
                )
                break
            except sqlite3.IntegrityError:
                continue
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_entries_public_id ON entries(public_id)"
    )
    # Background-matching results: per-owner queue of suggested matches.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_public_id TEXT NOT NULL,
            matched_public_id TEXT NOT NULL,
            score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(owner_public_id, matched_public_id)
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_suggestions_owner ON suggestions(owner_public_id)"
    )
    conn.commit()
    conn.close()


def insert_entry(entry: Entry) -> int:
    conn = get_db()
    public_id = entry.public_id or _generate_public_id()
    # Retry once on collision (extremely unlikely)
    for _ in range(5):
        try:
            cursor = conn.execute(
                """INSERT INTO entries (public_id, entry_type, name, gender, birth_date,
                   missing_date, location, physical_features, description, contact)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    public_id,
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
            break
        except sqlite3.IntegrityError:
            public_id = _generate_public_id()
    else:
        conn.close()
        raise RuntimeError("Failed to allocate a unique public_id after 5 retries")
    conn.commit()
    entry_id = cursor.lastrowid
    entry.id = entry_id
    entry.public_id = public_id
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
    """Internal lookup by integer PK. Use get_entry_by_public_id for client-facing paths."""
    conn = get_db()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return _row_to_entry(row) if row else None


def get_entry_by_public_id(public_id: str) -> Entry | None:
    if not public_id:
        return None
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM entries WHERE public_id = ?", (public_id,)
    ).fetchone()
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


def replace_suggestions(owner_public_id: str, results: list[tuple[str, float]]) -> None:
    """Replace the suggestion set for an owner with a fresh list of (public_id, score)."""
    conn = get_db()
    conn.execute("DELETE FROM suggestions WHERE owner_public_id = ?", (owner_public_id,))
    if results:
        conn.executemany(
            "INSERT INTO suggestions (owner_public_id, matched_public_id, score) VALUES (?, ?, ?)",
            [(owner_public_id, pid, score) for pid, score in results],
        )
    conn.commit()
    conn.close()


def get_suggestions(owner_public_id: str) -> list[tuple[Entry, float]]:
    """Load the latest stored suggestions for an owner, joined to candidate entries."""
    conn = get_db()
    rows = conn.execute(
        """SELECT e.*, s.score FROM suggestions s
           JOIN entries e ON e.public_id = s.matched_public_id
           WHERE s.owner_public_id = ?
           ORDER BY s.score DESC""",
        (owner_public_id,),
    ).fetchall()
    conn.close()
    out: list[tuple[Entry, float]] = []
    for r in rows:
        out.append((_row_to_entry(r), r["score"]))
    return out


def _row_to_entry(row: sqlite3.Row) -> Entry:
    return Entry(
        id=row["id"],
        public_id=row["public_id"] or "",
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
