# Reunite - AI-Powered Missing Children Matching Platform

**Reunite** uses EverOS semantic memory and an OpenRouter-backed (or OpenAI) conversational AI to help reconnect missing children with their families. Parents register descriptions of their missing child; children/adults with fragmentary childhood memories register what they remember. The system intelligently matches them using memory-based semantic search.

**Live Demo:** [https://reunite-evermind.vercel.app](https://reunite-evermind.vercel.app)

**Video Demo:** [Reunite_Final_Video.mp4](Reunite_Final_Video.mp4)

> **Note:** The live demo uses synthetic mock data to protect privacy. All names, locations, and descriptions are fictional.

---

## 1. Features

### 1.1 Bidirectional Smart Matching
- **Parents** describe their missing child (appearance, habits, last seen location, physical features)
- **Children/Adults** describe fragmentary childhood memories (sensory memories, places, people, events)
- The system searches the **opposite** database and ranks potential matches by relevance

### 1.2 AI Memory Guide (Conversational Recall Assistant)
- An assistant (OpenRouter by default, with OpenAI as a fallback) gently guides users through conversation to recall more details
- Uses 6 questioning strategies: sensory memories, daily routines, spatial memories, relationships, special events, physical details
- Secretly references potential matches from EverOS to ask targeted questions (e.g., if a match's father was a carpenter, asks "Do you remember any wood smells at home?")
- Every new detail from chat is **automatically stored in EverOS** as additional memory, improving future matches

### 1.3 My Entries & Ongoing Updates
- Users can register entries and return later to add more details via AI Chat
- Updated information is synced to both local database and EverOS (with stale memories cleared on update)
- Supports the realistic scenario where memories surface gradually over time

### 1.4 Ground Truth Evaluation System
- 46 mock entries: 15 matched pairs + 16 distractors (8 distractor parents + 8 distractor children)
- 3 difficulty levels: Easy (minor memory errors), Medium (wrong details), Hard (major distortions/fabricated memories)
- Automated evaluation script measuring Top-1, Top-3, Top-5 accuracy in both directions
- Current results: **87% Top-1, 100% Top-3** (Parent→Child), **73% Top-1, 100% Top-3** (Child→Parent), with 1/8 distractor false-positive rate at the calibrated 0.38 score threshold

---

## 2. How We Use EverOS Memory

### 2.1 Memory Storage Architecture
Each registered person is a **sender** within one of two groups in EverOS:
```
sender_id = "reunite_{entry_id}"
group_id  = "reunite_parents_v2" | "reunite_children_v2"
```

Per entry, we store **one English-only natural-sentence message** that EverOS extracts into episodes and atomic facts. Parents and children use distinct phrasings to give EverOS the right perspective:

| Field | Parent (Searching for child) | Child (Searching for family) |
|---|---|---|
| Lead | `Searching for a missing child named X (gender, born around Y), last seen around Z.` | `Person searching for their birth family (current/adoptive name: X), gender, born around Y, separated from family around Z.` |
| Location | `Last known location: ...` | `Place memory: ...` |
| Features | `Distinguishing physical features: ...` | `Physical features: ...` |
| Description | `Background: ...` | `Memories: ...` |

Chat messages from the AI guide are appended as additional memories per sender, building a richer profile over time.

### 2.2 Semantic Search for Matching
When matching, we run a multi-stage pipeline:

1. **Hard filter** in SQLite — gender must match, birth year within ±3, candidate pool ~halved
2. **Multi-query weighted EverOS hybrid search** in the *opposite* group:
   - `physical_features` (weight 0.55) — strongest signal: birthmarks, scars, distinguishing traits
   - `location` (weight 0.20) — last seen vs. place memory
   - `description` (weight 0.25) — background story vs. recall fragments
3. **Score combination** — episodes are mapped back to senders via `participants`, taking the max score per sender across each sub-query, then weighted-summed
4. **Threshold filter** — `min_score = 0.38` (calibrated against the GT distribution: real matches score 0.39–0.47, distractor top-1 ≤ 0.39)
5. **Keyword backstop** — for senders not returned by EverOS, we fall back to character-level Chinese-friendly Jaccard, capped just below the lowest EverOS score so it never out-ranks real semantic hits
6. If EverOS errors out entirely, the engine degrades to pure keyword matching so the UI never breaks

### 2.3 Progressive Memory Enhancement
The AI Chat feature creates a **growing memory profile** for each user:
- Initial registration → one structured English message
- Each chat turn → an additional `Additional recalled memory: ...` message
- More conversations = richer episodes = better future matches
- This mirrors real-world memory recall: details surface gradually over multiple sessions

---

## 3. How Memory Helps Users

### 3.1 Matching Despite Imperfect Memories
Missing children often have **distorted, fragmentary, or even fabricated memories**. EverOS semantic search can find connections even when:
- Locations are remembered wrong (child says "Thai restaurant" but family ran an Indian restaurant)
- Details are confused (child remembers "5th floor" but it was actually 3rd floor)
- Memories are mixed with dreams or TV scenes

### 3.2 AI-Guided Memory Recovery
The AI assistant uses EverOS matches as **hidden context** to guide questioning:
- If a potential match's parent was a mechanic, the AI asks about "oil smells" or "garage sounds"
- This helps users recall details they didn't know they remembered
- Each new detail is stored back into EverOS, creating a **virtuous cycle** of improving matches

### 3.3 Persistent, Searchable Memory
Unlike a static database entry, EverOS creates a **living memory profile**:
- Memories from different conversations are connected and searchable
- New entries in the system can be matched against existing memory profiles
- As more people register, the chance of finding a match improves for everyone

---

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- EverOS API key (from [everos.evermind.ai](https://everos.evermind.ai))
- OpenRouter API key (preferred) **or** OpenAI API key

### Setup
```bash
# Clone the repository
git clone https://github.com/visionxyz/Reunite.git
cd Reunite

# Install dependencies
uv sync

# Configure API keys
cp .env.example .env
# Edit .env: set EVERMEMOS_API_KEY and OPENROUTER_API_KEY (or OPENAI_API_KEY)

# Run the application
uv run python main.py
# Open http://127.0.0.1:8000
```

### Run Evaluation
```bash
# Make sure the server is running first
uv run python evaluate.py
```

---

## Tech Stack
- **Backend:** FastAPI + Python 3.12
- **Memory:** EverOS Cloud API v1 (semantic memory storage & hybrid search)
- **AI Assistant:** OpenRouter (default `openai/gpt-4o-mini`, configurable via `OPENAI_MODEL`); falls back to direct OpenAI if `OPENROUTER_API_KEY` is unset
- **Database:** SQLite (local metadata)
- **Frontend:** Single-page HTML/JS with Jinja2 templates

## Project Structure
```
reunite-app/
├── main.py              # Entry point
├── evaluate.py          # Ground truth evaluation script
├── app/
│   ├── main.py          # FastAPI routes
│   ├── models.py        # Data models
│   ├── database.py      # SQLite operations
│   ├── matching.py      # EverOS v1 matching engine
│   ├── assistant.py     # AI conversational guide (OpenRouter / OpenAI)
│   ├── mock_data.py     # 46 mock entries with ground truth
│   ├── templates/
│   │   └── index.html   # Single-page frontend
│   └── static/
│       └── style.css    # Styles
└── .env.example         # API key template
```
