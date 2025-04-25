from typing import List, Dict, Any, Optional
from agents.types import Agent, AgentRole, KnowledgeItem, Task, Message
import numpy as np
import os
import json
import sqlite3

try:
    import openai
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY
except ImportError:
    openai = None

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

class MemoryAgent(Agent):
    role = AgentRole.MEMORY

    def __init__(self, db_path: str = "ai_research_agent/knowledge.db"):
        self.db_path = db_path
        self.log: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                content TEXT,
                embedding TEXT,
                metadata TEXT
            )
        """)
        self.conn.commit()

    def embed(self, content: str) -> List[float]:
        if openai and openai.api_key:
            try:
                response = openai.Embedding.create(
                    input=content,
                    model="text-embedding-ada-002"
                )
                embedding = response["data"][0]["embedding"]
                self.log.append({"event": "embedding", "method": "openai"})
                return embedding
            except Exception as e:
                self.log.append({"event": "embedding_error", "error": str(e)})
        self.log.append({"event": "embedding", "method": "random"})
        return list(np.random.rand(1536))

    def embed_and_store(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        embedding = self.embed(content)
        item_id = f"item_{np.random.randint(1e9)}"
        item = KnowledgeItem(id=item_id, content=content, embedding=embedding, metadata=metadata)
        # Store in DB
        self.conn.execute(
            "INSERT INTO knowledge (id, content, embedding, metadata) VALUES (?, ?, ?, ?)",
            (item_id, content, json.dumps(embedding), json.dumps(metadata or {}))
        )
        self.conn.commit()
        self.log.append({"event": "embed_and_store", "item_id": item_id, "content": content})
        return item_id

    def semantic_search(self, query: str, top_k: int = 3) -> List[KnowledgeItem]:
        query_emb = self.embed(query)
        # Fetch all items from DB
        cur = self.conn.execute("SELECT id, content, embedding, metadata FROM knowledge")
        items = []
        for row in cur.fetchall():
            emb = json.loads(row[2])
            sim = cosine_similarity(query_emb, emb)
            items.append((sim, KnowledgeItem(id=row[0], content=row[1], embedding=emb, metadata=json.loads(row[3]))))
        items.sort(reverse=True, key=lambda x: x[0])
        self.log.append({"event": "semantic_search", "query": query, "top_k": top_k})
        return [item for sim, item in items[:top_k]]

    def receive_task(self, task: Task) -> None:
        self.log.append({"event": "receive_task", "task_id": task.id, "description": task.description})

    def send_message(self, message: Message) -> None:
        self.log.append({"event": "send_message", "to": message.recipient, "content": message.content})

    def get_status(self) -> Dict[str, Any]:
        cur = self.conn.execute("SELECT COUNT(*) FROM knowledge")
        count = cur.fetchone()[0]
        return {
            "role": self.role,
            "knowledge_count": count,
        }
