# Classic Aircraft Flight Planner

Demo Link: https://legacy-flight-plan.streamlit.app/

A multi-agent AI web app built with [AutoGen](https://github.com/microsoft/autogen), [Streamlit](https://streamlit.io/), and [Tavily](https://tavily.com/) that helps you find flights on vintage/classic aircraft, check visa requirements, and compare total travel costs — all in a single run.

---

## What it does

Enter a natural-language request like:

> *"I want to fly on a DC-9 in Southeast Asia. My nationality is British."*

A team of AI agents collaborates to:

1. **Find routes** — searches the internet for airlines still operating classic jets from the 1980s–2000s (B737-200, MD-80, B747-400, DC-9, Fokker 100, etc.)
2. **Check visa requirements** — verifies whether your nationality requires a visa for the destination
3. **Estimate costs** — calculates total trip cost (ticket + visa fees + travel docs) and ranks routes cheapest-first

Results stream live in the UI and conclude with a formatted summary card.

---

## Agent Architecture

| Agent | Role |
|---|---|
| `flight` | Searches for vintage aircraft routes via Tavily |
| `visa` | Checks visa eligibility for the passenger's nationality |
| `cost_planner` | Estimates and ranks total travel costs |
| `user_proxy` | Orchestrates the group chat; executes tool calls |

All agents run inside an AutoGen `GroupChat` managed by a `GroupChatManager`.

---

## Tech Stack

- **[AutoGen](https://github.com/microsoft/autogen)** — multi-agent orchestration
- **[OpenAI](https://platform.openai.com/)** — LLM backend (GPT-3.5-turbo / GPT-4o-mini / GPT-4o)
- **[Tavily](https://tavily.com/)** — real-time web search for flight data
- **[Streamlit](https://streamlit.io/)** — web UI

---

## Prerequisites

- Python 3.13+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Tavily API key](https://app.tavily.com/)

---

## Installation

```bash
git clone https://github.com/your-username/legacy-flight-autogen.git
cd legacy-flight-autogen

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## Running the app

```bash
streamlit run main.py
```

The app opens at `http://localhost:8501`.

1. Enter your **OpenAI** and **Tavily** API keys in the sidebar
2. Select a model and max conversation rounds
3. Type your flight request (or pick a quick preset)
4. Click **LAUNCH AGENTS** and watch the agents collaborate in real time

> API keys are used only for the current session and are never stored.

---

## Quick Presets

The app ships with five ready-made requests:

- B737 Classic in Africa (American passport)
- MD-80 in Latin America (British passport)
- B747-400 on Lufthansa (Malaysian passport)
- Fokker 100 in Europe (Australian passport)
- DC-9 within the USA (Canadian passport)

---

## Project Structure

```
legacy-flight-autogen/
├── main.py          # Streamlit app + AutoGen agent definitions
├── requirements.txt # Direct dependencies
└── pyproject.toml   # Project metadata
```

---

## License

MIT
