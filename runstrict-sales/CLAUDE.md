# RunStrict Sales Wiki — Schema

## Purpose

Sales and growth strategy for the RunStrict mobile app. Output supports
(a) pitch decks / partnership conversations, (b) growth experiments,
(c) channel planning, (d) a downstream sales-strategist agent.

## Page types (seed taxonomy)

- `entities/icps/<slug>.md` — ideal customer profiles. Sections:
  Profile · Jobs-to-be-done · Buying criteria · Anti-patterns.
- `entities/channels/<slug>.md` — App Store, Google Play, IG, YouTube,
  influencers, partnerships. Sections:
  Mechanics · CAC range · Examples · Status.
- `entities/competitors/<slug>.md` — direct + adjacent. Sections:
  Positioning · Pricing · Strengths · Weaknesses · Last reviewed.
- `entities/objections/<slug>.md` — common objections + responses.
- `concepts/<slug>.md` — sales/growth frameworks: SPIN, JTBD, MEDDIC,
  growth loops, retention curves, viral coefficients, etc.
- `plays/<slug>.md` — concrete playbooks. Required sections:
  Goal · ICP · Channel · Hook · Sequence · Result · Status.
  `status: hypothesis | running | won | killed`.

## Citation rules

- Same as root.
- For internal data (RunStrict analytics, app store metrics), cite the
  dashboard/report by date: `[runstrict-ga-2026-05]`.

## Lint specifics

- Plays with `status: running` and `updated:` > 14 days → flag (sales
  cycles are short; running plays should move fast).
- Killed plays → confirm postmortem section exists.
