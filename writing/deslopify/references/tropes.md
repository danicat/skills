# AI writing tropes to avoid

Use this reference to spot and remove common Large Language Model (LLM) writing habits while preserving the author's natural voice. Adapted for technical writing from [tropes.fyi](https://tropes.fyi) by [ossama.is](https://ossama.is) and expanded with modern reasoning-model tells and punctuation rules.

---

## 1. Word choice

### "Quietly" and magic adverbs

LLMs overuse *quietly* and similar adverbs (*deeply*, *fundamentally*, *remarkably*, *arguably*, *seamlessly*) to make routine behavior sound profound. Cut the adverb or state the measured effect.

**Avoid patterns like:**
- "quietly orchestrating workflows, decisions, and interactions"
- "fundamentally reshaping how teams ship software"
- "a quiet intelligence behind every request"

### "Delve" and inflated verbs

Overused verbs and filler openers signal unedited model output: *delve*, *utilize*, *leverage* (as a verb), *streamline*, *harness*, *foster*, *spearhead*, and *certainly*. Prefer *inspect*, *use*, *simplify*, or *build*.

**Avoid patterns like:**
- "Let's delve into the implementation details."
- "Delving deeper into the architecture..."
- "We need to leverage these robust frameworks to streamline deployment."

### "Tapestry" and grandiose nouns

Models substitute ornate abstractions for plain nouns: *tapestry* for anything connected, *landscape* or *realm* for any technical field, and *paradigm*, *synergy*, *beacon*, or *testament* for ordinary systems.

**Avoid patterns like:**
- "The rich tapestry of distributed systems..."
- "Navigating the complex landscape of modern cloud infrastructure..."
- "The ever-evolving ecosystem of developer tooling..."

### Copula dodges ("serves as")

Repetition penalties push models to avoid plain *is* and *are* in favor of *serves as*, *stands as*, *marks*, *represents*, or *boasts*. Use simple copulas or concrete technical verbs.

**Avoid patterns like:**
- "The gateway serves as the entry point for client traffic." (Write: *"The gateway routes client traffic."*)
- "This release marks a pivotal moment in the project's evolution."
- "The test suite stands as a testament to modular design."

---

## 2. Sentence structure

### Negative parallelism

Framing routine claims as theatrical contrasts (*"It's not X, it's Y"*, *"Not because X, but because Y"*, or *"The question isn't X. The question is Y."*) manufactures false profundity. State what the system does directly.

**Avoid patterns like:**
- "It's not a cache, it's a state engine."
- "Half the bugs you chase aren't in your code. They're in your mental model."
- "The question isn't whether agents can write code. The question is how we verify it."

### Dramatic countdowns ("Not X. Not Y. Just Z.")

Negating two or three candidates before naming the real subject builds artificial suspense. Name the subject in one direct clause.

**Avoid patterns like:**
- "Not a bug. Not a feature. A design flaw."
- "Not ten. Not fifty. Five hundred lint violations across `67` files."
- "Not recklessly, not completely, just enough to break consensus."

### Self-answering questions ("The X? A Y.")

Asking a short rhetorical question nobody asked and answering it in the next fragment (*"The result? Devastating."*) mimics ad copy rather than engineering prose.

**Avoid patterns like:**
- "The result? Instantaneous failovers."
- "The worst part? Nobody paged on-call."
- "The catch? Memory usage tripled under load."

### Anaphora abuse

Repeating the exact same clause opener across three or more consecutive sentences creates a speechwriter cadence out of place in technical docs.

**Avoid patterns like:**
- "They assume users will pay. They assume developers will migrate. They assume ecosystems will form."
- "It can parse schemas. It can validate payloads. It can generate mocks. It can export traces."

### Tricolon abuse

Grouping every noun phrase, adjective list, or contrast into neat triplets (*A, B, and C*). One rule-of-three phrase reads cleanly; back-to-back triplets expose template generation.

**Avoid patterns like:**
- "Products impress users; platforms empower builders. Products solve tasks; platforms create markets."
- "workflows, decisions, and interactions across teams, tools, and pipelines"

### Filler transitions ("It's worth noting")

Empty sentence starters introduce a claim without connecting it logically to the prior sentence: *It's worth noting*, *It bears mentioning*, *Importantly*, *Interestingly*, *Notably*. Delete the starter.

**Avoid patterns like:**
- "It's worth noting that this index increases write amplification."
- "Importantly, callers must close the response body."
- "Interestingly, the same bottleneck appears on ARM64."

### Superficial participle tails

Appending a trailing `-ing` clause (*highlighting its importance*, *underscoring our commitment*, *reflecting broader trends*) tacks hollow commentary onto concrete facts.

**Avoid patterns like:**
- "We migrated to gRPC, underscoring our commitment to low-latency services."
- "The scheduler pins worker threads, reflecting modern systems best practices."

