# Planning-only smoke test: architecture skill and architect agent

Status: **prepared, not run.** One attempt to start it on 12 November 2026
stopped at sign-in (see [bootstrap.md](bootstrap.md)). Nothing below has been
observed yet.

## Purpose and limits

This test shows whether Claude Code, in this repository, discovers the two
assets and follows them far enough to produce an architecture decision and an
architect report. It is planning only: no files are created, no Gradle or
Android code is generated, and nothing is built.

Passing it moves the assets from "structurally valid" to "exercised in
Claude". It does not show that a scaffold compiles or that the installation
steps work in another repository. Those belong to the consumer stage.

## Prerequisites

1. Signed in to Claude Code. From a terminal run `claude`, then `/login`, and
   complete the browser sign-in. Confirm with
   `claude -p "Reply with the word ready"`; it must print a reply and exit 0.
2. Current directory is the toolkit root, so the project skill and agent are
   in scope.
3. A fresh session. The `.claude/skills/` and `.claude/agents/` folders were
   created after earlier sessions started.
4. An empty scratch directory outside the toolkit to act as the target
   project. It stays empty for the whole test.

Setup, PowerShell:

```powershell
$Scratch = Join-Path $env:TEMP "toolkit-smoke-target"
New-Item -ItemType Directory -Force $Scratch | Out-Null
Get-ChildItem -Force $Scratch          # expect no output
git status --short > "$env:TEMP\toolkit-smoke-git-before.txt"
```

Setup, Bash:

```bash
SCRATCH="${TMPDIR:-/tmp}/toolkit-smoke-target"
mkdir -p "$SCRATCH"
ls -A "$SCRATCH"                       # expect no output
git status --short > "${TMPDIR:-/tmp}/toolkit-smoke-git-before.txt"
```

The fictional app used throughout is deliberately not the series' demo app:
name "Field Notes", base package `com.example.fieldnotes`, first feature
`notes`.

## How to run

Interactive is the reference method, because it shows the slash-command menu
and the delegation to the agent as they happen. Start it in plan mode so that
Claude Code itself blocks edits:

```
claude --permission-mode plan --add-dir <scratch path>
```

Headless is an alternative for S1, S2 and S4 when a transcript file is wanted.
Whether a typed `/skill-name` works in print mode has not been confirmed for
this version, so the headless prompts name the skill in words instead:

```
claude -p "<prompt>" --permission-mode plan --add-dir <scratch path> --output-format stream-json --verbose > <transcript file>
```

Run each case once. If a case fails, record the failure; do not rephrase the
prompt until it passes.

## Cases

### S1. Discovery

Prompt:

```text
Without using tools: what skills are available in this project, and which
subagent types can you delegate to? List names and descriptions.
```

Then, interactive only: type `/android-sel` and look at the menu.

| Check | Pass when |
|---|---|
| S1.1 Skill listed | The answer names `android-select-architecture` with the description from its frontmatter |
| S1.2 Agent listed | The answer names `android-architect` with the description from its frontmatter |
| S1.3 Slash menu | `/android-select-architecture` is offered, with the hint `[project-path] [first-feature-name]` |

If S1.1 or S1.2 fails, stop. Run `claude --debug` and look for a frontmatter
parse error before changing any file.

### S2. Skill, planning only

Prompt (interactive):

```text
/android-select-architecture <scratch path> notes

Planning only. App name: Field Notes. Base package: com.example.fieldnotes.
The notes feature lets one user create, list and delete short text notes on
the device. More features are planned and two developers will work on it.
Do steps 1 to 3 of the skill and show me the decision you would record in
step 4, in your reply. Do not create or change any file, do not run Gradle,
and do not scaffold. Finish with the skill's report.
```

Headless: replace the first line with "Use the android-select-architecture
skill for the project at `<scratch path>`, first feature `notes`."

