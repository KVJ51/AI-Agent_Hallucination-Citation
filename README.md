🤖 AI Agent for Hallucination Detection & Citation Generation

An intelligent AI agent that detects hallucinated content in LLM responses and automatically adds trustworthy citations using real web and academic sources.

This system improves the reliability, transparency, and credibility of AI-generated content by verifying claims and attaching real references.
🏗️ Architecture
text
Input Text → Extraction → [Retrieval + Citation Check] → Reasoning → Risk → JSON
                  ↓
             Real-time APIs (no database!)
5 Specialized Agents:

ExtractionAgent - Claims + citations

RetrievalAgent - Web + academic search

ReasoningAgent - LLM-as-judge

CitationAgent - DOI/URL validation

RiskScorer - Aggregate risk
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
bash
git clone https://github.com/KVJ51/ai-agent-h&c.git
cd ai-agent-h&c/backend
python -m venv venv
# Windows:
venv\Scripts\activate
Install dependencies

fastapi>=0.110.0
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.2
requests==2.31.0
spacy==3.7.2
nltk==3.8.1
beautifulsoup4==4.12.2
google-genai
serpapi==0.1.3
arxiv==2.1.0

pip install -r requirements.txt
python -m spacy download en_core_web_sm

Configure
bash
cp .env.example .env
notepad .env  # Add your API keys
.env:

text
OPENAI_API_KEY=sk-...
SERPAPI_KEY=...
CROSSREF_EMAIL=your@email.com
GOOGLE_API_KEY=..
Run
bash
python main.py
Server runs at: http://localhost:8000

Test
bash
# Health check
curl http://localhost:8000/api/health

# Verify text
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"content": "Your AI text here"}'
Frontend
bash
cd frontend
python -m http.server 3000
Open: http://localhost:3000

📁 Project Structure
text
ai-agent-h&c/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── config.py            # API keys + settings
│   ├── agents/              # 5 specialized agents
│   │   ├── extraction_agent.py
│   │   ├── reasoning_agent.py
│   │   ├── citation_agent.py
│   │   ├── risk_scorer.py
│   │   └── verification_agent.py  # Orchestrator
│   └── tools/
│       └── retrieval_tools.py     # Web/academic APIs
├── frontend/
│   └── index.html           # Interactive UI
├── .env                     # API keys
└── requirements.txt

