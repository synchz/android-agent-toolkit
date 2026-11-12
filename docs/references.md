# Sources and attribution

## Claude Code documentation

Consulted on 12 November 2026 to choose file locations and frontmatter fields.

| Page | Used for |
|---|---|
| [Skills](https://code.claude.com/docs/en/skills) | Project skill location `.claude/skills/<name>/SKILL.md`; frontmatter fields; supporting files referenced by relative links; the listing limit for descriptions; when a reload is needed |
| [Subagents](https://code.claude.com/docs/en/sub-agents) | Project agent location `.claude/agents/`; required `name` and `description`; `tools` and `skills` fields; how agents are invoked; when a restart is needed |
| [Project instructions](https://code.claude.com/docs/en/memory) | Role of `CLAUDE.md`. Not re-read for this work |
| [Quickstart](https://code.claude.com/docs/en/quickstart) | Installation pointer for users. Not re-read for this work |

Coverage: both pages were read to the end, in two passes each. The first pass
(about the first 100,000 characters) contained the frontmatter reference
tables and was read through an automated fetch that summarises content, so
field names and limits there were not seen verbatim. The second pass (the
remainder: sharing, examples and troubleshooting) was read as page text and
added no frontmatter fields. Re-check the pages before adding a field.

What the documentation requires, as used by the validator:

| Asset | Required by Claude Code | Not required by Claude Code |
|---|---|---|
| Skill | Frontmatter opens with `---` on the first line. Name must not contain control, zero-width, private-use, unassigned or direction-changing characters, non-plain blanks, leading or trailing spaces, `<` or `>` | Every field is optional. `name` defaults to the directory name; `description` is recommended. Unknown fields are ignored without an error. No maximum name length is stated |
| Subagent | `name` and `description`. Name is at most 256 characters, cannot start with `-` or contain `:` | The file name does not have to match `name`. Unknown fields are ignored |

Other documented behaviour relied on:

- A skill's `description` plus `when_to_use` is truncated at 1,536 characters
  in the listing Claude sees.
- If a skill's frontmatter YAML is malformed, Claude Code loads the body with
  empty metadata; `claude --debug` shows the parse error.
- Supporting files are referenced from `SKILL.md` by relative links.
- To confirm a skill is available, ask "What skills are available?".
- Existing `.claude/skills/` and `.claude/agents/` folders are watched. A
  folder that did not exist at session start needs `/reload-skills` (skills)
  or a restart (agents).
- A subagent's `skills` field injects the named skills' content at startup.
  The documentation does not say what happens when a named skill is absent.
- `claude plugin validate <dir>` is documented as finding `SKILL.md` files
  whose frontmatter does not parse. On version 2.1.316 it did not flag a
  deliberately broken copy, so this toolkit does not rely on it.

Fields this toolkit uses:

- Skill: `name`, `description`, `argument-hint`, and the `$ARGUMENTS`
  substitution in the body.
- Agent: `name`, `description`, `tools`, `skills`.

## Projects that informed the design

These were reviewed as described in the project's planning notes dated 12
November 2026. They were not cloned or re-audited while building this
repository, and no files, text or code were copied from them. The
descriptions below are observations, not claims that this toolkit matches
their capabilities or is endorsed by their authors.

| Project | Pattern observed | How it shaped this toolkit | Boundary |
|---|---|---|---|
| [android/skills](https://github.com/android/skills) | Modular `SKILL.md` instructions with supporting resources, organised by Android topic | Focused skills with clear triggers, outputs and verification steps | Starting with an architecture workflow is this toolkit's own choice. No endorsement is implied |
| [android/architecture-samples](https://github.com/android/architecture-samples) | Compose, ViewModels, coroutines and Flow, repositories over data sources, Hilt, several kinds of tests | The architecture skill is grounded in these familiar, testable patterns | Upstream describes itself as a sample, not a template. The separate domain module and five-module default are this toolkit's extension |
| [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | Role-based agents, workflow skills, documentation, and explicit limits on what has been verified | Small specialist roles, explicit handoffs, evidence levels kept distinct | Its hierarchy and large agent roster were deliberately not adopted |
| [skydoves/android-testing-skills](https://github.com/skydoves/android-testing-skills) | Identified in earlier research as a collection of Android testing skills | None yet | To be inspected when testing capabilities are built |

## Licensing

This repository is licensed under the Apache License, Version 2.0. The
`LICENSE` file is the unmodified text from apache.org and the copyright line
is in `NOTICE`.

Nothing from the projects above is included, so no upstream notices apply
today. Before reusing any upstream content in future, check that project's
current license for compatibility, keep its notices and record it in
`NOTICE`.
