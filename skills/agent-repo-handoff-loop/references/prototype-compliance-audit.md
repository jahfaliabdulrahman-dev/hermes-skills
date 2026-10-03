# Prototype-Compliance Audit for First-Time-Platform Founder Findings (2026-08-15)

## The case

The founder's first real iPhone walk produced three findings:
1. Auto-advance on brand/model select (picking a brand jumps to the next wizard step instead of staying and enabling «التالي»).
2. An "Android-looking" selector (stadium OutlinedButton + modal bottom sheet).
3. An "Android-looking" bottom nav (Material 3 NavigationBar pill capsule).

The auditor (Claude) did NOT open three founder decisions. It built the app for the
iOS simulator from an isolated clone, walked the same flow, then ran the SAME walk in
the binding prototype P1 (`design/prototype/proto_served.html`) at the SAME viewport
(402×874). Result:

- **Findings 1 and 2 were divergences, not decisions.** P1 keeps you on the step when
  you pick a brand (field fills, «التالي» enables, no navigation); the build jumps.
  P1's selector is a field with a ▾ caret + an inline expanding list card + pinned
  search + result counter («19 نتيجة من 19»); `08 §7.5.2` says verbatim «not a modal
  bottom sheet». The build ships the Material alternative. → UNBUILT ratified design:
  pre-decided, implement-to-prototype. No founder decision needed.
- **Finding 3 was also a divergence:** P1's bottom bar is text-only tabs, no icons,
  no capsule; the build ships the Material 3 NavigationBar.
- **Only ONE item was a real founder decision:** the emoji artwork. P1 uses emoji
  glyphs too (hero tile, bell, stethoscope), so on that axis the build was COMPLIANT —
  changing it means changing the prototype → genuine founder decision (founder ruled:
  leave it; redesign happens post-MVP).

Verdict: «Nothing here is broken; it is unbuilt.» OPEN STOPs: 0.

## Rules for the loop

1. **Classify before deciding.** A finding on a platform never tested is most often a
   divergence (build ≠ prototype → implement the prototype, no founder decision) and
   only sometimes a design change (prototype shows the same behaviour → real founder
   decision requiring DEC + prototype amendment). Present the classification with
   evidence; never forward raw findings as "the founder must decide".
2. **The side-by-side walk is the evidence** — same flow, same viewport, both sides
   (build + P1), screenshots. Never compare from memory or from the letter's narrative.
3. **Corrections against your own earlier claims are part of the job** — the auditor
   had previously told the founder the emoji artwork was the biggest "cheap" signal;
   walking P1 proved P1 uses emoji too, and the correction went in the SAME letter
   that resolved the findings (handoff/claude/20260815-180113.md).
4. The prototype is the law (the locked table's sibling): a divergence from it is a
   defect in the build, not a new product question.

## Why it matters

First-time-platform walks are the highest-yield testing the loop has done — they found
3 divergences 50+ build steps in, on a platform (iOS) that had never been exercised.
The Android walk in the same round (F-20260814-01/02/03) had already proven the same
mechanism on the primary platform: the founder's findings were routed through the
prototype before becoming rulings.
