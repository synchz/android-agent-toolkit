# Maintaining android-agent-toolkit

These are instructions for working on the toolkit itself. They are not
instructions for an Android app that uses the toolkit; that guidance lives in
[templates/consumer-claude-guidance.md](templates/consumer-claude-guidance.md).
Never copy this file into a consumer project.

## Scope

- This repository contains reusable Claude Code assets for Android
  development: skills, agents, a validator and documentation.
- Claude Code only. Do not add adapters for other assistants.
- No Android application, Gradle project or sample app lives here. The
  demonstration app is a separate repository. See
  [docs/decisions/001-toolkit-and-consumer-separation.md](docs/decisions/001-toolkit-and-consumer-separation.md).
- Add one capability at a time. Do not create placeholder skills, agents,
  hooks or scripts for future work.

## Layout

- `.claude/skills/<name>/` - canonical skills. Anything a skill needs must be
  inside its own directory, because consumers copy that directory alone.
- `.claude/agents/<name>.md` - canonical agents.
- `templates/` - text consumers merge into their own files.
- `docs/` - how the toolkit works, how to install it, current status, sources,
  decisions and verification records.
- `scripts/` - the structural validator and its tests.

## Rules for reusable assets

- Portable: no absolute paths, no references to folders outside this
  repository, no dependence on the author's machine.
- Generic: use placeholders such as `<feature>`; never hardcode an example
  app's name, package or feature.
- Use only frontmatter fields documented for Claude Code skills and
  subagents. Check the current official documentation before adding a field,
  and update the field lists in `scripts/validate_toolkit.py` to match.
- Quote any frontmatter value that contains a colon followed by a space.
- Agents do not coordinate by existing. Describe who invokes what; do not
  write instructions that assume automatic orchestration.

## Evidence

Keep three levels distinct in every document and report:

1. **Structurally valid** - the validator passes.
2. **Exercised in Claude** - a real Claude Code session discovered and invoked
   the asset.
3. **Verified in Android** - a consumer project generated with the asset built
   and ran, with recorded commands and results.

Never report a higher level from evidence of a lower one. Record what was run,
its exit code and what was not run in `docs/verification/`, and keep
[docs/status.md](docs/status.md) current. The README lists only capabilities
that exist.

## Validation

Requires Python 3.8 or newer, standard library only. Run from the repository
root before proposing a commit:

```
python scripts/validate_toolkit.py
python scripts/test_validate_toolkit.py
```

Use `py` in place of `python` on Windows if that is how Python is installed.
When adding a validator rule, add a failing fixture test for it and tag the
rule `CLAUDE` only if the official documentation states it; everything else
is `TOOLKIT`. Do not present a toolkit convention as a Claude requirement.

Runtime behaviour is checked with
[docs/verification/smoke-test-architecture.md](docs/verification/smoke-test-architecture.md),
which needs a signed-in Claude Code session.

## Git

- Work on `beta` or a focused branch from it. Do not reset, force-checkout or
  rewrite history.
- Do not push, create remotes, merge, tag releases or publish anything unless
  the user asks for that specific action.
