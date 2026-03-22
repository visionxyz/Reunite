# Reunite - AI-Powered Missing Children Matching Platform

**Reunite** uses EverMemOS semantic memory and OpenAI conversational AI to help reconnect missing children with their families. Parents register descriptions of their missing child; children/adults with fragmentary childhood memories register what they remember. The system intelligently matches them using memory-based semantic search.

**Live Demo:** [https://parent-child-mem.vercel.app](https://parent-child-mem.vercel.app)

**Video Demo:** [Reunite_Final_Video.mp4](Reunite_Final_Video.mp4)

> **Note:** The live demo uses synthetic mock data to protect privacy. All names, locations, and descriptions are fictional.

---

## 1. Features

### 1.1 Bidirectional Smart Matching
- **Parents** describe their missing child (appearance, habits, last seen location, physical features)
- **Children/Adults** describe fragmentary childhood memories (sensory memories, places, people, events)
- The system searches the **opposite** database and ranks potential matches by relevance

### 1.2 AI Memory Guide (Conversational Recall Assistant)
- An OpenAI-powered AI assistant gently guides users through conversation to recall more details
- Uses 6 questioning strategies: sensory memories, daily routines, spatial memories, relationships, special events, physical details
- Secretly references potential matches from EverMemOS to ask targeted questions (e.g., if a match's father was a carpenter, asks "Do you remember any wood smells at home?")
- Every new detail from chat is **automatically stored in EverMemOS** as additional memory, improving future matches

### 1.3 My Entries & Ongoing Updates
- Users can register entries and return later to add more details via AI Chat
- Updated information is synced to both local database and EverMemOS
- Supports the realistic scenario where memories surface gradually over time

### 1.4 Ground Truth Evaluation System
- 46 mock entries: 15 matched pairs + 16 distractors
- 3 difficulty levels: Easy (minor memory errors), Medium (wrong details), Hard (major distortions/fabricated memories)
- Automated evaluation script measuring Top-1, Top-3, Top-5 accuracy in both directions
- Current results: **80% Top-1, 100% Top-3** (Parent→Child), **80% Top-1, 93% Top-3** (Child→Parent)

---

## 2. How We Use EverMemOS Memory

### 2.1 Memory Storage Architecture
Each registered person is modeled as a **unique user** in EverMemOS:
```
user_id = "reunite_{entry_id}"
group_id = "parent_seeking" | "child_seeking"
```

Per user, we store:
- **Message 1:** Structured information (name, gender, birth date, location, physical features)
- **Message 2:** Detailed narrative description (with `flush=True` to trigger memory extraction)
- **Chat Messages:** Each new detail recalled during AI-guided conversations is appended as additional memory

EverMemOS asynchronously extracts episodic memories and user profiles from these messages.

### 2.2 Semantic Search for Matching
When searching for matches:
1. **Group-level search** queries all memories in the opposite group (e.g., searching `child_seeking` group for a parent's query)
2. Results are ranked by EverMemOS relevance scores
3. We use **rank-based normalization** (not raw scores) to avoid score magnitude bias
4. Final ranking combines: **85% keyword similarity + 15% EverMemOS rank bonus**
5. This hybrid approach achieves robust matching across all difficulty levels

### 2.3 Progressive Memory Enhancement
The AI Chat feature creates a **growing memory profile** for each user:
- Initial registration → 2 memories stored
- Each chat conversation → additional memories appended
- More conversations = richer memory profile = better matching accuracy
- This mirrors real-world memory recall: details surface gradually over multiple sessions

---

## 3. How Memory Helps Users

### 3.1 Matching Despite Imperfect Memories
Missing children often have **distorted, fragmentary, or even fabricated memories**. EverMemOS semantic search can find connections even when:
- Locations are remembered wrong (child says "Thai restaurant" but family ran an Indian restaurant)
- Details are confused (child remembers "5th floor" but it was actually 3rd floor)
- Memories are mixed with dreams or TV scenes

### 3.2 AI-Guided Memory Recovery
The AI assistant uses EverMemOS matches as **hidden context** to guide questioning:
- If a potential match's parent was a mechanic, the AI asks about "oil smells" or "garage sounds"
- This helps users recall details they didn't know they remembered
- Each new detail is stored back into EverMemOS, creating a **virtuous cycle** of improving matches

### 3.3 Persistent, Searchable Memory
Unlike a static database entry, EverMemOS creates a **living memory profile**:
- Memories from different conversations are connected and searchable
- New entries in the system can be matched against existing memory profiles
- As more people register, the chance of finding a match improves for everyone

---

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- EverMemOS API key (from [EverMemOS Console](https://console.evermemos.com))
- OpenAI API key

### Setup
```bash
# Clone the repository
git clone https://github.com/visionxyz/ParentChildMem.git
cd ParentChildMem

# Install dependencies
uv sync

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

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
- **Memory:** EverMemOS Cloud API (semantic memory storage & search)
- **AI Assistant:** OpenAI GPT-4o-mini (conversational recall guidance)
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
│   ├── matching.py      # EverMemOS matching engine
│   ├── assistant.py     # AI conversational guide
│   ├── mock_data.py     # 46 mock entries with ground truth
│   ├── templates/
│   │   └── index.html   # Single-page frontend
│   └── static/
│       └── style.css    # Styles
└── .env.example         # API key template
```
