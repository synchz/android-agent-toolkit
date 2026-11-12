# 001: Toolkit and consumer app are separate repositories

Date: 12 November 2026
Status: Accepted

## Context

The toolkit's purpose is to be installed into Android projects. An earlier
plan placed a demonstration app inside the toolkit repository, in an examples
directory, and built both together.

That arrangement hides the thing most worth proving: that the assets work
when copied into a project that knows nothing about the toolkit. With the app
inside the toolkit, a skill can quietly depend on toolkit-relative paths, the
toolkit's own `CLAUDE.md` or files that a real consumer would never have, and
nothing would fail.

## Decision

1. This repository contains only the toolkit: skills, agents, scripts,
   templates and documentation. It contains no Android application and no
   Gradle project.
2. The demonstration app is a separate repository with its own Git history,
   its own `CLAUDE.md`, and its own build and test evidence. Its location is
   chosen later.
3. Each repository is its own Git repository. Git is never initialised in a
   shared parent folder, and the app is never nested inside the toolkit.
4. Planning material kept alongside the toolkit on the author's machine is
   not part of the toolkit. Toolkit documentation is self-contained and takes
   distilled decisions from that material, not the material itself.
5. The toolkit's `CLAUDE.md` is for maintainers. Guidance for consumers is a
   template that is merged into the consumer's existing instructions.
6. Claude Code is the only supported assistant. Other platforms are future
   work.

## Consequences

- Installation is a real step that must be documented and tested, starting
  with manual copying.
- Skills must carry their own reference material and must not hardcode an
  example app's names or paths. The validator enforces the parts of this that
  can be checked mechanically.
- Verification has two stages. The toolkit can be structurally validated on
  its own; whether it produces a working Android project can be shown only in
  the consumer repository. Records must name both the toolkit revision and
  the consumer revision.
- A capability is first added here and then demonstrated there. Until the
  second stage has happened, the capability is reported as implemented, not
  verified.

## Alternatives considered

- **App bundled in the toolkit.** Simpler to start, one repository to manage.
  Rejected because it does not exercise installation and allows hidden
  coupling.
- **Toolkit developed inside the app and extracted later.** Rejected because
  extraction tends to be deferred, and app-specific names leak into reusable
  instructions.
