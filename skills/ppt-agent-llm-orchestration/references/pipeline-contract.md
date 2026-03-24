# Pipeline Contract

## Purpose

Define stable contracts for LLM-first PPT agent orchestration so that planning stays flexible while execution remains deterministic.

## Stage Contract

1. `Intent + Skill`
- Input: user message, selected slides, active PPT state.
- Output: `scope`, `skill_name`, `reason`.

2. `Director Layer`
- Input: message + per-slide text contexts.
- Output: director HTML with fields:
  - `title`
  - `summary`
  - `layout`
  - `background_prompt`
  - `illustration_prompt`

3. `Compile Layer`
- Input: director HTML.
- Output: execution JSON patch:
  - `slides[].slide_index`
  - `slides[].background_prompt`
  - `slides[].illustrations[]`
  - `slides[].text_edits[]`

4. `Execution Layer`
- Input: merged job JSON.
- Output: revised PPT/PDF + preview + revision metadata.

## Required Guardrails

- Explicit page references in message override UI selection.
- Image prompts must include no-text constraints.
- User-facing text must remain editable in PPT text boxes.
- LLM output is advisory until compiled and validated.

## Acceptance Checklist

- Target page hit rate is correct (no wrong-page edits).
- Scope is correct (no accidental full regenerate for page-level request).
- Generated images avoid gibberish text artifacts.
- Layout is readable and non-overlapping after quality pass.
