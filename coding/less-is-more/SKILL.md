---
name: less-is-more
description: >
  Frontend design and universal simplification skill that counters AI interface
  bloat across web UIs, toolbars, settings menus, and UI copy. Applies the
  Inverted Pyramid to keep the main subject front and center, hides settings in
  non-modal popovers, replaces text-heavy buttons with Material Symbols icons
  and hover hints, cuts redundant labels, and enforces plain English. Activate
  when designing UIs, simplifying cluttered layouts, replacing modal dialogs or
  noisy toolbars, tightening copy, or pruning feature scope.
license: Apache-2.0
metadata:
  category: coding
  tags: "frontend, design, ui, ux, minimalism, readability"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Less is more

Give the screen to the user's main work and hide the rest. AI models default to bloated interfaces because they try to look thorough by showing every control, setting, badge, and caption at once. When you try to do everything on one screen, you do everything in a mediocre way.

Focus on what matters and do the important things well. Every extra button, label, and subtitle steals attention from the main task.

## 1. Use the inverted pyramid to find what matters

Before writing layout code, ask: **"What's the user here to see, create, or do?"**

- In a game design tool, the **game description** is the main thing.
- In an avatar builder, the **avatar** is the main thing.
- In a paint or code studio, the **canvas** is the main thing.

Order the screen with the Inverted Pyramid:

1. **Forefront**: Give 80% or more of the screen to the main subject and the single primary action.
2. **Edges**: Place secondary actions around the edges as compact icons that stay out of the way.
3. **Hidden menu**: Tuck all settings, presets, and export options inside a menu or `popover`. Settings support the work; they're never the main event.

For deeper hierarchy rules, load the optional `inverted-pyramid` skill via `kungfu load inverted-pyramid`. You can also install it with `npx skills add danicat/skills --skill inverted-pyramid -y`.

## 2. Replace text buttons with icons and hover hints

Not every button needs a visible text label. Putting words on every action turns a clean toolbar into a wall of text like `[Copy Code] [Download File] [Open Settings] [Delete]`.

- Use [Material Symbols](https://fonts.google.com/icons) such as `settings`, `tune`, `content_copy`, `download`, `delete`, and `refresh` for toolbar and card actions.
- Give every icon button an `aria-label` and a hover hint with `popover="hint"` or `title`. The label appears only when the user points at the button.
- Save visible text for the single primary button on the screen, kept to 1 or 2 words like `Generate`, `Save`, or `Run`.

## 3. Hide settings in a menu, never in a modal

Details and settings should surface only when needed. Never dump sliders and dropdowns onto the main workspace, and never trap the user in a 1998-style modal dialog just to tweak a setting or view metadata.

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

<!-- 1. Forefront: The avatar and primary prompt take 80%+ of the screen -->
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

## 4. Cut filler subtitles and redundant labels

AI interfaces talk too much. When a heading, value, or icon is clear on its own, stop explaining it.

| Bloated AI Default ❌ | Clean Less-Is-More ✅ |
| :--- | :--- |
| Every `<h1>`, `<h2>`, and card has a gray subtitle. | Add a subtitle only when the title isn't self-evident. |
| `[Copy Code] [Download File] [Open Settings]` | Use Material Symbols `content_copy`, `download`, and `tune` with `popover="hint"`. |
| `Total Skills Count: 32` | Write `32 skills`. |
| `Last Updated Timestamp: 3 days ago` | Write `Updated 3d ago`. |
| 6 dropdowns and 4 toggles before the main canvas. | Use 1 `tune` icon button that opens a `popover="auto"` menu. |

## 5. Write plain English without bragging

When you do write text, make every word count. As the [Harvard Business Review jargon study](https://hbr.org/2021/03/do-you-have-a-jargon-problem) shows, writers use big words and hype to hide self-doubt, which lowers reader trust.

- **No bragging or marketing speak**: Cut `blazing-fast`, `world-class`, `seamless`, `robust`, `cutting-edge`, and `next-generation`. Good work speaks for itself.
- **No office jargon**: Replace `leverage`, `utilize`, `holistic`, and `synergy` with `use`, `run`, and `complete`.
- **No AI throat-clearing**: Cut `delve into`, `tapestry`, `landscape`, and `In today's fast-paced world`.
- **Hit clear scores**: Keep Gunning Fog at **11–15** and under **12** for UI copy, Slop under **20**, and Vale at **0 errors and warnings**.

To audit prose and strip AI clichés, load the optional `deslopify` skill via `kungfu load deslopify`. You can also install it with `npx skills add danicat/skills --skill deslopify -y`.

## 6. Apply the subtraction test

This philosophy applies to code, CLI tools, docs, and life. Before adding any button, subtitle, flag, or feature, ask: **"What breaks if you delete this?"** If nothing breaks, delete it. For deeper scope pruning, load the optional `uno-reverse` skill via `kungfu load uno-reverse` or install it with `npx skills add danicat/skills --skill uno-reverse -y`.

Only keep what protects the user:
- **Accessibility**: Keep semantic HTML, keyboard focus, strong contrast, and `aria-label` on every icon button.
- **Loud errors**: When an action fails, fail fast and show the exact error and fix.
- **Pre-delivery check**: Confirm the main subject gets 80% of the screen, secondary tools use icons with hover hints, settings live in a `popover`, and no redundant subtitles remain.
