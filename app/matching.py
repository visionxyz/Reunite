"""Matching engine powered by EverMemOS Cloud API."""

import os
import re
import uuid
from evermemos import EverMemOS
from app.models import Entry, MatchResult
from app import database as db

_client: EverMemOS | None = None


def _get_client() -> EverMemOS | None:
    global _client
    if _client is None:
        api_key = os.getenv("EVERMEMOS_API_KEY")
        if api_key and api_key != "your-evermemos-api-key-here":
            _client = EverMemOS(api_key=api_key)
    return _client


def _entry_user_id(entry: Entry) -> str:
    """Each entry maps to a unique user_id in EverMemOS."""
    return f"reunite_{entry.id}"


def _entry_group_id(entry: Entry) -> str:
    return "parent_seeking" if entry.entry_type == "家寻宝贝" else "child_seeking"


def store_memory(entry: Entry) -> bool:
    """Store an entry's info as memories in EverMemOS Cloud."""
    client = _get_client()
    if not client or not entry.id:
        return False

    mem = client.v0.memories
    user_id = _entry_user_id(entry)
    group_id = _entry_group_id(entry)
    ts = entry.created_at or "2026-01-01T00:00:00+00:00"

    # Message 1: structured info
    parts = [
        f"寻亲类型：{entry.entry_type}",
        f"姓名：{entry.name}" if entry.name else None,
        f"性别：{entry.gender}" if entry.gender else None,
        f"出生日期：{entry.birth_date}" if entry.birth_date else None,
        f"失踪/离家时间：{entry.missing_date}" if entry.missing_date else None,
        f"地点：{entry.location}" if entry.location else None,
        f"体貌特征：{entry.physical_features}" if entry.physical_features else None,
    ]
    basic_info = "\n".join(p for p in parts if p)

    try:
        mem.add(
            message_id=f"entry_{entry.id}_info_{uuid.uuid4().hex[:8]}",
            create_time=ts,
            sender=user_id,
            sender_name=entry.name or "未知",
            group_id=group_id,
            content=basic_info,
        )

        # Message 2: detailed description (with flush to trigger extraction)
        if entry.description:
            mem.add(
                message_id=f"entry_{entry.id}_desc_{uuid.uuid4().hex[:8]}",
                create_time=ts,
                sender=user_id,
                sender_name=entry.name or "未知",
                group_id=group_id,
                content=f"详细描述：{entry.description}",
                flush=True,
            )
        return True
    except Exception as e:
        print(f"[EverMemOS] store error: {e}")
        return False


def store_chat_memory(entry: Entry, user_message: str) -> bool:
    """Store a user's chat message as an additional memory in EverMemOS."""
    client = _get_client()
    if not client or not entry.id:
        return False

    mem = client.v0.memories
    user_id = _entry_user_id(entry)
    group_id = _entry_group_id(entry)

    try:
        mem.add(
            message_id=f"chat_{entry.id}_{uuid.uuid4().hex[:8]}",
            create_time="2026-01-01T00:00:00+00:00",
            sender=user_id,
            sender_name=entry.name or "未知",
            group_id=group_id,
            content=f"用户补充回忆：{user_message}",
            flush=True,
        )
        return True
    except Exception as e:
        print(f"[EverMemOS] chat memory store error: {e}")
        return False


def find_matches(entry: Entry, top_k: int = 10) -> list[MatchResult]:
    """Find matching entries from the opposite side."""
    search_type = "宝贝寻家" if entry.entry_type == "家寻宝贝" else "家寻宝贝"
    candidates = db.get_all_entries(entry_type=search_type)
    if not candidates:
        return []

    query_text = entry.to_search_text()
    client = _get_client()

    if client:
        return _evermemos_match(client, candidates, query_text, top_k)
    else:
        return _keyword_match(candidates, query_text, top_k)


def _evermemos_match(
    client: EverMemOS,
    candidates: list[Entry],
    query_text: str,
    top_k: int,
) -> list[MatchResult]:
    """Hybrid: keyword similarity primary, EverMemOS rank as tiebreaker."""
    mem = client.v0.memories
    n = len(candidates)

    # Step 1: Get EverMemOS scores for all candidates via group search
    group_id = _entry_group_id(candidates[0])
    user_scores: dict[str, float] = {}
    try:
        response = mem.search(
            extra_query={
                "group_id": group_id,
                "query": query_text,
                "top_k": 200,
            }
        )
        if response.result and response.result.memories:
            for m in response.result.memories:
                uid = getattr(m, "user_id", None)
                score = getattr(m, "score", None)
                if uid and score is not None:
                    # Keep best score per user
                    user_scores[uid] = max(user_scores.get(uid, 0), score)
    except Exception as e:
        print(f"[EverMemOS] search error: {e}")

    # Step 2: Convert EverMemOS scores to ranks (rank-based normalization)
    emo_ranks: dict[str, int] = {}
    if user_scores:
        sorted_users = sorted(user_scores.keys(), key=lambda u: user_scores[u], reverse=True)
        for rank, uid in enumerate(sorted_users):
            emo_ranks[uid] = rank  # 0 = best

    # Step 3: Combine keyword + EverMemOS rank
    results: list[MatchResult] = []
    for candidate in candidates:
        uid = _entry_user_id(candidate)
        kw_score = _keyword_similarity(query_text, candidate.to_search_text())

        if uid in emo_ranks:
            # Rank-based score: best rank gets 1.0, worst gets ~0
            rank_score = 1.0 - emo_ranks[uid] / max(len(emo_ranks), 1)
            final = 0.85 * kw_score + 0.15 * rank_score
        else:
            final = kw_score * 0.85  # Small penalty for missing from EverMemOS

        results.append(MatchResult(entry=candidate, score=final))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def _keyword_match(
    candidates: list[Entry], query_text: str, top_k: int
) -> list[MatchResult]:
    """Fallback: keyword-based matching when EverMemOS is unavailable."""
    results = []
    for candidate in candidates:
        score = _keyword_similarity(query_text, candidate.to_search_text())
        results.append(MatchResult(entry=candidate, score=score))
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def _keyword_similarity(text_a: str, text_b: str) -> float:
    """Character-level n-gram overlap for Chinese text."""
    chars_a = re.findall(r"[\u4e00-\u9fff\w]+", text_a)
    chars_b = re.findall(r"[\u4e00-\u9fff\w]+", text_b)
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
