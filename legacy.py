import autogen
import os
from dotenv import load_dotenv
load_dotenv()
from tavily import TavilyClient

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))  # ✅ read from env
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm_config = {"model": "gpt-3.5-turbo"}

# ── 1. Tavily search function ────────────────────────────────────────────────
def tavily_search(query: str) -> str:
    """Search the internet using Tavily for flight information."""
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )
    results = []
    for r in response.get("results", []):
        results.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n")
    return "\n---\n".join(results) if results else "No results found."


# ── 2. Tool schema ───────────────────────────────────────────────────────────
tavily_tool_schema = {
    "type": "function",
    "function": {
        "name": "tavily_search",
        "description": (
            "Search the internet for flights operating on older aircraft "
            "from the 1980s, 1990s, and 2000s (e.g. Boeing 737-200, MD-80, "
            "747-200, DC-9, etc.). Use this to find airlines still flying "
            "vintage/classic aircraft."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, e.g. 'airlines still flying Boeing 737-200 classic'"
                }
            },
            "required": ["query"]
        }
    }
}


# ── 3. Agents ────────────────────────────────────────────────────────────────
flight = autogen.AssistantAgent(
    name="flight",
    system_message=(
        "You're a flight planner focusing on old planes. Your job is to plan "
        "the customer's flight based on the aircraft type. Search the internet "
        "and find flights operating on older aircraft from the 1980s, 1990s, "
        "and 2000s (e.g. Boeing 737-200, MD-80, 747-200, DC-9, Fokker 100, etc.). "
        "Always use the tavily_search tool to find up-to-date information."
    ),
    llm_config={
        **llm_config,
        "tools": [tavily_tool_schema],
    },
)

visa = autogen.AssistantAgent(
    name="visa",
    system_message=(
        "You're a visa agent. Your job is to check and verify with the flight planner "
        "whether the customer is eligible for a visa or not depending on origin and destination. "
        "Once you have all the information needed, end your reply with TERMINATE."
    ),
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
)

cost_planner = autogen.AssistantAgent(
    name="SEO_Reviewer",
    llm_config=llm_config,
    system_message="You are a cost planner, you need to come up with possible cost of a flight plus the visa and documentation fees of countries based on the available flight routes"
        "Provide list of flight routes along with the total cost and rank up in ascending order "
        
        ,
)

# ── 4. UserProxyAgent — REQUIRED to execute tool calls ──────────────────────
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",          # fully automated
    max_consecutive_auto_reply=10,
    code_execution_config=False,       # no code execution needed
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

# ✅ Register the actual callable so AutoGen can invoke it when flight calls the tool
user_proxy.register_function(
    function_map={"tavily_search": tavily_search}
)


# ── 5. Group chat: all three agents collaborate ──────────────────────────────
groupchat = autogen.GroupChat(
    agents=[user_proxy, flight, visa, cost_planner],
    messages=[],
    max_round=20,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
)


# ── 6. Kick off ──────────────────────────────────────────────────────────────
task = """
    I want to fly on classic B737 in Africa. My nationality is American.
    Please find available routes and check if I need a visa.
"""

res = user_proxy.initiate_chat(
    recipient=manager,
    message=task,
    summary_method="last_msg",
)

print(res.summary)
