# skel: drive Cursor through the fixture the same way as Claude

**Status:** design, approved 2026-08-26. Branch `feat/skel-cursor-trial`, stacked on
`feat/skel-harness`.

Parent: [2026-08-24-skel-harness-design.md](2026-08-24-skel-harness-design.md).

## Why

`just skel trial claude` already scaffolds the fixture, feeds every prompt to one
session, and archives the transcript beside the agent's report. Cursor is a declared
harness with a bundle row and no trial row, so the same recipe cannot drive it.

The missing piece is how a Cursor session is named. Claude takes `--session-id` up
front, so the driver generates a UUID and the transcript path is known. Cursor does the
opposite: `agent create-chat` prints a UUID, and later prompts attach with `--resume`.
The driver has to learn the session from the harness before the first prompt, or it
cannot keep the prompts in one conversation and cannot find the transcript.

## Non-goals

A live Cursor trial, and the evidence archive it would produce, are out of scope. So is
anything Cursor-specific under `skel/`, and so is installing the almanac Cursor plugin
into a run (`--plugin-dir` and friends). This slice declares the trial and teaches the
driver to resolve a session the harness names. An operator with a local `agent` CLI can
then run it; CI does not.

`--sandbox disabled` is deferred. Add it if a live run stalls on the sandbox, not in
this cut.

## Decision: optional `create` on `[*.trial]`

How a harness names a session is a harness difference, so it belongs in
`harnesses.toml`. The driver stays generic: if `create` is set, run it in the run
directory and use stripped stdout as `{session}`; if it is absent, generate the id as
today.

Rejected alternatives:

- **Special-casing Cursor in Python.** A `if harness.name == "cursor"` branch would
  duplicate the table's job and make the next harness that names its own session a
  second special case.
- **Discovering the newest transcript.** That is what the parent design already calls
  out as hope: another Cursor session running at the same time wins the glob, and the
  archive attributes the wrong conversation to the trial.

`first`, `resume`, and `transcript` stay required. `create` and `version` stay optional.

## Cursor row

```toml
[cursor.trial]
# create-chat returns a UUID; first/resume both attach with --resume.
# --force is unattended file/shell approval; --trust skips the workspace prompt.
create = ["agent", "create-chat"]
first = [
    "agent", "-p", "--resume", "{session}",
    "--force", "--trust",
    "{prompt}",
]
resume = [
    "agent", "-p", "--resume", "{session}",
    "--force", "--trust",
    "{prompt}",
]
transcript = "~/.cursor/projects/*/agent-transcripts/{session}/{session}.jsonl"
version = ["agent", "--version"]
```

`--force` is Cursor's equivalent of Claude's `bypassPermissions`: without it a headless
session stalls on the first file or shell it needs approval for. `--trust` skips the
workspace prompt the same way. Both go into the table verbatim and are copied into each
archive's manifest, so a reader knows what the agent was allowed to do.

The first prompt uses `--resume` rather than a distinct open-session flag because
`create-chat` has already opened the session. `first` and `resume` happen to be the same
command; they remain two fields because the driver still distinguishes the opening turn
from the rest, and because a future Cursor CLI that opens differently should not have to
invent a third field.

The transcript glob keeps `{session}` in the path. Cursor writes
`~/.cursor/projects/<project>/agent-transcripts/<uuid>/<uuid>.jsonl`. The project
segment is a hash of the run directory, which the driver does not know, so `*` stands
in. The UUID is unique, so the glob is not "newest file wins" — it is the file whose
name is the session the create step just printed.

A missing `agent` binary fails as the first command that needs it, the same way a
missing `claude` already does. There is no Cursor-shaped error for that.

## Driver

1. Scaffold the run as today.
2. If `harness.trial.create` is set: run it in the run directory, with the same scrubbed
   environment the prompts inherit. Non-zero exit or empty stdout fails before any
   prompt, naming the harness, and does not archive. Else `{session}` is a UUID the
   driver generated.
3. Drive `first` / `resume` with `{session}` and `{prompt}` as today.
4. Collect the transcript via the configured glob. A missing transcript leaves
   `transcript` null in the manifest, as Claude already does — do not invent a path.
5. Zip the run.

Create is not a prompt. Its stdout is the session id, so it is captured rather than
streamed. The prompts still stream, because watching them is the only progress a
minutes-long trial has.

## Testing

Structural only. No live `agent` run, no network in CI.

- Optional `create` is accepted; `first`, `resume`, and `transcript` stay required.
- A harness with `create` uses stripped stdout as `{session}` before `first` runs.
- A failing or empty create names the harness and never reaches a prompt.
- The Cursor row parses. Claude still works with no `create`.
