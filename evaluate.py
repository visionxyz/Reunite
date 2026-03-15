"""Evaluation script: test matching accuracy against ground truth.

Usage:
    uv run python evaluate.py

Requires the app to be running (uv run python main.py).
"""

import requests
import sys
from app.mock_data import GROUND_TRUTH, PAIR_DIFFICULTY

API = "http://127.0.0.1:8000"


def main():
    # Fetch all entries
    entries = requests.get(f"{API}/api/entries").json()
    parents = [e for e in entries if e["entry_type"] == "家寻宝贝"]
    children = [e for e in entries if e["entry_type"] == "宝贝寻家"]

    # Sort by ID to match mock_data order
    parents.sort(key=lambda e: e["id"])
    children.sort(key=lambda e: e["id"])

    print(f"Total entries: {len(entries)} (Parents: {len(parents)}, Children: {len(children)})")
    print(f"Ground truth pairs: {len(GROUND_TRUTH)}")
    print("=" * 70)

    results = {"easy": [], "medium": [], "hard": []}
    all_results = []

    for parent_idx, child_idx in GROUND_TRUTH.items():
        parent = parents[parent_idx]
        child = children[child_idx]
        difficulty = PAIR_DIFFICULTY[parent_idx]

        # Get match results for this parent
        match_resp = requests.get(f"{API}/api/match/{parent['id']}").json()

        # Find where the correct child ranks
        correct_child_id = child["id"]
        rank = None
        score = 0.0
        for i, m in enumerate(match_resp):
            if m["entry"]["id"] == correct_child_id:
                rank = i + 1  # 1-based
                score = m["score"]
                break

        top1 = rank == 1
        top3 = rank is not None and rank <= 3
        top5 = rank is not None and rank <= 5

        result = {
            "pair": parent_idx,
            "difficulty": difficulty,
            "parent": parent["name"],
            "expected_child": child["name"][:30],
            "rank": rank,
            "score": score,
            "top1": top1,
            "top3": top3,
            "top5": top5,
            "top1_match": match_resp[0]["entry"]["name"][:30] if match_resp else "N/A",
            "top1_score": match_resp[0]["score"] if match_resp else 0,
        }
        results[difficulty].append(result)
        all_results.append(result)

        status = "HIT" if top1 else f"MISS (rank={rank})"
        print(f"[{difficulty:6s}] {parent['name']:20s} -> expected: {child['name'][:25]:25s} | {status:15s} | score={score:.2%} | top1: {match_resp[0]['entry']['name'][:25] if match_resp else 'N/A'} ({match_resp[0]['score']:.2%})")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for difficulty in ["easy", "medium", "hard"]:
        group = results[difficulty]
        n = len(group)
        if n == 0:
            continue
        t1 = sum(1 for r in group if r["top1"])
        t3 = sum(1 for r in group if r["top3"])
        t5 = sum(1 for r in group if r["top5"])
        avg_score = sum(r["score"] for r in group) / n
        print(f"  {difficulty:6s}: Top-1={t1}/{n} ({t1/n:.0%})  Top-3={t3}/{n} ({t3/n:.0%})  Top-5={t5}/{n} ({t5/n:.0%})  Avg Score={avg_score:.2%}")

    total = len(all_results)
    t1_all = sum(1 for r in all_results if r["top1"])
    t3_all = sum(1 for r in all_results if r["top3"])
    t5_all = sum(1 for r in all_results if r["top5"])
    avg_all = sum(r["score"] for r in all_results) / total
    print(f"  {'TOTAL':6s}: Top-1={t1_all}/{total} ({t1_all/total:.0%})  Top-3={t3_all}/{total} ({t3_all/total:.0%})  Top-5={t5_all}/{total} ({t5_all/total:.0%})  Avg Score={avg_all:.2%}")

    # Also test reverse direction: children finding parents
    print("\n" + "=" * 70)
    print("REVERSE DIRECTION: Children -> Parents")
    print("=" * 70)

    reverse_results = {"easy": [], "medium": [], "hard": []}
    all_reverse = []

    for parent_idx, child_idx in GROUND_TRUTH.items():
        parent = parents[parent_idx]
        child = children[child_idx]
        difficulty = PAIR_DIFFICULTY[parent_idx]

        match_resp = requests.get(f"{API}/api/match/{child['id']}").json()

        correct_parent_id = parent["id"]
        rank = None
        score = 0.0
        for i, m in enumerate(match_resp):
            if m["entry"]["id"] == correct_parent_id:
                rank = i + 1
                score = m["score"]
                break

        top1 = rank == 1
        top3 = rank is not None and rank <= 3
        top5 = rank is not None and rank <= 5

        result = {
            "pair": parent_idx,
            "difficulty": difficulty,
            "rank": rank,
            "score": score,
            "top1": top1,
            "top3": top3,
            "top5": top5,
        }
        reverse_results[difficulty].append(result)
        all_reverse.append(result)

        status = "HIT" if top1 else f"MISS (rank={rank})"
        print(f"[{difficulty:6s}] {child['name'][:25]:25s} -> expected: {parent['name']:20s} | {status:15s} | score={score:.2%}")

    print("\nREVERSE SUMMARY")
    print("-" * 70)
    for difficulty in ["easy", "medium", "hard"]:
        group = reverse_results[difficulty]
        n = len(group)
        if n == 0:
            continue
        t1 = sum(1 for r in group if r["top1"])
        t3 = sum(1 for r in group if r["top3"])
        t5 = sum(1 for r in group if r["top5"])
        avg_score = sum(r["score"] for r in group) / n
        print(f"  {difficulty:6s}: Top-1={t1}/{n} ({t1/n:.0%})  Top-3={t3}/{n} ({t3/n:.0%})  Top-5={t5}/{n} ({t5/n:.0%})  Avg Score={avg_score:.2%}")

    total = len(all_reverse)
    t1_all = sum(1 for r in all_reverse if r["top1"])
    t3_all = sum(1 for r in all_reverse if r["top3"])
    t5_all = sum(1 for r in all_reverse if r["top5"])
    avg_all = sum(r["score"] for r in all_reverse) / total
    print(f"  {'TOTAL':6s}: Top-1={t1_all}/{total} ({t1_all/total:.0%})  Top-3={t3_all}/{total} ({t3_all/total:.0%})  Top-5={t5_all}/{total} ({t5_all/total:.0%})  Avg Score={avg_all:.2%}")


if __name__ == "__main__":
    main()
