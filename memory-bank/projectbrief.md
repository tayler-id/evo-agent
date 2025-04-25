# Project Brief: AI Research Agent

## Mission Statement

Continuously capture everything I read, ask, build or say; surface the right snippet, contact, code-pattern or next action at the exact moment I need it.

## Core Goal

To build a modular, generative-AI powered knowledge management agent that closes the “dark-data” gap by turning unused personal data into actionable knowledge, maximizing decision quality and productivity.

## High-Level Modular Architecture

The system is composed of specialized micro-agents, each responsible for a core function:

| Layer           | Micro-agent   | Core Duty                                                      | Tooling Suggestion                |
|-----------------|--------------|----------------------------------------------------------------|-----------------------------------|
| Orchestration   | Planner      | Converts goals ↔ executable tasks; prioritizes                 | Google ADK proxy (Option 3)       |
| Thinking        | Researcher   | Web/local search → multi-source digest                         | Browser + custom ScrapeTool       |
| Memory          | Vector-DB    | Embeds & recalls notes, PDFs, code                             | pgvector on Postgres              |
| Reflection      | Critic       | Runs “Reflexion” self-talk after failures to improve next run  | Reflexion loop implementation     |
| Action          | Executor     | Triggers OS scripts, Git, calendar, Slack, Home-Assistant      | Shell / RPC adapters              |

Self-reflection loops (e.g., Reflexion) are used to improve coding-task success rates.

## Minimal Feature Set (v0.1)

- **Daily Digest:** Auto-summarize top 5 UX/AI/gardening papers; pull household calendar & weather conflicts.
- **Quick-Recall:** `/recall <topic>` returns the three most relevant past notes or code gists in <1s.
- **“Do-Next” Radar:** Watches active Git branches, garden hardening schedule, and onboarding mocks; pings when idle >20 min with next highest-value task.
- **Voice Drop:** Short mic-to-note capture using Whisper or MMS; auto-tagged into KM store.

## Key Requirements

- Modular, micro-agent architecture for extensibility and maintainability.
- Robust, AI-powered knowledge capture and retrieval.
- Seamless integration with external tools and data sources.
- Actionable, context-aware recommendations and reminders.

## Evolution Note

This marks a shift from a single-class agent to a multi-agent, modular system, with a broader mission and feature set focused on holistic knowledge management and productivity.
