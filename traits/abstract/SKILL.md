---
name: abstract
description: >
  Philosophical and inductive knowledge-distillation workflow that extracts
  general principles, causal laws, and portable concepts from concrete facts,
  evidence, and examples. Applies Aristotle's essence-versus-accident split,
  Bacon's inductive ascent, Peirce's concept naming, and Popper's flip test to
  turn raw facts into high-value knowledge without hollow platitudes. Activate
  when abstracting ideas, distilling lessons, or synthesizing principles from
  evidence.
license: Apache-2.0
metadata:
  category: traits
  tags: "abstraction, philosophy, epistemology, induction, principles, synthesis"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Abstract general ideas from concrete facts

In philosophy, **abstraction** means drawing general knowledge out of raw facts and cases. Without a clear method, agents fail at two extremes:
1. **Case-by-case recounting**: Repeating what happened in each event. This traps the insight inside local names, dates, and one-off details.
2. **Hollow truisms**: Stripping away so much substance that only a truism remains, such as *"test well"* or *"plan ahead."* Statements that forbid nothing teach nothing.

`abstract` uses four classic thinking tools to turn raw facts and cases into **portable, high-value rules**:

---

## 🏛️ The 4 pillars of abstraction

| Lens | Thinker | How it works in practice |
| :--- | :--- | :--- |
| **1. Essence vs. accident** | **Aristotle** | Split **essence**, or what makes the pattern hold, from **accidents** like time, place, path, tool name, or actor that can change without breaking the rule. |
| **2. Inductive ascent** | **Aristotle & Francis Bacon** | Climb from scattered facts to the **causal law** that explains *why* those facts happened before stating a general rule. |
| **3. Concept naming** | **C.S. Peirce** | Turn a repeated finding, such as *"this step failed because nobody checked the one-way action,"* into a crisp noun handle: *"the one-way action gate."* |
| **4. Flip test** | **Karl Popper** | Judge a rule by what it **forbids**. If no sensible person would ever defend the reverse of your statement, it's a truism, not knowledge. |

---

## 📋 Distillation workflow

- [ ] **Step 1: Anchor in concrete facts**
  List the specific facts, examples, incidents, quotes, or findings in front of you. Keep them tied to real proof before you interpret them.
- [ ] **Step 2: Strip accidents from essence**
  For each group of facts, drop the **accidents** such as local names, IDs, dates, or tool quirks. Keep only the **core structure**: the actors, motives, limits, and state changes that repeat across cases.
- [ ] **Step 3: State the causal law**
  Explain the mechanism that links cause to effect. An abstraction without a causal *why* is just a summary.
- [ ] **Step 4: Name the concept and write the rule**
  Coin a short, clear handle for the pattern after Peirce. Write the rule in 1 to 2 sentences so it guides choices in any domain.
- [ ] **Step 5: Run Popper's flip test and set limits**
  Check what the rule forbids, verify every gate below, and state the exact limits where the rule stops holding true.

---

## ✅ Quality gates

Before sharing abstracted ideas, test every rule against four checks:

1. **Popper's flip test**: State the reverse of your rule. If nobody would ever defend the reverse, such as *"write broken code,"* your rule carries zero signal. Rewrite it to expose a real trade-off or non-obvious insight.
2. **Aristotle's accident check**: A reader who knows nothing about the source project, chat, or domain history must be able to grasp and apply the concept right away.
3. **Causal grounding**: Every rule pairs *what holds true* with *why it works that way*, and cites the concrete facts that produced it.
4. **Clear scope limits**: Every general claim names the exact boundary where it fails or yields to another rule.

---

## 📄 Output template

```markdown
## 1. Concrete fact base
- **Fact 1**: <Concrete event, example, or finding + source>
- **Fact 2**: <Concrete event, example, or finding + source>
- **Fact 3**: <Concrete event, example, or finding + source>

## 2. Essence vs. accident split
| Pattern | Accidental details (stripped) | Essential structure (kept) |
| :--- | :--- | :--- |
| <Pattern 1> | <Local names, tools, dates, one-off setup> | <Core relationship that repeats across cases> |

## 3. Abstracted concepts and rules

### 1. <Crisp concept name>
- **General rule**: <1–2 sentences stating the portable principle or law>
- **Causal law (why it holds)**: <The mechanism that drives this outcome>
- **What it forbids (Popper flip test)**: <The plausible habit or choice this rule rules out>
- **Grounded in**: <Facts 1..N>
- **Scope limit**: <Where this rule stops holding true>
```
