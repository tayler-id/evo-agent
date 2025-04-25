from typing import List, Dict, Any, Optional
from agents.types import Agent, AgentRole, Task, Message
import json
import requests

class ResearcherAgent(Agent):
    role = AgentRole.RESEARCHER

    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def web_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a real research paper search using the OpenAlex API and return a list of result dicts.
        If no results are found in the abstract, retry with a title search.
        """
        self.log.append({"event": "web_search", "query": query, "top_k": top_k})
        try:
            # First, search abstracts
            url = f"https://api.openalex.org/works?filter=abstract.search:{requests.utils.quote(query)}&per-page={top_k}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            normalized = []
            for work in data.get("results", []):
                # Reconstruct abstract from abstract_inverted_index if present
                abstract = ""
                idx = work.get("abstract_inverted_index")
                if idx:
                    pos_to_word = {}
                    for word, positions in idx.items():
                        for pos in positions:
                            pos_to_word[pos] = word
                    abstract = " ".join([pos_to_word[i] for i in range(len(pos_to_word))])
                else:
                    abstract = "(No abstract available)"
                normalized.append({
                    "title": work.get("display_name", ""),
                    "url": work.get("id", ""),
                    "snippet": abstract,
                })
            if normalized:
                self.log.append({"event": "web_search_results", "count": len(normalized)})
                return normalized
            # If no results, retry with title search
            url_title = f"https://api.openalex.org/works?filter=title.search:{requests.utils.quote(query)}&per-page={top_k}"
            response_title = requests.get(url_title, timeout=10)
            response_title.raise_for_status()
            data_title = response_title.json()
            normalized_title = []
            for work in data_title.get("results", []):
                abstract = ""
                idx = work.get("abstract_inverted_index")
                if idx:
                    pos_to_word = {}
                    for word, positions in idx.items():
                        for pos in positions:
                            pos_to_word[pos] = word
                    abstract = " ".join([pos_to_word[i] for i in range(len(pos_to_word))])
                else:
                    abstract = "(No abstract available)"
                normalized_title.append({
                    "title": work.get("display_name", ""),
                    "url": work.get("id", ""),
                    "snippet": abstract,
                })
            if normalized_title:
                self.log.append({"event": "web_search_results_title_fallback", "count": len(normalized_title)})
                return normalized_title
            self.log.append({"event": "web_search_no_results"})
            return []
        except Exception as e:
            self.log.append({"event": "web_search_error", "error": str(e)})
            # Fallback to stub results
            return [{"title": f"Result {i+1}", "url": f"https://example.com/{i+1}", "snippet": "Stub result"} for i in range(top_k)]

    def local_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search local files/notes and return a list of result dicts.
        """
        self.log.append({"event": "local_search", "query": query, "top_k": top_k})
        return [{"title": f"Local Result {i+1}", "path": f"/path/to/file_{i+1}.md", "snippet": "Stub local result"} for i in range(top_k)]

    def synthesize_digest(self, sources: List[Dict[str, Any]]) -> str:
        """
        Synthesize a digest from multiple sources.
        """
        self.log.append({"event": "synthesize_digest", "source_count": len(sources)})
        # Simple concatenation for now; can be replaced with LLM summarization
        digest = "\n\n".join([f"{src.get('title', 'Untitled')}: {src.get('snippet', '')}" for src in sources])
        return digest

    def receive_task(self, task: Task) -> None:
        """
        Receive a research task (e.g., search, summarize).
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
