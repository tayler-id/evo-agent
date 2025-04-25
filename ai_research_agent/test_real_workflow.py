import json
from agents.memory.memory import MemoryAgent
from agents.researcher.researcher import ResearcherAgent

def main():
    # Load real search results
    with open("ai_research_agent/agents/researcher/real_search_results.json", "r") as f:
        results = json.load(f)

    # Synthesize digest as Researcher would
    researcher = ResearcherAgent()
    digest = researcher.synthesize_digest(results)

    print("=== Synthesized Digest ===")
    print(digest)
    print()

    # Store digest in Memory agent
    memory = MemoryAgent()
    item_id = memory.embed_and_store(digest, metadata={"source": "researcher", "topic": "AI papers"})
    print(f"Digest stored in memory as item_id: {item_id}")

    # Perform semantic search for "AI papers"
    recall_results = memory.semantic_search("AI papers", top_k=1)
    print("\n=== Quick Recall Result ===")
    if recall_results:
        print(recall_results[0].content)
    else:
        print("No recall result found.")

if __name__ == "__main__":
    main()
