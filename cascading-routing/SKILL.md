---
name: cascading-routing
description: Routes each task to the smallest sufficient Claude model (Haiku → Sonnet → Opus) to minimise token costs, escalating only when the lighter model cannot meet quality or complexity requirements.
---

# Cascading Routing

Cascading routing is a cost-optimisation strategy that dispatches every task to the cheapest model capable of handling it well. Instead of defaulting to the most powerful (and expensive) model for every request, the agent starts at the bottom of the model tier, evaluates whether the result is sufficient, and escalates only when it must. Applied consistently, this can cut token spend by 60–90 % on workloads that mix simple and complex tasks.

## When to Use This Skill

- You are building a pipeline or agent that handles a large volume of varied requests
- You want to reduce API costs without manually classifying every task up front
- You are processing mixed-complexity work: simple lookups, moderate summarisation, and hard multi-step reasoning all arrive in the same queue
- You are optimising a Claude Code workflow, a batch job, or a production API integration
- You want a principled escalation policy rather than ad hoc model selection

## Model Tiers

| Tier | Model | Best for |
|------|-------|----------|
| 1 — Fast | `claude-haiku-4-5-20251001` | Classification, extraction, lookup, short generation, translation |
| 2 — Balanced | `claude-sonnet-4-6` | Summarisation, code generation, moderate reasoning, multi-step instructions |
| 3 — Powerful | `claude-opus-4-7` | Complex reasoning, nuanced judgment, novel problem-solving, long-context synthesis |

## What This Skill Does

1. **Classifies task complexity**: Estimates upfront whether a task is simple, moderate, or complex based on signal words, length, and structure.
2. **Routes to the cheapest viable model**: Sends the task to the lowest tier that can plausibly handle it.
3. **Detects escalation signals**: Checks the response for confidence markers, hedging, incomplete reasoning, or explicit failure — and escalates if found.
4. **Carries context across tiers**: Passes the lower model's attempt as context when escalating, so the stronger model doesn't repeat work.
5. **Reports routing decisions**: Logs which tier handled each task and why, so you can tune thresholds over time.

## How to Use

### Basic Usage

```
Use cascading routing to answer this batch of questions as cheaply as possible: [paste tasks]
```

```
Route this task using the cheapest model that can handle it, escalating if needed
```

### With Explicit Tier Hints

```
Start at Haiku for this extraction task, escalate to Sonnet only if the output is incomplete
```

```
Use Opus for this task — it requires deep multi-step reasoning across a 50-page document
```

### For Batch Processing

```
I have 200 support tickets. Use cascading routing: classify each ticket (Haiku), 
draft a reply (Sonnet if complex, Haiku if simple), escalate edge cases to Opus.
```

## Routing Logic

### Step 1 — Pre-route classification

Assess the incoming task against these signals before calling any model:

**Route to Tier 1 (Haiku) if:**
- Task is a yes/no question, keyword extraction, entity tagging, or short translation
- Input is under ~500 tokens and output is expected under ~200 tokens
- No reasoning chain required; a single factual retrieval suffices

**Route to Tier 2 (Sonnet) if:**
- Task requires generating coherent prose, code, or structured output
- Input is 500–8 000 tokens or output is expected to be 200–2 000 tokens
- Moderate reasoning needed (e.g. summarise, compare, debug a function)

**Route to Tier 3 (Opus) if:**
- Task requires multi-step planning, deep domain expertise, or creative synthesis
- Input exceeds 8 000 tokens or the task explicitly asks for comprehensive analysis
- Previous tier explicitly failed or hedged heavily

### Step 2 — Execute and evaluate

After receiving a response from the routed tier, check for escalation signals:

- Response contains phrases like "I'm not sure", "I don't have enough information", "this may be incorrect"
- Response is truncated, logically inconsistent, or obviously incomplete
- Response fails a validation rule you specified (e.g. wrong format, missing required fields)
- You explicitly set a quality threshold the response does not meet

### Step 3 — Escalate if needed

If an escalation signal is detected:
1. Move up exactly one tier
2. Prepend the lower model's attempt to the new prompt as context: `"A prior attempt produced the following — please improve it: [attempt]"`
3. Re-evaluate the new response against the same criteria
4. Stop at Tier 3 (Opus); do not escalate further

### Step 4 — Return and log

Return the final response together with a routing summary:

```
[Tier used: Haiku | Escalated: No | Reason: Simple extraction task]
```

## Example

**User**: "Process these 5 tasks using cascading routing"

```
1. What is the capital of France?
2. Summarise this 2-page product brief and extract three key risks.
3. Review this 30-page architecture proposal and identify all security vulnerabilities.
4. Translate "Hello, world" into Spanish.
5. Write a Python function that parses ISO 8601 timestamps.
```

**Routing decisions**:

```
Task 1 → Haiku   (factual lookup, <10 tokens output)        ✓ No escalation
Task 2 → Sonnet  (summarisation + extraction, ~500 tokens)  ✓ No escalation
Task 3 → Opus    (long-doc reasoning, security expertise)   ✓ Direct route
Task 4 → Haiku   (short translation)                        ✓ No escalation
Task 5 → Sonnet  (code generation, moderate complexity)     ✓ No escalation
```

**Estimated cost vs. all-Opus baseline**: ~78 % reduction

## Tips

- Pre-route classification is free — invest a few tokens in classification to save many on execution
- Pass the lower model's failed attempt upward rather than discarding it; it gives the stronger model a head start
- Set explicit output-length limits when calling Haiku to avoid runaway responses that trigger false escalations
- Track your escalation rate per task type; a high rate on a category means that category should be pre-routed to Sonnet
- Use prompt caching (Anthropic's cache_control feature) on shared system prompts when running batches to cut costs further
- For latency-sensitive pipelines, run Haiku and Sonnet in parallel and discard the weaker result — saves escalation round-trip time when you can afford the extra Sonnet call

## Common Use Cases

- Customer support triage: Haiku labels tickets, Sonnet drafts replies, Opus handles escalations
- Document processing pipelines: Haiku extracts metadata, Sonnet summarises, Opus audits edge cases
- Code review at scale: Haiku flags style issues, Sonnet explains logic bugs, Opus redesigns architecture
- RAG systems: Haiku retrieves and ranks chunks, Sonnet synthesises answers, Opus reasons over conflicting sources
- Content moderation: Haiku handles clear-cut cases, Sonnet handles ambiguous ones, Opus reviews appeals
