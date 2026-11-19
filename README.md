# skills

Claude Code skills I use.

| Skill | What it does |
|---|---|
| [end-of-day](end-of-day/SKILL.md) | Reviews a day of Claude Code sessions in a repo (or every project), finds what cost the most time and tokens, and proposes numbered fixes to the setup. Run it as `/end-of-day`, optionally with a date or `all`. |
| [improve](improve/SKILL.md) | Reviews one area of a project (a system, pipeline, page or process) and proposes numbered improvements. Keeps a log per area, so each review builds on what earlier ones proposed, what you picked and what has changed since, then applies the items you pick. Run it as `/improve <area>`. |
| [reflect](reflect/SKILL.md) | Reviews the session you are in, as its last step: where you corrected Claude, detours, breakages and stale guidance. Checks for fixes already in place or tried before, then proposes numbered fixes to the setup and applies the ones you pick. Run it as `/reflect`. |
| [setup-dreaming](setup-dreaming/SKILL.md) | Sets up a nightly "dream" for a repo. It is a scheduled task that runs a workflow over the day's sessions, tidies memory, adds decisions and open questions to the repo's docs, and writes a report. Run `/setup-dreaming` in the repo. The skill must stay installed, because the task runs its scripts. |

## Install

Copy a skill's folder into `~/.claude/skills/`:

```bash
git clone https://github.com/zakcasey/skills.git
cp -R skills/end-of-day ~/.claude/skills/
```
