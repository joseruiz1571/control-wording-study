#!/usr/bin/env bun
// Scores a Jev jsonl with Phase-1 rules and pairs it against analysis/tables.json (Sonnet).
// Usage: bun second-assessor/score_jev.ts <jsonl> [--json out.json]
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";

const ROOT = join(import.meta.dir, "..");
const [file] = process.argv.slice(2);
const jsonOut = process.argv.includes("--json") ? process.argv[process.argv.indexOf("--json") + 1] : null;
const EXCLUDE = new Set(["SI-4.v1"]); // matches Phase 1: unreviewed rewrite, out of the flip denominator

const rows = readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((r) => r.ok);
const last = new Map<string, any>();
for (const r of rows) last.set(`${r.variant_id}|${r.replica}`, r);
const byVariant = new Map<string, any[]>();
for (const r of last.values()) (byVariant.get(r.variant_id) ?? byVariant.set(r.variant_id, []).get(r.variant_id)!).push(r);

const majority = (rs: any[]) => {
  const c: Record<string, number> = {};
  for (const r of rs) c[r.status] = (c[r.status] ?? 0) + 1;
  const top = Math.max(...Object.values(c));
  const tied = Object.keys(c).filter((k) => c[k] === top).sort();
  return { status: tied.length > 1 ? "split" : tied[0], unanimous: Object.keys(c).length === 1, counts: c };
};
const margin = (r: any) => { const p = Object.values(r.status_probabilities ?? {}).map(Number).sort((a, b) => b - a); return p.length > 1 ? p[0] - p[1] : null; };
const mean = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN);

const sonnet: any[] = JSON.parse(readFileSync(join(ROOT, "analysis/tables.json"), "utf8")).all_controls;
const controls: Record<string, any> = {};
for (const s of sonnet) {
  const vm: Record<string, any> = {};
  for (const v of ["v0", "v1", "v2", "v3", "v4"]) { const rs = byVariant.get(`${s.control_id}.${v}`); if (rs) vm[v] = majority(rs); }
  const scored = Object.entries(vm).filter(([v]) => !EXCLUDE.has(`${s.control_id}.${v}`)).map(([, m]) => (m as any).status);
  controls[s.control_id] = { vocab: s.vocab_pattern, vm, flip: new Set(scored).size > 1, sonnet: s.majority_by_variant, sonnetFlip: s.flips_5way };
}

const ids = Object.keys(controls);
const jf = ids.filter((k) => controls[k].flip), sf = ids.filter((k) => controls[k].sonnetFlip);
const census: Record<string, number> = {};
for (const r of last.values()) census[r.status] = (census[r.status] ?? 0) + 1;
const variants = [...byVariant.entries()];
const noisy = variants.filter(([, rs]) => !majority(rs).unanimous).map(([v]) => v).sort();

let agree = 0, cells = 0; const pairs: Record<string, number> = {};
for (const k of ids) for (const [v, m] of Object.entries(controls[k].vm) as any) {
  if (EXCLUDE.has(`${k}.${v}`)) continue;
  const s = controls[k].sonnet[v]; cells++; if (s === m.status) agree++;
  pairs[`${s} -> ${m.status}`] = (pairs[`${s} -> ${m.status}`] ?? 0) + 1;
}
const vocab: Record<string, [number, number]> = {};
for (const k of ids) { const e = (vocab[controls[k].vocab] ??= [0, 0]); e[0]++; if (controls[k].flip) e[1]++; }
const allIE = ids.filter((k) => Object.values(controls[k].vm).every((m: any) => m.status === "insufficient-evidence"));
const v0agree = ids.filter((k) => controls[k].vm.v0?.status === controls[k].sonnet.v0).length;

// single-replica X: score each replica index on its own
const reps = [...new Set([...last.values()].map((r) => r.replica))].sort();
const singleX = reps.map((rep) => ids.filter((k) => {
  const st = ["v0", "v1", "v2", "v3", "v4"].filter((v) => !EXCLUDE.has(`${k}.${v}`)).map((v) => last.get(`${k}.${v}|${rep}`)?.status);
  return new Set(st).size > 1;
}).length);

// probability margins: flipped vs stable controls, noisy vs unanimous variants
const flipSet = new Set(jf), noisySet = new Set(noisy);
const mFlip: number[] = [], mStable: number[] = [], mNoisy: number[] = [], mUnan: number[] = [];
for (const r of last.values()) { const m = margin(r); if (m == null) continue; (flipSet.has(r.control_id) ? mFlip : mStable).push(m); (noisySet.has(r.variant_id) ? mNoisy : mUnan).push(m); }
// per-control mean margin, to see whether low margin flags flippers (rank of flipped controls)
const ctrlMargin = ids.map((k) => ({ k, m: mean([...last.values()].filter((r) => r.control_id === k).map((r) => margin(r)!).filter((x) => x != null)), flip: controls[k].flip })).sort((a, b) => a.m - b.m);

const out = {
  file, sha256: createHash("sha256").update(readFileSync(file)).digest("hex"),
  n_ok: last.size, models: [...new Set([...last.values()].map((r) => r.response_model ?? r.jev_model_version))],
  X: `${jf.length}/${ids.length}`, jev_flips: jf, sonnet_flips: sf, overlap: jf.filter((k) => sf.includes(k)),
  noise: `${noisy.length}/${variants.length}`, noisy, census,
  single_replica_flips: singleX, cell_agreement: `${agree}/${cells}`, v0_agreement: `${v0agree}/${ids.length}`, pairs,
  vocab_flips: vocab, all_IE_controls: allIE.length,
  committed_cut: { controls: ids.length - allIE.length, jev_flips: jf.filter((k) => !allIE.includes(k)).length, sonnet_flips_same_set: sf.filter((k) => !allIE.includes(k)).length },
  margin: { flipped_controls: mean(mFlip), stable_controls: mean(mStable), noisy_variants: mean(mNoisy), unanimous_variants: mean(mUnan) },
  lowest_margin_controls: ctrlMargin.slice(0, 12).map((c) => `${c.k} ${c.m.toFixed(2)}${c.flip ? " FLIP" : ""}`),
  table: Object.fromEntries(ids.map((k) => [k, { jev: Object.fromEntries(Object.entries(controls[k].vm).map(([v, m]: any) => [v, m.status])), sonnet: controls[k].sonnet, flip: controls[k].flip, sonnetFlip: controls[k].sonnetFlip }])),
};
if (jsonOut) writeFileSync(jsonOut, JSON.stringify(out, null, 2));
const { table, ...summary } = out;
console.log(JSON.stringify(summary, null, 2));
