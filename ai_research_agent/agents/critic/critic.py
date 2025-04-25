from typing import List, Dict, Any, Optional
from agents.types import Agent, AgentRole, Task, Message

class CriticAgent(Agent):
    role = AgentRole.CRITIC

    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def monitor_outcome(self, outcome: Dict[str, Any]) -> None:
        """
        Monitor the outcome of a task or agent action.
        """
        self.log.append({"event": "monitor_outcome", "outcome": outcome})

    def trigger_reflection(self, context: Dict[str, Any]) -> str:
        """
        Run a self-reflection (Reflexion) loop and return recommendations.
        """
        self.log.append({"event": "trigger_reflection", "context": context})
        # Stub: In a real system, this would analyze context and generate recommendations.
        return "Stub recommendation: Consider alternative strategies."

    def receive_task(self, task: Task) -> None:
        """
        Receive a task (e.g., analyze outcome, reflect).
        """
        self.log.append({"event": "receive_task", "task_id": task.id, "description": task.description})

    def send_message(self, message: Message) -> None:
        """
        Send a message to another agent.
        """
        self.log.append({"event": "send_message", "to": message.recipient, "content": message.content})

    def get_status(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "log_length": len(self.log),
        }
