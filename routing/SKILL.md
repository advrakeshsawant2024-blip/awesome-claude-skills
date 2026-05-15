---
name: routing
description: Routes each request to the smallest sufficient Claude model (Haiku → Sonnet → Opus) to minimise token costs, escalating only when the lighter model cannot meet quality or complexity requirements.
---

# Routing

Routing is a cost-optimisation strategy that sends every request to the cheapest model capable of handling it well. Instead of defaulting to the most powerful (and expensive) model for every request, start at the bottom of the model tier, check whether the result is good enough, and escalate only when necessary. Applied consistently, this can cut token spend by 60–90 % on workloads that mix simple and complex tasks.

## When to Use This Skill

- You handle a large volume of varied requests and want to reduce API costs
- Tasks arrive in mixed complexity — some are quick lookups, others need deep reasoning
- You want a consistent escalation policy rather than guessing which model to use each time
- You are running batch jobs, pipelines, or high-frequency automations

## Model Tiers

| Tier | Model | Best for |
|------|-------|----------|
| 1 — Fast | `claude-haiku-4-5-20251001` | Classification, extraction, short translation, yes/no questions |
| 2 — Balanced | `claude-sonnet-4-6` | Summarisation, drafting, moderate analysis, multi-step instructions |
| 3 — Powerful | `claude-opus-4-7` | Complex reasoning, long-document synthesis, nuanced judgment |

## What This Skill Does

1. **Classifies complexity upfront**: Reads the task and estimates whether it is simple, moderate, or complex before calling any model.
2. **Routes to the cheapest viable tier**: Sends the task to the lowest model that can plausibly handle it.
3. **Detects when to escalate**: Checks the response for signs of uncertainty, incompleteness, or failure.
4. **Carries context upward**: Passes the lower model's attempt along when escalating so the stronger model can build on it rather than start over.
5. **Reports what happened**: Logs which tier handled each task and the reason, so you can tune over time.

## Routing Logic

### Pre-route — pick the starting tier

**Start at Tier 1 (Haiku) when:**
- Task is a yes/no question, label, tag, short translation, or simple lookup
- Expected output is under ~200 words
- No reasoning chain required

**Start at Tier 2 (Sonnet) when:**
- Task requires coherent prose, a draft, a summary, or code
- Input is 500–8 000 tokens or output is expected to be 200–2 000 words
- Moderate step-by-step reasoning is needed

**Start at Tier 3 (Opus) when:**
- Task requires multi-step planning, deep expertise, or synthesis across a long document
- Input exceeds 8 000 tokens
- The task explicitly asks for comprehensive analysis

### Escalate when the response shows

- Phrases like "I'm not sure", "I don't have enough information", or "this may be incorrect"
- Output is truncated, logically inconsistent, or clearly incomplete
- A required format or field is missing
- You set a quality bar the response does not meet

### How to escalate

1. Move up exactly one tier
2. Prepend the previous attempt: *"A prior attempt produced the following — please improve it: [attempt]"*
3. Re-evaluate; stop at Tier 3

## How to Use

### Basic

```
Route this task to the cheapest model that can handle it, escalating if needed: [task]
```

### Batch

```
I have 50 support emails. Use routing: classify each one (start at Haiku), 
draft a reply (Sonnet if the issue is complex, Haiku if it is simple), 
escalate complaints or edge cases to Opus.
```

### With an explicit starting point

```
Start at Haiku for this extraction task; escalate to Sonnet only if the output is incomplete.
```

## Example

**User**: "Process these 5 tasks using routing"

```
1. What is the capital of France?
2. Summarise this 2-page brief and list three key risks.
3. Review this 30-page proposal and find all compliance gaps.
4. Translate "Good morning" into Japanese.
5. Write a project status update email based on these bullet points.
```

**Routing decisions**:

```
Task 1 → Haiku   (factual lookup)                         ✓ No escalation
Task 2 → Sonnet  (summarisation + extraction)             ✓ No escalation
Task 3 → Opus    (long-doc reasoning, compliance domain)  ✓ Direct route
Task 4 → Haiku   (short translation)                      ✓ No escalation
Task 5 → Sonnet  (structured prose generation)            ✓ No escalation
```

**Estimated saving vs. all-Opus**: ~80 %

## Tips

- Classification costs almost nothing — a few tokens upfront saves many on execution
- Always pass failed attempts upward; the stronger model recovers faster with context than from scratch
- Track your escalation rate per task type; a high rate means that category should start at a higher tier
- Use Anthropic's prompt caching on shared system prompts when processing batches to cut costs further

## Common Use Cases

- Support ticket triage and reply drafting
- Document summarisation pipelines
- Content moderation (clear-cut cases at Haiku, ambiguous at Sonnet, appeals at Opus)
- Research assistants that mix quick lookups with deep analysis
- Email drafting and classification workflows
