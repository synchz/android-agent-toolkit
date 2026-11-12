# Layered modular architecture for Android: reference

Supporting reference for the `android-select-architecture` skill. It describes
structural variants, dependency rules and the conditions for choosing among
them. `<feature>` stands for the consumer's own feature name; `<base>` for the
app's base package.

This structure draws on widely used Android patterns: Compose UI with
ViewModel state holders, repositories over data sources, coroutines and Flow,
and Hilt for dependency injection. The separate domain module and the
five-module split are this toolkit's own default. They are not a copy of any
official sample and are not required by Android guidance.

## Layers

| Layer | Contains | Must not contain |
|---|---|---|
| UI | Composables, ViewModels, UI state and event types, feature navigation entry points | Repository implementations, database or network types |
| Domain | Plain Kotlin models, repository interfaces, use cases that enforce a business rule | Android framework, Compose, Hilt modules, persistence or network types |
| Data | Repository implementations, data sources, mapping between storage and domain models | Composables, ViewModels |

Dependencies point inward: UI depends on domain; data depends on domain;
domain depends on nothing in the app.

## Variants

### A. Single module, layered packages

One `:app` module with packages `<base>.ui.<feature>`, `<base>.domain`,
`<base>.data`, `<base>.di`.

Fits: a prototype, a one-or-two-screen app, a solo developer, or when build
time and team boundaries are not yet a concern. Boundaries are held by
convention and review only; nothing stops a ViewModel importing a data class.

Move up when: a second feature arrives, boundary violations appear in review,
or the domain needs to be tested without Android.

### B. Three modules

`:app` (entry, UI, navigation, DI wiring), `:domain` (pure Kotlin), `:data`.

Fits: a small app with a few features where the main value is a
compiler-enforced, Android-free domain. Features share one UI module.

Move up when: features need independent ownership or build isolation, or
shared UI components start to be copied between screens.

### C. Five modules (default for apps expected to grow)

| Module | Responsibility | May depend on |
|---|---|---|
| `:app` | Application class, single activity, navigation graph composition, Hilt wiring of implementations to contracts | `:feature:<feature>`, `:core:domain`, `:core:data`, `:core:designsystem` |
| `:feature:<feature>` | Composables, ViewModel, UI state for one feature | `:core:domain`, `:core:designsystem` |
| `:core:domain` | Models, repository interfaces, use cases | No project module |
| `:core:data` | Repository implementations and data sources | `:core:domain` |
| `:core:designsystem` | Theme, typography, shared stateless components | No project module |

Fits: more than one planned feature, more than one contributor, or an explicit
wish to demonstrate enforced boundaries. Each further feature becomes another
`:feature:<name>` module with the same dependency rule.

Cost: more Gradle files, more configuration to keep consistent, slower initial
setup. For a tiny app this is overhead without benefit; choose A or B and say
so in the decision.

## Dependency rules (variant C; B is the same without feature/designsystem)

1. `:core:domain` has no `project(...)` dependency and applies a pure Kotlin
   JVM plugin, not an Android library plugin. This makes Android imports a
   compile error rather than a review comment.
2. `:feature:*` never depends on `:core:data` or on another feature module.
   Cross-feature navigation is composed in `:app`.
3. `:core:data` depends on `:core:domain` only. Persistence entities and
   network DTOs stay inside data and are mapped to domain models at the
   boundary.
4. `:core:designsystem` knows nothing about features, domain models or data.
   Components take plain parameters.
5. `:app` is the only module that sees both contracts and implementations.

## Module build configuration

| Module | Plugins (resolve ids and versions from the version catalog) |
|---|---|
| `:app` | Android application, Kotlin Android, Compose compiler, Hilt, KSP |
| `:feature:<feature>` | Android library, Kotlin Android, Compose compiler, Hilt, KSP |
| `:core:domain` | Kotlin JVM |
| `:core:data` | Android library, Kotlin Android, Hilt, KSP. A Kotlin JVM module is enough while the only data source is in memory; it must become an Android library when an Android-dependent source is added |
| `:core:designsystem` | Android library, Kotlin Android, Compose compiler |

