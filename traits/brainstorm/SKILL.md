---
name: brainstorm
description: >
  Divergent ideation and option-generation engine that prevents LLM mode
  collapse through orthogonal axis perturbation and deferred convergence.
  Generates structurally distinct design alternatives across subtractive,
  convention-first, declarative, UX-backward, and first-principles lenses before
  scoring trade-offs. Activate when exploring alternative architectures,
  generating creative options, breaking out of local maxima, or comparing
  fundamentally different ways to solve a problem.
license: Apache-2.0
metadata:
  category: traits
  tags: "ideation, divergence, options, creativity, architecture, trade-offs"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Brainstorm orthogonal options

When an LLM generates ideas in a single pass, token conditioning causes **mode collapse**. Options two through five become minor tweaks of option one, and the session picks a winner before exploring the design space.

`brainstorm` prevents mode collapse in two ways:
1. **Orthogonal axes**: Each option must follow a distinct constraint rule instead of varying small details along a single path.
2. **Deferred judgment**: You hold off on ranking, scoring, and coding until you write out every option in full.

---

## 🧭 The 5 orthogonal lenses

Unless the user asks for custom angles, generate **5 distinct options**—one for each lens below:

| Lens | Core constraint question | What it forces |
| :--- | :--- | :--- |
| **1. Subtractive / zero-code** | *How can you solve or drop this problem by deleting code, cutting scope, or changing the workflow instead of building new tools?* | Challenges the assumption that you need new code at all. |
| **2. Convention-first baseline** | *What's the simplest, lowest-risk fix using standard library primitives and common idioms?* | Sets a realistic cost and complexity baseline. |
| **3. Declarative / data-driven** | *What happens when you move control flow out of code and into a static table, schema, state machine, or settings file?* | Separates policy and data from execution logic. |
| **4. UX-backward inversion** | *Starting from the ideal one-line caller API or human workflow, what internal design makes that interface work?* | Optimizes for ergonomics and low cognitive load first. |
| **5. Blank-slate / 10x scale** | *If you ignored legacy limits and designed from first principles for 10x scale or speed, what would you build?* | Breaks local maxima and small-step habits. |

---

## 📋 Operational workflow

- [ ] **Step 1: Problem framing and hard rules**
  State the core goal, hard limits, and non-goals in 3 to 5 short bullets. Don't propose solutions in this step.
- [ ] **Step 2: Lens selection**
  Pick the 5 standard lenses, or `N` custom axes if the user asked for a specific count or domain focus. If the user's limits conflict or seem unclear, call `ask_question` to clarify before generating options.
- [ ] **Step 3: Divergent generation**
  Write one concrete proposal per lens. When subagents are available, you can spawn one worker per lens so ideas don't anchor each other; otherwise step through each lens one by one. Every option must include:
  - **Core mechanism**: How the design works in 2 to 3 short sentences.
  - **Concrete sketch**: A brief code snippet, data schema, CLI call, or text diagram showing the design.
  - **Primary failure mode**: The exact case where this option breaks down or becomes the wrong choice.
- [ ] **Step 4: Validation gate and trade-off matrix**
  Run the validation check below to confirm that no two options share the same mechanism. Then score all options across **Effort**, **Maintenance Cost**, **Risk**, and **Ergonomics**, and note whether two options combine into a stronger hybrid.
- [ ] **Step 5: Interactive selection gate (`ask_question`)**
  Stop before editing project code. Present the option table and call `ask_question` so the user can pick a path, combine two options, or narrow the constraints.

---

## ✅ Validation gate

Before showing the brainstorm options to the user, check all three rules:

1. **Distinct mechanisms**: If two options differ only by library name, flag value, or label, drop the duplicate and write a new option from a different lens.
2. **Concrete sketch**: Every option includes a code block, schema, or diagram, not prose alone.
3. **Zero premature edits**: You haven't touched any project source files before the user picks an option in Step 5.

---

## 📄 Output template

```markdown
## 1. Problem framing and hard rules
- **Goal**: <1-sentence goal>
- **Hard limits**: <non-negotiable requirements>
- **Non-goals**: <what stays out of scope>

## 2. Orthogonal option portfolio

### Option 1: <Title> (Subtractive lens)
- **Core mechanism**: <2-3 sentences>
- **Concrete sketch**:
  ```<lang>
  <minimal code or schema>
  ```
- **Primary failure mode**: <when this fails>

## 3. Comparative trade-off matrix

| Option | Lens | Effort | Risk | Key advantage | Main trade-off |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. <Title>** | Subtractive | Low | Low | <advantage> | <trade-off> |
| **2. <Title>** | Baseline | Low-Med | Low | <advantage> | <trade-off> |
| **3. <Title>** | Declarative | Med | Low | <advantage> | <trade-off> |
| **4. <Title>** | UX-backward | Med | Med | <advantage> | <trade-off> |
| **5. <Title>** | Blank-slate | High | High | <advantage> | <trade-off> |

## 4. Hybrid synthesis
- **Recommended pairing**: <How two lenses combine, or why a single lens wins>
```
