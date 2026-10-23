---
name: less-is-more
description: >
  Life and craft philosophy inspired by MasterChef that teaches focusing on what
  is important and doing it well instead of crowding the plate with mediocre
  extras. Counters AI bloat across product scope, writing, architecture, and
  frontend UX by elevating the hero ingredient, applying the Inverted Pyramid,
  replacing noisy text buttons with Material Symbols icons and hover hints,
  hiding settings in non-modal popovers, and enforcing plain English. Activate
  when simplifying cluttered frontend interfaces, pruning feature scope,
  tightening prose, or focusing a design on what matters most.
license: Apache-2.0
metadata:
  category: traits
  tags: "philosophy, minimalism, focus, ux, frontend, readability"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  catalog: https://skills.danicat.dev
---

# Less is more

On *MasterChef*, nervous cooks try to impress the judges by crowding the plate with twelve components, three sauces, a foam, and extra garnishes. Because they split their focus twelve ways, every item comes out mediocre and the dish loses its point. Winning cooks keep it simple: they pick **one hero ingredient**, pair it with two or three elements that make it shine, and cook those few things to perfection.

AI models act like nervous cooks across everything they build. Whether asked to design a web app, write an essay, plan a project, or design an API, they try to look thorough by dumping every possible control, setting, badge, subtitle, caveat, and buzzword onto the plate at once.

**Less is more** is a life and craft philosophy: **focus on what matters and do the important things well.** When you try to do everything at once, you do everything in a mediocre way.

---

## 1. Pick the hero ingredient and cut competing garnishes

Before writing code, drafting prose, or planning a project, ask one question: **"What's the hero on this plate?"**

- **In a dish**: The seared scallop is the hero. A heavy truffle cream sauce that drowns out the scallop doesn't add value; it ruins the dish.
- **In a product or project plan**: The core job the user hired the tool to do is the hero. Ten half-baked side features steal time and polish from the main workflow.
- **In a document or pitch**: The main takeaway is the hero. Five pages of background throat-clearing bury the point.
- **In a user interface**: What the user came to see, create, or run is the hero:
  - In a game design tool, the **game description** is the hero.
  - In an avatar builder, the **avatar** is the hero.
  - In a paint or code studio, the **canvas** is the hero.

Apply two rules to every supporting element:
1. **Does it elevate the hero?** Every button, paragraph, flag, or feature earns its place only if it makes the hero clearer or stronger. If it competes with the hero for attention, cut it.
2. **Depth over breadth**: Three components executed at 10/10 beat ten components executed at 6/10. Spend your effort perfecting the core experience instead of adding extra garnishes.

---

## 2. Order attention with the inverted pyramid

Put the most important thing first and push secondary details down the hierarchy:

1. **Forefront**: Give 80% or more of the screen, the opening 150 words of a document, or the default CLI path to the main subject and primary action.
2. **Edges**: Place secondary actions around the edges so they stay within reach without blocking the work.
3. **Hidden menu**: Tuck settings, presets, export formats, and rare options inside a menu, `popover`, or appendix. Settings support the work; they're never the main event.

---

## 3. Clean up frontend interfaces to improve UX

Web apps and user interfaces are one of the best places to apply `less-is-more`.

### Replace text buttons with icons and hover hints
Not every button needs a visible text label. Putting words on every action turns a clean toolbar into a wall of text like `[Copy Code] [Download File] [Open Settings] [Delete]`.

- Use [Material Symbols](https://fonts.google.com/icons) such as `settings`, `tune`, `content_copy`, `download`, `delete`, and `refresh` for toolbar and card actions.
- Give every icon button an `aria-label` and a hover hint with `popover="hint"` or `title`. The label appears only when the user points at the button.
- Save visible text for the single primary button on the screen, kept to 1 or 2 words like `Generate`, `Save`, or `Run`.

### Hide settings in a menu, never in a modal
Details and settings should appear only when needed. Never dump sliders and dropdowns onto the main workspace, and never trap the user in a 1998-style modal dialog just to tweak a setting or view metadata.

- Put options behind one `settings` gear or `tune` sliders icon button that opens a light-dismiss `popover="auto"` menu. Clicking outside closes it right away.
- Anchor the `popover` to its button with `anchor-name`, `position-anchor`, and `margin: 0` so it drops down from the toolbar instead of centering on the screen.
- Group rare options inside `<details>` and `<summary>` tags within the settings menu so the default view stays short.

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
<style>
  .icon-btn { anchor-name: --config-btn; }
  #config-menu, #config-tip {
    position-anchor: --config-btn;
    position-area: block-end span-inline-start;
    position-try-fallbacks: flip-block, flip-inline;
    inset: auto;
    margin: 0;
  }
