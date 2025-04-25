from agents.researcher.researcher import ResearcherAgent
from agents.memory.memory import MemoryAgent
from agents.memory.knowledge_graph import KnowledgeGraph
import json
from dotenv import load_dotenv; load_dotenv()

def main():
    print("=== AI Research Agent CLI (Natural Language Mode) ===")
    print("Type any request in natural language. The agent will select and use the right tool automatically.")
    print("Type 'exit' to quit.\n")

    researcher = ResearcherAgent()
    memory = MemoryAgent()
    watchlist_path = "ai_research_agent/watchlist.json"
    kg = KnowledgeGraph()

    # Load or initialize watchlist
    try:
        with open(watchlist_path, "r") as f:
            watchlist = set(json.load(f))
    except Exception:
        watchlist = set()

    def save_watchlist():
        with open(watchlist_path, "w") as f:
            json.dump(list(watchlist), f)

    # Tool schemas for OpenAI function calling
    tool_schemas = [
        {
            "type": "function",
            "name": "shell_exec",
            "description": "Execute a shell command in the current directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"]
            }
        },
        {
            "type": "function",
            "name": "python_exec",
            "description": "Execute a Python code snippet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            }
        },
        {
            "type": "function",
            "name": "file_read",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Path to the file to read"}
                },
                "required": ["file"]
            }
        },
        {
            "type": "function",
            "name": "file_write",
            "description": "Write content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Path to the file to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["file", "content"]
            }
        },
        {
            "type": "function",
            "name": "browse",
            "description": "Fetch and display the content of a web page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to browse"}
                },
                "required": ["url"]
            }
        },
        {
            "type": "function",
            "name": "research",
            "description": "Perform research using OpenAlex (academic) or Perplexity (news/web).",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic"},
                    "source": {"type": "string", "enum": ["openalex", "news"], "description": "Source to use"}
                },
                "required": ["topic"]
            }
        },
        {
            "type": "function",
            "name": "message_notify_user",
            "description": "Send a message to the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Message text to display to user"}
                },
                "required": ["text"]
            }
        },
        {
            "type": "function",
            "name": "idle",
            "description": "Indicate all tasks are complete and enter idle state.",
            "parameters": {"type": "object"}
        }
    ]

    import subprocess
    import requests
    import os

    system_prompt = None

    while True:
        cmd = input(">> ").strip()
        if not cmd or cmd.lower() == "exit":
            print("Exiting AI Research Agent CLI.")
            break

        # Natural language mode: always use OpenAI function calling for tool selection
        try:
            import openai
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("(OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.)")
                continue
            client = OpenAI(api_key=api_key)
            system_msg = (
                "You are an autonomous AI agent with access to the following tools: "
                "shell_exec, python_exec, research, file_read, file_write, browse, message_notify_user, idle. "
                "Given a user request, select the most appropriate tool and return ONLY a valid JSON object, no explanation: "
                '{"tool": "<tool>", "args": {"arg1": "...", ...}}. '
                "If the request is a question, use 'research'. If it is a code or shell command, use the appropriate tool. "
                "If it is a file operation, use 'file_read' or 'file_write'. If it is a URL, use 'browse'. "
                "Never return an explanation, only the JSON object. If you cannot decide, default to research."
            )
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": cmd}
            ]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
                temperature=0
            )
            tool_call = response.choices[0].message.tool_calls[0] if response.choices[0].message.tool_calls else None
            if not tool_call:
                print("Could not parse tool selection from OpenAI.")
                continue
            tool = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"[Agent] Selected tool: {tool} with args: {args}")

            # Dispatch to the appropriate tool
            if tool == "python_exec":
                code = args.get("code", "")
                if code:
                    print(f"[Python] Executing code: {code}")
                    import tempfile
                    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                        f.write(code)
                        fname = f.name
                    result = subprocess.run(["python3", fname], capture_output=True, text=True)
                    print("=== Python Output ===")
                    print(result.stdout)
                    if result.stderr:
                        print("=== Python Error ===")
                        print(result.stderr)
                    kg.add_triple("python", "executed_code", code, {"stdout": result.stdout, "stderr": result.stderr})
                else:
                    print("No code provided.")
            elif tool == "shell_exec":
                shell_cmd = args.get("command", "")
                if shell_cmd:
                    print(f"[Shell] Executing: {shell_cmd}")
                    result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
                    print("=== Shell Output ===")
                    print(result.stdout)
                    if result.stderr:
                        print("=== Shell Error ===")
                        print(result.stderr)
                    kg.add_triple(shell_cmd, "executed_shell", result.stdout.strip(), {"stderr": result.stderr.strip()})
                else:
                    print("No shell command provided.")
            elif tool == "research":
                topic = args.get("topic", cmd)
                source = args.get("source", "news")
                print(f"[Researcher] Searching for: {topic} (source: {source})")
                if source == "news":
                    digest = perplexity_news_search(topic, system_prompt)
                    print("\n=== News Digest ===")
                    print(digest)
                    item_id = memory.embed_and_store(digest, metadata={"source": "news", "topic": topic, "system_prompt": system_prompt})
                    kg.add_triple(topic, "researched_news", digest, {"source": "news", "system_prompt": system_prompt})
                else:
                    results = researcher.web_search(topic, top_k=5)
                    digest = researcher.synthesize_digest(results)
                    print("\n=== Synthesized Digest ===")
                    if digest.strip():
                        print(digest)
                    else:
                        print("(No results found. Try a more general or academic query, e.g., 'AI code generation', 'transformer models', 'machine learning programming', etc.)")
                    item_id = memory.embed_and_store(digest, metadata={"source": "researcher", "topic": topic, "system_prompt": system_prompt})
                    kg.add_triple(topic, "researched_academic", digest, {"source": "openalex", "system_prompt": system_prompt})
                print(f"\n[Memory] Digest stored in memory as item_id: {item_id}\n")
            elif tool == "file_read":
                file_path = args.get("file", "")
                if file_path:
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                        print(f"=== File Content ({file_path}) ===")
                        print(content)
                        kg.add_triple(file_path, "read_file", content, {})
                    except Exception as e:
                        print(f"File read error: {e}")
                else:
                    print("No file path provided.")
            elif tool == "file_write":
                file_path = args.get("file", "")
                content = args.get("content", "")
                if file_path and content:
                    try:
                        with open(file_path, "w") as f:
                            f.write(content)
                        print(f"File {file_path} written successfully.")
                        kg.add_triple(file_path, "wrote_file", content, {})
                    except Exception as e:
                        print(f"File write error: {e}")
                else:
                    print("File path or content missing.")
            elif tool == "browse":
                url = args.get("url", "")
                if url:
                    try:
                        print(f"\n[Browser] Fetching: {url}")
                        page = requests.get(url, timeout=15)
                        if page.status_code == 200:
                            content = page.text[:2000]
                            print("=== Page Content (truncated) ===")
                            print(content)
                            kg.add_triple(url, "browsed", content, {"source": "browser"})
                        else:
                            print(f"Failed to fetch page: {page.status_code}")
                    except Exception as e:
                        print(f"Browser error: {e}")
                else:
                    print("No URL provided.")
            elif tool == "message_notify_user":
                text = args.get("text", "")
                print(f"[Agent] Message to user: {text}")
            elif tool == "idle":
                print("[Agent] All tasks complete. Entering idle state.")
                break
            else:
                print(f"Unknown tool selected: {tool}")
        except Exception as e:
            print(f"OpenAI tool selection error: {e}")
        # The rest of the CLI reserved commands (python, shell, etc.) remain unchanged below...
        if cmd.lower().startswith("python "):
            code = cmd[len("python "):].strip()
            if not code:
                print("Please provide Python code to execute.")
                continue
            try:
                print("\n[Python] Executing code...")
                import tempfile
                with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                    f.write(code)
                    fname = f.name
                result = subprocess.run(["python3", fname], capture_output=True, text=True)
                print("=== Python Output ===")
                print(result.stdout)
                if result.stderr:
                    print("=== Python Error ===")
                    print(result.stderr)
                kg.add_triple("python", "executed_code", code, {"stdout": result.stdout, "stderr": result.stderr})
            except Exception as e:
                print(f"Python execution error: {e}")
        elif cmd.lower().startswith("read "):
            file_path = cmd[len("read "):].strip()
            if not file_path:
                print("Please provide a file path to read.")
                continue
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                print(f"=== File Content ({file_path}) ===")
                print(content)
                kg.add_triple(file_path, "read_file", content, {})
            except Exception as e:
                print(f"File read error: {e}")
        elif cmd.lower().startswith("write "):
            parts = cmd.split(" ", 2)
            if len(parts) < 3:
                print("Usage: write <file> <content>")
                continue
            file_path, content = parts[1], parts[2]
            try:
                with open(file_path, "w") as f:
                    f.write(content)
                print(f"File {file_path} written successfully.")
                kg.add_triple(file_path, "wrote_file", content, {})
            except Exception as e:
                print(f"File write error: {e}")
        if cmd.lower() == "exit":
            print("Exiting AI Research Agent CLI.")
            break
        elif cmd.lower().startswith("shell "):
            shell_cmd = cmd[len("shell "):].strip()
            if not shell_cmd:
                print("Please provide a shell command to execute.")
                continue
            try:
                print(f"\n[Shell] Executing: {shell_cmd}")
                result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
                print("=== Shell Output ===")
                print(result.stdout)
                if result.stderr:
                    print("=== Shell Error ===")
                    print(result.stderr)
                kg.add_triple(shell_cmd, "executed_shell", result.stdout.strip(), {"stderr": result.stderr.strip()})
            except Exception as e:
                print(f"Shell execution error: {e}")
        elif cmd.lower().startswith("browse "):
            url = cmd[len("browse "):].strip()
            if not url:
                print("Please provide a URL to browse.")
                continue
            try:
                print(f"\n[Browser] Fetching: {url}")
                # Use Puppeteer MCP server to extract content
                puppeteer_url = "http://localhost:3001/tools/puppeteer_screenshot"
                payload = {"name": "cli_browse", "selector": "body", "width": 900, "height": 600}
                # This is a placeholder; in a real setup, you would use the puppeteer_navigate and puppeteer_screenshot tools
                # For now, just fetch the page content as a fallback
                page = requests.get(url, timeout=15)
                if page.status_code == 200:
                    content = page.text[:2000]  # Show first 2000 chars
                    print("=== Page Content (truncated) ===")
                    print(content)
                    kg.add_triple(url, "browsed", content, {"source": "browser"})
                else:
                    print(f"Failed to fetch page: {page.status_code}")
            except Exception as e:
                print(f"Browser error: {e}")
        elif cmd.lower().startswith("system "):
            system_prompt = cmd[len("system "):].strip()
            print(f"System prompt set for this session:\n{system_prompt}\n")
        elif cmd.lower().startswith("research "):
            # Allow: research <topic> [source]
            parts = cmd.split()
            if len(parts) < 2:
                print("Please provide a topic to research.")
                continue
            topic = " ".join(parts[1:-1]) if parts[-1] in ["openalex", "news"] else " ".join(parts[1:])
            source = parts[-1] if parts[-1] in ["openalex", "news"] else "openalex"
            print(f"\n[Researcher] Searching for: {topic} (source: {source})")
            if source == "news":
                def news_with_system(query):
                    import requests, os
                    api_key = os.getenv("PERPLEXITY_API_KEY")
                    if not api_key:
                        return "(Perplexity API key not found. Please set PERPLEXITY_API_KEY in your .env file.)"
                    try:
                        url = "https://api.perplexity.ai/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        model = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
                        messages = []
                        if system_prompt:
                            messages.append({"role": "system", "content": system_prompt})
                        messages.append({"role": "user", "content": query})
                        payload = {
                            "model": model,
                            "messages": messages
                        }
                        response = requests.post(url, headers=headers, json=payload, timeout=20)
                        if response.status_code != 200:
                            return f"(Perplexity news search error: {response.status_code} {response.reason}\n{response.text})"
                        data = response.json()
                        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return answer if answer else "(No Perplexity results found.)"
                    except Exception as e:
                        return f"(Perplexity news search error: {e})"
                digest = perplexity_news_search(topic, system_prompt)
                print("\n=== News Digest ===")
                print(digest)
                item_id = memory.embed_and_store(digest, metadata={"source": "news", "topic": topic, "system_prompt": system_prompt})
                kg.add_triple(topic, "researched_news", digest, {"source": "news", "system_prompt": system_prompt})
            else:
                results = researcher.web_search(topic, top_k=5)
                digest = researcher.synthesize_digest(results)
                print("\n=== Synthesized Digest ===")
                if digest.strip():
                    print(digest)
                else:
                    print("(No results found. Try a more general or academic query, e.g., 'AI code generation', 'transformer models', 'machine learning programming', etc.)")
                item_id = memory.embed_and_store(digest, metadata={"source": "researcher", "topic": topic, "system_prompt": system_prompt})
                kg.add_triple(topic, "researched_academic", digest, {"source": "openalex", "system_prompt": system_prompt})
            print(f"\n[Memory] Digest stored in memory as item_id: {item_id}\n")
        elif cmd.lower().startswith("loop "):
            # loop <topic> [n]
            parts = cmd.split()
            if len(parts) < 2:
                print("Please provide a topic to loop on.")
                continue
            topic = " ".join(parts[1:-1]) if parts[-1].isdigit() else " ".join(parts[1:])
            n = int(parts[-1]) if parts[-1].isdigit() else 3
            for i in range(n):
                print(f"\n[Loop {i+1}/{n}] Researching: {topic} (source: news)")
                def news_with_system(query):
                    import requests, os
                    api_key = os.getenv("PERPLEXITY_API_KEY")
                    if not api_key:
                        return "(Perplexity API key not found. Please set PERPLEXITY_API_KEY in your .env file.)"
                    try:
                        url = "https://api.perplexity.ai/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        model = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
                        messages = []
                        if system_prompt:
                            messages.append({"role": "system", "content": system_prompt})
                        messages.append({"role": "user", "content": query})
                        payload = {
                            "model": model,
                            "messages": messages
                        }
                        response = requests.post(url, headers=headers, json=payload, timeout=20)
                        if response.status_code != 200:
                            return f"(Perplexity news search error: {response.status_code} {response.reason}\n{response.text})"
                        data = response.json()
                        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return answer if answer else "(No Perplexity results found.)"
                    except Exception as e:
                        return f"(Perplexity news search error: {e})"
                digest = perplexity_news_search(topic, system_prompt)
                print("\n=== News Digest ===")
                print(digest)
                item_id = memory.embed_and_store(digest, metadata={"source": "news", "topic": topic, "system_prompt": system_prompt, "loop": i+1})
                kg.add_triple(topic, f"loop_{i+1}_researched_news", digest, {"source": "news", "system_prompt": system_prompt, "loop": i+1})
            print(f"\n[Loop] Completed {n} research cycles for topic: {topic}\n")
        elif cmd.lower().startswith("recall "):
            query = cmd[len("recall "):].strip()
            if not query:
                print("Please provide a query to recall.")
                continue
            recall_results = memory.semantic_search(query, top_k=1)
            print("\n=== Quick Recall Result ===")
            if recall_results:
                print(recall_results[0].content)
                kg.add_triple(query, "recalled", recall_results[0].content, {"action": "recall"})
            else:
                print("No recall result found.\n")
        elif cmd.lower().startswith("watch "):
            topic = cmd[len("watch "):].strip()
            if not topic:
                print("Please provide a topic to watch.")
                continue
            watchlist.add(topic)
            save_watchlist()
            print(f"Added '{topic}' to your watchlist.")
        elif cmd.lower() == "watchlist":
            if not watchlist:
                print("Your watchlist is empty. Add topics with 'watch <topic>'.")
                continue
            print("Your watchlist topics:")
            for t in watchlist:
                print(f"- {t}")
            print("\nChecking for new research on watchlist topics...")
            for t in watchlist:
                results = researcher.web_search(t, top_k=1)
                if results:
                    title = results[0].get("title", "")
                    print(f"Latest for '{t}': {title}")
                else:
                    print(f"No new research found for '{t}'.")
        elif cmd.lower().startswith("graph "):
            topic = cmd[len("graph "):].strip()
            if not topic:
                print("Please provide a topic to graph.")
                continue
            related = kg.related(topic)
            print(f"\n=== Knowledge Graph for '{topic}' ===")
            if related:
                for triple in related:
                    print(f"{triple['subject']} --[{triple['predicate']}]--> {triple['object']}")
            else:
                print("No related knowledge found.\n")
        elif cmd.lower() == "suggest":
            cur = memory.conn.execute("SELECT metadata FROM knowledge ORDER BY ROWID DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                metadata = row[0]
                try:
                    meta = eval(metadata) if isinstance(metadata, str) else metadata
                except Exception:
                    meta = {}
                topic = meta.get("topic", "AI research")
                print(f"Suggested next action: 'research {topic} updates' or 'recall {topic}'")
            else:
                print("No prior research found. Try 'research <topic>' first.")
        else:
            print("Unknown command. Use 'research <topic>', 'recall <query>', 'watch <topic>', 'watchlist', 'suggest', or 'exit'.")

if __name__ == "__main__":
    main()
