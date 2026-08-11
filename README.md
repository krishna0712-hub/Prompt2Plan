# Prompt2Plan ⚡

> **Prompt in, project plan out.**

Describe your project idea in plain English and instantly get:
1. 🏗️ **System Architecture Diagram** — auto-generated, interactive Mermaid.js visualization with TD/LR toggles
2. 📋 **Task Board** — Kanban-style drag-and-drop board with interactive task editing, deletion, and addition
3. 📅 **Milestone Timeline** — phased Gantt schedule chart with developer effort estimates
4. 💰 **Cloud Cost & Risk Analysis** — Starter vs Growth tier cloud infrastructure cost estimates and risk assessment
5. 📦 **Multi-Format Exporters** — single-click export to Markdown, JSON, Jira CSV, GitHub Issues CSV, and Printable PDF Reports

![Prompt2Plan](https://img.shields.io/badge/Stack-FastAPI%20+%20React%20+%20Groq-7C5CFF?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| **Backend** | Python 3.10+ & FastAPI | Serves REST API + builds and hosts React frontend from one process |
| **Frontend** | React 18 (Vite) + Tailwind CSS v4 | Framer Motion animations + `@hello-pangea/dnd` |
| **Database** | SQLite (SQLAlchemy ORM) | Auto-created zero-config database (`prompt2plan.db`) |
| **LLM** | Groq API (`llama-3.3-70b-versatile`) | High-speed cloud LLM inference |
| **LLM Fallback** | Hugging Face Inference API | Auto-fallback provider if Groq is unavailable |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Local CPU vector embeddings |
| **Vector Search** | FAISS (`faiss-cpu`) | In-process vector index of seed templates |
| **Knowledge Graph** | `kg.json` | 33 feature → component & dependency mappings |
| **Diagrams** | Mermaid.js | Client-side dark theme diagram rendering |
| **Exporters** | `backend/exporter.py` | Generates Jira CSV, GitHub Issues CSV, and Printable PDF HTML Reports |

---

## Quick Start

### Prerequisites
- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- A **free Groq API key** (optional, fallback engines work offline)

### 1. Get a free Groq API key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up and create an API key

### 2. Configure the API key
```bash
# Copy the example env file
cp backend/.env.example backend/.env

# Edit backend/.env and set your key:
# GROQ_API_KEY=gsk_your_key_here
```

### 3. Install dependencies & run the app
```bash
# Single command to build frontend and start backend
python run.py
```

### 4. Open the app
Navigate to **[http://localhost:8000](http://localhost:8000)**

---

## How It Works

```
User Prompt → NLP Extraction → [RAG Retrieval ∥ Knowledge Graph] → Architecture Generation
                                                                          ↓
  Frontend ← Exporters & CRUD ← Cost & Risk ← Milestones ← Effort ← Task Breakdown
```

### Complete 10-Phase Pipeline

1. **NLP Extraction** — Parses user text into domain, features, scale, and project type.
2. **RAG Retrieval** — Embeds features with `sentence-transformers`, searches FAISS vector index of seed templates.
3. **Knowledge Graph Lookup** — Fuzzy-matches features against 33 entries in `kg.json` to find required components & dependencies.
4. **Architecture Generation** — Merges RAG + KG context to generate a component relationship graph (JSON).
5. **Task Breakdown** — Expands components into concrete dev tasks using templates (~25 types) + LLM fallback.
6. **Effort Estimation** — Heuristic calculation: base hours x complexity multipliers x variance.
7. **Milestone Scheduling** — Groups tasks into 4 phases (Setup → Core Dev → Testing → Deployment), calculating day ranges at 6h/day.
8. **Persistence & Plan History** — Stores generated plans, architecture graphs, tasks, and milestones in SQLite.
9. **Cost & Risk Engine** — Estimates starter vs growth cloud hosting costs (Vercel, AWS, Supabase, Redis) and assesses technical risk.
10. **Multi-Format Exporters & Interactive Customization** — Direct exports to Jira CSV, GitHub Issues CSV, Markdown, JSON, and PDF Reports, plus live Task CRUD with dynamic milestone recalculation.

---

## Project Structure

```
prompt2plan/
├── backend/
│   ├── main.py                 # FastAPI application (API + static serving)
│   ├── database.py             # SQLAlchemy models & SQLite setup
│   ├── llm_client.py           # LLM client with Groq → HuggingFace fallback
│   ├── nlp_extraction.py       # Step 1: Feature requirement extraction
│   ├── rag_retrieval.py        # Step 2: FAISS vector similarity search
│   ├── knowledge_graph.py      # Step 3: KG component & dependency lookup
│   ├── architecture_gen.py     # Step 4: System architecture graph generator
│   ├── task_breakdown.py       # Step 5: Task breakdown engine
│   ├── effort_estimation.py    # Step 6: Developer effort estimator
│   ├── milestone_scheduler.py  # Step 7: Phase milestone scheduler
│   ├── cost_estimation.py     # Step 9: Infrastructure cost & risk analyzer
│   ├── exporter.py             # Step 10: Jira, GitHub, & HTML/PDF exporter
│   ├── data/
│   │   ├── seed_templates.json # Seed project templates (RAG corpus)
│   │   └── kg.json             # Feature → component dependency mapping
│   └── tests/                  # Pytest test suite (10 unit/integration tests)
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React wrapper with header & tab views
│   │   ├── index.css           # Glassmorphism styles & Tailwind directives
│   │   ├── components/
│   │   │   ├── PromptInput.jsx         # Hero prompt input & quick starters
│   │   │   ├── LoadingAnimation.jsx    # Concentric spinning rings & stage text
│   │   │   ├── ProjectHeader.jsx       # Plan summary & export dropdown toolbar
│   │   │   ├── ArchitectureDiagram.jsx # Mermaid.js renderer with TD/LR toggles
│   │   │   ├── TaskBoard.jsx           # Drag-and-drop Kanban board & Task CRUD
│   │   │   └── Timeline.jsx            # Gantt schedule chart & metrics dashboard
│   │   └── utils/
│   │       └── animations.js   # Framer Motion animation variants
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── run.py                      # Single entry point script (Windows compatible)
└── README.md
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/generate-plan` | Generate a full project plan from an idea string |
| `GET` | `/api/projects` | List recent saved plans |
| `GET` | `/api/projects/{id}` | Retrieve a specific project plan by ID |
| `GET` | `/api/projects/{id}/export?format={format}` | Export plan (`markdown`, `json`, `jira_csv`, `github_csv`, `pdf`) |
| `POST` | `/api/projects/{id}/tasks` | Add a custom task to a plan (recalculates milestones) |
| `PUT` | `/api/projects/{id}/tasks/{task_id}` | Update task status, hours, phase, or component |
| `DELETE` | `/api/projects/{id}/tasks/{task_id}` | Delete a task from a plan (recalculates milestones) |

---

## Testing

Run the automated backend test suite:
```bash
python run.py --test
```
or directly via pytest:
```bash
py -m pytest backend/tests
```

---

## License

MIT
