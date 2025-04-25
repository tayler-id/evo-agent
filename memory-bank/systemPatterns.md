# System Patterns: AI Research Agent

## Core Architecture (as of 2025-04-25 13:28)

The system is designed as a modular, multi-agent platform built upon the **Letta Stateful Agent Framework**. Each micro-agent is responsible for a distinct layer of the knowledge management workflow, leveraging Letta's capabilities for state management, memory, and tool execution. This enables extensibility, separation of concerns, and robust orchestration.

### Micro-Agent Layers

| Layer           | Micro-agent   | Core Duty                                                      | Tooling Suggestion (Letta-based)  |
|-----------------|--------------|----------------------------------------------------------------|-----------------------------------|
| Orchestration   | Planner      | Converts goals ↔ executable tasks; prioritizes                 | Letta Agent Coordination/Tools    |
| Thinking        | Researcher   | Web/local search → multi-source digest                         | Letta Tools (Browser, Custom)     |
| Memory          | Memory       | Embeds & recalls notes, PDFs, code; manages context            | Letta Memory Management           |
| Reflection      | Critic       | Runs “Reflexion” self-talk after failures to improve next run  | Custom Agent Logic within Letta   |
| Action          | Executor     | Triggers OS scripts, Git, calendar, Slack, Home-Assistant      | Letta Tools (Shell, Custom APIs)  |

### Key Design Patterns/Decisions

- **Letta Stateful Agent Framework:** Utilizes Letta for core agent management, state persistence, memory, and tool execution.
- **Micro-Agent Pattern:** Each agent (Planner, Researcher, etc.) is implemented as a Letta agent with a specific role and tools.
- **Orchestration Layer:** Handled by Letta's agent communication and tool-calling mechanisms, potentially guided by a dedicated Planner agent.
- **Reflection Loop:** The Critic agent logic is implemented within a Letta agent to analyze failures and potentially modify other agents' memory or prompts.
- **Letta Memory Management:** Leverages Letta's built-in capabilities for managing agent memory (working, archival) and context windows.
- **Letta Tooling System:** Agents are equipped with capabilities via Letta's tool definition and execution system (custom functions, pre-built tools).
- **Event-Driven/Reactive:** Agents can trigger actions or recommendations based on context changes (e.g., user idle, new calendar event).

### Component Relationships

```mermaid
flowchart TD
    U[User]
    U -- "Reads/Asks/Builds/Speaks" --> A[Action Capture]
    A -- "Capture/Embed" --> M[Memory (Vector-DB)]
    U -- "Requests /recall <topic>" --> Q[Quick-Recall]
    Q -- "Query" --> M
    M -- "Relevant Snippets" --> Q
    Q -- "Surface to User" --> U
    S[Scheduler/Context Watcher] -- "Idle/Context Change" --> P[Planner]
    P -- "Goal/Task" --> R[Researcher]
    R -- "Web/Local Search" --> D[Digest]
    D -- "Summarize" --> P
    P -- "Next Action" --> E[Executor]
    E -- "Trigger OS/External" --> X[External Tools]
    F[Critic] -- "Failure/Reflection" --> P
    V[Voice Drop] -- "Mic-to-Note" --> M
    D -- "Daily Digest" --> U
```

*(Diagram: User actions are captured and processed by Letta agents, updating Letta's managed memory. Quick-Recall queries Letta Memory. Context Watcher triggers Planner agent within Letta. Planner orchestrates other Letta agents (Researcher, Executor, Critic) via messages and tool calls. Voice Drop feeds Letta Memory. Digest agent provides daily summaries.)*

### Evolution Note

This architecture adopts the Letta framework to implement the distributed, micro-agent system, focusing on stateful interactions and leveraging Letta's built-in capabilities for memory and orchestration.
