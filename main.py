import streamlit as st
import autogen
import os
import threading
import queue
from tavily import TavilyClient

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Classic Aircraft Flight Planner",
    page_icon="✈️",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;600&display=swap');

  :root {
    --cream:   #f5f0e8;
    --rust:    #c0392b;
    --navy:    #1a2744;
    --gold:    #d4a017;
    --smoke:   #e8e0d0;
    --ink:     #1c1c1c;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--cream) !important;
    font-family: 'IBM Plex Mono', monospace;
    color: var(--ink);
  }

  /* Hide default Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Hero banner ── */
  .hero {
    background: var(--navy);
    color: var(--cream);
    padding: 2.4rem 2rem 1.6rem;
    margin-bottom: 2rem;
    border-bottom: 4px solid var(--rust);
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: "✈";
    font-size: 18rem;
    position: absolute;
    right: -2rem;
    top: -3rem;
    opacity: 0.04;
    line-height: 1;
  }
  .hero h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4rem;
    letter-spacing: 0.12em;
    margin: 0 0 0.3rem;
    color: var(--cream);
  }
  .hero .tagline {
    font-size: 0.75rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--gold);
    margin: 0;
  }
  .hero .stripe {
    width: 60px; height: 4px;
    background: var(--rust);
    margin: 0.8rem 0;
  }

  /* ── Section labels ── */
  .section-label {
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--rust);
    font-weight: 600;
    margin-bottom: 0.4rem;
  }

  /* ── API key panel ── */
  .api-panel {
    background: var(--navy);
    border-left: 4px solid var(--gold);
    padding: 1.4rem 1.6rem;
    border-radius: 2px;
    margin-bottom: 1.2rem;
  }
  .api-panel p {
    color: var(--smoke);
    font-size: 0.78rem;
    margin: 0 0 0.8rem;
    line-height: 1.6;
  }

  /* ── Streamlit inputs override ── */
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stSelectbox"] select {
    background: var(--smoke) !important;
    border: 1.5px solid #b0a898 !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    color: var(--ink) !important;
  }
  [data-testid="stTextInput"] input:focus,
  [data-testid="stTextArea"] textarea:focus {
    border-color: var(--rust) !important;
    box-shadow: 0 0 0 2px rgba(192,57,43,0.15) !important;
  }

  /* ── Run button ── */
  [data-testid="stButton"] > button {
    background: var(--rust) !important;
    color: white !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.3rem !important;
    letter-spacing: 0.15em !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.7rem 2.5rem !important;
    width: 100%;
    transition: background 0.2s;
  }
  [data-testid="stButton"] > button:hover {
    background: #a93226 !important;
  }

  /* ── Agent output stream ── */
  .agent-stream {
    background: var(--navy);
    color: #d4f5d4;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    padding: 1.4rem;
    border-radius: 2px;
    border-left: 4px solid var(--gold);
    white-space: pre-wrap;
    line-height: 1.8;
    min-height: 120px;
    max-height: 520px;
    overflow-y: auto;
  }

  /* Agent name badges */
  .badge-flight   { color: #7ec8e3; font-weight: 600; }
  .badge-visa     { color: #f5c842; font-weight: 600; }
  .badge-cost     { color: #a8e6a3; font-weight: 600; }
  .badge-proxy    { color: #e89a7c; font-weight: 600; }
  .badge-manager  { color: #c9b1ff; font-weight: 600; }

  /* ── Summary card ── */
  .summary-card {
    background: white;
    border: 1.5px solid var(--smoke);
    border-top: 4px solid var(--rust);
    padding: 1.6rem;
    border-radius: 2px;
    margin-top: 1.2rem;
    font-size: 0.82rem;
    line-height: 1.8;
  }
  .summary-card h3 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 0.1em;
    color: var(--navy);
    margin: 0 0 0.8rem;
  }

  /* ── Status pill ── */
  .status-pill {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  .status-running { background: #fff3cd; color: #856404; }
  .status-done    { background: #d1e7dd; color: #0f5132; }
  .status-error   { background: #f8d7da; color: #842029; }

  /* ── Divider ── */
  hr { border: none; border-top: 1px solid #ccc5b5; margin: 1.5rem 0; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 3px solid var(--rust);
  }
  [data-testid="stSidebar"] * { color: var(--cream) !important; }
  [data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.08) !important;
    color: var(--cream) !important;
    border-color: rgba(255,255,255,0.2) !important;
  }
  [data-testid="stSidebar"] label { color: var(--gold) !important; font-size: 0.7rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="tagline">Powered by AutoGen · Tavily · OpenAI</p>
  <div class="stripe"></div>
  <h1>Classic Aircraft Flight Planner</h1>
  <p style="color:#9ab0c8;font-size:0.8rem;margin:0.4rem 0 0;letter-spacing:0.05em;">
    Find flights on vintage jets · check visa requirements · compare total costs
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — API Keys
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:0.12em;">
        API KEYS
      </div>
      <div style="font-size:0.65rem;letter-spacing:0.25em;color:#d4a017;text-transform:uppercase;margin-bottom:1rem;">
        Configuration Panel
      </div>
    </div>
    """, unsafe_allow_html=True)

    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Your OpenAI API key (GPT-3.5-turbo)"
    )
    tavily_key = st.text_input(
        "Tavily API Key",
        type="password",
        placeholder="tvly-...",
        help="Your Tavily search API key"
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.65rem;color:#7a8fa8;line-height:1.8;">
      Keys are used only for this session and never stored.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Model selector
    model_choice = st.selectbox(
        "LLM Model",
        ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"],
        index=0,
    )

    max_rounds = st.slider("Max Rounds", min_value=5, max_value=30, value=12, step=1)

# ─────────────────────────────────────────────────────────────────────────────
# Main layout — Input columns
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

presets = {
    "B737 Classic · Africa · 🇺🇸 American": "I want to fly on classic B737 in Africa. My nationality is American.\nPlease find available routes and check if I need a visa.",
    "MD-80 · Latin America · 🇬🇧 British": "I want to fly on a McDonnell Douglas MD-80 in Latin America. My nationality is British.\nFind routes and check visa requirements.",
    "B747-400 · Asia · 🇲🇾 Malaysian": "I want to fly on a B747-400 on Lufthansa. My nationality is Malaysian.\nFind available routes and check if I need a visa.",
    "Fokker 100 · Europe · 🇦🇺 Australian": "I want to fly on a Fokker 100 in Europe. My nationality is Australian.\nFind available routes and visa info.",
    "DC-9 · USA · 🇨🇦 Canadian": "I want to fly on a Douglas DC-9 within the United States. My nationality is Canadian.\nFind routes and entry requirements.",
}

# Initialise task text in session_state
if "task_text" not in st.session_state:
    st.session_state.task_text = "I want to fly on classic B737 in Africa. My nationality is American.\nPlease find available routes and check if I need a visa."

with col_right:
    st.markdown('<div class="section-label">Quick Presets</div>', unsafe_allow_html=True)

    def apply_preset():
        chosen = st.session_state.preset_select
        if chosen != "— choose a preset —":
            st.session_state.task_text = presets[chosen]

    st.selectbox(
        "preset",
        label_visibility="collapsed",
        options=["— choose a preset —"] + list(presets.keys()),
        key="preset_select",
        on_change=apply_preset,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("▶  LAUNCH AGENTS", use_container_width=True)

with col_left:
    st.markdown('<div class="section-label">Your Request</div>', unsafe_allow_html=True)
    task_input = st.text_area(
        label="task",
        label_visibility="collapsed",
        key="task_text",
        height=140,
        placeholder="e.g. I want to fly on a DC-9 in Southeast Asia. My nationality is British.",
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Agent runner
# ─────────────────────────────────────────────────────────────────────────────
def run_agents(task: str, openai_key: str, tavily_key: str,
               model: str, max_rounds: int, msg_queue: queue.Queue):
    """Runs in a background thread; pushes chat lines into msg_queue."""
    try:
        os.environ["OPENAI_API_KEY"] = openai_key
        tavily_client = TavilyClient(api_key=tavily_key)

        def tavily_search(query: str) -> str:
            response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
            results = []
            for r in response.get("results", []):
                results.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n")
            return "\n---\n".join(results) if results else "No results found."

        tavily_tool_schema = {
            "type": "function",
            "function": {
                "name": "tavily_search",
                "description": (
                    "Search the internet for flights operating on older aircraft "
                    "from the 1980s, 1990s, and 2000s. Use this to find airlines "
                    "still flying vintage/classic aircraft."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"}
                    },
                    "required": ["query"]
                }
            }
        }

        llm_config = {"model": model}

        flight = autogen.AssistantAgent(
            name="flight",
            system_message=(
                "You're a flight planner focusing on old planes. Search the internet "
                "and find flights operating on older aircraft from the 1980s, 1990s, "
                "and 2000s (e.g. Boeing 737-200, MD-80, 747-400, DC-9, Fokker 100). "
                "Always use the tavily_search tool to find up-to-date information."
            ),
            llm_config={**llm_config, "tools": [tavily_tool_schema]},
        )

        visa = autogen.AssistantAgent(
            name="visa",
            system_message=(
                "You're a visa agent. Check and verify whether the customer is eligible "
                "for a visa depending on origin and destination. "
                "Once all information is gathered, end your reply with TERMINATE."
            ),
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
            llm_config=llm_config,
        )

        cost_planner = autogen.AssistantAgent(
            name="cost_planner",
            llm_config=llm_config,
            system_message=(
                "You are a cost planner. Based on the available flight routes, estimate "
                "the total cost including flight ticket, visa fees, and travel documentation. "
                "List all routes with total estimated costs ranked in ascending order."
            ),
        )

        # Custom PrintSink to capture agent messages into the queue
        class QueuePrint:
            def __init__(self, q): self.q = q
            def __call__(self, *args, **kwargs):
                msg = " ".join(str(a) for a in args)
                self.q.put(("msg", msg))

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=max_rounds,
            code_execution_config=False,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        )
        user_proxy.register_function(function_map={"tavily_search": tavily_search})

        groupchat = autogen.GroupChat(
            agents=[user_proxy, flight, visa, cost_planner],
            messages=[],
            max_round=max_rounds,
        )
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

        res = user_proxy.initiate_chat(
            recipient=manager,
            message=task,
            summary_method="last_msg",
        )

        msg_queue.put(("summary", res.summary))
        msg_queue.put(("done", None))

    except Exception as e:
        msg_queue.put(("error", str(e)))


# ─────────────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────────────
if "log_lines" not in st.session_state:
    st.session_state.log_lines = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "status" not in st.session_state:
    st.session_state.status = "idle"   # idle | running | done | error

# ─────────────────────────────────────────────────────────────────────────────
# On button click
# ─────────────────────────────────────────────────────────────────────────────
if run_btn:
    if not openai_key or not tavily_key:
        st.error("⚠️  Please enter both API keys in the sidebar before launching.")
    elif not st.session_state.task_text.strip():
        st.error("⚠️  Please describe your flight request.")
    else:
        st.session_state.log_lines = []
        st.session_state.summary = ""
        st.session_state.status = "running"
        st.session_state.msg_queue = queue.Queue()

        t = threading.Thread(
            target=run_agents,
            args=(st.session_state.task_text, openai_key, tavily_key,
                  model_choice, max_rounds, st.session_state.msg_queue),
            daemon=True,
        )
        t.start()
        st.session_state.thread = t

# ─────────────────────────────────────────────────────────────────────────────
# Live output rendering
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.status in ("running", "done", "error"):

    # Drain queue into log
    if st.session_state.status == "running" and "msg_queue" in st.session_state:
        q = st.session_state.msg_queue
        while not q.empty():
            kind, payload = q.get_nowait()
            if kind == "msg":
                st.session_state.log_lines.append(payload)
            elif kind == "summary":
                st.session_state.summary = payload
            elif kind == "done":
                st.session_state.status = "done"
            elif kind == "error":
                st.session_state.log_lines.append(f"\n❌ ERROR: {payload}")
                st.session_state.status = "error"

    # Status pill
    if st.session_state.status == "running":
        st.markdown('<span class="status-pill status-running">⏳ Agents running…</span>', unsafe_allow_html=True)
        st.button("↻ Refresh", key="refresh")
    elif st.session_state.status == "done":
        st.markdown('<span class="status-pill status-done">✅ Complete</span>', unsafe_allow_html=True)
    elif st.session_state.status == "error":
        st.markdown('<span class="status-pill status-error">❌ Error</span>', unsafe_allow_html=True)

    # Log window
    st.markdown('<div class="section-label">Agent Conversation Log</div>', unsafe_allow_html=True)

    def colorize(line: str) -> str:
        """Add color tags to agent names."""
        for name, cls in [("flight", "badge-flight"), ("visa", "badge-visa"),
                           ("cost_planner", "badge-cost"), ("user_proxy", "badge-proxy"),
                           ("GroupChatManager", "badge-manager")]:
            if name.lower() in line.lower()[:40]:
                return f'<span class="{cls}">{line}</span>'
        return line

    log_html = "\n".join(colorize(l) for l in st.session_state.log_lines[-200:])
    st.markdown(
        f'<div class="agent-stream">{log_html or "Waiting for agents…"}</div>',
        unsafe_allow_html=True
    )

    # Summary card
    if st.session_state.summary:
        st.markdown("""
        <div class="summary-card">
          <h3>📋 Final Summary</h3>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.summary)
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #ccc5b5;
            font-size:0.65rem;letter-spacing:0.15em;color:#888;text-align:center;
            text-transform:uppercase;">
  Classic Aircraft Flight Planner · AutoGen Multi-Agent System · Tavily Search
</div>
""", unsafe_allow_html=True)
