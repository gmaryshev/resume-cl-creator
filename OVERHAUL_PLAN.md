# Resume and Cover Letter Workflow Overhaul Plan

## Status

Phase 1 first increment implemented: the repository now has a checked-in
source registry, a Python context bundler, traceable JSON manifests, Copilot
summarization requests, focused tests, and a workflow entry point that invokes
the bundler before generation.

## Goals

1. Reduce model input tokens and generation cost without losing relevant evidence.
2. Preserve separate, understandable source files and folders.
3. Improve prompt, writing-rule, template, and LaTeX reliability.
4. Make generated runs consistent, inspectable, and easier to reproduce.
5. Keep automatic application tracking when PDFs compile successfully.
6. Leave room for future CLI, UI, and model-provider integrations without requiring them in the first phase.

## Guiding Design

Keep the repository's source material separated by purpose. Add a deterministic
context-bundling layer that reads approved sources, compacts them, and emits:

- A concise Markdown prompt package for chat/agent generation.
- A machine-readable JSON or YAML manifest describing included sources,
  transformations, priorities, and provenance.

The bundle is an optimization layer, not a replacement for the source files.
Every summarized or extracted fact should remain traceable to its source file
and section.

## Prioritized Phases

### Phase 0: Baseline and decisions

**Outcome:** A measured baseline and an agreed target for the overhaul.

- Inventory the current reference folders, templates, rules, generated outputs,
  and tracking files.
- Identify duplicate, conflicting, stale, and sensitive content.
- Record representative token counts and common LaTeX failure modes.
- Define the minimum supported generation input and output contract.
- Decide whether the manifest is JSON, YAML, or both.
- Define which files are approved sources and which are examples only.

**Acceptance criteria**

- A source inventory exists with ownership, purpose, and precedence.
- Baseline generation cost/size and compile failures are recorded.
- No source file is silently treated as authoritative without a documented rule.

### Phase 1: Context bundling and source traceability

**Outcome:** A script can assemble compact, job-specific context while leaving
the source folders intact.

- Define a source manifest format with:
  - source path and section identifiers;
  - source type and trust level;
  - always-include or optional status;
  - extraction/summarization status;
  - source hashes and bundle-generation metadata.
- Build a bundler that includes all approved reference content, then organizes
  and compacts it instead of requiring a single monolithic profile file.
- Add job-description context and a clear separation between:
  - immutable facts;
  - inferred relevance;
  - generation instructions;
  - prohibited claims.
- Emit both Markdown and machine-readable output.
- Use Copilot-assisted summarization for long narrative sources, with source
  citations and a retained fact-level trace. Keep the adapter boundary open for
  a future local or provider-backed implementation.
- Ensure failed or ambiguous summarization is surfaced rather than silently
  replaced with an empty or success-shaped result.

**Acceptance criteria**

- The bundle is generated from the same inputs deterministically except for
  explicitly recorded model-assisted summaries.
- Every generated fact or summary points to one or more source locations.
- The bundle is materially smaller than passing all source material directly
  while retaining all approved factual content needed for tailoring.
- A reviewer can inspect the manifest and understand why each source was used.

### Phase 2: Rules and prompt contract

**Outcome:** Generation instructions are concise, non-conflicting, and
verifiable.

- Consolidate overlapping resume rules and define precedence between:
  - global writing rules;
  - personal constraints;
  - template constraints;
  - job-specific tailoring instructions.
- Specify resume and cover-letter quality requirements:
  - truthful evidence only;
  - natural wording;
  - ATS-safe structure;
  - section naming;
  - bullet shape and length;
  - required and optional sections;
  - contact and date handling;
  - keyword use without keyword stuffing.
- Encode LaTeX safety rules, including the known spacing and command
  restrictions:
  - use `\resumeSection{}` instead of `\section*`;
  - do not combine `\par` and `\vspace`;
  - use `\\[Npt]` only where valid;
  - do not use `\\` in plain paragraph mode.
- Define explicit output schemas for resume, cover letter, tips, source files,
  and validation results.
- Separate stable instructions from per-job context so future caching or
  provider integrations remain possible.

**Acceptance criteria**

- There is one documented precedence model for conflicting instructions.
- Prompts can be assembled from the bundle without repeating static rules.
- The prompt contract identifies what the model must produce and what it must
  never invent.

### Phase 3: Template and LaTeX reliability

**Outcome:** Templates are easier to use correctly and failures are detected
before delivery.

- Annotate or restructure templates so structural areas and content insertion
  points are explicit.
- Separate style/configuration from generated content where practical.
- Create minimal skeleton templates for generation to reduce input tokens while
  preserving the approved visual design.
- Define a stable compile entry point for resume, cover letter, and tips.
- Add file-name and folder-name normalization rules.
- Preserve the current output organization unless a deliberate migration is
  approved.

**Acceptance criteria**

- A clean template compiles successfully from a fresh output directory.
- Generated LaTeX does not modify reference templates.
- Common spacing, section, and invalid-command failures are caught with clear
  diagnostics.

### Phase 4: Lightweight validation and run manifest

**Outcome:** A compile-successful run is also structurally auditable.

