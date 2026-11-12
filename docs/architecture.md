# Toolkit architecture

How the toolkit is organised and how its parts are meant to work together.
For what has actually been verified, see [status.md](status.md).

## Two repositories

| Repository | Contains |
|---|---|
| android-agent-toolkit (this one) | Reusable skills, agents, the validator, usage documentation |
| A consumer Android app (separate) | Android code, the app's own `CLAUDE.md`, Gradle build, tests, application evidence |

The toolkit never contains an Android application. Assets are copied from here
into a consumer app's `.claude/` folder. The reasons are in
[decisions/001-toolkit-and-consumer-separation.md](decisions/001-toolkit-and-consumer-separation.md).

## Layout

```text
README.md
CLAUDE.md                          maintainer instructions for this repository
.claude/
  skills/
    android-select-architecture/
      SKILL.md                     the procedure
      references/
        clean-architecture.md      variants and dependency rules
  agents/
    android-architect.md           read-only specialist
docs/                              this documentation
templates/
  consumer-claude-guidance.md      section to merge into an app's CLAUDE.md
scripts/
  validate_toolkit.py              structural validator
  test_validate_toolkit.py         fixture tests for the validator
docs/verification/
  bootstrap.md                     what was run, with results
  smoke-test-architecture.md       planning-only runtime test, not yet run
```

`.claude/skills/` and `.claude/agents/` hold the canonical assets. Everything
a skill needs sits inside its own directory, so copying that directory is
enough.

## Components and contracts

| Component | Responsibility | Output |
|---|---|---|
| Main Claude session | Reads the task, coordinates changes, runs checks, assembles evidence | A scoped change and a truthful report |
| Architecture skill | Repeatable procedure: inspect a project, select boundaries, record the decision, guide scaffolding, verify | Inspection summary, decision record, changes, check results, gaps |
| Architect agent | Specialist read-only analysis of requirements and dependencies | Recommended boundaries or review findings, trade-offs, checks to run |
| Validator | Structural checks on toolkit files | Nonzero exit when a required artifact is missing or invalid |
| Consumer build and tests | Verify generated Android code | Real Gradle and runtime results |

## How the skill and the agent relate

The skill is a procedure that the main session follows. The agent is a
separate context with read-only tools (`Read`, `Glob`, `Grep`) that returns a
report.

- The agent's definition preloads the skill through the documented `skills`
  field, so it reasons from the same reference on variants and dependency
  rules. It is instructed to apply only the analysis parts.
- The skill mentions the agent as an optional second opinion. It does not
  invoke it.
- Nothing is orchestrated automatically. An agent runs only when the main
  session delegates to it, either because the user names it ("use the
  android-architect agent to review the module boundaries") or because Claude
  matches the task to the agent's description.
- The main session owns the decision, all file changes and all checks. The
  agent's report is input, not evidence that anything builds.

Typical uses:

| Situation | What to do |
|---|---|
| New project, want a structure and a scaffold | Invoke the skill |
| Want boundaries assessed before committing to a structure | Ask for the agent, then invoke the skill with its recommendation |
| Scaffold exists, want it checked against its decision record | Ask for the agent to review |

## Default Android architecture the skill proposes

The skill's default for an app expected to grow is five modules: an
application module for entry, navigation composition and dependency wiring;
one module per feature for Compose UI and ViewModels; a pure Kotlin domain
module; a data module; and a design-system module. Feature code depends on
domain contracts, data implements them, and the application module wires
them. The skill also describes single-module and three-module variants and
requires a recorded reason for whichever it picks. The full rules travel with
the skill in
[clean-architecture.md](../.claude/skills/android-select-architecture/references/clean-architecture.md).

This is a description of what the skill should produce in a consumer project.
No such project has been generated yet.

## Validator

`scripts/validate_toolkit.py` needs Python 3.8+ and no third-party packages.

```
python scripts/validate_toolkit.py            # validate this repository
python scripts/validate_toolkit.py --root DIR # validate another copy
python scripts/test_validate_toolkit.py       # fixture tests
```

Exit code 0 means no structural errors, 1 means errors were listed, 2 means
the root directory was not found.

Every finding is printed with a source tag, so a failure says whether Claude
Code itself would object or only this repository does.

`[claude]`: documented Claude Code requirements and behaviour.

| Rule | What Claude Code does when it is broken |
|---|---|
| Frontmatter opens with `---` on line 1 and is closed | The file has no metadata |
| Frontmatter is parseable YAML | Loads a skill's body with empty metadata, so `/name` still works but the description cannot be matched |
| Skill name has no control, zero-width, private-use, unassigned or direction-changing character, no non-plain blank, no leading or trailing space, no `<` or `>` | Refuses the name |
| Skill `description` plus `when_to_use` is at most 1,536 characters | Truncates it in the skill listing |
| Subagent has `name` and `description` | Both are required |
| Subagent name is at most 256 characters, does not start with `-`, does not contain `:` | Not a valid name |
| `SKILL.md` is under 500 lines | A recommendation only; reported as a warning |

`[toolkit]`: conventions of this repository. Claude Code would accept a file
that breaks these.

| Convention | Why, and what Claude Code actually does |
|---|---|
| Required files exist | The repository's agreed layout |
| A skill declares `name` and `description` | Claude Code requires neither: `name` defaults to the directory name and `description` is only recommended |
| Skill name equals its directory; agent name equals its file stem | Claude Code uses the `name` field and does not compare it with the path. Matching keeps installation paths predictable |
| Names use lowercase letters, digits and single hyphens | Claude Code allows far more |
| Only documented frontmatter fields | Claude Code ignores unknown fields silently, which hides typos |
| Body is not empty; `tools`, when present, is not empty | Not addressed by the documentation |
| A skill preloaded by an agent exists here | The documentation does not say what happens when it is missing |
| Every supporting file in a skill directory is linked from `SKILL.md` | Claude loads supporting files only when the skill points to them |
| Relative links resolve, stay in the repository and, for skill files, stay in the skill directory | A skill is installed by copying its directory alone |
| No author-machine paths, no references to folders outside the repository, no example-app names in reusable assets | Portability and reuse |
| No Gradle or Android manifest files | The toolkit does not bundle an app |
| YAML outside the subset the validator can read (nested mappings, flow mappings, anchors) | May be valid for Claude Code; the validator cannot tell, so it stops |

The frontmatter field lists and the rules above were taken from the complete
skills and subagents pages. See [references.md](references.md).

It cannot check:

- whether Claude Code discovers, loads or correctly follows a skill or agent;
- whether the instructions are good or produce correct Android code;
- whether any Android project builds or runs;
- YAML in general. It parses only simple keys, quoted or plain values, block
  scalars and lists. Nested mappings, such as a `hooks` block, are reported as
  unsupported rather than validated.

Claude Code ships its own check, `claude plugin validate <dir>`. On version
2.1.316 it reported "Validation passed" for this repository's `.claude`
folders, but it also passed a deliberately broken copy (unclosed YAML list,
misspelt field, agent with no `name`), so its result is not used as evidence
here. See [verification/bootstrap.md](verification/bootstrap.md).

## Not included yet

Installer, plugin packaging, hooks, build or device scripts, and any
capability beyond architecture selection. They will be added when their
behaviour is defined and there is a consumer project to test them against.
