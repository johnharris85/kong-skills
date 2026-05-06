---
name: konnect-ai-gateway
description: Operate and troubleshoot Konnect AI Gateway for LLM traffic. Use for provider routing, AI Proxy setup, guardrails, prompt controls, LLM analytics, token or latency issues, or AI Gateway requests that work technically but fail governance or policy intent.
license: MIT
metadata:
  product: konnect
  category: ai-gateway
  tags:
    - kong
    - konnect
    - ai-gateway
    - llm
    - ai
---

# Konnect AI Gateway workflow

## Goal

Help an operator reason about Konnect AI Gateway as a governed LLM traffic
surface: provider routing, AI plugins, prompt controls, access, and LLM-aware
observability.

Use this skill for AI Gateway operator workflows, not for generic OpenAI or
prompt-engineering advice.

## Tool Selection

- Use the shared `kong-konnect` MCP server first for live inspection of control
  planes, Gateway entities, and LLM analytics surfaces.
- Prefer LLM-specific analytics when the user is asking about token usage,
  latency, or AI request health. `query_llm_analytics` is the right aggregated
  MCP surface when AI/LLM usage data is the real question.
- Preserve the repository's chosen declarative toolchain for implementation:
  `deck-gateway` for Gateway-entity GitOps, `terraform-konnect` for HCL-managed
  Konnect AI Gateway resources, `terraform-kong-gateway` for self-managed HCL,
  and `kongctl-declarative` only when the surrounding Konnect repo already uses
  that path.
- If live Konnect state matters and `kong-konnect` MCP is not connected, say so
  early and continue with repo config or user-provided artifacts.

## Workflow

### 1. Identify the failing AI Gateway layer

Clarify whether the issue is:

- provider routing or model targeting
- service / route setup for AI traffic
- AI Proxy or AI Proxy Advanced behavior
- prompt or response guardrails
- prompt decoration or template behavior
- semantic cache behavior
- LLM usage, latency, or token visibility

Do not flatten all AI Gateway issues into “the plugin is broken.”

### 2. Separate baseline proxying from AI governance

First prove:

- the AI request reaches the expected service and route
- the AI proxy layer is attached where the operator expects
- provider authentication expectations are clear

Only then reason about higher-level AI policies such as prompt guards or
templates.

### 3. Interpret the plugin stack in order

For governed LLM traffic, inspect the stack in this order:

- base AI proxying
- routing and model/provider selection
- authentication and access controls
- prompt decoration or template injection
- prompt / response guardrails
- semantic caching or other acceleration layers

This prevents chasing a guardrail symptom when the route or provider layer is
wrong.

### 4. Use LLM analytics for AI-specific runtime questions

If the question is about usage, tokens, latency, or cost-like behavior, prefer
the LLM analytics surface over generic API analytics.

Use AI-specific observability to answer:

- whether requests are reaching the AI Gateway
- whether token usage aligns with expectations
- whether latency or error rates are concentrated by route, provider, or model

### 5. Distinguish product governance from provider behavior

When a request reaches the provider but still behaves incorrectly, separate:

- Kong-side routing and policy intent
- provider-side model behavior
- prompt construction effects
- authorization or key-management assumptions

Do not promise that every bad model response is a Gateway bug.

### 6. Return the narrowest AI failure domain

Classify the issue as:

- route or service setup problem
- AI proxy / provider configuration problem
- auth or secret-management problem
- prompt decoration / template problem
- guardrail policy problem
- semantic cache or acceleration problem
- analytics / visibility problem rather than traffic failure

## Konnect-Specific Gotchas

- AI Gateway is still a Gateway surface first: route, service, and plugin
  placement still matter.
- Prompt and response guardrails extend a working AI proxy path; they do not
  replace it.
- LLM analytics should be treated as a distinct runtime surface from generic API
  analytics.
- A technically successful provider response can still violate policy intent.
- Quickstarts are useful for proving baseline capability, but they are not a
  substitute for a durable AI Gateway operating model.

## Validation Checklist

Before answering, verify that you can state:

- which AI Gateway layer is failing
- whether baseline proxying works before higher-level AI controls
- whether the issue is routing, auth, guardrails, prompt shaping, caching, or
  analytics
- whether LLM analytics or another observability surface is the right next
  step
- which declarative tool skill should own the resulting change

## Handoffs

- Use `konnect-observability-triage` when the main issue is dataset visibility
  rather than AI Gateway behavior itself.
- Use `konnect-gateway-triage` when the real blocker is generic Gateway
  connectivity or config rollout rather than an AI-specific layer.
- Use `deck-gateway`, `terraform-konnect`, `terraform-kong-gateway`, or
  `kongctl-declarative` when the operator wants to encode or apply the AI
  Gateway change as config.
