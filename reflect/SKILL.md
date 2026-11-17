---
name: reflect
description: End-of-session reflection on this conversation, proposing numbered fixes so the next session goes better.
disable-model-invocation: true
---

A **reflection** on the session you are in, run as its last step. You were there, so the evidence is your own context: where the user corrected you, where you went the long way round, what broke, what you had to piece together. The output is a numbered list of **fixes** to the setup (memory, CLAUDE.md or AGENTS.md, skills, scripts, checks, docs) that the user answers item by item ("apply 1, 3").

A reflection covers this one session, while the detail is still fresh. Reviews of a whole day or of one area of a project are other jobs; if the user runs them, their reports are history for step 2.

Logs live in `~/.claude/reflect/<repo>/<YYYY-MM-DD>-<session>.md`. `<repo>` is `basename -s .git "$(git remote get-url origin)"`, or the folder name outside git. `<session>` is the first 8 characters of this session's id. The transcript is `~/.claude/projects/<slug>/<id>.jsonl`, where `<slug>` is the working directory with every character other than a letter or digit replaced by `-`; if you can't tell the id, take the newest file there that contains a phrase from this conversation.

## 1. Recall

Walk the session from the first message, and list every **moment**: a point where the session lost time, tokens or the user's attention, or nearly went wrong. If the start of the session was summarised, read the transcript for the part you can no longer see (grep it for `"type":"user"` lines first rather than reading it whole). Look for:

- **Corrections**: the user said no, redirected you, or repeated an instruction. Quote their words.
- **Detours**: searches, reads or commands that found nothing, or a fact that took several calls to reach when one pointer would have done.
- **Breakages**: errors, failed checks, a hook that blocked you, a fix that needed a second try.
- **Rework**: something you did twice, or did by hand in several steps that a script or skill could do in one.
- **Stale guidance**: a doc, memory, skill or CLAUDE.md line that said one thing while the repo said another, or that you followed and it led you wrong.
- **Missing access**: information or a tool you needed and didn't have, so you guessed or asked.
- **Length**: the session took on a second job that belonged in a new session, or a long context was re-read many times.

Also note what worked well, for the **Keep** section.

Done when every moment has its evidence: the turn, the command or file, and roughly what it cost (calls, minutes, a wrong answer the user had to catch).

## 2. Check

For each moment, find out whether a fix already exists or was already tried:

- grep the places that hold standing guidance for the rule that would have prevented it: the repo's CLAUDE.md or AGENTS.md, the user's `~/.claude/CLAUDE.md`, the memory folder (`~/.claude/projects/<slug>/memory/`) if there is one, and the skill that was running;
- read earlier logs in `~/.claude/reflect/<repo>/` from the last 14 days, and any other review reports the user keeps under `~/.claude/` (for example `~/.claude/end-of-day/reports/<repo>/`), for the same fix proposed before and what the user picked.

A moment whose rule exists but wasn't followed is a **pointer** problem: the rule is worded weakly, sits where you don't read it, or lives in a long file. Fix the wording or the placement, not by adding a second copy. A fix the user skipped before comes back only with this session as new evidence, marked "skipped on <date>; now: <what happened>".

Done when every moment is marked new, already fixed (drop it), pointer problem, or skipped before.

## 3. Propose

Turn the moments into fixes. Several moments with one cause become one fix. Put each fix where it will be found next time, in this order of preference:

1. **A check** (a hook, a test, one of the repo's lint or check scripts, a script's own validation) when the mistake is mechanical: a check runs every time and costs no context.
2. **A skill edit** when the mistake happened inside a skill's run: add the missing step or sharpen the step's done condition.
3. **A new skill** when a multi-step procedure was pieced together by hand and will come back. Prefer extending an existing skill.
4. **A doc or pointer**: a line in the doc the agent was already reading, or a pointer to the doc it should have read. Keep CLAUDE.md and AGENTS.md short, since they load every session: put a pointer there and the detail in the doc it points at.
5. **A memory** for a preference or fact about the user, an account or a tool that no file in the repo records.

Write one numbered list, at most eight items, most valuable first. Each item:
- one plain sentence a non-technical reader follows: what changes and what the user gains. Files and paths on the next line;
- the moment it answers, with the evidence from step 1;
- the exact change: the line to add or replace, or the check to build;
- your recommendation: apply or skip, and why.

Then **Keep**: at most three things that worked, one line each. Then **Left open**: anything this session leaves unfinished that the user should know about (uncommitted edits, an unanswered question, a step skipped), or "nothing".

A session with no real moments gets a short reply saying so and no list: every item needs a real moment behind it.

Write the list into the log file, ending with `Picks: waiting`, then give the user the same list in chat and stop.

## 4. Apply

Apply only the numbers the user picked, within the repo's rules (its CLAUDE.md or AGENTS.md: who commits, which files are off limits, how decisions are recorded). If a picked fix needs a second change the user didn't see, ask before making it. When a fix writes or edits a skill, follow the `writing-for-agents` skill if it is installed. Run the repo's checks afterwards for any code, hook or script you touched.

In the log, replace `Picks: waiting` with `Picks (<date>):`, the user's words, and one line per item: applied (what changed where), skipped, or blocked.

Done when every picked item is applied or reported as blocked, and the log says which.
