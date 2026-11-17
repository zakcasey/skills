---
name: end-of-day
description: Review today's Claude sessions in this repo (or every project with "all"), find what wasted time or went wrong, and propose numbered fixes to the setup.
disable-model-invocation: true
---

A **retrospective** on one day of the user's Claude sessions: what cost the most, and which changes to the setup (CLAUDE.md, skills, scripts, scheduled tasks, docs, memory, session habits) would stop it happening again. If a nightly dream runs for the repo (the `setup-dreaming` skill in this repo), it already writes decisions and memory, so this covers friction and cost only.

**Scope:** the repo you run it in, meaning sessions started in its folder or in its worktrees. Find the root with `git rev-parse --show-toplevel`; outside a git repo, use the working directory. Arguments, all optional, in any order:
- a date (`2026-11-12`) to review that day instead of today;
- `all` to review every project's sessions instead.

Reports live in `~/.claude/end-of-day/reports/<repo folder name>/<YYYY-MM-DD>.md`, or under `all/` for an all-projects run.

## 1. Last time

Read the most recent earlier report for the same scope, if there is one. For each fix the user picked there, check whether it landed (file, script or task changed). Note any problem it targeted that showed up again today; that recurrence goes at the top of today's findings.

## 2. Digest

```
python3 ~/.claude/skills/end-of-day/digest.py <scratchpad>/eod --repo <repo root> [--day YYYY-MM-DD]
```

Leave out `--repo` for an `all` run. It writes one digest per session and `INDEX.md`, with real cost per session: forked and resumed sessions are de-duplicated, and this skill's own runs are left out. Read INDEX.md. Done when you know the session count, the five costliest sessions and the scheduled-task total.

## 3. Review

Split the digests into 3 to 5 groups by theme: scheduled runs, each repo's interactive work, and any large cluster such as a day of backlink sessions. Keep each group under ~400 KB. Send one subagent per group, all in one message, with the prompt in [reviewer-brief.md](reviewer-brief.md) filled in. Wait for every report.

## 3b. Skill candidates

Read `REQUESTS.md` (every request typed that day, in time order), then list the skills that already exist: `~/.claude/skills/`, the repo's `.claude/skills/`, and the skill list in your own context. A **skill candidate** is one of:
- the same kind of request three or more times in the day, in any wording ("draft responses", "can you respond", "send replies");
- a multi-step workflow done by hand that had to be pieced together again, or was done differently each time;
- a procedure the user had to explain or correct twice;
- an existing skill that should have been used and wasn't, or that needs a step it lacked.

For each candidate, note the name it would be typed as, its trigger, what it does in a line, whether it's user-invoked or model-invoked, and the evidence (count, sessions, times). Prefer extending an existing skill to adding a new one. Drop anything already covered.

## 4. Verify

Before you report a finding that names a file, a script, a count or a missing feature, check it in the repo yourself (grep, `git show --stat`, read the line). Drop or correct anything that doesn't hold. Subagent findings are claims until checked.

## 5. Report

Write the report file, then give the user the same content in chat:

1. **What cost the most:** three to five themes, each with the evidence that makes it concrete (session, time, numbers). Recurring problems from step 1 come first.
2. **Fixes:** one numbered list the user can answer item by item ("3 apply, 4 skip"). Each item is one fix: what changes, where, and which finding it answers. Group them under short headings, with skill candidates from 3b under their own **Skills** heading.
3. **Habits:** at most three, about how the user starts, splits or checks sessions, each tied to a cost seen today.
4. **Keep:** what worked.

Then stop and wait for the user's picks.

## 6. Apply

Build a picked skill (with the `writing-for-agents` skill's guidance, if it is installed) in the repo's `.claude/skills/` if it's about that repo, otherwise in `~/.claude/skills/`. Apply only the numbers the user picked, within the repo's own rules (its CLAUDE.md and memory: who commits, who deploys, which files are theirs). Send independent fixes to parallel subagents when they touch separate files; do the rest yourself. Run the repo's checks (tests, linters, type checks, its own check scripts, `node --check` on edited JavaScript) after. Append to the report file which fixes were applied and anything left for the user (restarts, commits, settings only they can change).
