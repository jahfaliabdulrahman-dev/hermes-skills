# Measuring implementer performance across loop generations

How to judge whether a NEW session configuration (skills-at-birth, brief skill
map, per-step HOW map, fresh rotation) actually outperforms the previous ones.
Collected on CarSah 2026-08-09 (baseline: session 103806 — no --skills, skill
map landed mid-session; candidate: session 210102 — all additions at birth).

## Metrics (all recoverable from git + reviews + session DB)

| Metric | Source | Meaning |
|---|---|---|
| Rounds to APPROVE per step | `handoff/claude/*.md` verdicts per step | 1 = accepted first try; 2+ = fix cycles |
| NEW STOPs per first delivery | review text (count STOP-ids FIRST filed there, not references to older ones) | first-submission quality |
| Messages consumed per step | `SELECT count(*) FROM messages WHERE session_id=?` at step boundaries | efficiency / context budget |
| skill_view count | same DB, `tool_name='skill_view'` | loads the map vs blind code-search |
| HOW-map line in 18 | grep the backlog entry for files/pointer/pitfalls | the new method actually applied |
| Test growth | commit bodies / review evidence (e.g. 202→206→217) | regression coverage per step |

## Baseline collection (BEFORE the step lands)

```bash
# per-step delivery commits (code → APPROVE) with timestamps
git log --format='%h|%ci|%s' --since=<start> | grep -E 'BL-0XX|review: BL-0XX'
# per-review STOP/CARRY/ACCEPT tallies + verdict
for f in handoff/claude/*.md; do grep -c 'STOP-' $f; grep -m1 '^verdict' $f; done
# session size + skill loads
sqlite3 ~/.hermes/state.db "SELECT count(*) FROM messages WHERE session_id='<id>'"
sqlite3 ~/.hermes/state.db "SELECT count(*) FROM messages WHERE session_id='<id>' AND tool_name='skill_view'"
```

## Verdict criteria (pre-set, then compare)

- Clean win: 1 round + 0-2 new STOPs + messages < ~400 + HOW-map line present
  + the contradiction/evidence notes in the delivery.

## Extracting the improvement story (evidence for a third-party claim)

When the founder asks to PROVE the loop improved (e.g. a research-grade
appendix: "why does the weak implementer rarely get rejected by the frontier
auditor"), assemble from the repo — no recollection needed:

1. **Full verdict history** — every review's verdict + STOP tally, oldest →
   newest (this reveals the inflection):
   ```bash
   for f in $(ls -t handoff/claude/*.md); do
     stops=$(grep -c "STOP-" "$f")
     verdict=$(grep -im1 "APPROVE\|REQUEST_CHANGES\|BLOCK\|verdict:" "$f" | cut -c1-90)
     echo "$(basename $f) | STOPs=$stops | $verdict"
   done
   ```
2. **First-delivery STOPs per step** — count STOP-ids filed in the FIRST
   review of a step's initial SUBMIT (not the fix-round reviews). The trend
   series (e.g. 17 → 1 → 0 across steps) is the core evidence.
3. **Inflection timing** — governance commit dates vs the defect data:
   `git log --format="%h %ad %s" --date=format:"%m-%d %H:%M" --grep="skill map|HOW map|brief|coordinator"`
   — show that the bad step was BEFORE the layer landed and every step after
   improved (the causal story is in the dates).
4. **The auditor's own words** — grep review titles/verdicts for
   self-corrections ("I over-classified it", "the black screen I dismissed was
   a real defect") — the strongest qualitative evidence is the STRONG auditor
   admitting its own errors while the weak implementer's work passes.
5. **Session effort** — message counts per session (`SELECT count(*) FROM
   messages WHERE session_id=?`) + birth times, to show the era each step ran
   in.
6. **Test growth** — count test declarations directly in the repo now
   (`grep -rc "testWidgets(\|test(" test/`) plus the historical series from
   review letters.
7. **Limitations section — mandatory** (research manners): small samples, the
   model ran at max effort, the AUDITOR itself matured (its checks got
   stronger), "rarely rejected" is directional not absolute. An evidence
   appendix that states its own limits is trusted; one that overclaims is
   discarded.
- Partial: 1-2 rounds, moderate STOPs — additions helped, keep tuning.
- No win: 3+ rounds or many STOPs — re-audit the rails (directive, map,
  auditor checks), not just the model.

## Caveats (honest comparison)

- Steps are NOT equal: a form+transaction step (BL-040, 17 STOPs on first
  delivery) is heavier than a read-only outlook card (BL-032, 0 STOPs). Compare
  like-for-like step classes, or normalize by test count / touched layers.
- A session's LAST steps are done while fatigued (message count near the
  rotation threshold) — a heavy step landed at 2000+ messages is harder than
  the same step at 150. Note the session size when judging.
- The additions change the SYSTEM, not the model: clean rounds prove the rails
  work; the model stays the same weak/flash tier.
