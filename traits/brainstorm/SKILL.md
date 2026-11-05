---
name: brainstorm
description: >
  Divergent ideation and option-generation engine that breaks LLM mode collapse
  using symmetry-breaking algorithms and optional parallel subagent dispatch.
  Applies taboo deflection, assumption inversion, tension breaking,
  cross-domain transfer, and testable bets to generate 3 high-conviction
  proposals per run, or fans out identical instructions across N subagents
  before reducing consensus and outlier breakthroughs. Activate on
  brainstorm(N), /brainstorm, or when exploring non-obvious solutions,
  architectures, or creative directions.
license: Apache-2.0
metadata:
  category: traits
  tags: "ideation, divergence, creativity, architecture, subagents, trade-offs"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.1"
  catalog: https://skills.danicat.dev
---

# Brainstorm high-signal options

Standard LLM brainstorming fails in four ways:
1. **Greedy mode collapse**: In a single pass, token weights pull every idea toward the most common textbook answer. Options two and three become minor edits of option one.
2. **Box-checking filler**: Fixed domain templates force the agent to write one real answer and pad the rest with weak decoys.
3. **Parallel rail lock**: When parallel workers share fixed buckets, every worker walks down the same rails and returns near-twin ideas.
4. **Checklist poisoning**: When the framing step dumps raw examples or topic lists into `Hard limits`, workers cram every prompt noun into the output instead of abstracting the core idea.

`brainstorm` solves this with **essence-first framing**, **six symmetry-breaking steps**, and **same-prompt parallel dispatch** via `brainstorm(N)`. Instead of sorting ideas into fixed buckets or reciting a topic list, each run strips one-off details, burns the obvious default, and flips hidden premises. It then breaks the core bottleneck and frames **3 high-conviction testable bets**.

---

## 🔬 The 6 symmetry-breaking algorithms

Every brainstorm agent runs these six steps to break out of local maxima:

| Algorithm | How it works | Why it breaks mode collapse |
| :--- | :--- | :--- |
| **1. Unscripted micro-probe** | Run 1 or 2 fast read-only checks on the workspace, data, or prior art before drafting ideas. | Grounds ideas in real bottlenecks and gives parallel workers different starting facts on turn 1. |
| **2. Burn the default** | Name the 1 to 3 most obvious textbook answers in one sentence each and ban them in a **Banned default box**. | Knocks the agent off its top token peak before it drafts real proposals. |
| **3. Assumption flip** | List 3 to 5 hidden premises baked into the request or current setup. Ask what design appears if each premise is false. | Different runs flip different premises and branch into distinct solution trees without custom prompts. |
| **4. Tension breaking** | State the core conflict: *"Improving X hurts Y because of Z."* Attack or remove `Z` instead of sliding along `X vs. Y`. | Rejects weak middle grounds and forces a concrete causal mechanism. |
| **5. Cross-domain transfer** | Strip domain nouns to expose the bare pattern, such as queue starvation or cold-start trust. Import a working fix from a distant field. | Pulling models from packet routing, compilers, kitchens, or biology creates high natural spread. |
| **6. Testable bets** | Frame each of the **3 proposals** with a Popper flip-test bet, a code or schema sketch, a concrete cost floor, and an exact stop rule. | Replaces vague `Low / Medium / High` labels with testable claims and clear breaking points. |

---

## ⚡ Single-agent and parallel dispatch modes

Check the prompt to pick the right run mode:

1. **Single-agent mode (`DOP = 1`, default)**:
   - Use when the user invokes `brainstorm` or `/brainstorm` with no count or `N <= 1`.
   - Run the 6 algorithms directly in the current session to produce **3 distinct proposals**, then stop at `ask_question`.
2. **Parallel dispatch mode (`DOP = N`, where `N > 1`)**:
   - Use when the user gives a worker count, such as `brainstorm(10)`, `/brainstorm 10`, `/brainstorm(10)`, or *"brainstorm this across 10 agents"*.
   - The active agent acts strictly as a **non-blocking lead**. It spawns `N` concurrent `research` subagents with `Model: "inherit"`, stops calling tools right away to end its turn, and runs the **Reduce pass** once all `N` workers finish.

