export const meta = {
    name: "almanac-audit",
    description:
        "Re-verify every almanac entry against the current tree (read-only; returns per-entry verdicts).",
    phases: [
        { title: "Verify", detail: "run each entry's verify line and judge the claim" },
    ],
};

// ---- Schema (hard-validated at the subagent boundary) ----------------------

const VERDICT_SCHEMA = {
    type: "object",
    additionalProperties: false,
    properties: {
        results: {
            type: "array",
            items: {
                type: "object",
                additionalProperties: false,
                properties: {
                    file: { type: "string" },
                    title: { type: "string" },
                    verdict: { enum: ["holds", "falsified", "unverifiable"] },
                    command: { type: "string" },
                    evidence: { type: "string" },
                    proposedAction: { type: "string" },
                },
                required: [
                    "file",
                    "title",
                    "verdict",
                    "command",
                    "evidence",
                    "proposedAction",
                ],
            },
        },
    },
    required: ["results"],
};

// ---- Input -----------------------------------------------------------------

const files = Array.isArray(args && args.files) ? args.files : [];
if (files.length === 0) return { error: "no entry files supplied", results: [] };

const BATCH_SIZE = 3;
const batches = [];
for (let i = 0; i < files.length; i += BATCH_SIZE) {
    batches.push(files.slice(i, i + BATCH_SIZE));
}

log(`Auditing ${files.length} entries in ${batches.length} batches`);

// ---- Verify (parallel batches of entries) ----------------------------------

const PROMPT = `Re-verify these almanac entries against the repository AS IT IS NOW. Each entry is a
recorded fact that future agents act on without re-deriving it, so your job is to find out
whether the claim is still true — not whether it reads plausibly.

For EACH file listed below:

1. Read the file. Its front matter carries a \`title\` (the claim) and usually a \`verify\`
   line (how to re-check it cheaply). The body states the consequence.
2. Run the \`verify\` line, or the closest faithful read-only equivalent if the command has
   drifted (a renamed path, a moved file, a flag that changed spelling). "Faithful" means
   it tests the same load-bearing detail the claim rests on — not merely the neighbourhood
   that detail lives in.
3. Compare the ACTUAL output against what the claim predicts, and assign a verdict:

   - "holds"        — you RAN a check and its output CONFIRMS the claim.
   - "falsified"    — you RAN a check and its output CONTRADICTS the claim.
   - "unverifiable" — you could not run a conclusive check: the command no longer works,
                      the path moved and no faithful equivalent exists, or verifying would
                      need credentials, network access, or production.

HARD RULES — these are not style preferences:

- "holds" REQUIRES positive evidence produced during THIS run. If you did not run
  something conclusive, the verdict is "unverifiable" — NEVER "holds". A confident reading
  of the entry's own prose is not evidence; the entry restating its claim proves nothing.
- Do NOT edit any file. Do NOT run any command that mutates state, writes to a database,
  installs, deploys, or reaches production. If verifying the claim would require that,
  return "unverifiable" and say so in \`evidence\`.
- If the verify line is BROKEN but the claim still looks true by other means, the verdict
  is "unverifiable" (not "falsified", and not "holds") — and \`proposedAction\` should
  repair the verify line so the entry becomes re-checkable again.
- An entry with NO verify line at all is "unverifiable" unless you can devise and run a
  conclusive read-only check yourself; \`proposedAction\` should then supply a verify line.

Return, per file:

- \`file\`           — the path exactly as given to you.
- \`title\`          — the entry's \`title\` front-matter value.
- \`verdict\`        — one of the three above.
- \`command\`        — EXACTLY what you ran (the literal command line). If you ran nothing,
                     say so plainly, e.g. "none — requires production access".
- \`evidence\`       — QUOTE THE ACTUAL OUTPUT. Not a summary, not a paraphrase, not your
                     interpretation of it. Trim long output, but what you include must be
                     verbatim. If there was no output, say "no output" and name the exit
                     status you observed.
- \`proposedAction\` — what a maintainer should do. For "holds": "none — claim confirmed;
                     eligible for a \`verified\` bump to today's date". Otherwise a concrete
                     edit ("delete the entry: the flag is now present"), a repaired verify
                     line, or what a human would need to check by hand.

Files to verify:
`;

const verdicts = await pipeline(batches, (batch, _original, i) =>
    agent(`${PROMPT}${batch.map((f) => `- ${f}`).join("\n")}`, {
        label: `verify:batch-${i + 1}`,
        phase: "Verify",
        schema: VERDICT_SCHEMA,
    })
);

// ---- Merge + account for every input file ----------------------------------

const results = verdicts.filter(Boolean).flatMap((r) => r.results || []);

// Match on basename: an agent may return an absolute or normalized path, and a
// `missing` warning that fires spuriously on every run is one nobody reads. Almanac
// filenames are unique by the one-fact-per-file rule, so basenames are safe keys.
const basename = (p) => String(p).split("/").pop();
const seen = new Set(results.map((r) => basename(r.file)));
const missing = files.filter((f) => !seen.has(basename(f)));

if (missing.length > 0) {
    log(
        `WARNING: ${missing.length} entr${missing.length === 1 ? "y" : "ies"} came back with no verdict — this is NOT a pass. Re-run these: ${missing.join(", ")}`
    );
}

const count = (v) => results.filter((r) => r.verdict === v).length;
const falsified = count("falsified");
const unverifiable = count("unverifiable");
const holds = count("holds");

log(
    `Verdicts: ${holds} holds, ${falsified} falsified, ${unverifiable} unverifiable (${results.length}/${files.length} entries returned)`
);

return {
    audited: files.length,
    returned: results.length,
    missing,
    falsified: results.filter((r) => r.verdict === "falsified"),
    unverifiable: results.filter((r) => r.verdict === "unverifiable"),
    holds: results.filter((r) => r.verdict === "holds"),
};
