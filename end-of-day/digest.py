#!/usr/bin/env python3
"""Condense one day's Claude Code transcripts into one digest per session, plus INDEX.md with real
per-session cost. Used by the /end-of-day skill.

Usage: digest.py OUT_DIR [--day YYYY-MM-DD] [--repo PATH]
  --day   the day to review (default: today, local time)
  --repo  only sessions run in this folder or in worktrees under it (pass the repo root);
          without it, every project

REQUESTS.md lists every request typed in an interactive session, in time order, for spotting repeats.
Each digest keeps user messages, Claude's prose, one line per tool call, tool errors and denials.
Tool output and file contents are dropped. Forked or resumed sessions copy their parent's history
into a new file, so messages are de-duplicated by id across all files: a fork's digest shows only
its own new turns, and the cost columns count each message once.
"""
import glob, json, os, re, sys
from collections import Counter
from datetime import datetime, timedelta

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
out_dir = args[0]
day = args[args.index("--day") + 1] if "--day" in args else datetime.now().strftime("%Y-%m-%d")
repo = os.path.abspath(os.path.expanduser(args[args.index("--repo") + 1])) if "--repo" in args else None
start = datetime.strptime(day, "%Y-%m-%d").astimezone()
end = start + timedelta(days=1)
os.makedirs(out_dir, exist_ok=True)

