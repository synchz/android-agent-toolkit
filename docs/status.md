# Status

Last updated: 12 November 2026

**Toolkit implemented; Android generation not yet verified.**

## Evidence levels

| Asset | Structurally valid | Exercised in Claude | Verified in Android |
|---|---|---|---|
| `android-select-architecture` skill | Yes | No | No |
| `android-architect` agent | Yes | No | No |
| Manual installation steps | Not applicable | Not carried out | Not carried out |
| `validate_toolkit.py` | Fixture tests pass | Not applicable | Not applicable |

- **Structurally valid** means `scripts/validate_toolkit.py` exits 0. It says
  nothing about whether the instructions work.
- **Exercised in Claude** means a real Claude Code session listed and invoked
  the asset. Two attempts, one in each verification pass, could not run
  because the command-line sign-in had expired. This is still pending.
- **Verified in Android** means a consumer project produced with the asset
  built and ran with recorded results. No consumer project exists yet.

Commands, exit codes and environment are in
[verification/bootstrap.md](verification/bootstrap.md).

## Pending checks

1. **Blocked on sign-in.** Run `claude`, enter `/login`, complete the browser
   sign-in and exit. `claude -p "Reply with the word ready"` must then exit 0.
2. The planning-only smoke test in
   [verification/smoke-test-architecture.md](verification/smoke-test-architecture.md),
   from a fresh session in this repository. It covers discovery, the skill up
   to a decision, delegation to the agent with its preloaded skill and output
   contract, and a case that should not get five modules. It generates no
   Android code.
3. Installation into a consumer repository, following
   [installation.md](installation.md), then discovery there.
4. A full run of the skill in the consumer repository, with Gradle results.

## Open decisions

- Location, name and base package of the sample app repository.

Decided: Apache-2.0 license, copyright synchz; public repository under the
synchz GitHub account, default branch `beta`.

## Next action

Use the toolkit in a separate sample repository: create it outside this
folder, install the architecture skill and architect agent, run the skill for
the app's first feature, build it, and record both the toolkit revision and
the sample revision. Only after that can the architecture capability be
called verified.

## Not started

Feature, persistence, unit-testing, UI-testing, device-verification, security
and release capabilities; installer; plugin packaging; hooks.
