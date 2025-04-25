from typing import Any, Dict, List, Optional, Protocol, Union
from enum import Enum

class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    MEMORY = "memory"
    CRITIC = "critic"
    EXECUTOR = "executor"

class TaskStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(
        self,
        id: str,
        description: str,
        role: AgentRole,
        status: TaskStatus = TaskStatus.PENDING,
        context: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
    ):
        self.id = id
        self.description = description
        self.role = role
        self.status = status
        self.context = context or {}
        self.result = result

class Message:
    def __init__(
        self,
        sender: AgentRole,
        recipient: AgentRole,
        content: str,
        payload: Optional[Dict[str, Any]] = None,
    ):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.payload = payload or {}

class Agent(Protocol):
    role: AgentRole

    def receive_task(self, task: Task) -> None:
        ...

    def send_message(self, message: Message) -> None:
        ...

    def get_status(self) -> Dict[str, Any]:
        ...

# Knowledge item for memory agent
class KnowledgeItem:
    def __init__(
        self,
        id: str,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.content = content
        self.embedding = embedding or []
        self.metadata = metadata or {}
