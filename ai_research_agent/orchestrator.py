from agents.types import AgentRole, Task, Message, TaskStatus
from agents.planner.planner import PlannerAgent
from agents.researcher.researcher import ResearcherAgent
from agents.memory.memory import MemoryAgent
from agents.critic.critic import CriticAgent
from agents.executor.executor import ExecutorAgent

class MessageBus:
    def __init__(self, agents):
        self.agents = agents
        self.log = []

    def send(self, message: Message):
        self.log.append({"event": "send", "from": message.sender, "to": message.recipient, "content": message.content})
        agent = self.agents.get(message.recipient)
        if agent:
            agent.receive_task(Task(
                id="msg_" + message.content[:8],
                description=message.content,
                role=message.recipient,
                status=TaskStatus.PENDING,
                context=message.payload
            ))

class Orchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.memory = MemoryAgent()
        self.critic = CriticAgent()
        self.executor = ExecutorAgent()
        self.agents = {
            AgentRole.PLANNER: self.planner,
            AgentRole.RESEARCHER: self.researcher,
            AgentRole.MEMORY: self.memory,
            AgentRole.CRITIC: self.critic,
            AgentRole.EXECUTOR: self.executor,
        }
        self.bus = MessageBus(self.agents)

    def run_demo_workflow(self):
        # Step 1: Planner receives a high-level goal
        goal_task = Task(
            id="goal_1",
            description="Summarize top 5 AI papers and store in memory.",
            role=AgentRole.PLANNER
        )
        self.planner.receive_task(goal_task)

        # Step 2: Planner decomposes and assigns a research task
        research_task = Task(
            id="research_1",
            description="Find top 5 AI papers.",
            role=AgentRole.RESEARCHER
        )
        self.planner.assign_task(research_task, AgentRole.RESEARCHER)
        self.researcher.receive_task(research_task)

        # Step 3: Researcher performs real web search and synthesizes digest
        results = self.researcher.web_search("top AI papers", top_k=5)
        digest = self.researcher.synthesize_digest(results)

        # Step 4: Memory agent stores the digest
        item_id = self.memory.embed_and_store(digest, metadata={"source": "researcher", "topic": "AI papers"})

        # Step 5: Quick-Recall: perform semantic search for "AI papers"
        recall_results = self.memory.semantic_search("AI papers", top_k=1)
        recalled_content = recall_results[0].content if recall_results else None

        # Step 6: Critic reviews the process
        outcome = {"task": "research_1", "result": digest}
        self.critic.monitor_outcome(outcome)
        recommendation = self.critic.trigger_reflection({"task": "research_1", "result": digest})

        # Step 7: Executor could be triggered for further actions (stub)
        action = {"type": "notify", "message": "Digest stored in memory as " + item_id}
        self.executor.execute_action(action)

        # Log summary
        return {
            "planner_log": self.planner.log,
            "researcher_log": self.researcher.log,
            "memory_log": self.memory.log,
            "critic_log": self.critic.log,
            "executor_log": self.executor.log,
            "message_bus_log": self.bus.log,
            "final_digest": digest,
            "memory_item_id": item_id,
            "critic_recommendation": recommendation,
            "quick_recall_result": recalled_content
        }

if __name__ == "__main__":
    orchestrator = Orchestrator()
    summary = orchestrator.run_demo_workflow()
    for k, v in summary.items():
        print(f"{k}: {v}\n")
