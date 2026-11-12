#!/usr/bin/env python3
"""Fixture tests for validate_toolkit.py.

Usage:
    python scripts/test_validate_toolkit.py

Each test copies the real toolkit into a temporary directory, applies one
deliberate defect and asserts that the validator reports it. Nothing in the
working tree is modified. Standard library only.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import validate_toolkit  # noqa: E402

SKILL = ".claude/skills/android-select-architecture/SKILL.md"
SKILL_REF = ".claude/skills/android-select-architecture/references/clean-architecture.md"
AGENT = ".claude/agents/android-architect.md"


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="toolkit-fixture-")
        self.fixture = Path(self._tmp.name) / "toolkit"
        shutil.copytree(
            ROOT, self.fixture,
            ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def tearDown(self):
        self._tmp.cleanup()

    # helpers
    def edit(self, relative, old, new):
        path = self.fixture / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, "fixture precondition: %r not in %s" % (old, relative))
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def append(self, relative, extra):
        path = self.fixture / relative
        path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")

    def errors(self):
        return validate_toolkit.validate(self.fixture)[0]

    def assert_rejected(self, fragment):
        errors = self.errors()
        self.assertTrue(
            any(fragment in e for e in errors),
            "expected an error containing %r, got: %r" % (fragment, errors))

    # valid input
    def test_unmodified_copy_passes(self):
        self.assertEqual(self.errors(), [])

    def test_cli_exit_codes(self):
        script = str(SCRIPTS / "validate_toolkit.py")
        ok = subprocess.run([sys.executable, script, "--root", str(self.fixture)],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

        (self.fixture / "README.md").unlink()
        bad = subprocess.run([sys.executable, script, "--root", str(self.fixture)],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        self.assertIn("ERROR [toolkit] README.md: required file is missing", bad.stdout)

        missing = subprocess.run(
            [sys.executable, script, "--root", str(self.fixture / "no-such-dir")],
            capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)

    # required files
    def test_missing_agent_file(self):
        (self.fixture / AGENT).unlink()
        self.assert_rejected(AGENT + ": required file is missing")

    def test_missing_skill_reference(self):
        (self.fixture / SKILL_REF).unlink()
        self.assert_rejected(SKILL_REF + ": required file is missing")
        self.assert_rejected("broken link 'references/clean-architecture.md'")

    # skill metadata
    def test_skill_without_frontmatter(self):
        path = self.fixture / SKILL
        path.write_text("# No frontmatter\n\nBody.\n", encoding="utf-8")
        self.assert_rejected("first line must be '---'")

    def test_skill_unclosed_frontmatter(self):
        path = self.fixture / SKILL
        path.write_text("---\nname: android-select-architecture\n\nBody.\n",
                        encoding="utf-8")
        self.assert_rejected("frontmatter is not closed")

    def test_skill_missing_description(self):
        path = self.fixture / SKILL
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        path.write_text("".join(l for l in lines if not l.startswith("description:")),
                        encoding="utf-8")
        self.assert_rejected("'description' is required")

    def test_skill_name_differs_from_directory(self):
        self.edit(SKILL, "name: android-select-architecture", "name: android-architecture")
        self.assert_rejected("does not match directory")

    def test_skill_unknown_field(self):
        self.edit(SKILL, "name: android-select-architecture",
                  "name: android-select-architecture\nallowed_tools: Read")
        self.assert_rejected("unknown field 'allowed_tools'")

    def test_skill_unquoted_colon_in_value(self):
        self.edit(SKILL, "description: ", "description: Note: ")
        self.assert_rejected("invalid YAML")

    def test_skill_empty_body(self):
        path = self.fixture / SKILL
        path.write_text(
            "---\nname: android-select-architecture\ndescription: Something.\n---\n",
            encoding="utf-8")
        self.assert_rejected("body is empty")

    def test_skill_directory_without_skill_file(self):
        (self.fixture / ".claude/skills/android-empty").mkdir()
        self.assert_rejected("skill directory has no SKILL.md")

    def test_skill_unlinked_supporting_file(self):
        orphan = self.fixture / ".claude/skills/android-select-architecture/references/orphan.md"
        orphan.write_text("# Orphan\n", encoding="utf-8")
        self.assert_rejected("supporting file is not linked from SKILL.md")

    def test_skill_name_claude_refuses(self):
        self.edit(SKILL, "name: android-select-architecture", 'name: "android-<select>"')
        self.assert_rejected("[claude]")
        self.assert_rejected("Claude Code refuses a skill name")

    def test_skill_name_with_zero_width_character(self):
        self.edit(SKILL, "name: android-select-architecture",
                  "name: android-select\u200b-architecture")
        self.assert_rejected("Claude Code refuses a skill name")

    def test_skill_description_over_listing_limit(self):
        self.edit(SKILL, "description: ", "description: " + "word " * 320)
        self.assert_rejected("the skill listing truncates at 1536")

    # source tags
    def test_convention_findings_are_tagged_toolkit(self):
        self.edit(SKILL, "name: android-select-architecture", "name: android-architecture")
        errors = self.errors()
        self.assertTrue(errors)
        self.assertTrue(all(e.startswith("[toolkit] ") for e in errors), errors)

    def test_claude_requirement_findings_are_tagged_claude(self):
        self.edit(AGENT, "name: android-architect\n", "")
        errors = self.errors()
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith("[claude] "), errors)

    def test_unsupported_yaml_is_tagged_toolkit_not_claude(self):
        self.edit(AGENT, "tools: Read, Glob, Grep",
                  "tools: Read, Glob, Grep\nhooks:\n  PreToolUse:\n    - matcher: Bash")
        errors = self.errors()
        self.assertTrue(any("nested mappings are not supported" in e
                            and e.startswith("[toolkit] ") for e in errors), errors)

    # agent metadata
    def test_agent_missing_name(self):
        self.edit(AGENT, "name: android-architect\n", "")
        self.assert_rejected("'name' is required")

    def test_agent_missing_description(self):
        path = self.fixture / AGENT
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        path.write_text("".join(l for l in lines if not l.startswith("description:")),
                        encoding="utf-8")
        self.assert_rejected("'description' is required")

    def test_agent_name_with_colon(self):
        self.edit(AGENT, "name: android-architect", 'name: "android:architect"')
        self.assert_rejected("not contain ':'")

    def test_agent_unknown_field(self):
        self.edit(AGENT, "tools: ", "allowed-tools: ")
        self.assert_rejected("unknown field 'allowed-tools'")

    def test_agent_preloads_missing_skill(self):
        self.edit(AGENT, "  - android-select-architecture", "  - android-missing-skill")
        self.assert_rejected("preloaded skill 'android-missing-skill' does not exist")

    def test_agent_name_differs_from_file(self):
        self.edit(AGENT, "name: android-architect", "name: architect")
        self.assert_rejected("does not match file name")

    # links and portability
    def test_broken_link_in_docs(self):
        self.append("README.md", "\nSee [missing](docs/does-not-exist.md).\n")
        self.assert_rejected("broken link 'docs/does-not-exist.md'")

    def test_link_inside_code_block_is_ignored(self):
        self.append("README.md", "\n```\n[missing](docs/does-not-exist.md)\n```\n")
        self.assertEqual(self.errors(), [])

    def test_skill_link_leaving_skill_directory(self):
        self.append(SKILL, "\nSee [install](../../../docs/installation.md).\n")
        self.assert_rejected("leaves the skill directory")

    def test_link_leaving_repository(self):
        self.append("README.md", "\nSee [plan](../outside.md).\n")
        self.assert_rejected("leaves the repository")

    def test_sibling_planning_folder_reference(self):
        self.append("docs/architecture.md",
                    "\nRead `../" + "references/Some_Plan.md` first.\n")
        self.assert_rejected("sibling planning folder")

    def test_author_machine_path(self):
        self.append(SKILL, "\nCopy from `C:" + "\\Users\\someone\\toolkit`.\n")
        self.assert_rejected("absolute Windows user path")

    def test_example_app_name_in_reusable_asset(self):
        self.append(SKILL_REF, "\nThe Task " + "Manager app uses this.\n")
        self.assert_rejected("example-app name in a reusable asset")

    # no bundled application
    def test_bundled_gradle_project(self):
        app = self.fixture / "examples" / "app"
        app.mkdir(parents=True)
        (app / "settings.gradle.kts").write_text("rootProject.name = \"x\"\n",
                                                 encoding="utf-8")
        self.assert_rejected("must not bundle an application")


if __name__ == "__main__":
    unittest.main(verbosity=2)
