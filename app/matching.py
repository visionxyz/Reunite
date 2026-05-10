"""Matching engine powered by EverOS Cloud (v1 API)."""

import os
import re
import time
import uuid
from datetime import datetime
from everos import EverOS
from app.models import Entry, MatchResult, PARENT_SEEKING, CHILD_SEEKING
from app import database as db

_client: EverOS | None = None


def _get_client() -> EverOS | None:
    global _client
    if _client is None:
        api_key = os.getenv("EVERMEMOS_API_KEY")
        if api_key and api_key != "your-evermemos-api-key-here":
            _client = EverOS(api_key=api_key)
    return _client


def _entry_user_id(entry: Entry) -> str:
    """Each entry maps to a unique sender within its group."""
    return f"reunite_{entry.id}"


PARENT_GROUP = "reunite_parents_v2"
CHILD_GROUP = "reunite_children_v2"


def _entry_group_id(entry: Entry) -> str:
    return PARENT_GROUP if entry.entry_type == PARENT_SEEKING else CHILD_GROUP


def _ts_ms(entry: Entry | None = None) -> int:
    if entry and entry.created_at:
        try:
            return int(datetime.fromisoformat(entry.created_at).timestamp() * 1000)
        except Exception:
            pass
    return int(time.time() * 1000)


# Gender values are now stored canonically in English; no translation needed.


def _strip_around(s: str) -> str:
    """Drop a leading 'around'/'approx' (any case) so we can prefix our own."""
    return re.sub(r"^\s*(around|approx\.?|approximately)\s+", "", s, flags=re.I).strip()


def _strip_current_name_wrap(name: str) -> str:
    """Mock data wraps adoptive names as '(Current name: X)'. Unwrap to just X."""
    m = re.match(r"^\(Current name:\s*(.+?)\)\s*$", name, flags=re.I)
    return m.group(1) if m else name


def _clean(s: str) -> str:
    """Trim trailing whitespace and stray dots so our template can add its own."""
    return s.rstrip(" .。\t\n")


def _entry_to_english(entry: Entry) -> str:
    """Render an Entry as a single English paragraph for EverOS extraction."""
    lines: list[str] = []
    is_parent = entry.entry_type == PARENT_SEEKING

    name = _strip_current_name_wrap(entry.name) if entry.name else ""
    is_adoptive_name = bool(entry.name) and entry.name != name
    birth = _clean(_strip_around(entry.birth_date))
    missing = _clean(_strip_around(entry.missing_date))
    location = _clean(entry.location)
    features = _clean(entry.physical_features)
    description = _clean(entry.description)

    gender = entry.gender if entry.gender and entry.gender != "unknown" else None
    age_bits = []
    if gender:
        age_bits.append(gender)
    if birth:
        age_bits.append(f"born around {birth}")

    if is_parent:
        head = "Searching for a missing child"
        if name:
            head += f" named {name}"
        if age_bits:
            head += " (" + ", ".join(age_bits) + ")"
        if missing:
            head += f", last seen around {missing}"
        lines.append(head + ".")
        if location:
            lines.append(f"Last known location: {location}.")
        if features:
            lines.append(f"Distinguishing physical features: {features}.")
        if description:
            lines.append(f"Background: {description}.")
    else:
        head = "Person searching for their birth family"
        if name:
            label = "adoptive name" if is_adoptive_name else "current name"
            head += f" ({label}: {name})"
        if age_bits:
            head += ", " + ", ".join(age_bits)
        if missing:
            head += f", separated from family around {missing}"
        lines.append(head + ".")
        if location:
            lines.append(f"Place memory: {location}.")
        if features:
            lines.append(f"Physical features: {features}.")
        if description:
            lines.append(f"Memories: {description}.")

    return "\n".join(lines)


def _entry_to_message(entry: Entry) -> dict:
    return {
        "role": "user",
        "content": _entry_to_english(entry),
        "sender_id": _entry_user_id(entry),
        "sender_name": entry.name or "Unknown",
        "timestamp": _ts_ms(entry),
        "message_id": f"entry_{entry.id}_{uuid.uuid4().hex[:8]}",
    }


def store_memory(entry: Entry) -> bool:
    """Store a single entry and force boundary detection.

    EverOS's semantic boundary detector waits for a sliding-window topic
    shift before producing a MemCell. Since each entry is a single
    message, that shift never arrives on its own — so we explicitly
    flush() to make the extraction happen now.
    Use store_memories_batch() for bulk loads to avoid N flushes."""
    client = _get_client()
    if not client or not entry.id:
        return False
    gid = _entry_group_id(entry)
    try:
        client.v1.memories.group.add(group_id=gid, messages=[_entry_to_message(entry)])
        client.v1.memories.group.flush(group_id=gid)
        return True
    except Exception as e:
        print(f"[EverOS] store error: {e}")
        return False


