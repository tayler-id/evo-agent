from typing import List, Dict, Any, Optional
from agents.types import Agent, AgentRole, Task, Message, TaskStatus

class PlannerAgent(Agent):
    role = AgentRole.PLANNER

    def __init__(self):
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.log: List[Dict[str, Any]] = []

    def receive_task(self, task: Task) -> None:
        """Receive a new high-level goal or task and add it to the queue."""
        self.task_queue.append(task)
        self.log.append({"event": "receive_task", "task_id": task.id, "description": task.description})

    def decompose_task(self, task: Task) -> List[Task]:
        """
        Decompose a high-level task into actionable subtasks for other agents.
        This is a stub; actual decomposition logic will be implemented later.
        """
        # Example: return [Task(...), Task(...)]
        self.log.append({"event": "decompose_task", "task_id": task.id})
        return []

    def assign_task(self, subtask: Task, agent_role: AgentRole) -> None:
        """
        Assign a subtask to another agent.
        """
        # In a real system, this would send the task to the appropriate agent.
        self.log.append({"event": "assign_task", "subtask_id": subtask.id, "assigned_to": agent_role})

    def monitor_progress(self) -> None:
        """
        Monitor the status of all active tasks and update as needed.
        """
        self.log.append({"event": "monitor_progress"})

    def send_message(self, message: Message) -> None:
        """
        Send a message to another agent.
        """
        self.log.append({"event": "send_message", "to": message.recipient, "content": message.content})

    def get_status(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "queue_length": len(self.task_queue),
            "active_tasks": list(self.active_tasks.keys()),
            "completed_tasks": list(self.completed_tasks.keys()),
        }
