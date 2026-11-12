---
name: android-select-architecture
description: Select, record and scaffold a layered modular architecture for a new or early-stage Android app built with Kotlin and Jetpack Compose. Use when starting an Android project, choosing module boundaries, deciding between a single-module and multi-module structure, or preparing the foundation before the first feature is built.
argument-hint: "[project-path] [first-feature-name]"
---

# Select an Android architecture

Arguments supplied with this invocation: `$ARGUMENTS`

Take a new or early-stage Android project from "no agreed structure" to a
recorded architecture decision, a module scaffold that matches it, and real
check results. The patterns, module variants and dependency rules you apply are
in [references/clean-architecture.md](references/clean-architecture.md). Read
that file before step 3.

This skill covers the architecture foundation only. It does not build feature
screens, add database persistence, write the test suite or prepare a release.

## Inputs

Resolve each input from the invocation arguments, the conversation and the
project files first. Ask the user only for a missing input that blocks safe
progress, and ask for all of them in one message.

| Input | How to resolve it |
|---|---|
| Target project path | Argument, else the current working directory. Confirm it is the app repository, not this toolkit's own repository. |
| App name and base package | Existing `settings.gradle(.kts)`, `namespace`/`applicationId`; otherwise ask. |
| First feature name | Argument or the user's request. Use the user's name for it everywhere (module, package, classes). Never substitute an example name. |
| Feature scope | What the first feature must do and what is explicitly out of scope. |
| Existing files | Inspect; never assume an empty directory. |
| Environment | Which of JDK, Android SDK, Gradle wrapper and device/emulator are actually available. |
| Architecture preferences | Stated constraints such as single module, a different DI library, or minimum SDK. Stated preferences override this skill's defaults. |

## Procedure

### 1. Inspect

Read before deciding. Record what you found, including what is absent.

- Top-level layout, `settings.gradle(.kts)`, included modules, `gradle/libs.versions.toml`, Gradle wrapper version, existing `CLAUDE.md` and docs.
- For each existing module: applied plugins, dependencies on other modules, DI, navigation and UI approach.
- Git state. If there are uncommitted user changes, do not overwrite or revert them; work around them or ask.
- Environment: run version checks (`java -version`, the Gradle wrapper with `--version`, `adb version`) and note each tool as available, missing or not checked. Do not infer availability.

If the project already has several modules or substantial code, stop treating
this as a greenfield selection. Summarise the existing structure, compare it
with the reference, and propose incremental changes for the user to approve.
Do not restructure existing code as a side effect of this skill.

### 2. Resolve blocking decisions

Ask only when the answer changes the structure and cannot be read from the
project: base package, first feature name, minimum SDK when nothing sets it,
or a DI/persistence preference the user hinted at. State the default you will
use for anything you do not ask about.

### 3. Decide

Choose one variant from the reference (single module with packages, three
modules, or the five-module default) and justify it against this app's
expected size, team, number of features and build needs. The five-module
structure is a default for apps expected to grow, not a requirement. If a
simpler variant fits, choose it and say what would trigger moving up.

For the chosen variant, write down:

- Each module, its single responsibility and its allowed dependencies.
- Where the first feature's UI, state holder, domain contract and data implementation live.
- Which use cases exist and what rule each one enforces. Do not create a use case that only forwards a call to a repository.
- The first data source. Default to an in-memory repository implementation unless the user asked for persistence now.
- What is deliberately deferred.

For a second opinion on boundaries or a review of an existing structure, the
main session may delegate analysis to the `android-architect` agent if it is
installed. This skill never does that automatically. The agent returns
recommendations; the session using this skill still makes and records the
decision.

### 4. Record the decision

Before generating code, write the decision into the target project, in its
existing decisions/docs location if it has one, otherwise
`docs/architecture/001-architecture-decision.md`. Include: context, chosen
variant, module table with dependencies, rejected alternatives with reasons,
deferred items and the checks that will show the structure holds.

Present the decision and the list of files you intend to create. If the user
has not already asked you to scaffold, wait for confirmation here.

### 5. Scaffold

Create only what the decision lists.

- Versions: do not write versions from memory. Look up current stable, mutually compatible versions of the Android Gradle Plugin, Kotlin, the Compose BOM, Hilt and the Gradle wrapper in official documentation and pin them in `gradle/libs.versions.toml`. Record where each came from. If you cannot look them up, say so and mark the pinned versions as unverified.
- Gradle wrapper: if the project has no wrapper, generate it with an installed `gradle wrapper` or ask the user to create the project shell from Android Studio. Never hand-write or fabricate `gradle-wrapper.jar`.
- Modules: follow the plugin and dependency rules in the reference. Keep the domain module free of Android, Compose and persistence types.
- Wiring: the application module binds data implementations to domain contracts. Feature code depends on domain contracts only.
- Scope: add the minimum code that proves the wiring works end to end for the first feature, such as one model, one repository contract, one in-memory implementation, one state holder and one screen that renders its state. Leave full feature behaviour to feature work.
- Do not add placeholder modules, empty use cases, unused dependencies or sample content unrelated to the user's feature.

### 6. Verify

Run the checks that the environment allows, from the target project root, and
capture the exact command, exit code and the relevant output lines. On Windows
use `.\gradlew.bat`; elsewhere `./gradlew`.

| Check | Command | Shows |
|---|---|---|
| Modules resolve | `./gradlew projects` | Settings include every decided module |
| Build | `./gradlew assembleDebug` | All modules compile and the app packages |
| Unit tests | `./gradlew testDebugUnitTest` and `./gradlew test` for pure Kotlin modules | Existing tests pass; report "no tests" honestly |
| Domain purity | `./gradlew :<domain-module>:dependencies --configuration compileClasspath` | No Android, Compose or persistence artifacts on the domain classpath |
| Dependency direction | Read each module's build file against the decision table | No feature-to-data or domain-to-anything project dependency |
| Launch, only if a device or emulator is attached | `./gradlew installDebug` then start the launcher activity | The app starts and shows the first screen |

A check that cannot run is "not run" with the reason (for example "Android SDK
not found"). It is never reported as passed. If a check fails, fix the cause
and rerun; do not weaken the check or remove a module to make it pass without
recording that change in the decision.

### 7. Report

End with a report in this shape:

1. **Inspected** - project path, what existed, environment availability.
2. **Decision** - variant, module table, where the decision record was written.
3. **Changes** - files created or modified, grouped by module.
4. **Verification** - each check with command, exit code and result: passed, failed or not run.
5. **Gaps** - unverified versions, checks not run, deferred work, open questions.

State plainly whether the architecture is "scaffolded and built", "scaffolded,
not built" or "decided only". Files existing is not evidence that they compile.
