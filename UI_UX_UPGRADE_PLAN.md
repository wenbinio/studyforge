# StudyForge UI/UX Upgrade Plan (Checklist-Only)

This document provides a thorough UI/UX upgrade plan for StudyForge’s desktop apps (`study_app`, `study_app_v2`) with **checklists only** (no phased roadmap).

It is grounded in:
- Current codebase structure and styling (`ui/styles.py`, `ui/app.py`, tab modules)
- Established UX best practices (consistency, visibility of system status, recognition over recall, error prevention, accessibility contrast/focus)
- Common patterns from successful learning apps (clear review workflows, quick capture/generation, low-friction progress feedback)

---

## 1) Current-State Audit Checklist (from code)

- [x] Confirm shared design system exists in both variants via `ui/styles.py` (colors, fonts, spacing tokens).
- [x] Confirm sidebar + tab architecture is consistent and scalable (`ui/app.py` + per-tab `CTkFrame` pattern).
- [x] Confirm dark-first visual style is already implemented and can be iterated without structural rewrite.
- [x] Confirm semantic color intent exists (`success`, `warning`, `danger`, rating colors), even if usage is inconsistent.
- [x] Confirm consistent typography baseline (`Segoe UI`, compact study-oriented density).
- [x] Confirm focus mode capability already exists in Notes (supports deep-work UX).
- [x] Normalize hardcoded per-file hex colors to style tokens (notably in flashcards/quiz/settings/notes/participation).
- [x] Standardize button hierarchy (primary/secondary/tertiary/destructive) across all tabs.
- [x] Improve keyboard-first navigation consistency (especially tab traversal and explicit focus visibility).
- [x] Improve visual contrast of muted text and secondary labels on dark surfaces.

---

## 2) Product-Level UX Goals Checklist

- [ ] Make daily workflow obvious in under 10 seconds: **Review due cards → Quiz weak areas → Capture note gaps**.
- [ ] Reduce cognitive overhead: fewer competing accent colors and fewer one-off button styles.
- [ ] Make progress legible at a glance: due count, streak trend, today’s completion, next best action.
- [ ] Keep AI actions explicit and safe: clear loading/error/success states; no ambiguous “silent failure.”
- [ ] Preserve “power-user speed” via keyboard shortcuts while improving discoverability for new users.

---

## 3) Color System Upgrade Checklist

### A. Token model (what to define)
- [ ] Keep existing dark theme base, but formalize role-based tokens:
  - [ ] `bg.canvas`, `bg.surface`, `bg.elevated`, `bg.input`
  - [ ] `text.primary`, `text.secondary`, `text.tertiary`, `text.inverse`
  - [ ] `action.primary`, `action.primary_hover`, `action.secondary`, `action.ghost`
  - [ ] `state.success`, `state.warning`, `state.error`, `state.info`
  - [ ] `focus.ring`, `border.default`, `border.strong`
- [x] Map all module-level hardcoded colors to tokens.
- [x] Keep one primary accent family for global action identity.
- [x] Reserve alternate accent(s) only for mode indicators (e.g., interleaved mode), not general action buttons.

### B. Contrast/readability guardrails
- [x] Ensure body text contrast is comfortably readable on primary and secondary dark surfaces.
- [x] Increase contrast for muted metadata labels where currently too dim.
- [ ] Ensure state colors are not color-only signals (pair with icon/text label).
- [x] Ensure focus indicator is always visible against dark backgrounds.

### C. Suggested palette direction (starting point, not mandatory)
- [ ] Keep dark navy/purple base but reduce saturation in large surfaces.
- [ ] Keep violet as primary accent for brand continuity.
- [ ] Use a clearer “info blue” for neutral status and links.
- [ ] Slightly warm success/warning/error tones for better differentiation in dark UI.

---

## 4) Typography & Spacing Checklist

- [ ] Keep Segoe UI as default desktop typeface for native readability.
- [ ] Tighten hierarchy to 3 practical levels:
  - [ ] Page title
  - [ ] Section heading
  - [ ] Body/meta text
- [ ] Standardize min touch/click target heights (buttons, segmented controls, nav items).
- [ ] Normalize vertical rhythm (consistent gaps between sections/cards/forms).
- [ ] Ensure line length in note/quiz explanation areas stays comfortably scannable.

---

## 5) Navigation & Information Architecture Checklist

- [ ] Keep left-sidebar model, but clarify “primary flow” ordering:
  - [ ] Dashboard
  - [ ] Review (Flashcards)
  - [ ] Quiz
  - [ ] Notes
  - [ ] Timer
  - [ ] Specialty tabs (Hypotheticals/Essays/Participation)
  - [ ] Settings