| Check | Pass when |
|---|---|
| S2.1 Skill loaded | The transcript shows the skill being invoked, not only similar advice |
| S2.2 Reference read | The supporting reference inside the skill directory is read before the decision |
| S2.3 Inspection first | The reply reports that the target directory is empty and states which tools (JDK, Gradle, SDK, device) are available, missing or not checked, without guessing |
| S2.4 Consumer names | Modules, packages and classes use `notes` and `com.example.fieldnotes`. No `tasks` feature or other example name appears |
| S2.5 Justified variant | One variant is chosen with reasons tied to the stated facts (several features, two developers), and at least one alternative is rejected with a reason |
| S2.6 Module table | Each module has a responsibility and allowed dependencies; domain depends on no project module; the feature module does not depend on data |
| S2.7 No padding | Every use case named has a rule it enforces; an in-memory data source is the default and its consequence is stated |
| S2.8 Versions | No library or plugin version is asserted from memory; the reply says versions will be looked up when scaffolding |
| S2.9 Honest report | The five report sections are present; every check is "not run"; the final state is "decided only" |
| S2.10 No side effects | The scratch directory is still empty and `git status --short` in the toolkit is unchanged |

### S3. Architect agent

Prompt:

```text
Use the android-architect subagent to recommend a module structure for a new
Android app at <scratch path>. App: Field Notes, base package
com.example.fieldnotes, first feature notes (create, list and delete short
text notes on the device). More features are planned; two developers.
Return its report to me unchanged, then tell me separately whether you
agree. Do not create or change any file.
```

| Check | Pass when |
|---|---|
| S3.1 Delegated | The transcript shows a subagent run of type `android-architect`. An answer written by the main session alone is a fail |
| S3.2 Output contract | The report has the six sections in order: Request understood, Evidence inspected, Recommendation, Trade-offs, Checks for the invoking session, Open questions |
| S3.3 Skill preload | The report applies the variants and dependency rules from the skill's reference, or states plainly that the skill content was not available to it. Record which. This is the only observation of the `skills` preload |
| S3.4 Read-only | The subagent used only `Read`, `Glob` and `Grep`; it wrote nothing and ran no command |
| S3.5 No build claims | Nothing is described as building, running or passing; the checks section lists commands for the caller |
| S3.6 Consumer names | As S2.4 |
| S3.7 No orchestration | The agent did not scaffold, and the main session did not start scaffolding on its own after the report |
| S3.8 No side effects | As S2.10 |

### S4. Simplification

Tests that the five-module default is not imposed.

Prompt:

```text
Use the android-select-architecture skill, planning only, for the project at
<scratch path>. App: Tip Split, base package com.example.tipsplit. It is a
single-screen calculator with no stored data, built by one developer as a
weekend project, and no further features are planned. Feature name:
calculator. Show the decision in your reply. Do not create or change files.
```

| Check | Pass when |
|---|---|
| S4.1 Simpler variant | The single-module or three-module variant is chosen, with the reason, and the reply says what would trigger moving up |
| S4.2 No unused parts | No data module, repository or use case is proposed without a stated job |
| S4.3 No side effects | As S2.10 |

## After the run

PowerShell:

```powershell
Get-ChildItem -Force $Scratch          # expect no output
git status --short > "$env:TEMP\toolkit-smoke-git-after.txt"
Compare-Object (Get-Content "$env:TEMP\toolkit-smoke-git-before.txt") (Get-Content "$env:TEMP\toolkit-smoke-git-after.txt")   # expect no output
Remove-Item $Scratch
```

Bash:

```bash
ls -A "$SCRATCH"                       # expect no output
git status --short | diff "${TMPDIR:-/tmp}/toolkit-smoke-git-before.txt" -   # expect no output
rmdir "$SCRATCH"
```

`Remove-Item` without `-Recurse` and `rmdir` both refuse a non-empty
directory, which is itself a check that nothing was written.

## Recording results

Copy this table into [bootstrap.md](bootstrap.md) with real values. Use
"pass", "fail" or "not run"; for a fail, quote the relevant line. Keep
transcripts out of the repository unless they have been reviewed for anything
private.

| Field | Value |
|---|---|
| Date | |
| Claude Code version | |
| Model | |
| Method | interactive / headless |
| Toolkit revision, and whether the tree was clean | |
| S1.1 to S1.3 | |
| S2.1 to S2.10 | |
| S3.1 to S3.8 | |
| S4.1 to S4.3 | |
| Deviations from this procedure | |

A pass here is one run on one model. It shows the assets can work, not that
they work reliably.
