# Architecture

This system implements a **reliability gate** for LLM outputs.

Rather than trusting a single model response, it evaluates
output stability by measuring agreement across multiple
generations using UQLM.

## Flow

Prompt
 → N model generations
 → UQLM uncertainty scoring
 → Policy enforcement
 → Accept / Reject

## Design Principles

- Fail fast
- Explicit trust decisions
- Model-agnostic reliability layer
