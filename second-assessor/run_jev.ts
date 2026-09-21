#!/usr/bin/env bun
// Second assessor (v2 serializer): Jev as a parallel assessor over the same 40x5 control strings,
// with per-control evidence equal to what Sonnet retrieved in Phase 1.
// Usage: bun second-assessor/run_jev.ts --out second-assessor/runs/smoke.jsonl [--controls "AC-6(9),AC-2(7)"] [--replicas 5] [--dry]
import { readFileSync, existsSync, appendFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";

const ROOT = join(import.meta.dir, "..");
const API_URL = "https://api.typesafe.ai/v1/systemone";
const MODEL = "jev-latest";
const SPEND_STOP_USD = 2.0;
const USD_PER_INPUT_TOKEN = 0.1 / 1e6; // same estimate rule as the v1 run, for comparable spend figures
const CONCURRENCY = 4;

const args = process.argv.slice(2);
const flag = (n: string) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : undefined; };
const OUT = flag("--out") ?? "second-assessor/runs/full.jsonl";
const ONLY = flag("--controls")?.split(",").map((s) => s.trim());
const REPLICAS = Number(flag("--replicas") ?? 5);
const DRY = args.includes("--dry");

function apiKey(): string {
  const k = process.env.TYPESAFE_API_KEY;
  if (!k) throw new Error("Set TYPESAFE_API_KEY in the environment");
  return k.trim();
}

function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = []; let row: string[] = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true;
    else if (c === ",") { row.push(cell); cell = ""; }
    else if (c === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; }
    else if (c !== "\r") cell += c;
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  const [head, ...body] = rows;
  return body.filter((r) => r.length === head.length).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}

// Evidence per control = Phase-1 retrievedEvidence from <control>.v0-r01 (constant across all 600 Phase-1 runs).
function evidenceFor(controlId: string) {
  const raw = JSON.parse(readFileSync(join(ROOT, "runs/raw", `${controlId}.v0-r01.json`), "utf8"));
  const res = raw.results ? raw.results[0] : raw;
  const items = res.retrievedEvidence.map((e: any) => ({ id: e.id, source: e.source, sha256: e.sha256, payload: e.payload }));
  if (items.length === 0) {
    // getModelCard returned null to Sonnet's loop; make "collector ran, found nothing" visible.
    const payload = null;
    return [{ id: `${controlId}-model-card-null`, source: "sagemaker:model-card", sha256: createHash("sha256").update("null").digest("hex"), payload }];
  }
  return items;
}

const fixture = JSON.parse(readFileSync(join(ROOT, "evidence/model-stale.json"), "utf8"));
const EVIDENCE_SHA = readFileSync(join(ROOT, "evidence/HASH.txt"), "utf8").match(/[0-9a-f]{64}/)![0];

function buildRequest(v: Record<string, string>) {
  return {
    model: MODEL,
    state: {
      question_template_id: "cwvs-jev-v1",
      study: "control-wording-variance-study-phase2-jev-parallel",
      evidence_file_sha256: EVIDENCE_SHA,
      target_name: fixture.modelName,
      endpoint_name: fixture.endpointName,
      control_id: v.variant_id,
      framework: "SP 800-53 Rev 5",
      pattern: v.mlassure_pattern,
      collectors_declared: v.collectors.split("|").join(","),
      control_statement: v.control_text.trim(),
      evidence_snippet: evidenceFor(v.control_id),
      task: "Assess whether control_statement is met given only evidence_snippet for target_name/endpoint_name. Do not invent evidence ids. Choose the single best mlassure Judgment.status and confidence.",
      allowed_status: ["satisfied", "partially-satisfied", "not-satisfied", "not-applicable", "insufficient-evidence"],
      allowed_confidence: ["high", "medium", "low"],
    },
    questions: {
      status: {
        type: "choice",
        instructions: "Which mlassure Judgment.status best fits whether the control statement is met by the evidence_snippet alone?",
        criteria: {
          "satisfied": "Evidence fully meets the control statement.",
          "partially-satisfied": "Evidence partially meets the control; material gaps remain.",
          "not-satisfied": "Evidence shows the control statement is not met.",
          "not-applicable": "Control does not apply to this target/endpoint.",
          "insufficient-evidence": "Evidence_snippet is too thin to judge either way.",
        },
      },
      confidence: {
        type: "choice",
        instructions: "How confident is the status choice above?",
        criteria: {
          high: "Clear match between statement and evidence; little ambiguity.",
          medium: "Reasonable match with some residual uncertainty.",
          low: "Ambiguous; status is a weak best guess.",
        },
      },
    },
  };
}