ROOT = os.path.join(os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"), "projects")
HOME_SLUG = os.path.expanduser("~").replace("/", "-").replace(".", "-")  # how Claude Code names project folders
SELF_MARK = "/end-of-day"  # this skill's own runs are skipped


def local(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def text_of(c):
    if isinstance(c, str):
        return c
    return " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))


files = []
# Claude Code names each project folder after the session's working directory, with every
# character other than a letter or digit turned into "-". Worktrees under the repo
# (<repo>/.claude/worktrees/<name>) get the repo's name followed by "--claude-worktrees-<name>".
repo_slug = re.sub(r"[^A-Za-z0-9]", "-", repo) if repo else None
for path in glob.glob(os.path.join(ROOT, "*", "*.jsonl")):
    folder = os.path.basename(os.path.dirname(path))
    if repo_slug and folder != repo_slug and not folder.startswith(repo_slug + "--"):
        continue
    if datetime.fromtimestamp(os.path.getmtime(path)).astimezone() >= start:
        files.append(path)
files.sort(key=os.path.getmtime)

seen_ids = set()
requests = []  # every typed request, for spotting repeated workflows (skill candidates)
seen_msgs = set()
index = []
for path in files:
    proj = os.path.basename(os.path.dirname(path))
    proj = proj[len(HOME_SLUG):].strip("-") if proj.startswith(HOME_SLUG) else proj.strip("-")
    proj = proj or "home"
    sid = os.path.basename(path)[:8]
    lines, tools, asks = [], Counter(), []
    cost = Counter()
    first = last = None
    kind = "interactive"
    skip = False
    with open(path, errors="replace") as fh:
        for raw in fh:
            try:
                o = json.loads(raw)
            except ValueError:
                continue
            if o.get("type") not in ("user", "assistant") or o.get("isSidechain"):
                continue
            ts = o.get("timestamp")
            if not ts:
                continue
            t = local(ts)
            if not (start <= t < end):
                continue
            m = o.get("message") or {}
            if o.get("uuid") in seen_ids:
                continue  # copied from a parent session (fork or resume)
            seen_ids.add(o.get("uuid"))
            # One API message is logged as several lines (one per content block), each repeating its usage.
            mid = m.get("id")
            new_msg = bool(mid) and mid not in seen_msgs
            if mid:
                seen_msgs.add(mid)
            first = first or t
            last = t
            hm = t.strftime("%H:%M")
            c = m.get("content")
            if o["type"] == "user":
                if isinstance(c, str) or any(isinstance(x, dict) and x.get("type") == "text" for x in (c or [])):
                    if o.get("isMeta"):
                        continue
                    s = text_of(c)
                    if SELF_MARK in s[:300] or "end-of-day/SKILL.md" in s[:300]:
                        skip = True
                    if s.startswith("<local-command") or s.startswith("<command-"):
                        continue
                    if s.lstrip().startswith("<scheduled-task"):
                        kind = "scheduled"
                    lines.append(f"\n[{hm}] USER: {s[:2500]}")
                    if kind == "interactive" and not s.lstrip().startswith("<"):
                        asks.append((t, sid, " ".join(s.split())[:200]))
                for x in c if isinstance(c, list) else []:
                    if isinstance(x, dict) and x.get("type") == "tool_result" and x.get("is_error"):
                        s = text_of(x.get("content"))
                        tag = "DENIED" if ("denied" in s.lower() or "rejected" in s.lower()) else "ERR"
                        lines.append(f"   !{tag}: {s[:300]}")
                        cost["errors"] += 1
            else:
                u = (m.get("usage") or {}) if new_msg else {}
                cost["out"] += u.get("output_tokens", 0)
                cost["cache_read"] += u.get("cache_read_input_tokens", 0)
                cost["cache_write"] += u.get("cache_creation_input_tokens", 0)
                cost["turns"] += 1 if new_msg else 0
                cost["peak_ctx"] = max(cost["peak_ctx"], u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0))
                if m.get("model") and not m["model"].startswith("<"):
                    cost["model:" + m["model"].replace("claude-", "")] = 1
                for x in c or []:
                    if x.get("type") == "text" and x["text"].strip():
                        lines.append(f"[{hm}] CLAUDE: {x['text'][:1500]}")
                    elif x.get("type") == "tool_use":
                        tools[x["name"]] += 1
                        i = x.get("input") or {}
                        brief = i.get("description") or i.get("command") or i.get("file_path") or i.get("query") or i.get("url") or i.get("prompt", "")[:120]
                        lines.append(f"   > {x['name']}: {str(brief)[:160]}")
    if skip or not lines or not first:
        continue
    models = ",".join(k[6:] for k in cost if k.startswith("model:"))
    name = f"{proj}_{first.strftime('%H%M')}_{sid}.txt"
    head = (f"PROJECT {proj}  SESSION {sid}  {kind}  {first:%H:%M}-{last:%H:%M}  model={models}\n"
            f"turns={cost['turns']} out={cost['out']} cache_read={cost['cache_read']} peak_ctx={cost['peak_ctx']} "
            f"errors={cost['errors']}\nTOOLS {dict(tools.most_common(12))}\n")
    with open(os.path.join(out_dir, name), "w") as f:
        f.write(head + "\n".join(lines))
    requests.extend((t, proj, sid_, a) for t, sid_, a in asks)
    index.append((proj, kind, first, last, sid, cost, models, os.path.getsize(os.path.join(out_dir, name)) // 1024, name))

index.sort(key=lambda x: x[2])
with open(os.path.join(out_dir, "INDEX.md"), "w") as f:
    f.write(f"# Sessions on {day}{' in ' + repo if repo else ' (every project)'}\n\n| file | project | kind | time | model | turns | out | cache read | peak ctx | errors | KB |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    for p, k, a, b, s, c, mo, kb, n in index:
        f.write(f"| {n} | {p} | {k} | {a:%H:%M}-{b:%H:%M} | {mo} | {c['turns']} | {c['out']} | {c['cache_read']} | {c['peak_ctx']} | {c['errors']} | {kb} |\n")
    tot = Counter()
    for x in index:
        c = x[5]
        tot.update({k: v for k, v in c.items() if not k.startswith("model:") and k != "peak_ctx"})
    f.write(f"\nTotal: {len(index)} sessions, {tot['turns']} turns, {tot['out']} output tokens, {tot['cache_read']} cache-read tokens, {tot['errors']} tool errors.\n")
with open(os.path.join(out_dir, "REQUESTS.md"), "w") as f:
    f.write(f"# Every request typed in an interactive session on {day}, in time order\n\n")
    for t, p, sid_, a in sorted(requests):
        f.write(f"- {t:%H:%M} {p} {sid_}: {a}\n")
print(f"{len(index)} sessions{' in ' + repo if repo else ' in every project'} -> {out_dir}/INDEX.md")