### 🔒 The same-prompt & clean-framing rules

In parallel mode, you test how the six steps and turn-1 probes lead equal agents to new ideas:

- **Same prompt for all `N` workers**: Every subagent gets the **exact same problem setup and the exact same `brainstorm` instructions**.
- **No per-worker personas or split lenses**: Never tell Worker 1 to focus on speed and Worker 2 to focus on cost. Never split fixed buckets across workers.
- **Strip accidents out of `Hard limits`**: Before framing the problem, split the **essence**—the core goal and boundary rules—from **accidents** like tool names, URLs, or raw topic lists. Put only true structural bounds such as latency caps, word counts, or format rules into `Hard limits`. Pass raw examples and topic lists as `Context seeds` to abstract from, never as a checklist that every bet must repeat.
- **Natural spread only**: Let turn-1 micro-probes, premise flips, cross-domain models, and token sampling drive the spread across workers.

```text
+-------------------------------------------------------------------------+
|                   PARALLEL BRAINSTORM TOPOLOGY (DOP = N)                |
|                                                                         |
|                             ROOT LEAD AGENT                             |
|                (Frames problem, dispatches N, yields turn)              |
|                     /             |             \                       |
|                    v              v              v                      |
|             +------------+ +------------+ +------------+                |
|             |  Worker 1  | |  Worker 2  | |  Worker N  |                |
|             | (Same inst)| | (Same inst)| | (Same inst)|                |
|             | -> 3 Bets  | | -> 3 Bets  | | -> 3 Bets  |                |
|             +------------+ +------------+ +------------+                |
|                    \              |              /                      |
|                     v             v             v                       |
|                        LEAD AGENT REDUCE PASS                           |
|         (Cluster 3N bets -> Gravity Well vs. Outliers -> User Gate)     |
+-------------------------------------------------------------------------+
```

### Worker prompt template

Call `invoke_subagent` with `TypeName: "research"` and `Model: "inherit"` to spawn `N` workers. Send this exact prompt to each worker:

```markdown
You are an independent brainstorm agent exploring high-signal options for the problem below.

### Problem setup and hard rules
- **Goal**: [1-sentence core goal abstracted from raw examples]
- **Hard limits**: [Strict structural bounds ONLY (e.g. latency, word count, format)—never a checklist of topics or examples]
- **Context seeds**: [Raw examples, topics, or prior art to abstract from—never recite as a checklist]
- **Non-goals**: [What stays out of scope]

### Mandatory 6-step ideation algorithm
Run all 6 steps in order before writing your final 3 proposals:
1. **Unscripted micro-probe**: If workspace files or search tools are available, run 1 to 2 fast read-only checks to inspect real bottlenecks, code, or prior art. Do not edit any files.
2. **Burn the default (Taboo box)**: List the 1 to 3 most obvious textbook answers in one sentence each and ban them. You may not propose them as your 3 bets.
3. **Assumption flip**: List 3 to 5 hidden premises in the problem or current design and state what happens when each premise is flipped or removed.
4. **Tension breaking**: State the core trade-off conflict ("Improving X hurts Y because of Z") and look for mechanisms that remove Z directly.
5. **Cross-domain transfer**: Strip domain nouns to name the abstract bottleneck, then map a working mechanism from an unrelated field (such as packet routing, compilers, kitchens, biology, or auctions).
6. **Commit to 3 testable bets**: Pick your 3 strongest, most distinct mechanisms. Synthesize the context seeds into one unified idea rather than stuffing every prompt noun into a checklist. Do not use vague "Low/Med/High" ratings. For each bet, provide:
   - **Title & spark** (which flipped premise or cross-domain model sparked it)
   - **The bet (Popper flip test)**: The non-obvious claim that makes this win, plus the sensible counter-view it rejects.
   - **Core mechanism & concrete sketch**: 2 to 3 sentences explaining how it works, plus a code snippet, schema, CLI call, or text diagram.
   - **Cost floor**: Concrete cost in lines of code, moving parts, latency, or user steps.
   - **Stop rule**: The exact condition, scale limit, or metric that proves this bet wrong.

Send your complete output back to the parent agent via `send_message` (include your Banned default box, Flipped premises, Core conflict, and 3 Testable bets).
```