- [ ] Add optional compact/collapsed sidebar behavior for smaller laptop screens.
- [ ] Strengthen active-state indication (background + text/icon + optional left rail marker).
- [ ] Ensure hover, active, and keyboard-focus states are all distinct.
- [ ] Add contextual header action per tab: “primary next action” visible immediately.

---

## 6) Component System Checklist

### Buttons
- [x] Define and enforce 4 button variants: primary, secondary, ghost, destructive.
- [ ] Use consistent corner radius, padding, icon placement, and disabled styles.
- [ ] Ensure every critical action has loading and completion feedback.

### Cards/Panels
- [ ] Standardize card elevation model (flat/raised) and border usage.
- [ ] Keep card headers concise with predictable title + metadata slots.
- [ ] Ensure empty-state cards include one clear recovery/action path.

### Forms/Inputs
- [ ] Standardize input labels, helper text, and error states.
- [ ] Ensure required-field and validation messaging is immediate and local.
- [ ] Ensure entry focus state is highly visible in dark mode.

### Status/Badges/Progress
- [ ] Define badge variants (topic, due, difficulty, AI-generated, complete/incomplete).
- [ ] Standardize progress bar and countdown visual language across Pomodoro + quiz flows.
- [ ] Ensure performance states are understandable without relying on color alone.

---

## 7) Tab-Specific UX Checklist

### Dashboard
- [ ] Prioritize “What should I do now?” above passive metrics.
- [ ] Highlight due workload and estimated completion effort for today.
- [ ] Keep analytics concise; avoid over-dense stat grids.

### Flashcards
- [ ] Make review modes (normal/interleaved) explicit with segmented control styling.
- [ ] Keep answer/reveal/rating flow visually linear and low-friction.
- [ ] Standardize rating button semantics and spacing for fast repeated use.

### Quiz
- [ ] Clarify quiz setup choices before generation (note source, count, difficulty, mode).
- [ ] Improve answer feedback hierarchy: correctness first, explanation second, source context third.
- [ ] Keep next-question CTA placement fixed and predictable.

### Notes
- [ ] Keep capture/edit/preview controls in a stable top toolbar.
- [ ] Improve affordance for import/export/search/find workflows.
- [ ] Ensure focus mode strips non-essential chrome while keeping critical controls discoverable.

### Pomodoro
- [ ] Strengthen timer state transitions with clearer visual/audio cues.
- [ ] Improve legibility of current session type and cycle progress.
- [ ] Keep start/pause/reset controls consistent with app-wide button system.

### Settings
- [ ] Group settings by task (AI connection, study defaults, interface).
- [ ] Ensure API connection testing clearly communicates success/failure/retry paths.
- [ ] Keep sensitive fields masked and explain storage behavior clearly.

---

## 8) Accessibility & Usability Checklist

- [ ] Ensure keyboard navigation covers primary workflows end-to-end.
- [ ] Ensure visible focus indicators on all interactive elements.
- [ ] Ensure text contrast and control contrast are readable in dark mode.
- [ ] Ensure icons/emojis are paired with text labels (no icon-only critical controls).
- [ ] Ensure error messages are specific, local, and actionable.
- [ ] Ensure long-running AI actions provide progress/status feedback.
- [ ] Ensure destructive actions have confirmation affordances where appropriate.

---

## 9) Competitor-Informed Design Checklist (What to Emulate/Avoid)

### Emulate
- [ ] Fast “start review now” entry point from home/dashboard.
- [ ] Clear due counts and session momentum indicators.
- [ ] Lightweight creation flows (add note/card/question in minimal steps).
- [ ] Immediate feedback loops after each review/quiz interaction.
- [ ] Strong consistency in component styling across modules.

### Avoid
- [ ] Over-gamification that hides actual learning progress.
- [ ] Too many simultaneous accent colors competing for attention.
- [ ] Dense controls without hierarchy in high-frequency study screens.
- [ ] Deep setting dependencies that block first successful session.
- [ ] Modal-heavy flows that interrupt rapid review loops.

---

## 10) Definition of Done Checklist (for future implementation PRs)

- [x] All hardcoded UI colors replaced by shared tokens or documented exceptions.
- [x] All major interactive components use standardized variant system.
- [ ] All tabs pass keyboard navigation and focus visibility spot-check.
- [ ] Dashboard/Flashcards/Quiz/Notes/Pomodoro/Settings all show consistent action hierarchy.
- [ ] Muted/secondary text remains readable on dark surfaces.
- [ ] Empty/loading/error/success states are present for major user flows.
- [ ] No regressions in existing behavior while applying visual/interaction updates.
