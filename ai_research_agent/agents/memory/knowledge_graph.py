import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

class KnowledgeGraph:
    def __init__(self, db_path: str = "ai_research_agent/knowledge.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_graph (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                predicate TEXT,
                object TEXT,
                metadata TEXT
            )
        """)
        self.conn.commit()

    def add_triple(self, subject: str, predicate: str, object_: str, metadata: Optional[Dict[str, Any]] = None):
        self.conn.execute(
            "INSERT INTO knowledge_graph (subject, predicate, object, metadata) VALUES (?, ?, ?, ?)",
            (subject, predicate, object_, json.dumps(metadata or {}))
        )
        self.conn.commit()

    def query(self, subject: Optional[str] = None, predicate: Optional[str] = None, object_: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT subject, predicate, object, metadata FROM knowledge_graph WHERE 1=1"
        params = []
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if predicate:
            query += " AND predicate = ?"
            params.append(predicate)
        if object_:
            query += " AND object = ?"
            params.append(object_)
        cur = self.conn.execute(query, params)
        results = []
        for row in cur.fetchall():
            results.append({
                "subject": row[0],
                "predicate": row[1],
                "object": row[2],
                "metadata": json.loads(row[3])
            })
        return results

    def related(self, topic: str) -> List[Dict[str, Any]]:
        # Find all triples where the topic is subject or object
        cur = self.conn.execute(
            "SELECT subject, predicate, object, metadata FROM knowledge_graph WHERE subject = ? OR object = ?",
            (topic, topic)
        )
        results = []
        for row in cur.fetchall():
            results.append({
                "subject": row[0],
                "predicate": row[1],
                "object": row[2],
                "metadata": json.loads(row[3])
            })
        return results
