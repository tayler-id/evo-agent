# AI Research Agent Modular Architecture

## Overview

The agent is now a natural language, autonomous assistant operating in a Manus/Cline-compliant agent loop. It uses OpenAI function calling (gpt-3.5-turbo-1106) with JSONSchema tool definitions to select and execute the right tool for any user request, including shell, python, research, file, browser, and user messaging actions. The agent supports a persistent system prompt, knowledge graph, and multi-turn, context-aware workflows.

## Directory Structure

```
ai_research_agent/
  agents/
    planner/
      .clinerules
    researcher/
      .clinerules
    memory/
      .clinerules
    critic/
      .clinerules
    executor/
      .clinerules
    __init__.py
    types.py
    memory/knowledge_graph.py
  cli.py
  cli.clinerules
  ARCHITECTURE.md
  .env
  ...
```

## Agent Loop and Tool Selection

- **Natural Language Interface:** Any user input is interpreted as a request; the agent uses OpenAI function calling to select and execute the appropriate tool.
- **Tool Schemas:** All tools are defined in JSONSchema format and passed to OpenAI for function selection. Tools include:
  - shell_exec
  - python_exec
  - research (OpenAlex/Perplexity)
  - file_read
  - file_write
  - browse
  - message_notify_user
  - idle
- **Persistent System Prompt:** The agent supports a detailed, user-configurable system prompt that guides all actions and tool selection.
- **Knowledge Graph & Memory:** All actions, research, and results are stored in a persistent SQLite knowledge graph, enabling context-aware recall and reasoning.
- **Fallback Logic:** If OpenAI returns code or shell blocks instead of JSON, the agent extracts and executes them.

## Component Relationships

```mermaid
flowchart TD
    U[User]
    U -- "Natural Language Request" --> AGENT[AI Agent Loop (OpenAI Function Calling)]
    AGENT -- "Tool Selection" --> TOOLS[Tool Layer (shell, python, research, file, browser, message, idle)]
    TOOLS -- "Action/Result" --> KG[Knowledge Graph & Memory]
    AGENT -- "Recall/Reason" --> KG
    AGENT -- "System Prompt" --> AGENT
    AGENT -- "Planner/Knowledge/Reflexion (planned)" --> AGENT
    AGENT -- "User Message" --> U
```

## Cline/Manus Compliance

- All tools are defined in JSONSchema and documented in .clinerules and the memory bank.
- The agent loop, system prompt, and knowledge graph are persistent and user-configurable.
- Sequentialthinking and context7 are used for planning, troubleshooting, and documentation.
- All integration steps, tool schemas, and error handling are documented for Cline/Manus compliance.

## Pending Next Steps

- Expand tool schemas (planner, knowledge, datasource, event stream, reflexion)
- Implement planner module for multi-step task planning
- Integrate knowledge and datasource modules
- Add event stream and reflexion/self-critique
- Update all docs and .clinerules as new capabilities are added
