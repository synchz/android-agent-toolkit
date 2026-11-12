#!/usr/bin/env python3
"""Structural validator for android-agent-toolkit.

Usage:
    python scripts/validate_toolkit.py [--root PATH]

Exit codes:
    0  no structural errors found
    1  one or more structural errors, each printed as
       "ERROR [<source>] <path>: <message>"
    2  usage error (for example, the root directory does not exist)

Requires Python 3.8+ and the standard library only.

Every finding carries a source tag:
    [claude]   a documented Claude Code requirement or behaviour. Breaking it
               means Claude Code refuses the asset, drops its metadata or
               truncates it.
    [toolkit]  a convention of this repository. Claude Code would accept the
               file; this project chooses not to.

Claude Code rules checked (skills and subagents documentation, read in full
on 2026-11-12):
    - frontmatter opens with '---' on line 1 and is closed
    - frontmatter is parseable YAML (only partly checked, see below);
      malformed YAML makes Claude Code load a skill with empty metadata
    - a skill name holds no control, zero-width, private-use, unassigned or
      direction-changing character, no non-plain blank, no leading or
      trailing space and no '<' or '>'
    - a skill's description plus when_to_use is cut at 1,536 characters in
      the skill listing
    - a subagent has 'name' and 'description'; its name is at most 256
      characters, does not start with '-' and does not contain ':'
    - SKILL.md under 500 lines is recommended (warning only)

Toolkit conventions checked (stricter than Claude Code):
    - required files exist
    - a skill declares 'name' and 'description' (Claude Code defaults the
      name to the directory and treats description as recommended)
    - a skill name equals its directory; an agent name equals its file stem;
      both use lowercase letters, digits and single hyphens
    - only documented frontmatter fields appear (Claude Code ignores unknown
      fields silently)
    - the body is not empty; 'tools', when present, is not empty
    - a skill that an agent preloads exists in this repository (the
      documentation does not say what Claude Code does when it is missing)
    - every supporting file in a skill directory is linked from SKILL.md
    - links, portability and no-bundled-app rules listed below

What this checks:
    - required toolkit files exist
    - skill and agent frontmatter is present, uses documented fields, and
      carries the required values
    - relative Markdown links resolve, stay inside the repository, and (for
      skill files) stay inside the skill's own directory
    - reusable Markdown does not point at author-machine paths, sibling
      planning folders or example-app names
    - no Android/Gradle project has been bundled into the toolkit

What this cannot check:
    - whether Claude Code discovers or correctly invokes the skill or agent
    - whether the instructions are good, complete or produce correct output
    - whether any generated Android project builds or runs
    - full YAML validity: only a small subset of YAML is parsed (see
      parse_simple_yaml); nested mappings are reported as unsupported
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote as url_unquote

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "NOTICE",
    "CLAUDE.md",
    ".gitignore",
    ".claude/skills/android-select-architecture/SKILL.md",
    ".claude/skills/android-select-architecture/references/clean-architecture.md",
    ".claude/agents/android-architect.md",
    "docs/architecture.md",
    "docs/installation.md",
    "docs/status.md",
    "docs/references.md",
    "docs/decisions/001-toolkit-and-consumer-separation.md",
    "docs/verification/bootstrap.md",
    "templates/consumer-claude-guidance.md",
    "scripts/validate_toolkit.py",
]

# Field names from the frontmatter reference tables of the Claude Code skills
# and subagents documentation, read in full on 2026-11-12. Claude Code ignores
# unknown fields silently; rejecting them is a toolkit convention so that
# typos do not go unnoticed. `claude plugin validate --strict <dir>` is the
# authoritative check for what the installed Claude Code version recognises.
SKILL_FIELDS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools",
    "disallowed-tools", "model", "effort", "context", "agent", "background",
    "hooks", "paths", "shell", "metadata", "license", "compatibility",
}
AGENT_FIELDS = {
    "name", "description", "tools", "disallowedTools", "model",
    "permissionMode", "maxTurns", "autoCompactWindow", "skills", "mcpServers",
    "hooks", "memory", "background", "omitClaudeMd", "effort", "isolation",
    "color", "initialPrompt", "experimental",
}

SKILL_LISTING_LIMIT = 1536   # description + when_to_use, per the skills docs
SKILL_MAX_LINES = 500        # recommended SKILL.md size, per the skills docs
AGENT_NAME_LIMIT = 256       # per the subagents docs
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # toolkit convention

ANDROID_PROJECT_FILES = {
    "settings.gradle", "settings.gradle.kts", "build.gradle",
    "build.gradle.kts", "gradlew", "gradlew.bat", "AndroidManifest.xml",
}

# (pattern, message) applied to every Markdown file in the repository.
PORTABILITY_PATTERNS = [
    (re.compile(r"\b[A-Za-z]:[\\/]+Users[\\/]"), "absolute Windows user path"),
    (re.compile(r"(?<![\w.])/(?:home|Users)/[\w.-]+/"), "absolute user home path"),
    (re.compile(r"\.\.[\\/](?:references|tasks)[\\/]"),
     "reference to a sibling planning folder outside the repository"),
    (re.compile(r"examples[\\/]task-manager"), "superseded bundled-app path"),
]
# Applied only to reusable assets under .claude/.
REUSABLE_PATTERNS = [
    (re.compile(r"task[ -]?manager", re.IGNORECASE),
     "example-app name in a reusable asset"),
    (re.compile(r":feature:tasks\b"), "example feature module in a reusable asset"),
]

LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
FENCE_RE = re.compile(r"^(\s*)(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")


CLAUDE = "claude"    # documented Claude Code requirement or behaviour
TOOLKIT = "toolkit"  # convention of this repository


class FrontmatterError(Exception):
    """source is CLAUDE for malformed frontmatter, TOOLKIT for YAML that may
    be valid but is outside the subset this validator can read."""

    def __init__(self, message, source=CLAUDE):
        super().__init__(message)
        self.source = source


def split_frontmatter(text):
    """Return (frontmatter_lines, body). The opening --- must be line 1."""
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        raise FrontmatterError("first line must be '---' to open the frontmatter")
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    raise FrontmatterError("frontmatter is not closed with '---'")


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _plain_scalar(raw, key):
    if raw[0] in "\"'":
        if len(raw) < 2 or raw[-1] != raw[0]:
            raise FrontmatterError("'%s': unterminated quoted value" % key)
        return raw[1:-1]
    if raw[0] in "{&*!%@`|>":
        raise FrontmatterError(
            "'%s': value starts with '%s', which this validator does not support"
            % (key, raw[0]), TOOLKIT)
    raw = re.split(r"\s+#", raw, maxsplit=1)[0].rstrip()
    if ": " in raw or raw.endswith(":"):
        raise FrontmatterError(
            "'%s': unquoted value contains ': ', which is invalid YAML; "
            "quote the value or rephrase it" % key)
    return raw


def parse_simple_yaml(lines):
    """Parse the YAML subset used by this toolkit's frontmatter.

    Supported: top-level 'key: value' scalars (plain or quoted), block scalars
    ('>' and '|'), inline lists ('[a, b]') and block lists ('- item').
    Anything else raises FrontmatterError.
    """
    data = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            raise FrontmatterError("unexpected indented line: %r" % line.strip())
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?$", line.rstrip())
        if not match:
            raise FrontmatterError("cannot parse line: %r" % line.strip())
        key, raw = match.group(1), (match.group(2) or "").strip()
        if key in data:
            raise FrontmatterError("duplicate key '%s'" % key)
        i += 1
        if raw == "" or re.match(r"^[>|][+-]?$", raw):
            block = []
            while i < len(lines) and (not lines[i].strip() or lines[i][0] in " \t"):
                block.append(lines[i])
                i += 1
            items = [b.strip() for b in block if b.strip()]
            if raw:
                data[key] = (" " if raw[0] == ">" else "\n").join(items)
            elif not items:
                data[key] = ""
            elif all(item == "-" or item.startswith("- ") for item in items):
                data[key] = [_unquote(item[1:]) for item in items]
            else:
                raise FrontmatterError(
                    "'%s': nested mappings are not supported by this validator" % key,
                    TOOLKIT)
        elif raw.startswith("["):
            if not raw.endswith("]"):
                raise FrontmatterError("'%s': unterminated inline list" % key)
            inner = raw[1:-1].strip()
            data[key] = [_unquote(p) for p in inner.split(",")] if inner else []
        else:
            data[key] = _plain_scalar(raw, key)
    return data


def claude_skill_name_problem(name):
    """Return why Claude Code would refuse this skill name, or None."""
    if name != name.strip(" "):
        return "leading or trailing space"
    for char in name:
        category = unicodedata.category(char)
        if char in "<>":
            return "'<' or '>'"
        if category.startswith("C"):
            return ("control, zero-width, private-use, unassigned or "
                    "direction-changing character")
        if category in ("Zl", "Zp") or (category == "Zs" and char != " "):
            return "non-plain blank"
    return None


def _as_list(value):
    """Normalise a comma-separated string or a list to a list of names."""
    if isinstance(value, list):
        return [v.strip() for v in value if v.strip()]
    return [v.strip() for v in str(value).split(",") if v.strip()]


def strip_code(text):
    """Blank out fenced code blocks and inline code, keeping line numbers."""
    out, fence = [], None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if fence is None and match:
            fence = match.group(2)
            out.append("")
        elif fence is not None:
            if line.strip().startswith(fence):
                fence = None
            out.append("")
        else:
            out.append(INLINE_CODE_RE.sub("", line))
    return out


def _inside(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


class Validator:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.warnings = []

    def rel(self, path):
        try:
            return Path(path).resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def error(self, path, message, source=TOOLKIT):
        self.errors.append("[%s] %s: %s" % (source, self.rel(path), message))

    def warn(self, path, message, source=TOOLKIT):
        self.warnings.append("[%s] %s: %s" % (source, self.rel(path), message))

    def read(self, path):
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self.error(path, "cannot read as UTF-8 text (%s)" % exc)
            return None

    def walk(self):
        for path in sorted(self.root.rglob("*")):
            parts = path.relative_to(self.root).parts
            if ".git" in parts or "__pycache__" in parts:
                continue
            yield path

    # -- individual checks -------------------------------------------------

    def check_required_files(self):
        for name in REQUIRED_FILES:
            if not (self.root / name).is_file():
                self.error(self.root / name, "required file is missing")

    def load_frontmatter(self, path, allowed_fields):
        text = self.read(path)
        if text is None:
            return None
        try:
            fm_lines, body = split_frontmatter(text)
            data = parse_simple_yaml(fm_lines)
        except FrontmatterError as exc:
            self.error(path, "frontmatter: %s" % exc, exc.source)
            return None
        for key in sorted(set(data) - allowed_fields):
            self.error(path, "frontmatter: unknown field '%s'" % key)
        if not body.strip():
            self.error(path, "body is empty; instructions are required")
        return data, text

    def check_skills(self):
        skills_dir = self.root / ".claude" / "skills"
        names = set()
        if not skills_dir.is_dir():
            return names
        for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                self.error(skill_dir, "skill directory has no SKILL.md")
                continue
            names.add(skill_dir.name)
            loaded = self.load_frontmatter(skill_file, SKILL_FIELDS)
            if loaded is None:
                continue
            data, text = loaded
            name = data.get("name")
            if not name or not isinstance(name, str):
                self.error(skill_file, "frontmatter: 'name' is required by this toolkit")
            else:
                problem = claude_skill_name_problem(name)
                if problem:
                    self.error(skill_file,
                               "frontmatter: Claude Code refuses a skill name "
                               "with a %s" % problem, CLAUDE)
                if not NAME_RE.match(name):
                    self.error(skill_file,
                               "frontmatter: name '%s' must be lowercase letters, "
                               "digits and single hyphens" % name)
                if name != skill_dir.name:
                    self.error(skill_file,
                               "frontmatter: name '%s' does not match directory '%s'"
                               % (name, skill_dir.name))
            description = data.get("description")
            if not description or not isinstance(description, str):
                self.error(skill_file, "frontmatter: 'description' is required by this toolkit")
            else:
                listing = len(description) + len(str(data.get("when_to_use", "")))
                if listing > SKILL_LISTING_LIMIT:
                    self.error(skill_file,
                               "frontmatter: description plus when_to_use is %d "
                               "characters; the skill listing truncates at %d"
                               % (listing, SKILL_LISTING_LIMIT), CLAUDE)
            line_count = len(text.splitlines())
            if line_count > SKILL_MAX_LINES:
                self.warn(skill_file, "%d lines; documentation recommends under %d"
                          % (line_count, SKILL_MAX_LINES), CLAUDE)
            self.check_skill_resources_linked(skill_dir, skill_file, text)
        return names

    def check_skill_resources_linked(self, skill_dir, skill_file, text):
        """Every supporting file must be reachable from SKILL.md by a link."""
        linked = set()
        for _, target in self.iter_links(text):
            target = url_unquote(target.split("#", 1)[0])
            if target and not SCHEME_RE.match(target):
                linked.add((skill_file.parent / target).resolve())
        for path in sorted(skill_dir.rglob("*")):
            if path.is_file() and path != skill_file and path.resolve() not in linked:
                self.error(path, "supporting file is not linked from SKILL.md")

    def check_agents(self, skill_names):
        agents_dir = self.root / ".claude" / "agents"
        if not agents_dir.is_dir():
            return
        seen = {}
        for agent_file in sorted(agents_dir.rglob("*.md")):
            loaded = self.load_frontmatter(agent_file, AGENT_FIELDS)
            if loaded is None:
                continue
            data, _ = loaded
            name = data.get("name")
            if not name or not isinstance(name, str):
                self.error(agent_file, "frontmatter: 'name' is required", CLAUDE)
            else:
                if len(name) > AGENT_NAME_LIMIT or name.startswith("-") or ":" in name:
                    self.error(agent_file,
                               "frontmatter: name must be at most %d characters, "
                               "not start with '-' and not contain ':'" % AGENT_NAME_LIMIT,
                               CLAUDE)
                if not NAME_RE.match(name):
                    self.error(agent_file,
                               "frontmatter: name '%s' must be lowercase letters, "
                               "digits and single hyphens" % name)
                if name != agent_file.stem:
                    self.error(agent_file,
                               "frontmatter: name '%s' does not match file name '%s'"
                               % (name, agent_file.stem))
                if name in seen:
                    self.error(agent_file, "frontmatter: name '%s' is also used by %s"
                               % (name, self.rel(seen[name])))
                seen.setdefault(name, agent_file)
            description = data.get("description")
            if not description or not isinstance(description, str):
                self.error(agent_file, "frontmatter: 'description' is required", CLAUDE)
            if "tools" in data and not _as_list(data["tools"]):
                self.error(agent_file, "frontmatter: 'tools' is present but empty")
            for skill in _as_list(data.get("skills", [])):
                if skill not in skill_names:
                    self.error(agent_file,
                               "frontmatter: preloaded skill '%s' does not exist "
                               "under .claude/skills/" % skill)

    def iter_links(self, text):
        for number, line in enumerate(strip_code(text), start=1):
            for match in LINK_RE.finditer(line):
                yield number, match.group(1).strip("<>").strip()

    def check_markdown(self):
        skills_dir = (self.root / ".claude" / "skills").resolve()
        claude_dir = (self.root / ".claude").resolve()
        for path in self.walk():
            if not path.is_file() or path.suffix.lower() != ".md":
                continue
            text = self.read(path)
            if text is None:
                continue
            resolved = path.resolve()

            patterns = list(PORTABILITY_PATTERNS)
            if _inside(resolved, claude_dir):
                patterns += REUSABLE_PATTERNS
            for number, line in enumerate(text.splitlines(), start=1):
                for pattern, message in patterns:
                    if pattern.search(line):
                        self.error(path, "line %d: %s" % (number, message))

            boundary = None
            if _inside(resolved, skills_dir):
                relative = resolved.relative_to(skills_dir)
                if len(relative.parts) > 1:
                    boundary = skills_dir / relative.parts[0]

            for number, target in self.iter_links(text):
                if DRIVE_RE.match(target) or target.startswith(("/", "\\")):
                    self.error(path, "line %d: absolute link '%s'" % (number, target))
                    continue
                if target.startswith("#") or SCHEME_RE.match(target):
                    continue
                file_part = url_unquote(target.split("#", 1)[0])
                if not file_part:
                    continue
                destination = (path.parent / file_part).resolve()
                if not _inside(destination, self.root):
                    self.error(path, "line %d: link '%s' leaves the repository"
                               % (number, target))
                elif boundary is not None and not _inside(destination, boundary):
                    self.error(path,
                               "line %d: link '%s' leaves the skill directory, so "
                               "it would break when the skill is copied"
                               % (number, target))
                elif not destination.exists():
                    self.error(path, "line %d: broken link '%s'" % (number, target))

    def check_no_android_project(self):
        for path in self.walk():
            if path.is_file() and path.name in ANDROID_PROJECT_FILES:
                self.error(path,
                           "Android/Gradle project file found; the toolkit must "
                           "not bundle an application")

    def run(self):
        self.check_required_files()
        skill_names = self.check_skills()
        self.check_agents(skill_names)
        self.check_markdown()
        self.check_no_android_project()
        return self.errors


def validate(root):
    """Return (errors, warnings) for the toolkit at root."""
    validator = Validator(root)
    validator.run()
    return validator.errors, validator.warnings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Structural checks for android-agent-toolkit. Passing does "
                    "not show that Claude discovers the assets or that any "
                    "Android project builds.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent),
                        help="toolkit root directory (default: parent of scripts/)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print("usage error: root is not a directory: %s" % root, file=sys.stderr)
        return 2

    errors, warnings = validate(root)
    for message in warnings:
        print("WARN  %s" % message)
    for message in errors:
        print("ERROR %s" % message)
    if errors:
        print("FAILED: %d structural error(s), %d warning(s)" % (len(errors), len(warnings)))
        return 1
    print("OK: structural checks passed, %d warning(s). This does not verify "
          "Claude discovery or Android builds." % len(warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
