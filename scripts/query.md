# /query — Answer a question from the wiki

Triggered by: `/query <question>` or just a natural-language question while
in a domain context.

## Steps

1. **Confirm the domain.** If ambiguous, ask. Do NOT query across domains.
2. **Find candidate pages.** Search `<domain>/wiki/` by:
   - title / aliases matching the question's nouns
   - `tags:` matching
   - full-text grep for key terms

   Cap at ~10 candidates.
3. **Read the candidates.** Also follow `[[wikilinks]]` one hop deep.
4. **Synthesize the answer** with this structure:
   - **Direct answer** (1-3 sentences)
   - **Reasoning** with citations `[[page]]` or `[source-id]`
   - **Confidence**: high | medium | low | speculative
   - **Open questions** if any
   - **Source pages used** (list at the bottom)
5. **Offer `/file-answer`** at the end if the answer is non-trivial:
   > "이 답변을 wiki에 저장하시겠어요? /file-answer 로 page 로 promote 가능합니다."

## Confidence rules

- **high**: all claims cited, sources are recent (<6mo for finance, <12mo
  for education/sales), no contradictions among sources.
- **medium**: cited, but sources older OR one minor contradiction.
- **low**: gaps in citation OR significant contradiction OR sparse coverage.
- **speculative**: no direct source coverage; reasoning from concepts only.

## Never

- Pull facts from your training data without saying so explicitly.
- Cite a page you didn't actually read this turn.
- Cross domains.