### False ranges ("From X to Y")

Using *from X to Y* when X and Y do not sit on an ordered scale (*"from developer productivity to cultural transformation"*). Reserve *from X to Y* for real ranges (`from 10ms to 250ms`, `from parser to linker`); otherwise list items plainly.

**Avoid patterns like:**
- "From rapid prototyping to enterprise governance and cultural transformation."
- "From fixing race conditions to rethinking team topology."

### Gerund fragment litanies

Following a complete sentence with a string of subjectless `-ing` fragments adds word count without new information.

**Avoid patterns like:**
- "Fixing small bugs. Writing straightforward handlers. Closing well-scoped tickets."
- "Shipping faster. Scaling cleaner. Sleeping better."

### Reasoning-trace throat-clearing

Modern thinking models leak internal deliberation phrases into final prose: *Let's carefully consider*, *To answer this thoroughly*, *Upon closer inspection*, *At its core*, *When it comes to*. Strip the deliberation wrapper and start with the conclusion.

**Avoid patterns like:**
- "When it comes to state synchronization, at its core we must carefully consider network partitions."
- "Upon closer inspection, it becomes clear that the mutex is held across I/O."

### Symmetric fence-sitting

Models avoid taking a stand by ending technical comparisons with balanced boilerplate (*"While both X and Y have strengths, the best choice depends on your specific use case and requirements."*). State the concrete workload threshold, team constraint, or latency budget that tips the decision.

**Avoid patterns like:**
- "Ultimately, both REST and gRPC have their place, and the right choice depends on your specific architecture."
- "Each trade-off carries pros and cons depending on your organizational priorities."

---

## 3. Paragraph structure

### Staccato fragment paragraphs

Breaking ordinary explanations into single-sentence or two-word paragraphs manufactures LinkedIn-style melodrama instead of coherent engineering reasoning.

**Avoid patterns like:**
- "He deployed on Friday. Without flags. To production. On bare metal."
- "Monoliths scale. Until they don't."

### Disguised listicles

Wrapping an unnumbered list into repetitive paragraphs opening with *"The first challenge is... The second challenge is... The third challenge is..."*. Either use a real numbered list or write genuine transitions explaining how one constraint causes the next.

**Avoid patterns like:**
- "The first bottleneck is connection setup. The second bottleneck is TLS handshakes. The third bottleneck is header parsing."

---

## 4. Tone

### False suspense ("Here's the kicker")

Promising a dramatic twist before delivering a routine technical point: *Here's the kicker*, *Here's the thing*, *Here's where it gets interesting*, *Here's what most engineers miss*, *Here's the deal*.

**Avoid patterns like:**
- "Here's where it gets interesting: the buffer never shrinks."
- "Here's what most people miss about SQLite WAL mode."

### Patronizing analogies ("Think of it as")

Defaulting to elementary metaphors (*"Think of a mutex like a bathroom key"*, *"a Swiss Army knife for telemetry"*) when addressing developers who already understand the underlying mechanism.

**Avoid patterns like:**
- "Think of Kubernetes as an air-traffic controller for your containers."
- "Think of it as a highway lane system for async tasks."

### Futurist invitations ("Imagine a world")

Opening arguments with utopian sales pitches (*"Imagine a world where every deploy verifies itself..."*) instead of describing what the software actually does today.

**Avoid patterns like:**
- "Imagine a world where your editor, issue tracker, and CI pipeline share one memory."
- "In that world, incidents stop being firefights and start becoming learning loops."

### Performative vulnerability

Polished, risk-free fourth-wall breaks that simulate candor without admitting a real mistake or cost.

**Avoid patterns like:**
- "This isn't a rant; it's a diagnosis."
- "And yes, since we're being honest, every cloud vendor is guilty of this."

### Unproven certainty ("The truth is simple")

Declaring a claim *simple*, *obvious*, or *unambiguous* instead of proving it with evidence, or dismissing prior factors with *"None of those is the real story. The real story is..."*.

**Avoid patterns like:**
- "The reality is simpler and less flattering."
- "History is unambiguous on this architectural pattern."
- "Latency isn't the real story. The real story is control-plane lock-in."

### Grandiose stakes inflation

Treating routine library releases, config changes, or benchmarks as turning points in computing history.

**Avoid patterns like:**
- "This release redefines the next era of backend engineering."
- "A shift that changes everything about how humans write software."

### Pedagogical hand-holding ("Let's break this down")

Assuming a teacher-to-student posture with expert peers: *Let's break this down*, *Let's unpack this*, *Let's dive in*, *Let's explore*.

**Avoid patterns like:**
- "Let's unpack what happens under the hood step by step."
- "Before we dive in, let's explore why caching is hard."

### Vague attributions

