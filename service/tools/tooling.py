import anthropic
import requests

anthropic_client = anthropic.Anthropic(api_key="your_api_key_here")

# Create tools with them such as MCP, use only recognisable journals and databases for the web search tool
def web_search_tool(query):
    url=f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Web search failed with status code {response.status_code}")
    return response.json() # Feed the full response into it

# Generate subagents based on the plan purpose, only if they can run in parallel
def generate_subagent(user_id, thread_id, purpose, context):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": "Generate an action agent based on the current plan in the memory and the tools available."}],
    )
    return response.content[0].text

tools_schema = [
    {
        "name": "web_search",
        "description": "Search academic databases like ArXiv for research papers",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }, 
    {
        "name": "generate_subagent",
        "description": "Generate a subagent to perform a specific task based on the current plan and context",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user"
                },
                "thread_id": {
                    "type": "string",
                    "description": "The ID of the thread"
                },
                "purpose": {
                    "type": "string",
                    "description": "The specific purpose or task for the subagent"
                },
                "context": {
                    "type": "string",
                    "description": "The relevant context or information for the subagent to consider"
                }
            },
            "required": ["user_id", "thread_id", "purpose", "context"]
        }

    }
]
