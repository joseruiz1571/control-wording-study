#!/usr/bin/env python3
"""Phase 5 runner: rewritten variants (allowlist) × 3 replicas, temperature 0, resume-safe.

Does not modify the frozen evidence file. Does not push. Stop-and-report
is the parent's job at $40; this script logs failures and continues after
one retry. Exit 2 if ANTHROPIC_API_KEY is missing.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Study repo root (this file lives in runs/).
ROOT = Path(__file__).resolve().parents[1]
# Local mlassure checkout: MLASSURE_ROOT env, else sibling ../src/mlassure lab layout.
MLASSURE = Path(
    os.environ.get("MLASSURE_ROOT", str(ROOT.parent / "src" / "mlassure"))
).expanduser().resolve()
TARGET = ROOT / "evidence" / "model-stale.json"
YAML_DIR = ROOT / "controls" / "yaml_rewritten"
RAW = ROOT / "runs" / "raw"
JSONL = ROOT / "runs" / "phase5.jsonl"
STATE = ROOT / "runs" / "phase5_state.json"
MODEL = "claude-sonnet-4-6"
TEMP = "0"
REPLICAS = 3

RAW.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    env_path = MLASSURE / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)


def load_state() -> dict:
    if STATE.is_file():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"completed": [], "failed": [], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def append_jsonl(obj: dict) -> None:
    with JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def run_one(variant_id: str, replica: int) -> dict:
    report_path = RAW / f"{variant_id}-r{replica:02d}.json"
    yaml_path = YAML_DIR / f"{variant_id}.yaml"
    cmd = [
        "bun",
        "run",
        "src/cli/index.ts",
        "assess",
        "--controls",
        str(yaml_path),
        "--target",
        str(TARGET),
        "--live",
        "--temperature",
        TEMP,
        "--model",
        MODEL,
        "--report",
        str(report_path),
    ]
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(MLASSURE),
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    elapsed = round(time.time() - started, 3)
    record = {
        "variant_id": variant_id,
        "replica": replica,
        "model": MODEL,
        "temperature": 0,
        "returncode": proc.returncode,
        "elapsed_s": elapsed,
        "report_path": str(report_path) if proc.returncode == 0 else None,
        "stderr_tail": (proc.stderr or "")[-2000:],
        "stdout_tail": (proc.stdout or "")[-2000:],
    }
    if proc.returncode == 0 and report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        results = report.get("results") or []
        result = results[0] if results else {}
        judgment = result.get("judgment") or {}
        record.update(
            {
                "control_id": result.get("controlId"),
                "control_text": result.get("controlIntent"),
                "verdict": judgment.get("status"),
                "confidence": judgment.get("confidence"),
                "rationale": judgment.get("rationale"),
                "evidence_cited": judgment.get("evidenceCited"),
                "retrieved_evidence": result.get("retrievedEvidence"),
                "llm_model": report.get("llmModel"),
                "llm_temperature": report.get("llmTemperature"),
                "run_at": report.get("runAt"),
            }
        )
    return record


def main() -> int:
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY missing. Set it in the environment or in a local mlassure/.env (MLASSURE_ROOT).", file=sys.stderr)
        return 2
    allow_path = ROOT / "runs" / "phase5_allowlist.json"
    allow = set(json.loads(allow_path.read_text(encoding="utf-8")))
    yamls = sorted(p for p in YAML_DIR.glob("*.yaml") if p.stem in allow)
    if len(yamls) != len(allow):
        print(f"allowlist {len(allow)} yaml {len(yamls)}", file=sys.stderr)
        return 1
    state = load_state()
    done = set(state.get("completed") or [])
    total = len(yamls) * REPLICAS
    n = 0
    for y in yamls:
        variant_id = y.stem
        for replica in range(1, REPLICAS + 1):
            key = f"{variant_id}-r{replica:02d}"
            n += 1
            if key in done:
                continue
            print(f"[{n}/{total}] {key}", flush=True)
            record = run_one(variant_id, replica)
            if record["returncode"] != 0:
                blob = (record.get("stderr_tail") or "") + (record.get("stdout_tail") or "")
                if "credit balance is too low" in blob:
                    append_jsonl(record)
                    state.setdefault("failed", []).append(key)
                    save_state(state)
                    print("ABORT: Anthropic credit balance too low. Not retrying the remaining queue.", flush=True)
                    return 3
                print(f"  retry once: {key} rc={record['returncode']}", flush=True)
                record = run_one(variant_id, replica)
                record["retried"] = True
            if record["returncode"] != 0:
                record["failed"] = True
                state.setdefault("failed", []).append(key)
                print(f"  FAILED {key}", flush=True)
            else:
                done.add(key)
                state["completed"] = sorted(done)
            append_jsonl(record)
            save_state(state)
    print(f"done. completed={len(state['completed'])} failed={len(state.get('failed') or [])}")
    return 0 if not state.get("failed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