Citing unnamed authorities (*"experts argue"*, *"industry reports suggest"*, *"many engineers believe"*) instead of linking a specific benchmark, RFC, paper, or post-mortem. If you cannot name the source, state the mechanism directly.

**Avoid patterns like:**
- "Industry observers have noted growing fatigue with microservice sprawl."
- "Experts agree that memory safety is a top priority."

### Invented concept labels

Coining grandiose compound labels by pairing a domain word with an abstract crisis noun (*the supervision paradox*, *the velocity trap*, *context creep*, *the abstraction tax*) and treating the coined phrase as established theory.

**Avoid patterns like:**
- "Teams fall victim to the orchestration paradox."
- "This creates an observability vacuum across services."

### Colon-pivot headline formulas

Generating synthetic two-part titles shaped like *"Beyond X: How Y Redefines Z"*, *"The Hidden Cost of X: Why Y Matters"*, or *"From Hype to Production: Building X"*. Write direct titles naming the concrete tool, bug, or result (*"Cutting PostgreSQL p99 latency with partial GIN indexes"*).

**Avoid patterns like:**
- "Beyond Caching: How In-Memory Projections Redefine Read Scalability"
- "From Toy Demos to Production: Mastering Agent Workflows"

---

## 5. Formatting

### Em dashes and spaced double hyphens

LLMs lean heavily on em dashes (`U+2014`), en dashes (`U+2013`), and spaced double hyphens as all-purpose clause connectors, dramatic pauses, and parenthetical pivots. Ban mid-sentence em dashes, en dashes, and spaced double hyphens completely. Split thoughts into crisp sentences with periods, or connect them cleanly with commas, colons, or parentheses.

**Rewrite interrupted clauses cleanly:**
- Instead of joining a dramatic aside with mid-sentence dashes, write: *"The failure was systemic, even though nobody discussed it in post-mortems."*
- Instead of pivoting with a dash between two clauses, use a period or colon: *"The retry loop did not time out. It exhausted every file descriptor on the host."*

### Mechanical bold-first bullet walls

Formatting every bullet across an entire article with `**Bold Title**: Sentence...` creates a textbook wall that signals raw LLM output when overused in **narrative essays, blog posts, and social posts**. Match formatting to the document type:
- **Narrative prose (essays, blog posts, stories, social posts)**: Prefer connected paragraphs or plain bullets without bolded prefixes.
- **Reference documentation (`README.md`, CLI flags, API specs, changelogs)**: Concise bold-lead definitions and Markdown tables help engineers scan keys fast and remain appropriate.

### Decorative Unicode glyphs and curly quotes

Inserting Unicode arrows (`→`, `⇒`) as lazy mid-sentence causal connectors or mixing typographic curly quotes (`“ ”`, `‘ ’`) into plain Markdown source files signals copy-pasted chat output. Use plain ASCII `->` or `=>` only where shorthand fits (or write active verbs in prose), and keep straight ASCII quotes (`"`, `'`) in Markdown and code.

**Avoid patterns like:**
- "More retries → higher queue depth → cascading timeouts in prose paragraphs"
- "Mixing “curly quotes” into plain Markdown files"

---

## 6. Composition

### Fractal summaries

Summarizing what a section will say, saying it, and then summarizing what the section just said at every heading level. Let each section start with substance and stop when its point is complete.

**Avoid patterns like:**
- "In this section, we'll examine... As we've seen in this section, the worker pool..."
- "And that brings us full circle to where we started."

### Dead metaphors

Introducing a metaphor (*walls and doors*, *plumbing*, *primitives*, *guardrails*) and repeating it ten times across one article. Use a metaphor once if it clarifies a mechanism, then return to literal terms.

### Historical analogy stacking

Stacking rapid-fire tech-history parallels (*"Apple didn't build Uber. Facebook didn't build Spotify. AWS didn't build Airbnb."*) to claim inevitability by association instead of proving the technical point on its own merits.

### One-point dilution

Stretching an `800`-word engineering insight into `3,500` words by restating the same thesis through five metaphors and redundant examples. Cut every paragraph that does not add a new mechanism, measurement, or trade-off.

### Content duplication

Repeating the same constraint or explanation almost verbatim in two different sections of a long document. Consolidate each fact in one canonical section.

### Signposted conclusions

Announcing the ending with *"In conclusion"*, *"To sum up"*, *"Wrapping up"*, or *"In summary"*. End directly with concrete trade-offs, runnable next steps, or open engineering questions.

### Formulaic concession beats ("Despite its challenges")

Closing sections with the rigid template *"Despite these challenges, X remains a promising cornerstone for..."*. State the actual unresolved limits plainly and stop.

---

## Editorial rule of thumb

A single word or structure in isolation rarely ruins a draft; clusters of these patterns flatten technical writing into generic filler. Cut synthetic scaffolding, keep the author's genuine voice and quirks intact, and anchor every claim in concrete mechanisms or measurements.