- Keep every version in `gradle/libs.versions.toml`. Look up current stable,
  mutually compatible versions in official release notes when scaffolding;
  the Kotlin, Compose compiler, KSP and Hilt versions constrain each other.
- Use one `compileSdk`, `minSdk` and JVM target across modules. Convention
  plugins in an included build are reasonable once three or more modules
  repeat the same configuration; for a first scaffold, duplication in a few
  small build files is acceptable and easier to read.
- Give every Android module a unique `namespace` under `<base>`.

## Dependency injection

- Repository interfaces live in domain; implementations live in data.
- Bindings (`@Binds` or `@Provides` in a Hilt module) connect them. Place the
  module in `:core:data` if data applies Hilt, or in `:app`. Either way only
  `:app` needs both on its classpath at runtime.
- Use cases and repository implementations can use constructor injection with
  `javax.inject.Inject`, which is a plain JVM annotation. If the team wants
  the domain module to carry no annotations at all, provide use cases from a
  Hilt module in `:app` instead. Record which choice was made.
- ViewModels use `@HiltViewModel` and receive domain types only.

## Use cases

Create a use case when it holds a rule that would otherwise be duplicated or
hidden in a ViewModel: validation, combining repositories, ordering, filtering
by a business condition. Name it for the rule, and give it one public
operation.

Do not create a use case that only forwards one repository call. A ViewModel
may call a repository interface directly for plain reads. Add the use case
when a rule appears.

## State and data flow

- Repositories expose observable data as `Flow` and one-shot operations as
  `suspend` functions.
- A ViewModel turns domain flows into a single immutable UI state exposed as
  `StateFlow`, and exposes functions for user events.
- Composables receive state and callbacks. The screen-level composable obtains
  the ViewModel; the content composable below it is stateless and previewable.
- Dispatchers are injected rather than hardcoded, so tests can control them.

## First data source

Start with an in-memory repository implementation backed by a
`MutableStateFlow` unless persistence was requested. It proves the wiring and
keeps the first build small. Because feature and domain code see only the
interface, replacing it with a database-backed implementation later changes
the data module and the binding, not the feature.

State the consequence in the decision record: in-memory data is lost when the
process ends.

## Navigation

The navigation graph is composed in `:app`. Each feature exposes an entry
point (a route definition and a function that registers its screen); it does
not reference other features. Keep navigation composition separate from
business behaviour: a ViewModel emits a result or state, and the screen or
graph decides where to go.

## Testing seams this structure provides

- Domain: plain JVM unit tests, no Android runtime.
- Data: repository tests against the in-memory or fake data source.
- Feature: ViewModel tests with a fake repository implementing the domain
  interface; Compose tests against the stateless content composable.

The scaffold should leave these seams usable. Writing the test suite is
separate work.

## Checks that the structure holds

| Rule | How to check |
|---|---|
| Domain is Android-free | Its build file applies only a Kotlin JVM plugin; its compile classpath lists no `androidx`, `com.android` or persistence artifacts |
| Feature does not see data | No `project(":core:data")` in any feature build file |
| Data depends only on domain | Its only `project(...)` dependency is domain |
| Design system is independent | No `project(...)` dependencies |
| Wiring works | The debug build assembles and the app launches to the first screen |

These checks show that boundaries are declared and compile. They do not show
that the design is right for the product; that remains a judgement recorded in
the decision.

## Simplifying or deviating

Deviation is expected when the project calls for it. Record the reason.

- No shared UI yet: omit `:core:designsystem` and keep the theme in `:app`
  until a second feature needs it.
- Different DI library or manual DI: keep the same boundaries; replace the
  Hilt-specific wiring.
- Existing single-module app: do not split everything at once. Extract the
  domain first, since it has no dependencies, then data, then features.
