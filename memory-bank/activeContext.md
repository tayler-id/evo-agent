# Active Context: AI Research Agent (as of 2025-04-25 13:29)

## Current Focus

- **Adopt Letta Platform:** Transition the project architecture to utilize the Letta Stateful Agent Framework as the core infrastructure.
- **Implement Micro-Agents on Letta:** Begin implementing the defined micro-agents (Planner, Researcher, Memory, Critic, Executor) as Letta agents.
- **Leverage Letta Features:** Utilize Letta's capabilities for state management, persistent memory, context handling, tool execution, and multi-agent coordination.
- **Documentation Update:** Ensure all Memory Bank files accurately reflect the adoption of Letta and the revised technical approach.

## Recent Changes

- **Framework Evaluation:** Compared Letta Platform and Google ADK as potential frameworks for the multi-agent system.
- **Decision Made:** Selected Letta Platform as the core framework due to its strong focus on stateful agents, memory management, and integrated development environment.
- **Documentation Updated:** Updated `techContext.md` and `systemPatterns.md` to reflect the adoption of Letta.
- *Previous work on OpenAI function calling loop and SQLite knowledge graph provides valuable concepts but will be adapted or replaced by Letta's mechanisms.*

## Next Steps

- **Setup Letta Environment:** Install Letta (e.g., using Docker or Desktop) and the Python client (`letta-client`).
- **Scaffold Letta Agents:** Create the basic structure for the core micro-agents (Planner, Researcher, Memory, Critic, Executor) within the Letta framework.
- **Implement Core Memory Agent:** Focus on implementing the Memory agent using Letta's memory management features (archival, working memory).
- **Define Letta Tools:** Start defining essential capabilities (e.g., shell execution, web search) as Letta tools.
- **Basic Agent Interaction:** Implement a simple workflow involving 2-3 agents interacting via Letta (e.g., User -> Planner -> Executor).
- **Explore ADE:** Utilize the Letta Agent Development Environment for monitoring and debugging.
- **Update `progress.md`:** Reflect the shift to Letta implementation in the progress tracking document.

## Active Decisions & Considerations

- **Letta as Core Framework:** The project will be built on the Letta platform, leveraging its stateful agent capabilities.
- **Micro-Agent Mapping:** The previously defined micro-agent roles (Planner, Researcher, etc.) will be mapped to Letta agents.
- **Memory Management:** Rely primarily on Letta's built-in memory and context management features.
- **Tool Implementation:** Existing tool concepts will be implemented as Letta tools.

## Key Learnings/Insights

- Evaluating different agent frameworks (Letta, ADK) highlighted the importance of aligning framework strengths (statefulness vs. orchestration) with core project goals.
- Letta's focus on stateful agents and integrated memory management appears well-suited for the knowledge management aspects of this project.
- Adopting a comprehensive framework like Letta requires updating architectural plans and documentation thoroughly.
- *Previous learnings about function calling and tool schemas remain relevant for defining tools within Letta.*
