# Consumer guidance: android-agent-toolkit

This is a template for an Android app repository that has installed assets
from android-agent-toolkit. Merge the section below into the app's existing
`CLAUDE.md`. Do not replace that file, and do not copy the toolkit's own
maintainer `CLAUDE.md` into the app. If the app has no `CLAUDE.md`, create one
with the app's own instructions and add this section to it.

Replace each `<placeholder>`. Delete lines that do not apply.

---

## Android toolkit assets

Installed from android-agent-toolkit, revision `<toolkit commit or version>`,
on `<date>`.

| Asset | Path | Use |
|---|---|---|
| Architecture skill | `.claude/skills/android-select-architecture/` | Select, record and scaffold the module structure |
| Architect agent | `.claude/agents/android-architect.md` | Read-only boundary recommendations and reviews |

These files are owned by the toolkit. Do not edit them here; change them
upstream and reinstall, so the recorded revision stays true.

### Working rules

- Architecture decision record: `<path, e.g. docs/architecture/001-architecture-decision.md>`.
  Read it before adding a module or a cross-module dependency. Changing the
  structure means updating the record first.
- Use the `android-select-architecture` skill when establishing or revisiting
  the module structure. Use the `android-architect` agent when a second
  opinion or a boundary review is wanted; it reports and does not edit.
- Report a build, test or device check as passed only with the command and
  its result. A check that could not run is "not run", with the reason.

### Project facts

- Base package: `<base package>`
- Build command: `<e.g. ./gradlew assembleDebug>`
- Unit test command: `<e.g. ./gradlew testDebugUnitTest>`
- Environment notes: `<JDK version, SDK location, device or emulator availability>`
