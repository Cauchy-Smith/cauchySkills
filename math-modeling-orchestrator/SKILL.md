---
name: math-modeling-orchestrator
description: Coordinate a math-modeling project from problem interpretation through compliance review using project state, stage-specific skills, quality gates, dependency versioning, and rollback.
metadata:
  short-description: Manage six-stage math-modeling work with gates and traceable versions
---

# Math Modeling Orchestrator

Use this as the single entry point for a mathematical-modeling project. The user describes the work; the orchestrator chooses the stage, loads only the required stage skill, executes it, validates its gate, and records the result.

## 1. Establish State

Work from the project root and inspect `project-state.json` first. Parse it as JSON and preserve unknown fields when updating it.

If it is missing, infer the furthest stage from these artifacts, in order:

`problem-analysis.md` -> `model-plan.md` or `model-contract.md` -> `code/` -> `results/` -> `paper/` -> `audit/`

Then create a compact state file with this shape:

```json
{
  "current_stage": "Stage 1",
  "current_role": "Solver",
  "stage_status": "IN_PROGRESS",
  "completed_stages": [],
  "versions": {"model": null, "code": null, "result": null, "figure": null, "paper": null},
  "pending_issues": [],
  "last_gate": {"stage": null, "status": null, "checked_at": null, "issues": []}
}
```

If the user explicitly requests one independent stage, honor that request while still recording state and running that stage's gate. Otherwise, prefer `current_stage` from state, then inferred artifacts, then the user's wording.

## 2. Stage Routing

Load the mapped stage skill before doing stage work. Locate a skill by its exact name in configured skill roots (a skill folder's `SKILL.md`) or a project-local `stages/<name>.md`; read the selected file completely. Do not load unrelated stage skills or re-run completed stages.

| Stage | Role | Stage skill | Required output |
| --- | --- | --- | --- |
| Stage 1: Problem interpretation | Solver | `problem-analysis` | `problem-analysis.md` |
| Stage 2: Model construction | Solver | `modeling` | `model-plan.md` and `model-contract.md` |
| Stage 3: Code solving | Coder | `coding` | runnable code under `code/` and execution notes |
| Stage 4: Visualization | Coder | `visualization` | figures/tables under `results/` or `figures/` |
| Stage 5: Paper writing | Writer | `paper-writing` | LaTeX source and compiled PDF under `paper/` |
| Stage 6: Compliance review | Reviewer | `compliance` | audit report under `audit/` |

If a required stage skill cannot be located, do not silently substitute or claim completion: record a failed gate with the missing skill and tell the user what is blocked.

When entering a stage, report only:

```text
当前阶段：Stage N｜<stage name>
当前角色：<role>
阶段 Skill：已自动加载
前置状态：<relevant versions and prior gate>
正在执行：<short numbered list from the stage skill>
```

## 3. Stage Gates

After the stage skill produces its output, update `project-state.json`, then run the gate. A gate is `PASS` only when the output exists, is internally consistent, and has no unresolved blocking issue.

- **G1**: problem, objectives, constraints, assumptions, and requested deliverables are explicit; ambiguities are listed.
- **G2**: variables, parameters, assumptions, equations/algorithm, objective, constraints, and validation plan form a reproducible model contract.
- **G3**: code reads the model contract, handles inputs/errors, runs successfully, and records reproducible parameters and outputs.
- **G4**: every claimed result has a traceable source; figures/tables are legible, labeled, and consistent with result data.
- **G5**: paper sections, formulas, figures, tables, and conclusions agree with the current model/result versions; the LaTeX source compiles successfully to the final PDF; limitations and references are present where needed.
- **G6**: compliance audit checks format, citation/data claims, formula and unit consistency, reproducibility, and unresolved risks; the report distinguishes PASS, FIX, and BLOCKED.

Record `last_gate.status` as `PASS` or `FAIL`, with timestamp and actionable issues. A failed gate keeps the project in that stage. Do not advance merely because the work looks plausible.

## 4. Version and Rollback Rules

Treat the dependency chain as `model -> code -> result -> figure -> paper -> audit`. When an upstream artifact changes materially, increment its version and mark every dependent downstream version `STALE` in state. Never write a paper or audit from stale results.

If a later stage reveals a model or data defect, roll back to the earliest affected stage, mark downstream artifacts stale, and rerun each dependent stage and gate in order. Preserve prior files when practical; state is the source of truth for which versions are current.

## 5. Operating Constraints

- Use existing project conventions and stage-skill instructions before inventing structure.
- Create only the artifacts required by the current stage; do not add speculative templates, wrappers, or dependencies.
- Use structured JSON editing for state and keep updates atomic enough to avoid half-written state.
- Keep user-facing updates concise; expose the current stage, gate, versions, blockers, and next action, not internal routing mechanics.
- At completion of a stage, show the generated output path(s), gate result, state update, and whether the next stage is unlocked.
