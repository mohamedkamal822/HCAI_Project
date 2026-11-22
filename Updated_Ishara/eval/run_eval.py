"""
CoMind evaluation harness.

Runs every prompt in eval/test_set.csv through the real FastAPI backend,
saves the outputs and traces, and computes the metrics from the project plan.

    cd eval
    python run_eval.py                 # in-process (FastAPI TestClient)
    python run_eval.py --url http://127.0.0.1:8000   # against a running server

Outputs: eval/outputs/run_<time>.jsonl and eval/outputs/summary_<time>.json
"""

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
BACKEND = EVAL_DIR.parent / "backend"
sys.path.insert(0, str(BACKEND))


def make_client(url):
    if url:
        import httpx
        return httpx.Client(base_url=url, timeout=30)
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app)


def run_case(client, row):
    exact = row["exact_only"] == "1"
    t0 = time.perf_counter()
    if row["mode"] == "error":
        r = client.post("/chat", json={"message": "Doctor", "simulate_error": True})
    elif row["mode"] == "alternatives":
        first = client.post("/chat", json={"message": "brother"}).json()
        r = client.post("/alternatives", json={"trace_id": first["trace_id"]})
    else:
        r = client.post("/chat", json={"message": row["Prompt"], "exact_only": exact})
    ms = (time.perf_counter() - t0) * 1000
    return r.json(), ms


def recompute_ok(engine, row, data):
    """O4: recompute the decision from the index and compare it with the trace."""
    if row["mode"] != "chat":
        return None
    again = engine.decide(row["Prompt"], exact_only=row["exact_only"] == "1")
    t = data["trace"]
    same_rule = again["rule"] == t["rule"]
    same_entries = [x["id"] for x in again["results"]] == [x["id"] for x in t["results"]]
    same_scores = [c.get("score") for c in again["candidates"]] == [c.get("score") for c in t["candidates"]]
    return same_rule and same_entries and same_scores


def reply_matches_trace(data):
    """O4 (reply side): every result label named in the trace appears in the reply or card, and no video
    is returned unless the trace has a result."""
    t = data["trace"]
    if data["rule"] in ("R1", "R2"):
        r0 = t["results"][0]
        return (r0["arabic"] in data["reply"] or r0["english"] in data["reply"]) and bool(data["results"])
    if data["rule"] in ("R4", "R5", "R7", "R0", "R6"):
        return not data["results"]
    return bool(data["results"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=None)
    args = ap.parse_args()

    from engine import Engine
    engine = Engine()
    client = make_client(args.url)

    rows = list(csv.DictReader(open(EVAL_DIR / "test_set.csv", encoding="utf-8")))
    out_dir = EVAL_DIR / "outputs"
    out_dir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    results = []

    for row in rows:
        data, ms = run_case(client, row)
        got_rule = data["rule"]
        got_entry = data["results"][0]["id"] if data.get("results") else ""
        rule_ok = got_rule == row["expected_rule"]
        entry_ok = (row["expected_entry"] == "" and (got_rule not in ("R1", "R2"))) or got_entry == row["expected_entry"]
        if row["mode"] == "alternatives":
            entry_ok = got_entry != "akhoia"
        rec = {
            "id": row["ID"], "prompt": row["Prompt"], "type": row["Type"], "persona": row["Persona"],
            "tests_principle": row["Tests principle?"], "expected_rule": row["expected_rule"],
            "expected_entry": row["expected_entry"], "got_rule": got_rule, "got_entry": got_entry,
            "pass": rule_ok and entry_ok, "reply": data["reply"], "reply_source": data["trace"].get("reply_source"),
            "trace_id": data["trace_id"], "ms": round(ms, 1),
            "recompute_ok": recompute_ok(engine, row, data), "reply_matches_trace": reply_matches_trace(data),
            "pair": row["pair"], "trace": data["trace"],
        }
        results.append(rec)
        print(f'{rec["id"]:4} {"PASS" if rec["pass"] else "FAIL"}  {got_rule:3} {got_entry:14} {row["Prompt"][:40]}')

    with open(out_dir / f"run_{stamp}.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def pct(xs):
        xs = list(xs)
        return round(100 * sum(xs) / len(xs), 1) if xs else None

    normal_exact = [r for r in results if r["type"] == "normal" and r["expected_rule"] in ("R1", "R2")]
    nomatch_scope = [r for r in results if r["expected_rule"] in ("R4", "R5")]
    unsafe = [r for r in results if r["type"] == "unsafe"]
    pairs = {}
    for r in results:
        if r["pair"]:
            pairs.setdefault(r["pair"], []).append(r["got_entry"] or r["got_rule"])
    times = [r["ms"] for r in results]
    summary = {
        "run": stamp,
        "prompts": len(results),
        "overall_pass_rate_%": pct(r["pass"] for r in results),
        "O1_exact_match_accuracy_%": pct(r["pass"] for r in normal_exact),
        "O3_no_match_and_out_of_scope_handling_%": pct(r["pass"] for r in nomatch_scope),
        "safe_handling_rate_unsafe_%": pct(r["pass"] for r in unsafe),
        "O4_trace_recomputation_match_%": pct(r["recompute_ok"] for r in results if r["recompute_ok"] is not None),
        "O4_reply_agrees_with_trace_%": pct(r["reply_matches_trace"] for r in results),
        "O11_language_parity_pairs_%": pct(len(set(v)) == 1 for v in pairs.values()),
        "model_replies_used": sum(r["reply_source"] == "model" for r in results),
        "response_time_ms_avg": round(statistics.mean(times), 1),
        "response_time_ms_max": round(max(times), 1),
        "by_type_pass_%": {t: pct(r["pass"] for r in results if r["type"] == t)
                           for t in ("normal", "edge case", "out of scope", "unsafe")},
        "failures": [r["id"] for r in results if not r["pass"]],
    }
    json.dump(summary, open(out_dir / f"summary_{stamp}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
