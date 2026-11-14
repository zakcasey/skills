#!/usr/bin/env python3
"""Condense one repo's Claude Code transcripts from a time window into one readable digest per
session: user messages, Claude's prose, the files each session edited and its git branch. Tool
output and file contents are dropped. Used by the nightly dream task that /setup-dreaming creates.

Usage: extract.py SINCE_ISO UNTIL_ISO OUT_DIR --repo PATH [--task TASK_ID]
  --repo  the repo root; sessions run in it or in worktrees under it are included
  --task  the dream task's id; its own earlier runs are skipped so it never reviews itself

Writes <session>.md per session, INDEX.md (largest first) and groups.json: the digests packed into
groups of up to ~80 KB, one analyzer agent each.
"""
import glob, json, os, re, sys
from datetime import datetime

args = sys.argv[1:]
if len(args) < 3 or "--repo" not in args:
    sys.exit(__doc__)
since = datetime.fromisoformat(args[0].replace("Z", "+00:00"))
until = datetime.fromisoformat(args[1].replace("Z", "+00:00"))
out_dir = args[2]
repo = os.path.abspath(os.path.expanduser(args[args.index("--repo") + 1]))
task = args[args.index("--task") + 1] if "--task" in args else None
os.makedirs(out_dir, exist_ok=True)

# Claude Code names each project folder after the session's working directory with every
# character other than a letter or digit turned into "-"; worktrees under the repo get the
# repo's name followed by "--claude-worktrees-<name>".
ROOT = os.path.join(os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"), "projects")
slug = re.sub(r"[^A-Za-z0-9]", "-", repo)
roots = [os.path.join(ROOT, slug)] + glob.glob(os.path.join(ROOT, slug + "--*"))
own_mark = f'scheduled-task name="{task}"' if task else None

MAX_TEXT = 4000
index = []
for root in roots:
    for path in glob.glob(os.path.join(root, "*.jsonl")):
        if datetime.fromtimestamp(os.path.getmtime(path)).astimezone() < since:
            continue
        lines, edited, first_user = [], set(), None
        branches, earlier, skip = set(), False, False
        with open(path, errors="replace") as f:
            for raw in f:
                try:
                    o = json.loads(raw)
                except ValueError:
                    continue
                if o.get("type") not in ("user", "assistant") or o.get("isSidechain"):
                    continue
                ts = o.get("timestamp")
                if not ts:
                    continue
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                content = (o.get("message") or {}).get("content")
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                # Earlier runs of the dream would only feed its own output back in.
                if own_mark and o["type"] == "user" and any(
                    own_mark in (p.get("text") or "") for p in content or [] if isinstance(p, dict)
                ):
                    skip = True
                    break
                if t < since:
                    earlier = True
                    continue
                if t >= until:
                    continue
                if o.get("gitBranch"):
                    branches.add(o["gitBranch"])
                for part in content or []:
                    if not isinstance(part, dict):
                        continue
                    kind = part.get("type")
                    if kind == "text":
                        text = part["text"].strip()
                        if not text or text.startswith("<system-reminder>"):
                            continue
                        if o["type"] == "user" and first_user is None:
                            first_user = text[:300]
                        who = "USER" if o["type"] == "user" else "CLAUDE"
                        lines.append(f"[{ts[11:16]}Z] {who}: {text[:MAX_TEXT]}")
                    elif kind == "tool_use":
                        fp = (part.get("input") or {}).get("file_path")
                        if part.get("name") in ("Edit", "Write", "NotebookEdit") and fp:
                            edited.add(fp)
        if skip or not lines:
            continue
        sid = os.path.basename(path)[:-6]
        with open(os.path.join(out_dir, f"{sid}.md"), "w") as out:
            out.write(f"# Session {sid}\nSource: {path}\n")
            if branches:
                out.write(f"Git branch: {', '.join(sorted(branches))}\n")
            if earlier:
                out.write("Started before this window: earlier messages were covered by a previous run.\n")
            out.write("\n")
            if edited:
                out.write("Files edited:\n" + "\n".join(f"- {p}" for p in sorted(edited)) + "\n\n")
            out.write("\n\n".join(lines) + "\n")
        index.append((sid, len(lines), (first_user or "").replace("\n", " ")[:160]))

with open(os.path.join(out_dir, "INDEX.md"), "w") as out:
    for sid, n, first in sorted(index, key=lambda x: -x[1]):
        out.write(f"- {sid}.md ({n} messages): {first}\n")

# One analyzer per group. Big digests go alone; small ones (scheduled runs, quick questions)
# are packed together so the night doesn't spend an agent on every two-line session.
GROUP_BYTES = 80_000
sizes = sorted(
    ((os.path.join(out_dir, f"{sid}.md"), os.path.getsize(os.path.join(out_dir, f"{sid}.md"))) for sid, _, _ in index),
    key=lambda x: -x[1],
)
groups, current, current_size = [], [], 0
for p, size in sizes:
    if size >= GROUP_BYTES:
        groups.append([p])
        continue
    if current and current_size + size > GROUP_BYTES:
        groups.append(current)
        current, current_size = [], 0
    current.append(p)
    current_size += size
if current:
    groups.append(current)
with open(os.path.join(out_dir, "groups.json"), "w") as out:
    json.dump(groups, out, indent=1)
print(f"{len(index)} sessions -> {out_dir} ({len(groups)} groups in groups.json)")