- Add basic checks for:
  - required output files;
  - expected folder layout;
  - PDF existence;
  - LaTeX compilation status;
  - missing or malformed source references;
  - accidental personal-information substitution from templates;
  - duplicate or inconsistent application identifiers.
- Produce a run manifest containing the job description, bundle manifest,
  rules/template versions, generated paths, model metadata when available, and
  validation results.
- Keep validation at the selected basic quality-gate level initially; design
  interfaces so ATS and visual checks can be added later.
- Ensure errors are explicit and stop completion when required artifacts are
  missing.

**Acceptance criteria**

- A run cannot be reported complete if required PDFs or tracking rows are
  missing.
- Validation output identifies the exact failed check and relevant path.
- A successful run can be inspected without reconstructing the original
  context manually.

### Phase 5: Tracking and operational integration

**Outcome:** Tracking remains automatic and consistent with successful output.

- Keep the current policy that a completed, compile-successful run is logged as
  an application with status `Applied`.
- Preserve matching `application_id` values between applications and status
  history.
- Make the logging step consume validated run metadata rather than re-infer
  paths or facts.
- Retain blank values for unavailable facts and never guess them.
- Add duplicate-run detection and version allocation rules.
- Document the boundary clearly so a future explicit-submission mode can be
  introduced without corrupting current history.

**Acceptance criteria**

- Successful runs create exactly one valid application record and one matching
  status-history record.
- Failed or incomplete runs do not create success-shaped tracking records.
- Re-running a job creates an intentional version rather than overwriting
  prior outputs.

### Phase 6: Future interfaces and optimization

**Outcome:** The workflow can evolve beyond chat/agent instructions without
rewriting its core.

- Treat the Markdown bundle and machine-readable manifest as a stable interface
  between context preparation and generation.
- Add optional CLI/task integration around the bundler, compiler, validator,
  and tracker.
- Evaluate caching of stable rules, profile facts, and template skeletons.
- Add selectable model roles later, such as a lower-cost tips or summarization
  pass, while preserving provenance and validation.
- Consider a UI only after the file contracts and validation behavior are
  stable.

**Acceptance criteria**

- A future interface can invoke the same bundle and validation contracts.
- Model/provider changes do not require reorganizing source folders.
- Cost improvements can be measured against the Phase 0 baseline.

## Proposed Component Boundaries

- **Source registry:** declares approved inputs, trust, precedence, and scope.
- **Context bundler:** extracts, compacts, prioritizes, and packages content.
- **Summarization adapter:** runs local summarization with source traceability.
- **Prompt assembler:** combines stable rules with the per-job bundle.
- **Template/compiler adapter:** creates and compiles generated documents.
- **Validator:** checks artifacts, structure, LaTeX status, and basic integrity.
- **Run manifest writer:** records inputs, versions, hashes, outputs, and checks.
- **Tracker:** writes application and status-history records from validated runs.

These components should initially be simple scripts or library modules rather
than a full application. Their boundaries should not assume a particular model
provider or UI.

## Feature Backlog Mapping

### First implementation focus

- Consolidate and clarify rules without forcing source-file consolidation.
- Add source selection and context bundling.
- Add traceable local summarization for narrative material.
- Reduce template and prompt token volume.
- Fix and formalize LaTeX reliability constraints.
- Preserve compile-success automatic application logging.

### Later, after the baseline is stable

- Advanced ATS and content checks.
- Visual PDF regression checking.
- Multiple model roles and cost-aware routing.
- Prompt caching or API-based generation.
- CLI/task orchestration.
- Interactive UI and external integrations.

## Open Decisions

1. JSON, YAML, or both for the machine-readable manifest.
2. Exact source registry format and how approved content is marked.
3. Local summarization model/runtime and acceptable summary drift.
4. Whether source hashes should be mandatory for every run.
5. Whether generated bundles and run manifests are committed, ignored, or
   retained only with outputs.
6. How version numbers are allocated when parallel runs occur.
7. Whether the current `Applied` behavior should eventually be configurable
   without changing historical records.
8. Whether tips remain part of the main generation pass or become a separate,
   lower-cost pass.
9. Which existing generated output should become the approved quality example.
10. Privacy policy for generated bundles, logs, caches, and local model data.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Compaction removes a useful fact | Preserve source traceability and require reviewable manifests |
| Summarization introduces unsupported claims | Keep summaries source-linked and validate against source facts |
| More rules increase prompt size | Separate stable rules from per-job context and measure token costs |
| Template changes break existing outputs | Use versioned templates and compile regression fixtures |
| Automatic tracking records an unsubmitted application | Document the current boundary and design a future configurable mode |
| Bundler becomes a new opaque dependency | Keep source registry, bundle, and manifest human-inspectable |
| Personal data leaks into examples or templates | Add template contamination checks and explicit approved-source rules |

## Initial Definition of Done

The first implementation phase is complete when:

- separated reference folders remain intact;
- a documented registry identifies approved source material;
- one command or task produces Markdown and machine-readable context bundles;
- long narrative content can be summarized through Copilot with source
  traceability;
- stable rules and template instructions are not duplicated in every bundle;
- the known LaTeX spacing restrictions are encoded and checked;
- a representative generation compiles into the expected output structure;
- the successful run creates the required tracking rows;
- the bundle size and generation cost can be compared with the baseline.
