🤖 AI Agent for Hallucination Detection & Citation Generation

An intelligent AI agent that detects hallucinated content in LLM responses and automatically adds trustworthy citations using real web and academic sources.

This system improves the reliability, transparency, and credibility of AI-generated content by verifying claims and attaching real references.

🏗️ Architecture
Input Text → Extraction → [Retrieval + Citation Check] → Reasoning → Risk → JSON
                   ↓
              Real-time APIs
🧩 Five Specialized Agents
Agent	Role
ExtractionAgent	Extracts claims and potential citations
RetrievalAgent	Searches web + academic sources
ReasoningAgent	LLM-as-judge to verify truthfulness
CitationAgent	Validates DOI / URL sources
RiskScorer	Aggregates hallucination risk
🚀 Features
🔍 Hallucination Detection

Identifies unsupported or fabricated statements in AI responses.

📚 Automatic Citations

Adds references from:

Google Search

arXiv research papers

Verified web sources

🌐 Web + Academic Fact Checking

Uses live search and academic APIs to validate claims.

⚡ FastAPI Backend

Exposes REST endpoints for easy integration with chatbots or apps.

🧠 NLP Processing

Uses SpaCy & NLTK to analyze and split claims.

🚀 Quick Start (5 Minutes)
Prerequisites

Python 3.9+

Setup
git clone https://github.com/KVJ51/ai-agent-h&c.git
cd ai-agent-h&c/backend
python -m venv venv

Activate venv (Windows):

venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
⚙️ Configure
cp .env.example .env
notepad .env

.env file:

OPENAI_API_KEY=sk-...
SERPAPI_KEY=...
CROSSREF_EMAIL=your@email.com
GOOGLE_API_KEY=...
▶️ Run Backend
python main.py

Server runs at:

http://localhost:8000
🧪 Test API

Health Check

curl http://localhost:8000/api/health

Verify Text

curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"content": "Your AI text here"}'
🌐 Frontend
cd frontend
python -m http.server 3000

Open in browser:

http://localhost:3000
📁 Project Structure
ai-agent-h&c/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── config.py            # API keys + settings
│   ├── agents/              # 5 specialized agents
│   │   ├── extraction_agent.py
│   │   ├── reasoning_agent.py
│   │   ├── citation_agent.py
│   │   ├── risk_scorer.py
│   │   └── verification_agent.py
│   └── tools/
│       └── retrieval_tools.py
├── frontend/
│   └── index.html
├── .env
└── requirements.txt
