# Education Consulting Wiki — Schema

## Purpose

KB for education consulting: course strategy, admissions cases, learning
frameworks. Output supports (a) client conversations, (b) course material
drafts, (c) a downstream consulting-agent.

## Page types (seed taxonomy)

- `entities/students/<handle>.md` — ANONYMIZED handle only. Required sections:
  Background · Goals · Constraints · Plan · Updates (chronological).
- `entities/schools/<slug>.md` — schools, universities, programs.
- `entities/programs/<slug>.md` — specific degree/certificate tracks.
- `entities/career-paths/<slug>.md` — target outcome trajectories.
- `concepts/<slug>.md` — admissions strategy, learning theory, etc.
- `cases/<slug>.md` — composite/anonymized journeys. Required sections:
  Setup · Challenge · Intervention · Outcome · Lessons.

## PII rule (CRITICAL)

- Real names live in `raw/` (immutable, never indexed).
- Wiki entity pages use anonymized handles: `student-S2026-01`,
  `student-S2026-02`, etc.
- Mapping (real name → handle) is kept in a single private file
  `raw/_PRIVATE_handle-map.md` (gitignored, never committed).
- Lint regex check: flag any wiki/ page containing a real-name pattern
  not in an allowlist of public figures.

## Citation rules

- Same as root: `[source-id]` for raw, `[[...]]` for cross-links.
- Anonymize quotes from student conversations.

## Lint specifics

- Real-name leak check (highest severity).
- Cases with `status: open` and `updated:` > 60 days → flag for follow-up.
