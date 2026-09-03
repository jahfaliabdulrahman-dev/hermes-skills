# 2026-08-08: Sync Direction Regression Case Study

Case history for `skill-ecosystem-sync`. Two distinct failure modes surfaced in
one session; both are now encoded as rules in the main SKILL.md — this file
preserves the concrete detail that proves them.

## Case 1 — Local digest vs canonical repo (sync-direction rule)

Local `flutter-lessons-patterns` was a **2.9.0 digest (112 lines, only
LL-043..049)** while the repo held the **canonical 2.16.0 (2087 lines,
LL-043..051 + 18 references)**. A blind local→repo push would have deleted
~35 accumulated patterns from the public repo.

- Correct direction was **repo → local**; references were byte-identical so
  nothing was lost.
- Rule (main SKILL.md): if repo version is higher or richer, restore
  repo → local; never push the regression. When versions tie, compare content
  (line counts, reference files) before choosing direction.

## Case 2 — Personal paths re-contaminating public files (pre-push gate)

`flutter-soul-stewardship` + `system-prompt-rebuild.md` had
`/Users/<name>/...` (personal absolute paths) replacing the generalized
`<profile-home>` placeholders; `azdal-full-structure.md` had
`~/Projects/Azdal/` (concrete project path) replacing
`~/Projects/<project>/`.

- Rule (main SKILL.md): the pre-push scan must hit on any personal absolute
  path or concrete project path; on a hit, revert the file to HEAD **and**
  restore the generalized placeholder into the LOCAL copy too — otherwise the
  next sync re-dirties it.
