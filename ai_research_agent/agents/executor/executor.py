from typing import List, Dict, Any, Optional
from agents.types import Agent, AgentRole, Task, Message

class ExecutorAgent(Agent):
    role = AgentRole.EXECUTOR

    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def execute_action(self, action: Dict[str, Any]) -> str:
        """
        Execute an action request (e.g., OS script, Git, calendar, Slack, Home-Assistant).
        Returns a result string or status.
        """
        # Stub: In a real system, this would dispatch to the appropriate adapter.
        self.log.append({"event": "execute_action", "action": action})
        return "Stub execution: action dispatched."

    def receive_task(self, task: Task) -> None:
        """
        Receive a task (e.g., execute an action).
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