def store_memories_batch(entries: list[Entry]) -> int:
    """Bulk-store entries: one add call per group with all messages packed in,
    then a single flush per group. Returns count successfully added."""
    client = _get_client()
    if not client or not entries:
        return 0

    by_group: dict[str, list[dict]] = {}
    for e in entries:
        if not e.id:
            continue
        by_group.setdefault(_entry_group_id(e), []).append(_entry_to_message(e))

    total = 0
    for group_id, messages in by_group.items():
        try:
            client.v1.memories.group.add(group_id=group_id, messages=messages)
            client.v1.memories.group.flush(group_id=group_id)
            total += len(messages)
        except Exception as ex:
            print(f"[EverOS] batch add error in {group_id}: {ex}")
    return total


def flush_group(group_id: str) -> bool:
    """Trigger episode extraction for a whole group. Call after a batch of
    store_memory() so all messages are processed together rather than racing."""
    client = _get_client()
    if not client:
        return False
    try:
        client.v1.memories.group.flush(group_id=group_id)
        return True
    except Exception as e:
        print(f"[EverOS] flush error: {e}")
        return False


def store_chat_memory(entry: Entry, user_message: str) -> bool:
    """Store a user's chat message as an additional group memory."""
    client = _get_client()
    if not client or not entry.id:
        return False

    user_id = _entry_user_id(entry)
    group_id = _entry_group_id(entry)

    try:
        client.v1.memories.group.add(
            group_id=group_id,
            messages=[{
                "role": "user",
                "content": f"Additional recalled memory: {user_message}",
                "sender_id": user_id,
                "sender_name": _strip_current_name_wrap(entry.name) if entry.name else "Unknown",
                "timestamp": _ts_ms(),
                "message_id": f"chat_{entry.id}_{uuid.uuid4().hex[:8]}",
            }],
        )
        client.v1.memories.group.flush(group_id=group_id)
        return True
    except Exception as e:
        print(f"[EverOS] chat memory store error: {e}")
        return False


def delete_memory(entry: Entry) -> bool:
    """Remove all memories for an entry (used before re-storing on update)."""
    client = _get_client()
    if not client or not entry.id:
        return False
    try:
        client.v1.memories.delete(
            group_id=_entry_group_id(entry),
            sender_id=_entry_user_id(entry),
        )
        return True
    except Exception as e:
        print(f"[EverOS] delete error: {e}")
        return False


DEFAULT_MIN_SCORE = 0.38  # Calibrated: GT matches score 0.39-0.47, distractors top1 ≤ 0.39
BIRTH_YEAR_TOLERANCE = 3  # Allow ±N years between parent and child birth_date


def _extract_year(s: str) -> int | None:
    """Pull a plausible 4-digit year out of free-form text like '2006-03',
    '2006 (approx)', 'Around 2007', 'born between 2004 and 2006'."""
    if not s:
        return None
    m = re.search(r"(19|20)\d{2}", s)
    return int(m.group()) if m else None


def _passes_hard_filter(query: Entry, candidate: Entry) -> bool:
    """Reject candidates that conflict with query on objective attributes."""
    # Gender: if both specified, must match exactly
    if query.gender and candidate.gender and query.gender != candidate.gender:
        return False
    # Birth year: if both specified, must be within tolerance
    qy, cy = _extract_year(query.birth_date), _extract_year(candidate.birth_date)
    if qy and cy and abs(qy - cy) > BIRTH_YEAR_TOLERANCE:
        return False
    return True


def _build_query_text(entry: Entry) -> str:
    """Compact, signal-dense query for semantic search.
    Drops noisy fields (type/name/gender/birth_date — handled as hard filters
    or irrelevant) and leads with the strongest evidence (physical features)."""
    parts = []
    if entry.physical_features:
        parts.append(entry.physical_features)
    if entry.location:
        parts.append(entry.location)
    if entry.description:
        parts.append(entry.description)
    if entry.missing_date:
        parts.append(f"around {entry.missing_date}")
    return "\n".join(parts)


