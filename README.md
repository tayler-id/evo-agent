# Evo Agent (AI Research Agent)

## Mission Statement

Continuously capture everything I read, ask, build or say; surface the right snippet, contact, code-pattern or next action at the exact moment I need it.

## Overview

Evo Agent is a modular, generative-AI powered knowledge management agent designed to close the “dark-data” gap by turning unused personal data into actionable knowledge, maximizing decision quality and productivity. It leverages the [Letta Stateful Agent Framework](https://docs.letta.com/) to manage stateful, multi-agent interactions.

## Core Features (v0.1 Roadmap)

-   **Daily Digest:** Auto-summarize top 5 UX/AI/gardening papers; pull household calendar & weather conflicts.
-   **Quick-Recall:** `/recall <topic>` returns the three most relevant past notes or code gists in <1s.
-   **Do-Next Radar:** Watches active Git branches, garden hardening schedule, and onboarding mocks; pings when idle >20 min with next highest-value task.
-   **Voice Drop:** Short mic-to-note capture using Whisper or MMS; auto-tagged into KM store.

## Architecture

The system employs a modular, multi-agent architecture built on the Letta platform:

-   **Planner:** Orchestrates tasks and goals.
-   **Researcher:** Handles web/local search and information synthesis.
-   **Memory:** Manages persistent knowledge, context, and recall using Letta's memory features.
-   **Critic:** Implements self-reflection loops (e.g., Reflexion) for improvement.
-   **Executor:** Interacts with external tools and systems (shell, APIs, etc.) via Letta tools.

## Technology Stack

-   **Core Framework:** [Letta Platform](https://docs.letta.com/)
-   **Primary Language:** Python 3
-   **Key Libraries:** `letta-client`, `openai`, `python-dotenv`

## Setup

1.  **Install Letta:** Set up the Letta server environment using either [Letta Desktop](https://docs.letta.com/quickstart/desktop) or [Docker](https://docs.letta.com/quickstart/docker). Ensure the server is running (typically accessible at `http://localhost:8283`).
2.  **Clone Repository:**
    ```bash
    git clone https://github.com/tayler-id/evo-agent.git
    cd evo-agent
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r ai_research_agent/requirements.txt
    ```
4.  **Environment Variables:** Create a `.env` file inside the `ai_research_agent` directory and add necessary API keys (e.g., `OPENAI_API_KEY`). See `.gitignore` for structure.

## Usage

The primary interface is currently through the command line:

```bash
python ai_research_agent/cli.py "Your natural language request here"
```

(Note: Specific CLI usage details may evolve as development progresses.)
