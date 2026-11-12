# Bootstrap verification record

Date: 12 November 2026 (two passes on the same day)
Scope: first capability (architecture skill, architect agent, documentation,
validator). Toolkit only; no consumer project exists.

**Result: toolkit implemented and structurally valid. Claude discovery and
invocation not verified, blocked by an expired sign-in. Android generation
remains unverified until the toolkit is used and checked in the separate
sample repository.**

## Environment

| Item | Value |
|---|---|
| Operating system | Windows 11 Home Single Language, 10.0.26200 |
| Shell | Windows PowerShell 5.1 |
| Claude Code | 2.1.316 |
| Git | 2.51.0.windows.1 |
| Python (`python`) | 3.10.11 |
| Python (`py`) | 3.13.7 |
| JDK, Android SDK, Gradle, device | Not checked; not needed for this stage |

## Git state

| Item | Value |
|---|---|
| Repository | Initialised in the toolkit folder only, with `git init -b beta` (exit 0). The parent folder is not a Git repository |
| Branch | `beta` |
| Revision | Both passes ran before any commit existed. See `git log` for the first commit, which followed them |
| Working tree during the passes | All toolkit files untracked |
| Remotes during the passes | None |

The results below are tied to the working tree as it stood when the commands
were run. Publication to a public GitHub repository was requested by the
owner afterwards and is not part of the bootstrap task.

## Pass 2: validator review, documentation check, smoke-test attempt

### Validator review

The validator did not say which of its rules come from Claude Code and which
are this repository's choices, and several conventions read as if they were
requirements. Changes made:

| Change | Detail |
|---|---|
| Source tags | Every finding is printed as `[claude]` or `[toolkit]`. The split is documented in the script's header and in [../architecture.md](../architecture.md) |
| Added Claude rule | Skill names are checked against the documented list of refused characters. Previously only the stricter toolkit pattern was checked |
| Reclassified | Skill `name` and `description` being present, name matching the path, lowercase-hyphen names, unknown fields, empty body and the preloaded-skill check are now labelled as toolkit conventions. Claude Code requires none of them |
| Parser limits | YAML the validator cannot read (nested mappings and similar) is tagged `[toolkit]`, since it may be valid for Claude Code |
| Tests | 8 added: refused skill names, listing limit, agent `description` and `:` in a name, and three that assert the tags themselves |

### Documentation check

The remaining part of both official pages was read (see
[../references.md](../references.md)). It contained no further frontmatter
fields, so the field lists are unchanged. It did add: malformed skill YAML is
loaded with empty metadata rather than refused; "What skills are available?"
is the documented way to confirm a skill; and `claude plugin validate` exists.

One limitation remains: the frontmatter tables themselves were read through a
summarising fetch, not verbatim.

### Commands and results

All run from the toolkit root.

| # | Command | Exit code | Result |
|---|---|---|---|
| 1 | `python scripts/validate_toolkit.py` | 0 | Passed. `OK: structural checks passed, 0 warning(s).` |
| 2 | `python scripts/test_validate_toolkit.py` | 0 | Passed. `Ran 33 tests ... OK` |
| 3 | `claude plugin validate .claude/skills` | 0 | "Validation passed" |
| 4 | `claude plugin validate .claude/agents --strict` | 0 | "Validation passed" |
| 5 | `claude plugin validate .claude --strict` | 0 | "Validation passed" |
| 6 | Commands 3 and 4 against a temporary copy with an unclosed YAML list in the skill description, a misspelt skill field and the agent's `name` removed | 0 and 0 | "Validation passed" for both. **The tool did not detect the defects**, and its JSON report listed no inspected contents. Results 3 to 5 are therefore not counted as evidence |
| 7 | `claude -p "<ask whether the skill and agent are listed>" --max-turns 1` | 1 | Failed before running: `Failed to authenticate: OAuth session expired and could not be refreshed`. One attempt was made in this pass and it was not retried |

Commands 1 and 2 were run again after the documentation edits in this pass,
with the same results.

### Smoke test

A planning-only smoke test for the skill and the agent is written in
[smoke-test-architecture.md](smoke-test-architecture.md): discovery, the
skill stopping at a decision, delegation to the agent with its output
contract, and a case where the five-module default should not be chosen. It
creates no files and no Android code.

**It has not been run.** Command 7 is its first step and it stopped at
sign-in.

Action needed to unblock: in a terminal, run `claude`, enter `/login`,
complete the browser sign-in, then exit. Check with
`claude -p "Reply with the word ready"`, which must print a reply and exit 0.
After that the smoke test can be run from a fresh session in the toolkit
folder.

## Pass 1: bootstrap