---

## 🔄 Lead agent reduce pass

Once all `N` workers finish and wake the lead agent, don't dump `3 × N` raw ideas onto the user. Run this 4-step Reduce pass to extract signal:

1. **Cluster by causal mechanism**:
   Group all `3 × N` proposals by how they work under the hood. Ignore title changes, merge matching ideas into clusters, and count how many workers (`M` out of `N`) found each cluster on their own.
2. **Map the signal bands**:
   Sort the clusters into three bands:
   - **The gravity well (`>= 30%` of workers)**: Mechanisms reached by 30% or more of the workers on their own. This marks the safe default core—or shows where mode collapse still pulled agents together.
   - **The outlier frontier (1 to 2 workers)**: Unique mechanisms found by only one or two workers that escaped the gravity well. Treat these as top picks, because real breakthroughs often sit in the tails.
   - **Conflict forks**: Pairs of workers that reached clashing conclusions from the same prompt. These forks expose a hidden trade-off in the problem itself.
3. **Prune weak or invalid ideas**:
   Drop any proposal that breaks a hard limit, fails Popper's flip test, or loses to another cluster on every metric.
4. **Score spread and open selection gate**:
   Count the session stats: `N` workers, `3N` raw proposals, `K` unique mechanisms, and the spread ratio `K / 3N`. Present the grouped report and call `ask_question` so the user can pick a winner or merge a core idea with an outlier.

---

## 📋 Workflow checklists

### Single-agent checklist
- [ ] **Step 1: Frame hard rules, strip accidents, & run micro-probe**
  State the goal, structural hard limits, context seeds, and non-goals in 3 to 5 bullets. Keep raw examples and topic lists in `Context seeds` rather than `Hard limits` so they don't force checklist stuffing. Run 1 or 2 read-only checks to ground the problem in real facts.
- [ ] **Step 2: Burn the default & flip premises**
  Write the **Banned default box** with 1 to 3 textbook answers. List 3 to 5 hidden premises, flip them, state the core `X vs. Y` conflict, and pull 1 to 2 cross-domain models.
- [ ] **Step 3: Draft 3 testable bets**
  Write 3 distinct proposals. Each bet must include its **Popper flip-test claim**, **concrete sketch**, **cost floor**, and **stop rule**.
- [ ] **Step 4: Run quality gate**
  Check that none of the 3 bets repeat the banned default, stuff context seeds into a checklist, or share the same mechanism. Note how two bets might combine.
- [ ] **Step 5: User selection gate (`ask_question`)**
  Share the brainstorm report and call `ask_question` before touching any project source files.

### Parallel lead checklist
- [ ] **Step 1: Parse `N`, strip accidents, & frame shared problem setup**
  Read the worker count `N`, separate structural `Hard limits` from raw `Context seeds`, and write the shared problem setup. Never put a list of user topics or examples into `Hard limits`. If hard limits conflict, call `ask_question` before spawning workers.
- [ ] **Step 2: Dispatch `N` equal workers & yield turn**
  Spawn `N` concurrent `research` subagents with `Model: "inherit"` using the worker prompt template. Stop calling tools right away so the chat stays unblocked.
- [ ] **Step 3: Cluster & map signal bands (Reduce)**
  When all `N` workers finish, group the `3 × N` raw bets into `K` unique mechanism clusters. Split them into the **Gravity well**, **Outlier frontier**, and **Conflict forks**.
- [ ] **Step 4: Score spread & combine**
  Compute the spread scorecard (`K` unique mechanisms out of `3N` raw bets, banned-default overlap, and top cross-domain models).
- [ ] **Step 5: User selection gate (`ask_question`)**
  Share the reduced report and call `ask_question` so the user can pick a path or merge mechanisms.

---

## ✅ Quality gate

Before showing results to the user, check all five rules:

1. **Burned default enforced**: The report lists 1 to 3 obvious textbook answers in the Banned default box. None of the main proposals repeat them.
2. **Zero checklist stuffing**: Proposals abstract and unify `Context seeds` into a coherent mechanism or story rather than reciting every prompt noun as a list.
3. **Distinct causal mechanisms**: No two final proposals differ only by library name, tuning flag, or label.
4. **No vague labels**: Every proposal swaps `Low / Medium / High` ratings for a concrete sketch, a cost floor, a Popper flip test, and a clear stop rule.
5. **Zero early edits**: Project source files stay untouched until the user picks an option via `ask_question`.