def find_matches(
    entry: Entry,
    top_k: int = 10,
    min_score: float = DEFAULT_MIN_SCORE,
) -> list[MatchResult]:
    """Find matching entries from the opposite side.

    Pipeline: hard filter (gender, birth year) → compact semantic query →
    EverOS hybrid (or keyword fallback) → score threshold.
    Empty list = "no meaningful match" (search miss).
    """
    search_type = CHILD_SEEKING if entry.entry_type == PARENT_SEEKING else PARENT_SEEKING
    candidates = db.get_all_entries(entry_type=search_type)
    candidates = [c for c in candidates if _passes_hard_filter(entry, c)]
    if not candidates:
        return []

    client = _get_client()

    if client:
        results = _everos_match(client, candidates, entry, top_k)
    else:
        results = _keyword_match(candidates, _build_query_text(entry), top_k)

    return [r for r in results if r.score >= min_score]


def _search_scores(
    client: EverOS, group_id: str, query: str
) -> dict[str, float]:
    """Run one EverOS hybrid search and return {sender_id: best_score}."""
    out: dict[str, float] = {}
    if not query.strip():
        return out
    try:
        response = client.v1.memories.search(
            query=query,
            filters={"group_id": group_id},
            method="hybrid",
            top_k=100,
        )
        episodes = response.data.episodes if response.data else None
        if not episodes:
            return out
        for ep in episodes:
            if ep.score is None:
                continue
            senders: list[str] = []
            if ep.user_id:
                senders.append(ep.user_id)
            if ep.participants:
                senders.extend(ep.participants)
            for sid in set(senders):
                out[sid] = max(out.get(sid, 0), ep.score)
    except Exception as e:
        print(f"[EverOS] search error: {e}")
    return out


def _everos_match(
    client: EverOS,
    candidates: list[Entry],
    query: Entry,
    top_k: int,
) -> list[MatchResult]:
    """Multi-query EverOS scoring: separate searches for physical features,
    location, and description, weighted by signal strength."""
    group_id = _entry_group_id(candidates[0])

    # Three weighted sub-queries — strongest signal first
    feat_scores = _search_scores(client, group_id, query.physical_features) if query.physical_features else {}
    loc_scores  = _search_scores(client, group_id, query.location) if query.location else {}
    desc_query = "\n".join(p for p in [query.description, f"around {query.missing_date}" if query.missing_date else None] if p)
    desc_scores = _search_scores(client, group_id, desc_query) if desc_query else {}

    if not (feat_scores or loc_scores or desc_scores):
        # All EverOS searches empty/failed → keyword fallback
        return _keyword_match(candidates, _build_query_text(query), top_k)

    W_FEAT, W_LOC, W_DESC = 0.55, 0.20, 0.25
    all_uids = set(feat_scores) | set(loc_scores) | set(desc_scores)
    user_scores: dict[str, float] = {}
    for uid in all_uids:
        user_scores[uid] = (
            W_FEAT * feat_scores.get(uid, 0)
            + W_LOC  * loc_scores.get(uid, 0)
            + W_DESC * desc_scores.get(uid, 0)
        )

    min_everos = min(user_scores.values()) if user_scores else 0.0
    backstop_ceiling = max(min_everos - 0.01, 0.0)

    fallback_query = _build_query_text(query)
    results: list[MatchResult] = []
    for candidate in candidates:
        uid = _entry_user_id(candidate)
        if uid in user_scores:
            final = user_scores[uid]
        else:
            kw = _keyword_similarity(fallback_query, candidate.to_search_text())
            final = min(kw, backstop_ceiling) if user_scores else kw
        results.append(MatchResult(entry=candidate, score=final))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def _keyword_match(
    candidates: list[Entry], query_text: str, top_k: int
) -> list[MatchResult]:
    """Fallback: keyword-based matching when EverOS is unavailable."""
    results = []
    for candidate in candidates:
        score = _keyword_similarity(query_text, candidate.to_search_text())
        results.append(MatchResult(entry=candidate, score=score))
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def _keyword_similarity(text_a: str, text_b: str) -> float:
    """Character-level n-gram overlap for Chinese text."""
    chars_a = re.findall(r"[一-鿿\w]+", text_a)
    chars_b = re.findall(r"[一-鿿\w]+", text_b)
    words_a = set("".join(chars_a))
    words_b = set("".join(chars_b))
    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b
    char_sim = len(intersection) / len(union) if union else 0.0

    text_a_flat = "".join(chars_a)
    text_b_flat = "".join(chars_b)
    bigrams_a = set(text_a_flat[i : i + 2] for i in range(len(text_a_flat) - 1))
    bigrams_b = set(text_b_flat[i : i + 2] for i in range(len(text_b_flat) - 1))
    bigram_inter = bigrams_a & bigrams_b
    bigram_union = bigrams_a | bigrams_b
    bigram_sim = len(bigram_inter) / len(bigram_union) if bigram_union else 0.0

    return 0.4 * char_sim + 0.6 * bigram_sim
