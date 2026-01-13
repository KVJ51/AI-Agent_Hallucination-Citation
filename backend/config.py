import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_TITLE = "AI Hallucination & Citation Verification Agent"
    API_VERSION = "2.0.0"
    API_DESCRIPTION = "Real-time agent for detecting hallucinations and validating citations"
    
    # Google Gemini / LLM
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "") 
    LLM_MODEL = "gemini-1.5-flash"
    
    # Search APIs
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")  # Alternative to SerpAPI
    
    # Academic APIs
    CROSSREF_EMAIL = os.getenv("CROSSREF_EMAIL", "your-email@example.com")
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    
    # Models
    NLI_MODEL = "microsoft/deberta-large-mnli"  # Fast NLI model
    
    # Timeouts
    API_TIMEOUT = 15
    SEARCH_TIMEOUT = 10
    LLM_TIMEOUT = 30
    
    # Agent Configuration
    SEARCH_BUDGET = 5  # Max searches per claim
    MAX_EVIDENCE_PER_CLAIM = 3  # Max papers to retrieve
    CONFIDENCE_THRESHOLD = 0.6  # Min confidence to make judgment
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

config = Config()
