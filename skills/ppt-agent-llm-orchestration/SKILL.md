---
name: ppt-agent-llm-orchestration
description: "LLM-first PPT Agent orchestration for uploaded .pptx workflows. Use when users ask for Kimi or Manus style PPT generation or refinement with multi-step agent control: intent routing via skills, per-slide text understanding and polishing, director-layer HTML layout planning, HTML-to-JSON compile, image generation orchestration, and final editable PPT output."
---

# PPT Agent LLM Orchestration

## Overview

Run PPT generation and refinement as an agent pipeline, not a single regex patch step.
Keep JSON as the execution contract, but let the LLM produce and iterate director-layer HTML first.
Compile HTML to JSON for stable execution.

## Workflow

1. Determine scope and runtime skill first.
- Use runtime skills as the control plane:
  - `slide_refine`
  - `deck_optimize`
  - `deck_regenerate`
  - `shape_replace`
  - `preview_refresh`
- Treat regex or keyword extraction as fallback guards, not the primary planner.
- If the user explicitly mentions a page, force page-level scope.

2. Build an LLM director-layer plan.
- Prefer `layout_engine=director_html` when LLM is enabled.
- Let the LLM return either:
  - director HTML directly, or
  - structured slide cards rendered to director HTML.
- Require text polishing for title and summary before compile.

3. Compile director HTML to execution JSON.
- Parse HTML deterministically.
- Produce:
  - `slides[].slide_index`
  - `slides[].background_prompt`
  - `slides[].illustrations[]`
  - `slides[].text_edits[]`
- Keep all coordinates and node overrides in JSON.

4. Execute image and PPT pipeline.
- Run Comfy image generation with no-text constraints.
- Apply page edits and shape replacements.
- Keep visible text editable in PPT text boxes.

5. Run quality and feedback loop.
- Verify target page hit, readability, and overlap.
- If result mismatches intent, rerun from director HTML stage with tightened constraints.

## Repo Mapping

- Planner and routing:
  - `tools/ppt_agent/application/planner.py`
  - `tools/ppt_agent/application/skill_router.py`
- Director layer:
  - `tools/ppt_agent/application/director_html.py`
- Execution:
  - `tools/ppt_agent/application/orchestrator.py`
- Server endpoints:
  - `tools/ppt_agent/presentation/server_*`

For detailed contracts and acceptance checks, read:
- `references/pipeline-contract.md`