const variants = parseCsv(readFileSync(join(ROOT, "controls/control_set.accepted.csv"), "utf8"))
  .filter((v) => !ONLY || ONLY.includes(v.control_id));

if (DRY) {
  const want = flag("--show") ?? variants[0].variant_id;
  console.log(JSON.stringify(buildRequest(variants.find((v) => v.variant_id === want)!), null, 2));
  process.exit(0);
}

mkdirSync(dirname(join(ROOT, OUT)), { recursive: true });
const outPath = join(ROOT, OUT);
const done = new Set<string>(); let spent = 0;
if (existsSync(outPath)) for (const l of readFileSync(outPath, "utf8").split("\n").filter(Boolean)) {
  const r = JSON.parse(l); if (r.ok) { done.add(`${r.variant_id}|${r.replica}`); spent += r.cost_usd_est ?? 0; }
}

const jobs: { v: Record<string, string>; replica: string }[] = [];
for (const v of variants) for (let i = 1; i <= REPLICAS; i++) {
  const replica = `r${String(i).padStart(2, "0")}`;
  if (!done.has(`${v.variant_id}|${replica}`)) jobs.push({ v, replica });
}
console.log(`variants=${variants.length} jobs=${jobs.length} already_done=${done.size} spent=$${spent.toFixed(4)}`);

const KEY = apiKey();
let stop = false, n = 0;
async function one(job: (typeof jobs)[number]) {
  const request = buildRequest(job.v);
  const t0 = performance.now();
  const row: any = {
    variant_id: job.v.variant_id, control_id: job.v.control_id, variant: job.v.variant, replica: job.replica,
    serializer: "v2-matched-evidence", access_path: "typesafe-direct", api_url: API_URL,
    ts: new Date().toISOString(), request,
  };
  try {
    const resp = await fetch(API_URL, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${KEY}` }, body: JSON.stringify(request) });
    row.http_status = resp.status;
    const body: any = await resp.json().catch(() => null);
    row.elapsed_s = +((performance.now() - t0) / 1000).toFixed(3);
    row.response = body;
    const ans = body?.answers?.status ?? body?.status;
    row.status = ans?.choice ?? null;
    row.status_probabilities = ans?.probabilities ?? null;
    row.status_choice_confidence = ans?.confidence ?? null;
    row.response_model = body?.model ?? body?.model_version ?? null;
    row.usage = body?.usage ?? null;
    row.ok = resp.ok && typeof row.status === "string" && request.state.allowed_status.includes(row.status);
    row.cost_usd_est = (row.usage?.input_tokens ?? 0) * USD_PER_INPUT_TOKEN;
  } catch (e: any) { row.ok = false; row.error = String(e?.message ?? e); }
  spent += row.cost_usd_est ?? 0; row.spent_usd_cum = spent;
  appendFileSync(outPath, JSON.stringify(row) + "\n");
  if (++n % 50 === 0) console.log(`${n}/${jobs.length} spent=$${spent.toFixed(4)}`);
  if (spent >= SPEND_STOP_USD) stop = true;
}
let idx = 0;
await Promise.all(Array.from({ length: CONCURRENCY }, async () => { while (!stop && idx < jobs.length) await one(jobs[idx++]); }));
console.log(`finished n=${n} spent=$${spent.toFixed(4)} stop_triggered=${stop}`);