</style>

<!-- 1. Forefront: The hero (avatar + primary prompt) takes 80%+ of the screen -->
<main class="studio">
  <header class="toolbar">
    <h1>Avatar Studio</h1>
    <!-- 2. Edges: Icon-only Material button + hover hint -->
    <button type="button" class="icon-btn"
            commandfor="config-menu" command="toggle-popover"
            interestfor="config-tip" aria-label="Settings">
      <span class="material-symbols-outlined" aria-hidden="true">tune</span>
    </button>
    <div id="config-tip" popover="hint">Settings</div>
  </header>

  <figure class="avatar-stage">
    <img src="avatar.webp" alt="Generated character avatar" width="512" height="512">
  </figure>

  <form class="prompt-bar">
    <input type="text" placeholder="Describe your avatar..." aria-label="Avatar prompt">
    <button type="submit">Generate</button>
  </form>

  <!-- 3. Hidden menu: Settings live in a light-dismiss popover -->
  <aside id="config-menu" popover="auto">
    <label>Style <select name="style"><option>Pixel</option><option>Vector</option></select></label>
    <details>
      <summary>Advanced</summary>
      <label>Seed <input type="number" name="seed" value="42"></label>
    </details>
  </aside>
</main>
```

### Cut filler subtitles and redundant labels
When a heading, number, or icon is clear on its own, stop explaining it:

| Over-Plated AI Default ❌ | Clean Less-Is-More ✅ |
| :--- | :--- |
| Every `<h1>`, `<h2>`, and card has a gray subtitle. | Add a subtitle only when the title isn't self-evident. |
| `[Copy Code] [Download File] [Open Settings]` | Use Material Symbols `content_copy`, `download`, and `tune` with `popover="hint"`. |
| `Total Skills Count: 32` | Write `32 skills`. |
| `Last Updated Timestamp: 3 days ago` | Write `Updated 3d ago`. |
| 6 dropdowns and 4 toggles before the main canvas. | Use 1 `tune` icon button that opens a `popover="auto"` menu. |

---

## 4. Write plain English without bragging

Just as insecure cooks hide a poorly cooked steak under three sauces, insecure writers use big words and hype to cover up weak ideas. As the [Harvard Business Review jargon study](https://hbr.org/2021/03/do-you-have-a-jargon-problem) shows, pretentious phrasing lowers reader trust.

- **No bragging or marketing speak**: Cut `blazing-fast`, `world-class`, `seamless`, `robust`, `cutting-edge`, and `next-generation`. Good work speaks for itself.
- **No office jargon**: Replace `leverage`, `utilize`, `holistic`, and `synergy` with `use`, `run`, and `complete`.
- **No AI throat-clearing**: Cut `delve into`, `tapestry`, `landscape`, and `In today's fast-paced world`.
- **Hit clear scores**: Keep Gunning Fog at **11–15** and under **12** for UI copy, Slop under **20**, and Vale at **0 errors and warnings**.

---

## 5. Wipe the rim of the plate before serving

Before a dish leaves the pass, a chef wipes the rim of the plate and removes anything that doesn't belong. Run this final check before shipping a screen, doc, code change, or plan.

- [ ] **Hero check**: Can a newcomer tell what the hero is within 2 seconds?
- [ ] **Craft check**: Are the 1 to 3 core elements finished to a high standard instead of diluted by side features?
- [ ] **Subtraction test**: Ask **"What breaks if you delete this?"** for every remaining button, subtitle, flag, or paragraph. If nothing breaks, remove it.
- [ ] **Safety floor**: Keep what protects the user—semantic HTML, keyboard focus, strong contrast, `aria-label` on icon buttons, and loud, actionable error messages when an action fails.
