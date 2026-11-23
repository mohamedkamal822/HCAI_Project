"""Run the 40-prompt evaluation set against Ishara's FastAPI backend.

Usage: python run_evaluation.py [--url http://127.0.0.1:8000]
Without --url, FastAPI TestClient is used. Reports go to evaluation_outputs/.
"""
import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent


def make_client(url):
    if url:
        import httpx
        return httpx.Client(base_url=url, timeout=30)
    from fastapi.testclient import TestClient
    # Support running this file from either the project root or backend/.
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))
    from backend.main import app
    return TestClient(app)


def run_case(client, row):
    started = time.perf_counter()
    mode = row.get("mode", "chat")
    if mode == "error":
        response = client.post("/chat", json={"message": row["Prompt"], "simulate_error": True})
    elif mode == "alternatives":
        first = client.post("/chat", json={"message": row["Prompt"]}).json()
        response = client.post("/alternatives", json={"trace_id": first["trace_id"]})
    else:
        response = client.post("/chat", json={"message": row["Prompt"], "exact_only": row.get("exact_only") == "1"})
    return response.json(), (time.perf_counter() - started) * 1000


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--url")
    args = parser.parse_args()
    client = make_client(args.url)
    with (BACKEND_DIR / "evaluation_test_set.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    output_dir = BACKEND_DIR / "evaluation_outputs"
    output_dir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    results = []
    for row in rows:
        data, elapsed = run_case(client, row)
        trace = data.get("trace") or {}
        found = data.get("results") or []
        got_entry = found[0].get("id", "") if found else ""
        expected_rule, expected_entry = row.get("expected_rule", ""), row.get("expected_entry", "")
        rule_ok = data.get("rule") == expected_rule
        entry_ok = got_entry == expected_entry if expected_entry else data.get("rule") not in {"R1", "R2"}
        if row.get("mode") == "alternatives":
            entry_ok = bool(got_entry) and got_entry != expected_entry
        result = {
            "id": row.get("ID"), "prompt": row.get("Prompt"),
            "expected_rule": expected_rule, "got_rule": data.get("rule"),
            "expected_entry": expected_entry, "got_entry": got_entry,
            "pass": rule_ok and entry_ok, "reply_source": trace.get("reply_source"),
            "trace_id": data.get("trace_id"), "elapsed_ms": round(elapsed, 1), "trace": trace,
        }
        results.append(result)
        print(f'{result["id"]:4} {"PASS" if result["pass"] else "FAIL"}  {str(result["got_rule"]):3} {got_entry:16} {str(result["prompt"])[:40]}')
    with (output_dir / f"run_{stamp}.jsonl").open("w", encoding="utf-8") as target:
        for result in results:
            target.write(json.dumps(result, ensure_ascii=False) + "\n")
    elapsed = [item["elapsed_ms"] for item in results]
    summary = {
        "run": stamp, "prompts": len(results),
        "pass_rate_percent": round(100 * sum(item["pass"] for item in results) / len(results), 1) if results else None,
        "average_ms": round(statistics.mean(elapsed), 1) if elapsed else None,
        "max_ms": max(elapsed) if elapsed else None,
        "failures": [item["id"] for item in results if not item["pass"]],
    }
    (output_dir / f"summary_{stamp}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
