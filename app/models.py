"""Data models for the Reunite app."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class EntryType(str, Enum):
    PARENT_SEEKING = "家寻宝贝"  # Parents looking for children
    CHILD_SEEKING = "宝贝寻家"  # Children/adults looking for family


class Gender(str, Enum):
    MALE = "男"
    FEMALE = "女"
    UNKNOWN = "未知"


@dataclass
class Entry:
    id: Optional[int] = None  # Internal SQLite PK; never exposed to clients
    public_id: str = ""  # Opaque random ID exposed in URLs, localStorage, etc.
    entry_type: str = ""  # EntryType value
    name: str = ""  # Name or alias
    gender: str = ""  # Gender value
    birth_date: str = ""  # Approximate birth date, e.g. "1995" or "1995-03"
    missing_date: str = ""  # When the child went missing
    location: str = ""  # Province/city of missing or remembered location
    physical_features: str = ""  # Birthmarks, scars, etc.
    description: str = ""  # Detailed narrative description
    contact: str = ""  # Contact info
    created_at: str = ""

    def to_search_text(self) -> str:
        """Combine all fields into a single text for embedding."""
        parts = [
            f"类型：{self.entry_type}",
            f"姓名：{self.name}" if self.name else "",
            f"性别：{self.gender}" if self.gender else "",
            f"出生日期：{self.birth_date}" if self.birth_date else "",
            f"失踪时间：{self.missing_date}" if self.missing_date else "",
            f"地点：{self.location}" if self.location else "",
            f"体貌特征：{self.physical_features}" if self.physical_features else "",
            f"详细描述：{self.description}" if self.description else "",
        ]
        return "\n".join(p for p in parts if p)

    def to_dict(self) -> dict:
        """Public dict — drops the internal integer id; clients use public_id."""
        d = asdict(self)
        d.pop("id", None)
        return d


@dataclass
class MatchResult:
    entry: Entry
    score: float  # 0-1 similarity score
