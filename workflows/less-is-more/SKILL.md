---
name: less-is-more
description: >
  Craft philosophy focused on removing clutter, cutting visual pollution, and
  doing one core thing at a high standard instead of shipping ten mediocre
  extras. Guides product scope, interface design, software architecture, and
  writing toward clarity, restraint, and excellence. Activate when simplifying
  cluttered designs, trimming feature creep, cleaning up noisy interfaces, or
  sharpening focus on what matters most.
license: Apache-2.0
metadata:
  category: workflows
  tags: "philosophy, minimalism, focus, ux, craft, simplicity"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Less is more

On *MasterChef*, nervous cooks try to impress the judges by crowding the plate with twelve components, three sauces, and extra garnishes. Because they split their focus twelve ways, every item comes out average and the dish loses its point. Winning cooks pick **one hero ingredient**, pair it with two or three elements that lift it, and execute those few things at a high standard.

AI models act like nervous cooks. Given a blank page, screen, or codebase, they try to look thorough by piling on panels, badges, subtitles, settings, flags, and caveats all at once. That impulse creates visual pollution and dilutes quality.

**Less is more** is the discipline of restraint: **remove clutter, protect focus, and do one core thing well.**

---

## 1. Name the hero and cut competing garnishes

Before building a screen, scoping a feature, designing an API, or writing a document, answer one question: **What is the hero?**

- **Give the hero the stage:** Dedicate at least 80% of the screen, the opening of a document, or the default CLI path to the main subject and primary action.
- **Cut anything that competes:** Every supporting button, panel, flag, or paragraph earns its place only if it makes the hero clearer or stronger. If it pulls attention away from the hero, remove it.
- **Aim for excellence over breadth:** One capability finished to a 10/10 standard beats ten half-baked extras at 6/10. Put your effort into speed, responsiveness, edge cases, and craft on the main job instead of adding side features.

---

## 2. Eliminate visual pollution

Cluttered interfaces tire the user before any real work begins. Strip visual noise from every screen:

1. **Delete redundant subtitles and labels:** When a heading, icon, or metric is already clear, stop explaining it underneath. Write `38 skills` instead of `Total Skills Count: 38`, and `Updated 3d ago` instead of `Last Updated Timestamp: 3 days ago`.
2. **Quiet secondary actions:** Keep visible text for the single primary button on screen, using 1 or 2 plain words such as `Run`, `Save`, or `Publish`. Use clean icons with accessible labels and hover hints for secondary toolbar actions instead of a row of text buttons.
3. **Keep settings out of the main view:** Settings support the work; they are never the work. Tuck secondary controls and rare options behind a single menu or light-dismiss popover rather than scattering sliders across the workspace or blocking the screen with a modal dialog.
4. **Let whitespace work:** Calm spacing and clear margins are not empty real estate. They guide the eye straight to what matters.

---

## 3. Keep scope, code, and prose lean

Apply the same restraint below the surface:

- **Product scope:** Ship the smallest complete workflow that solves the real problem cleanly. Leave speculative extras out until real usage asks for them.
- **Code and architecture:** Prefer one direct code path and sensible defaults over wrapper layers, speculative abstractions, and sprawling configuration flags.
- **Writing:** Lead with the outcome in plain words. Cut corporate jargon, empty hype, and throat-clearing introductions. Strong work speaks for itself without bragging.

---

## 4. Wipe the rim of the plate before serving

Before a dish leaves the pass, a chef wipes the rim of the plate to clear stray smudges. Run this final check before shipping a screen, code change, plan, or document:

- [ ] **2-second hero check:** Can a newcomer tell what the main subject and primary action are within two seconds?
- [ ] **Subtraction pass:** For every remaining element, ask *"What breaks if I delete this?"* If nothing breaks and focus improves, delete it.
- [ ] **Excellence check:** Is the core experience fast, cohesive, and finished to a high standard rather than diluted by extras?
- [ ] **Safety floor:** Keep what protects the user: semantic markup, keyboard access, legible contrast, accessible icon labels, and clear error messages when an action fails.
