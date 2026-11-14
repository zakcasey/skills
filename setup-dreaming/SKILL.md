---
name: setup-dreaming
description: Set up a nightly "dream" for the current repo, a scheduled task that reviews the day's Claude Code sessions, updates memory and the repo's docs, and writes a report. Use when the user asks to set up dreaming, nightly review or memory consolidation for a repo.
disable-model-invocation: true
---

A **dream** is a nightly hindsight pass over one repo's Claude Code sessions. A workflow reads each session's digest, pulls out what is worth keeping, and verifies possible rule breaches against the current code. Then two writers run side by side: one tidies the memory folder (`~/.claude/projects/<repo>/memory`) and one adds decisions, open questions and doc facts to the repo's docs. A report lands each morning. This skill sets that up for the repo it is run in.

Files in this folder:
- [extract.py](extract.py): turns a window of transcripts into digests and analyzer groups.
- [dream.workflow.js](dream.workflow.js): the workflow, shared by every repo; per-repo settings come in as args.
- [task-prompt.md](task-prompt.md): the scheduled task's prompt, with `{{PLACEHOLDERS}}`.

The task needs the Workflow tool, so it runs workflows each night: that is a standing opt-in. Say so when you confirm the setup.

## 1. Gather the repo's details

- **REPO**: `git rev-parse --show-toplevel`, or the working directory outside git.
- **NAME**: the repo folder's name, kebab-case. **TASK_ID**: `<NAME>-nightly-dream`. Stop and tell the user if `list_scheduled_tasks` already has a dream task for this repo.
- **MEMORY_DIR**: `~/.claude/projects/<slug>/memory`, where `<slug>` is REPO with every character other than a letter or digit replaced by `-` (`/Users/me/dev/app` → `-Users-me-dev-app`). Expand `~` to the absolute path. Create the folder if it's missing.
- **SKILL_DIR**: the absolute path of this skill's folder. The task runs the scripts from here, so the skill must stay installed.
- **TASK_DIR**: `~/.claude/scheduled-tasks/<TASK_ID>`, absolute.
- **OWNER**: the user's first name if CLAUDE.md or memory gives it, else `the user`.

Read the repo's CLAUDE.md and AGENTS.md, then look for:
- a **decision log** (e.g. `decisions.md`, `docs/adr/`, `DECISIONS.md`);
- an **open-questions** doc;
- **off-limits paths**: folders the rules say not to edit, or data the dream should never write to (vendored code, data dumps, private research).

## 2. Ask

One AskUserQuestion with up to three questions. Each one states what you found:
1. **Time**: when to run. Default to midnight local. Tasks run only while the Claude app is open, and a missed run happens the next time it opens.
2. **Docs**: whether the dream may edit the decision log and open-questions doc you found, or only update memory and the report. If you found neither, ask whether to record decisions in the report only (the default) or to create `docs/decisions.md`.
3. **Off-limits**: confirm the paths you plan to protect, if any.

## 3. Install

1. Link the shared workflow once, if it isn't already linked: `mkdir -p ~/.claude/workflows && ln -s <SKILL_DIR>/dream.workflow.js ~/.claude/workflows/nightly-dream.js`. If a different file already has that name, leave it alone. The task prompt falls back to passing the script text.
2. Fill in `task-prompt.md`: replace every `{{…}}`. `DECISIONS_DOC` and `OPEN_QUESTIONS_DOC` are JSON strings of paths relative to REPO, or `null`. `OFF_LIMITS` is a JSON array of relative paths (`[]` for none). `OFF_LIMITS_SENTENCE` is `, or anything under <paths>` or empty. Afterwards, grep the result for `{{` and make sure nothing is left.
3. Call `create_scheduled_task` with `taskId` TASK_ID, `title` `<Repo name> nightly dream`, a one-line `description`, the filled prompt, and `cronExpression` for the chosen time (`0 0 * * *` for midnight). The task's own folder becomes TASK_DIR. Make `reports/` in it.

## 4. Confirm

Tell the user:
- when the task runs;
- what it may edit (memory and which docs);
- that it never commits;
- where reports go (`TASK_DIR/reports/`).

Offer a first run now with `run_scheduled_task`. With no `last-run` file it covers the last 24 hours.