---

## 📄 Output templates

### Single-agent output template

```markdown
## 1. Problem framing & symmetry breaking
- **Goal & hard limits**: <1-sentence goal + non-negotiable rules>
- **Banned default (Option 0)**: <The 1–3 obvious textbook answers taken off the table>
- **Core conflict**: Improving <X> hurts <Y> because of <Z>.
- **Flipped premises & cross-domain seeds**:
  1. *Premise*: <Assumption> -> *Flip*: <What if false?>
  2. *Cross-domain seed*: <Mechanism imported from an unrelated field>

## 2. Three testable bets

### Bet 1: <Title>
- **Sparked by**: <Flipped premise or cross-domain model>
- **The bet (Popper flip test)**: <Why this wins, and the sensible counter-view it rejects>
- **Core mechanism**: <2–3 sentences explaining how it works>
- **Concrete sketch**:
  ```<lang>
  <minimal code, schema, CLI call, or diagram>
  ```
- **Cost floor**: <Moving parts, lines of code, latency, or user steps>
- **Stop rule**: <Exact condition or scale limit where this bet fails>

## 3. Bet comparison & synthesis

| Bet | Core mechanism | Unique upside | Cost floor | Stop rule |
| :--- | :--- | :--- | :--- | :--- |
| **1. <Title>** | <Mechanism> | <What only this unlocks> | <Concrete cost> | <When it breaks> |
| **2. <Title>** | <Mechanism> | <What only this unlocks> | <Concrete cost> | <When it breaks> |
| **3. <Title>** | <Mechanism> | <What only this unlocks> | <Concrete cost> | <When it breaks> |

- **Recommended synthesis**: <How two bets combine, or which bet wins and why>
```

### Parallel Map-Reduce output template

```markdown
## 1. Parallel spread scorecard
- **Swarm size**: `<N>` equal workers (`<3 * N>` raw bets generated)
- **Distinct mechanisms found**: `<K>` unique clusters (Spread ratio: `<K / 3N>%`)
- **Banned defaults filtered**: <Top textbook clichés burned across workers>
- **Core conflict identified**: <Primary X vs. Y bottleneck>

## 2. The gravity well (Consensus core)
*Mechanisms found by several workers on their own—the high-confidence default.*

### Cluster 1: <Title> (`<M>/<N>` workers converged)
- **The bet**: <Shared thesis & Popper flip test>
- **Core mechanism & best sketch**:
  ```<lang>
  <cleanest code, schema, or diagram merged from the M workers>
  ```
- **Cost floor**: <Concrete cost>
- **Stop rule**: <Exact failure boundary>

## 3. The outlier frontier (High-alpha breakthroughs)
*Unique mechanisms found by only 1 or 2 workers that escaped mode collapse.*

### Outlier A: <Title> (`1/<N>` workers—sparked by <flip or cross-domain model>)
- **The bet**: <Non-obvious thesis>
- **Core mechanism & concrete sketch**:
  ```<lang>
  <minimal code, schema, or diagram>
  ```
- **Unique upside**: <What this unlocks that the consensus core misses>
- **Cost floor**: <Concrete cost>
- **Stop rule**: <Exact failure boundary>

## 4. Conflict forks (Where workers disagreed)
- **Fork 1 (<Axis>)**: Worker(s) `<#>` bet on `<Mechanism A>` because `<Premise 1>`, while Worker(s) `<#>` bet on `<Mechanism B>` because `<Premise 2>`.

## 5. Final portfolio matrix & synthesis

| Option | Signal band | Worker count | Unique upside | Cost floor | Stop rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **<Title>** | Gravity well | `<M>/<N>` | <Upside> | <Cost> | <Stop rule> |
| **<Title>** | Outlier | `1/<N>` | <Upside> | <Cost> | <Stop rule> |

- **Hybrid recommendation**: <How to pair the strongest consensus foundation with the highest-upside outlier mechanism>
```
