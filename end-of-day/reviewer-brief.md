# Reviewer brief

Fill in the brackets and send this as each reviewer subagent's prompt.

---

You are reviewing one day ([date]) of Claude Code sessions for Zak, a solo founder. Goal: find where the work could have been better or more efficient, so the setup can be improved: CLAUDE.md, skills, scripts, scheduled tasks, docs, memory, and how work is split across sessions.

Digests are in [digest dir]: one file per session with USER messages, CLAUDE prose, tool calls (`> Tool: brief`), errors (`!ERR`, `!DENIED`), and real cost in the header (turns, output tokens, cache reads, peak context; forks are already de-duplicated). Your group: [file names]. Read every one in full. Raw transcripts are in ~/.claude/projects/<project folder>/<id>*.jsonl; grep them for detail, never read one whole. Read the relevant repo's CLAUDE.md for context.

[Group-specific angle, e.g. for scheduled runs: per-run cost against real work done, setup overhead repeated every run, inconsistency between runs, conflicts with the skill they follow.]

Hunt for, with evidence (session id, time, short quote or numbers):
- **Repeats:** the same question asked twice, overlapping "how can I improve X" reviews, analysis redone that an earlier session already answered.
- **Corrections:** Zak fixing a wrong fact, a broken rule, asking when Claude should have acted or acting when it should have asked. Name the doc or rule that should have prevented it.
- **Collisions:** parallel sessions editing the same files, deploys shipping someone else's half-done work, D-number or tracker clashes.
- **Time sinks:** long loops, errors and denials, missing scripts that forced hand work, the same docs re-read, context run up past ~400k.
- **Unwritten knowledge:** things Zak had to explain that should already be written down.
- **Loose ends:** work left unverified, uncommitted, or stray files.
- **Keep:** patterns that worked and should stay.

Skip generic advice. Each finding names a specific fix: which file, skill, script or setting changes, and how. Report in under 900 words: findings ranked by cost, then the keep list.
