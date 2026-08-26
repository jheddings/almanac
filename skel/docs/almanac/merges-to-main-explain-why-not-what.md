---
title: Merges to main explain why, not what
kind: rule
recorded: 2026-08-26
source: "Project conventions, set when this repository was initialized"
tags: [git, commits, history, conventions]
---

**Applies when:** you are about to merge a branch to `main`.

The commit body explains **why** the change was made: the constraint it satisfies, the
alternative it rejected, the thing that would otherwise have broken. The diff already
says what changed — do not restate it.

**Why:** `main`'s history is this repository's record of its own decisions. A body that
paraphrases the diff leaves the reasoning nowhere, so the next person re-derives it from
scratch, or repeats a choice that was already considered and turned down.
