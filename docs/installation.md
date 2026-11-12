# Installation

Installation is manual and selective: you copy one skill directory and one
agent file into your Android app's repository. There is no installer, plugin
package or marketplace command.

These steps have been written but not yet carried out against a real consumer
project. See [status.md](status.md).

## What gets installed

| Source in the toolkit | Destination in your app |
|---|---|
| `.claude/skills/android-select-architecture/` (the whole directory, including `references/`) | `.claude/skills/android-select-architecture/` |
| `.claude/agents/android-architect.md` | `.claude/agents/android-architect.md` |

Nothing else is copied. In particular, do not copy the toolkit's `CLAUDE.md`,
`docs/`, `scripts/` or `.gitignore` into your app.

The agent preloads the skill, so install both. If you install only the skill,
it works on its own. Installing only the agent is not supported.

## Before you copy

1. Have a local copy of the toolkit and note its revision:

   ```
   git -C <toolkit-path> rev-parse --short HEAD
   git -C <toolkit-path> status --short
   ```

   If the second command prints anything, the copy has uncommitted changes and
   the revision alone does not identify what you are installing. Commit or
   note that.

2. Check for name conflicts in your app. If either destination already
   exists, stop and decide deliberately: keep yours, or back it up and
   replace it. Do not merge the two by hand.

   Also check your user-level folders, `~/.claude/skills/` and
   `~/.claude/agents/`, for the same names. A same-named asset there can make
   it unclear which one Claude Code uses.

## Copy: PowerShell (Windows)

Set both paths explicitly. Run from anywhere.

```powershell
$Toolkit = "<path to android-agent-toolkit>"
$App     = "<path to your Android app repository>"

$SkillDst = Join-Path $App ".claude\skills\android-select-architecture"
$AgentDst = Join-Path $App ".claude\agents\android-architect.md"

if ((Test-Path $SkillDst) -or (Test-Path $AgentDst)) {
    Write-Error "Destination already exists. Resolve the conflict before installing."
} else {
    New-Item -ItemType Directory -Force (Join-Path $App ".claude\skills") | Out-Null
    New-Item -ItemType Directory -Force (Join-Path $App ".claude\agents") | Out-Null
    Copy-Item -Recurse (Join-Path $Toolkit ".claude\skills\android-select-architecture") $SkillDst
    Copy-Item (Join-Path $Toolkit ".claude\agents\android-architect.md") $AgentDst
}
```

## Copy: Bash (macOS, Linux, Git Bash)

```bash
TOOLKIT="<path to android-agent-toolkit>"
APP="<path to your Android app repository>"

SKILL_DST="$APP/.claude/skills/android-select-architecture"
AGENT_DST="$APP/.claude/agents/android-architect.md"

if [ -e "$SKILL_DST" ] || [ -e "$AGENT_DST" ]; then
  echo "Destination already exists. Resolve the conflict before installing." >&2
else
  mkdir -p "$APP/.claude/skills" "$APP/.claude/agents"
  cp -R "$TOOLKIT/.claude/skills/android-select-architecture" "$SKILL_DST"
  cp "$TOOLKIT/.claude/agents/android-architect.md" "$AGENT_DST"
fi
```

Both scripts refuse to overwrite. Neither touches your `CLAUDE.md`,
`.claude/settings.json` or any other existing file.

## After you copy

1. **Record the version.** Merge the section from
   [templates/consumer-claude-guidance.md](../templates/consumer-claude-guidance.md)
   into your app's existing `CLAUDE.md` and fill in the toolkit revision and
   date. Merge it; do not replace your file. If your app has no `CLAUDE.md`,
   create one for your app and include the section.

2. **Make Claude Code pick up the files.** Claude Code watches existing
   `.claude/skills/` and `.claude/agents/` folders. If either folder did not
   exist when your session started, restart Claude Code in the app
   repository (for skills, `/reload-skills` is the documented alternative).

3. **Confirm discovery.** In Claude Code, opened in your app repository:

   - type `/android-select-architecture` and confirm it is offered in the
     slash-command menu;
   - ask "Which subagents are available in this project?" and confirm
     `android-architect` is listed.

   If either is missing, the files are not installed correctly for your
   Claude Code version. Do not proceed as though they were.

4. Commit the installed files in your app repository so that teammates get
   the same version.

## Updating

Remove the installed files as described below, then install again from the
newer toolkit revision and update the recorded revision. Do not edit the
installed files in place; local edits make the recorded revision untrue.

## Removal

Delete exactly the two installed paths and nothing else.

PowerShell:

```powershell
Remove-Item -Recurse (Join-Path $App ".claude\skills\android-select-architecture")
Remove-Item (Join-Path $App ".claude\agents\android-architect.md")
```

Bash:

```bash
rm -r "$APP/.claude/skills/android-select-architecture"
rm "$APP/.claude/agents/android-architect.md"
```

Then remove the "Android toolkit assets" section from your app's `CLAUDE.md`.
Leave `.claude/skills/` and `.claude/agents/` themselves in place if they hold
anything else. Architecture decision records and code that the skill created
in your app belong to your app and are not removed.