| # | Command | Exit code | Result |
|---|---|---|---|
| 1 | `python scripts/validate_toolkit.py` | 0 | Passed |
| 2 | `py scripts/validate_toolkit.py` (Python 3.13.7) | 0 | Passed |
| 3 | `python scripts/test_validate_toolkit.py` | 0 | Passed, 25 tests at that time |
| 4 | `python scripts/validate_toolkit.py --root ..` (the parent planning folder, which is not a toolkit) | 1 | Rejected as expected with 29 errors: 14 missing required files and 15 portability findings in planning documents |
| 5 | `claude agents` | 1 | Not usable as a check. It requires an interactive terminal |
| 6 | `claude agents --json` | 0 | Not a discovery check. In this version it lists running sessions, not agent definitions |
| 7 | `claude -p "<ask whether the skill and agent are listed>" --max-turns 1` | 1 | Failed before running: same authentication error as above |

Correction: the first version of this record said the 25 tests held 23 defect
cases. The correct count was 22.

## What the fixture tests cover

Each test copies the toolkit into a temporary directory, introduces one
defect and asserts that the validator reports it. The working tree is not
modified. Of the 33 tests, 2 cover valid input and command-line exit codes
(0, 1 and 2), 1 confirms that a link inside a code block is ignored, and 30
each introduce a defect.

| Defect | Source tag | Observed |
|---|---|---|
| Skill with no frontmatter | claude | Rejected |
| Skill with unclosed frontmatter | claude | Rejected |
| Skill value with an unquoted colon-space | claude | Rejected |
| Skill name containing `<` and `>` | claude | Rejected |
| Skill name containing a zero-width character | claude | Rejected |
| Skill description over 1,536 characters | claude | Rejected |
| Agent missing `name` | claude | Rejected, and the only finding carries the claude tag |
| Agent missing `description` | claude | Rejected |
| Agent name containing `:` | claude | Rejected |
| Agent file removed | toolkit | Rejected |
| Skill reference file removed | toolkit | Rejected, with the broken link also reported |
| Skill missing `description` | toolkit | Rejected |
| Skill `name` different from directory | toolkit | Rejected, and every finding carries the toolkit tag |
| Skill with a misspelt field | toolkit | Rejected |
| Skill with empty body | toolkit | Rejected |
| Skill directory without `SKILL.md` | toolkit | Rejected |
| Supporting file not linked from `SKILL.md` | toolkit | Rejected |
| Agent with an undocumented field | toolkit | Rejected |
| Agent with a nested `hooks` mapping | toolkit | Reported as unsupported by the validator, not as a Claude error |
| Agent preloading a skill that does not exist | toolkit | Rejected |
| Agent `name` different from file name | toolkit | Rejected |
| Broken link in README | toolkit | Rejected |
| Skill link pointing outside its directory | toolkit | Rejected |
| Link pointing outside the repository | toolkit | Rejected |
| Reference to a sibling planning folder | toolkit | Rejected |
| Author-machine absolute path | toolkit | Rejected |
| Example-app name in a reusable asset | toolkit | Rejected |
| Gradle settings file added | toolkit | Rejected |
| Missing README through the command line | toolkit | Exit 1 with a tagged message |

The 30 defect tests cover the first 28 rows: two of them reuse a defect (the
missing agent `name` and the mismatched skill `name`) to assert the source
tag. The last row comes from the command-line test.

## Summary

| Item | State |
|---|---|
| Required files present | Passed |
| Skill and agent metadata meet documented Claude Code rules, as far as the validator checks them | Passed |
| Skill and agent metadata meet toolkit conventions | Passed |
| Local links resolve | Passed |
| Validator rejects invalid fixtures | Passed, 30 defect tests over 28 distinct defects |
| No bundled Android application or Gradle project | Passed |
| Independent check with `claude plugin validate` | **Inconclusive.** It passes, but it also passes broken input |
| Planning-only smoke test prepared | Done |
| Skill discovered by Claude Code | **Not run.** Blocked by sign-in |
| Agent discovered by Claude Code | **Not run.** Blocked by sign-in |
| Skill invoked in a session | **Not run** |
| Agent delegated to, with skill preloaded | **Not run** |
| Installation steps carried out on a consumer project | **Not run.** No consumer project exists |
| Android project generated, built, tested, launched | **Not run** |

## Remaining gaps

- No runtime evidence of any kind. Everything that passed is a check on file
  structure.
- The validator reads only a subset of YAML. Frontmatter it accepts could
  still be rejected by Claude Code's parser, and the one tool that would
  confirm this locally did not prove reliable.
- The frontmatter field tables were read through a summarising fetch.
- The agent's `skills` preload and `tools` restriction are written as
  documented but have not been observed working. What Claude Code does when
  a preloaded skill is missing is undocumented.
- Whether a typed `/skill-name` works in print mode on this version is
  unconfirmed; the smoke test's headless prompts avoid depending on it.
- The results above were recorded before the first commit, against the
  working tree. The first commit contains that tree plus the license files;
  the validator and tests were rerun on it before committing (exit 0, 33
  tests).

## What remains to be run

1. Sign in, as described under "Smoke test" above.
2. Run [smoke-test-architecture.md](smoke-test-architecture.md) from a fresh
   session in the toolkit folder and record its results table here and in
   [../status.md](../status.md).
3. Then the consumer stage, in a separate repository: install following
   [../installation.md](../installation.md), repeat discovery, run the skill,
   build the result, and record both revisions.
