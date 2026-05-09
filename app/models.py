"""Data models for the Reunite app."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

# Canonical enum values stored in SQLite. All comparisons in matching.py,
# assistant.py, and the frontend reference these strings literally.
PARENT_SEEKING = "parent_seeking"   # parent looking for a missing child
CHILD_SEEKING = "child_seeking"     # child/adult looking for their birth family

GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDER_UNKNOWN = "unknown"


@dataclass
class Entry:
    id: Optional[int] = None  # Internal SQLite PK; never exposed to clients
    public_id: str = ""  # Opaque random ID exposed in URLs, localStorage, etc.
    entry_type: str = ""  # PARENT_SEEKING or CHILD_SEEKING
    name: str = ""  # Name or alias
    gender: str = ""  # GENDER_MALE / GENDER_FEMALE / GENDER_UNKNOWN
    birth_date: str = ""  # Approximate birth date, e.g. "1995" or "1995-03"
    missing_date: str = ""  # When the child went missing
    location: str = ""  # Province/city of missing or remembered location
    physical_features: str = ""  # Birthmarks, scars, etc.
    description: str = ""  # Detailed narrative description
    contact: str = ""  # Contact info
    created_at: str = ""

    def to_search_text(self) -> str:
        """Compact, label-free text for keyword similarity fallback.
        Skips fields that are noisy across parent/child wording (type, name,
        gender, birth_date — those are handled by the hard filter)."""
        parts = []
        if self.physical_features:
            parts.append(self.physical_features)
        if self.location:
            parts.append(self.location)
        if self.description:
            parts.append(self.description)
        if self.missing_date:
            parts.append(self.missing_date)
        return "\n".join(parts)

    def to_dict(self) -> dict:
        """Public dict — drops the internal integer id; clients use public_id."""
        d = asdict(self)
        d.pop("id", None)
        return d


@dataclass
class MatchResult:
    entry: Entry
    score: float  # 0-1 similarity score
