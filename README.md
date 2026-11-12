# android-agent-toolkit

A small set of Claude Code skills and agents that help an Android developer
take a new Kotlin/Compose project from architecture choices to implemented,
checked features, with honest records of what was actually verified.

## Status

Early beta. One capability exists. It has been structurally validated; it has
not yet been exercised in a Claude Code session or used to generate an Android
project.

| Level | Meaning | Current state |
|---|---|---|
| Implemented | The files exist and pass the structural validator | Architecture skill, architect agent |
| Exercised in Claude | A real Claude Code session discovered and invoked the asset | Not yet |
| Verified in Android | A consumer project produced with the asset built and ran | Not yet |
| Planned | Not started | See the roadmap below |

Details and the next action are in [docs/status.md](docs/status.md). The
evidence behind this table is in
[docs/verification/bootstrap.md](docs/verification/bootstrap.md).

## Quickstart

Prerequisites: Claude Code, and an Android app repository (new or early-stage)
that you want to structure. The toolkit is Claude Code only.

1. Copy the skill directory and the agent file into your app's `.claude/`
   folder, following [docs/installation.md](docs/installation.md).
2. Open Claude Code in your app repository and run:

   ```
   /android-select-architecture . <your-first-feature-name>
   ```

   or ask in plain language, for example "choose a module structure for this
   app before I build the first feature".
3. Review the architecture decision Claude writes, then let it scaffold and
   run the checks your environment allows.

Because the skill has not yet been run end to end, treat the first run as a
trial and check its output.

## Capabilities

| Asset | Type | Inputs | Output | Evidence |
|---|---|---|---|---|
| [`android-select-architecture`](.claude/skills/android-select-architecture/SKILL.md) | Skill | Project path, app/package name, first feature name and scope, existing files, environment, preferences | Inspection summary, recorded architecture decision, module scaffold, check results, open gaps | Structural validation only |
| [`android-architect`](.claude/agents/android-architect.md) | Agent (read-only) | A recommend or review request, project path, feature names | Recommended boundaries or review findings, trade-offs, checks for the caller to run | Structural validation only |
| [`validate_toolkit.py`](scripts/validate_toolkit.py) | Maintainer script | Toolkit root | Exit 0 or a list of structural errors | Fixture tests, see the verification record |

## Workflow

Every capability follows the same five steps.

1. **Inspect** - read the project and the environment before deciding.
2. **Plan** - choose and record a decision, with alternatives and reasons.
3. **Implement** - change only what the plan lists.
4. **Verify** - run real checks; record commands and results.
5. **Report** - say what passed, what failed and what was not run.

How the skill, the agent and your Claude session relate is described in
[docs/architecture.md](docs/architecture.md).

## Installation and consumer guidance

- [docs/installation.md](docs/installation.md) - manual, selective install,
  conflict handling, version recording and removal.
- [templates/consumer-claude-guidance.md](templates/consumer-claude-guidance.md) -
  a section to merge into your app's existing `CLAUDE.md`. Do not replace your
  file with it, and do not copy this repository's `CLAUDE.md`, which is for
  toolkit maintainers.

## Sample application

There is no sample application yet. It will be a separate repository and will
be linked here once it exists and has been built.

## Limitations

- No runtime evidence yet: discovery by Claude Code and Android generation are
  both unverified.
- The architecture skill targets new or early-stage Kotlin/Compose apps. It
  does not migrate legacy code.
- The validator checks structure, metadata and local links. It says nothing
  about instruction quality or Android correctness.
- Installation is manual. There is no installer, plugin package or
  marketplace command.
- No hooks are shipped.

## Roadmap

Planned, not built. Each step adds a toolkit capability and then demonstrates
it in the separate sample repository.

| Step | Toolkit capability | Demonstration |
|---|---|---|
| 1 | Architecture skill and architect agent (implemented, unverified) | Generate and verify an architecture foundation |
| 2 | Feature skill and builder agent | Add a first feature |
| 3 | Persistence skill | Local database storage |
| 4 | Unit-testing skill and test agent | Behavioural tests |
| 5 | Feature workflow improvements | Edit and complete flows |
| 6 | UI-testing and device-verification skills | User journeys on a device |
| 7 | Security and release-verification skills | Local data review, minified build |
| 8 | Packaging and beta documentation | Clean install and reproducibility |

## Attribution

The toolkit's structure and approach were informed by several public
projects. No files were copied from them. See
[docs/references.md](docs/references.md).

## License

Copyright 2026 synchz. Licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE) and [NOTICE](NOTICE). The software is provided "as is",
without warranties of any kind.

Skills and agents you copy into your own project remain under this license;
keep the notice when you redistribute them. Code that Claude generates in
your project while following them is yours.
