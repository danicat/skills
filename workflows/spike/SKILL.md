---
name: spike
description: >
  Pragmatic Agile spike workflow for retiring technical, design, or functional
  risk before committing to implementation or estimates. Applies Extreme
  Programming risk-reduction rules with a right-sized toolkit, spanning spec and
  source audits, blast-radius traces, state-table walk-throughs, and throwaway
  probes, to deliver a fast, proof-backed Go/No-Go/Pivot verdict. Activate when
  running a spike or resolving a blocking unknown.
license: Apache-2.0
metadata:
  category: workflows
  tags: "spike, agile, xp, uncertainty, risk-reduction, feasibility, architecture"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Pragmatic spikes to retire risk

In Agile and Extreme Programming, a **spike** is a short, time-boxed probe. Teams run one **to buy certainty when a hard unknown blocks a design choice or effort size**.

Without strict focus, agents either polish a prototype into half-baked app code or write a long essay that retires zero risk. A good spike picks **the cheapest method that yields hard proof**, stays inside a tight scope box, and stops the moment it answers the blocking question.

---

## 🧭 Agile spike types & right-sized methods

Agile splits spikes into two camps. **Technical Spikes** test *how or whether a mechanism works*, while **Functional Spikes** clarify *what the workflow, edge-case rule, or contract must be*. Smart teams don't write code when a faster check settles the question:

| Spike type & unknown | Fastest method | Hard proof produced |
| :--- | :--- | :--- |
| **Technical: External API, quota, license, or wire behavior** | **Spec, contract, or upstream source audit** to read RFCs, vendor limits, pricing tiers, or library source code directly. | Exact spec clauses, rate ceilings, or upstream source links. |
| **Technical: Legacy coupling, migration cost, or blast radius** | **System seam & call-graph trace** to map callers, state changes, and schema borders in the project. | Caller map, breaking-change list, and clean seam points. |
| **Technical: Runtime speed, memory cap, or SDK fit** | **Throwaway code or benchmark probe** that runs a small script or test in `/tmp` or scratch space. | Measured timings, memory peaks, exit codes, or live traces. |
| **Functional: Unclear domain rules, edge cases, or state flows** | **Scenario & state-table walk-through** to map real inputs, failure modes, and conflict rules in a table. | Decision table, edge-case matrix, and clear rule contract. |

---

## 🔒 Pragmatic spike rules

1. **One question, one exit bar**:
   State the exact question the spike must answer and the **pass bar**, `GO` versus `NO-GO`, before you start. Never let a spike drift into open-ended browsing.
2. **Time-box and stop at "good enough"**:
   Keep the effort tightly bounded. Stop as soon as you have enough proof to decide, or as soon as the probe shows the path costs too much.
3. **Throwaway probes, lasting knowledge**:
   Any code or script written during a spike stays in `/tmp` or scratch space and never lands in tracked app files. The real output is the **decision record and updated estimate**.

---

## 📋 Spike workflow

- [ ] **Step 1: Frame the unknown and pass bar**
  Write down the exact technical or functional question, why it blocks design or sizing, the `GO / NO-GO` bar, and the scope box.
- [ ] **Step 2: Pick the cheapest proof method**
  Choose the fastest method from the preceding table: spec or source audit, system seam trace, state-table walk-through, or `/tmp` probe.
- [ ] **Step 3: Run the probe and collect proof**
  Capture hard facts such as source lines, quota limits, state tables, or live timings rather than hunches.
- [ ] **Step 4: Keep the workspace clean**
  Confirm that any scratch scripts stay in `/tmp` or scratch space and that `git status` in the project workspace is clean.
- [ ] **Step 5: Issue the verdict and unblock planning**
  Deliver the Spike Report below with a clear **`GO`**, **`NO-GO`**, or **`PIVOT`** verdict and its impact on effort size.

---

## ✅ Quality gates

Before closing the spike, verify all three checks:

1. **Proof over hunches**: Every claim rests on hard facts such as upstream source or spec links, call traces, state tables, or live probe numbers.
2. **Zero workspace pollution**: No scratch hacks or temp files remain in tracked project folders.
3. **Decision-ready handoff**: The report gives a clear `GO / NO-GO / PIVOT` verdict and states how the findings change the plan or effort size.

---

## 📄 Output template

```markdown
## 1. Spike charter
- **Spike type**: <Technical Spike | Functional Spike>
- **Blocking question**: <What specific unknown blocks design or sizing?>
- **Decision bar**: <What must hold true for a GO verdict?>
- **Method chosen**: <Spec/Source Audit | System Seam Trace | State Walk-Through | Throwaway Probe>

## 2. Proof & findings
- **Targets checked / setup**: <Upstream specs, project seams, state matrix, or `/tmp/spike-*` probe>
- **Hard findings**:
  - <Verified fact, limit, trace path, or measured metric>
  - <Surfaced edge cases, hidden coupling, or operational risks>

## 3. Verdict & planning impact
- **Verdict**: **[GO | NO-GO | PIVOT]**
- **Effort / risk impact**: <Low / Medium / High and why>
- **Next step**: <Concrete path forward for the build plan>
```
