# Technical Context: AI Research Agent

## Core Technology

- **Language:** Python 3 (primary), with potential for polyglot micro-agents (Node.js, Go, etc.) as needed.
- **Micro-Agent Framework:** Letta Platform (Stateful Agent Framework) - provides the core infrastructure for building, deploying, and managing stateful, multi-agent systems.
- **Persistence & Memory:** Letta manages agent state persistence and provides sophisticated context/memory management capabilities. (Specific database backend like Postgres/pgvector might be used internally by Letta or allow integration, TBC).
- **Orchestration:** Letta platform handles agent orchestration, state management, inter-agent communication, and tool execution.
- **Web/Local Search:** Researcher agent uses browser automation (e.g., Puppeteer, Playwright) and custom scraping tools.
- **Reflection:** Critic agent implements Reflexion/self-talk loops for self-improvement.
- **Action Layer:** Executor agent interfaces with OS (shell), Git, calendar APIs, Slack, and Home-Assistant via adapters.
- **Voice-to-Text:** Integration with Whisper or MMS for mic-to-note capture.

## Dependencies

- **Core:** Python 3, Letta Platform (Server & Client SDK), OpenAI/Anthropic/HuggingFace SDKs (as needed for LLM providers), Puppeteer/Playwright (for browser tools), python-dotenv, shell/RPC adapters (as Letta tools).
- **Optional/Planned:** Redis (caching), Seaborn/Plotly (advanced visualization), Home-Assistant SDK, Slack API, calendar APIs.

## Development Environment

- Modular codebase structured around Letta agents and tools.
- Letta Agent Development Environment (ADE) for visual building, monitoring, and debugging.
- Letta Server instance (running via Docker, Desktop, or Cloud) manages agent execution and state.
- Environment variables for API keys and Letta server configuration, managed via `.env` and python-dotenv.
- Requirements tracked, including `letta-client`.
- Local/remote browser automation for web search and scraping (integrated as Letta tools).

## Technical Constraints (Current)

- **Distributed System:** Letta provides the framework for inter-agent communication and state management.
- **Persistence:** Letta handles agent state persistence.
- **Extensibility:** Each agent must expose a clear API/contract for easy swapping or extension.
- **Security:** Sensitive data (API keys, personal notes) must be protected in transit and at rest.
- **Performance:** Quick-Recall and context triggers must respond in <1s for good UX.

## Tool Usage Patterns

- Modular adapters for external integrations (browser, shell, calendar, Slack, etc.).
- Standard logging and monitoring per agent.
- Use of type hints and interface definitions for maintainability.
