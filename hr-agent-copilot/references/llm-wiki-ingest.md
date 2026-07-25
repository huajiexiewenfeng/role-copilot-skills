# HR JD Ingest Contract

Use this domain contract with `llm-wiki-ingest` when historical job
descriptions should become durable HR Wiki records. Phase 1 handles JD content
only.

## Evidence Gate

LLM extraction must select verbatim source ranges. For Codex tasks, preserve
`thread_id`, `turn_id`, `item_id`, `start`, `end`, and the original-message
checksum. Show the exact ranges and risk flags before asking for confirmation.

Do not import resumes, candidate facts, names, contact details, screening
scores, rankings, interview feedback, offers, rejections, or hiring outcomes.
A mixed message is skipped unless the user confirms a precise JD-only range.
The pattern scan is a guardrail, not a complete privacy guarantee.

## Identity

- `job_id` identifies the long-lived recruiting position. Propose it, but do
  not merge two positions without user confirmation.
- `jd_version_id` is generated only from confirmed verbatim JD evidence after
  Unicode NFC normalization, LF line endings, and outer trim.
- LLM summaries, extracted fields, and inferred structure never participate in
  `jd_version_id`.

## Products

`jd_version` is immutable and cites `source_id`. `job_profile` is the current
catalog entry and lists known `jd_version_id` values. In both Markdown records,
separate source-backed facts, interpretation, and unknowns. Never present an
inference as source text.

Write the immutable version first. Update `job_profile` only when it does not
already reference that version. Append `hr_jd_import` with the deterministic
event ID `hr-jd-import:{source_id}:{job_id}:{jd_version_id}`. Treat
`already_exists` as a successful retry and never overwrite the prior version.

All writes go through `llm-wiki-runtime`; fallback must not raw-write into
`.llm-wiki`.
