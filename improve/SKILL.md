---
name: improve
description: Review one area of a project (a system, pipeline, page, process or repo) and propose numbered improvements that build on earlier reviews instead of redoing them. Use when the user asks how to improve, optimise or find room for improvement in something.
---

A **review** of one area, which ends in a numbered list the user answers item by item ("apply 1, 3, 4"). What makes it this skill rather than a fresh look: every review knows what earlier reviews proposed, what the user picked or skipped, and what has been decided since, so it builds on them.

Each repo keeps a review log per area in `~/.claude/improve/<repo>/<area>.md`. `<repo>` is the repository name from `basename -s .git "$(git remote get-url origin)"`, or the folder name when there's no remote, so a renamed folder keeps its logs. `<area>` is a short kebab-case name such as `checkout`, `deploy-pipeline` or `landing-page`. Reuse an existing log's name when the request matches it (`ls` the folder first).

A log opens with an `Area:` line naming the files it covers, then a `## Check later` list (see step 4), then one dated section per review.

## 1. History

Read, before looking at the area itself:
- the area's log, if there is one: every earlier review's list, the user's picks, and what was applied;
- neighbouring logs: any other log in the folder whose `Area:` line names the same files and which changed in the last 14 days;
- the repo's decision log, if it has one, entries from the last 14 days that touch the area;
- `git log --since="14 days ago" --stat` for the area's files, plus `git status --short` and `git diff --stat` for uncommitted work. Where there's no repository, use file dates.

Run every line in the log's `## Check later` list that has come due, and open the review with the results: what held, what didn't, what is still too early. A nightly task may already have run a line and written `Result (<date>): …` under it; use that result unless it says "too early" or is more than a few days old.

If a review of this area was applied in the last two or three days, say so too: what changed. Then carry on, but weight the list towards what that review couldn't see.

If the area is a skill or script created or rewritten in the last 24 hours, or one with a run in progress, say so and recommend running it once (or letting the run finish) before reviewing it: a review that early proposes changes the next run would have shown were unneeded, and its edits collide with the run.

Done when you can say, for this area, what was proposed before, what was picked, what was skipped, what has changed since, and the result of every due check.

## 2. Look

Read the area as it stands now: the docs the repo's CLAUDE.md or AGENTS.md points to for it, the code, scripts, data and outputs. Measure where you can: counts, costs, error rates, conversion, time taken. Every proposal needs evidence from this step, not general good practice.

## 3. Propose

One numbered list, at most ten items, most valuable first. Each item is about 50 words:
- first, one plain sentence a non-technical reader follows: what changes in everyday terms and what the user gains. File, script and column names come after it, on their own line;
- the evidence that makes it worth doing;
- its cost: API units, money or the user's time ("no cost" when there is none);
- how it relates to history: **new**, **builds on** <earlier item or decision>, or **replaces** <decision>, with the reason that decision no longer holds.

An item that needs a number proposes one, with the reason for it and what it moves ("timeout goes from 10 s to 30 s"), so the user answers yes, no or another number. Don't ask the user to come up with the figure themselves.

An item that adds a limit (a cap, threshold, stop rule, ban, budget or queue size) starts with "Adds a limit:" and says what it stops, so it doesn't pass unseen inside "Apply all".

An item the user skipped in an earlier review comes back only with new evidence, marked "skipped on <date>; now: <what changed>". Where two items pull against each other, say so in both. Group items under short headings when there are more than five. End the list with the total cost.

Write the list into the area's log under today's date, ending with the line `Picks: waiting`, then stop and wait for the user's picks.

## 4. Apply

Apply only the numbers the user picked. Where the repo's rules say new limits need the user's own ask, "Apply all" or a range doesn't cover an "Adds a limit:" item: apply the rest, then ask about each of those by number.

Before editing, check whether another session is working on the same files: `git diff --stat` on them, and, where session tools are available, any sessions active in the last hour. If one is, or if an item has already been done elsewhere (a decision, draft or commit since the review), say so and skip or merge rather than redo it.

If applying an item needs a second change the user didn't see in the list (an item that reweights a score and so implies new prices, say), ask before making that second change: "apply" covers the item as written.

Follow the repo's rules (its CLAUDE.md or AGENTS.md and memory: who commits, who deploys, how decisions are recorded). A picked item that changes a rule or a standing choice becomes an entry in the repo's decision log, if it has one. Independent items that touch separate files can go to parallel subagents. Run the repo's checks afterwards.

Finish in the log:
- Replace `Picks: waiting` with `Picks (<date>):` and the user's words, then one line per item: applied (what changed where), skipped, blocked, or no answer. An item with no answer is named once in the closing report and may return in the next review; a skipped one follows the skip rule in step 3.
- For each applied item whose effect can't be seen yet, add a line to `## Check later` at the top of the log: what should be true, by what date, and the command or place that shows it. Delete a line once a later review has run it and reported the result. Where a nightly dream task is set up for the repo (the [setup-dreaming](../setup-dreaming/SKILL.md) skill), it runs due lines each night and writes the result under them.
- Anything left for the user.

Done when every picked item is applied or reported as blocked, the log says which, and every unconfirmed effect has a `Check later` line.
