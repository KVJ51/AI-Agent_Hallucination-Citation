from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging
from contextlib import asynccontextmanager

from agents.verification_agent import VerificationAgent
from config import config

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- LIFESPAN ----------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Hallucination & Citation Verification Agent started")
    yield
    logger.info("Agent shutdown")

# ---------------- APP ----------------
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
    lifespan=lifespan
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- EXCEPTION HANDLERS ----------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles validation errors with detailed diagnosis and corrective guidance.
    """
    errors = []
    for error in exc.errors():
        # Get field location (e.g., body -> text)
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Unknown error")
        
        # Self-diagnosis / Corrective Guidance
        guidance = "Ensure request matches schema."
        error_type = error.get("type", "")
        
        if "missing" in error_type:
             guidance = f"The required field '{loc}' is missing. Please include it."
        elif "min_length" in error_type:
             ctx = error.get("ctx", {})
             limit = ctx.get("limit_value", 5)
             guidance = f"The field '{loc}' must be at least {limit} characters long."
        elif "json_invalid" in error_type:
             guidance = "Invalid JSON format. Check for syntax errors."

        errors.append({
            "location": loc,
            "message": msg,
            "guidance": guidance
        })

    logger.warning(f"Client validation error: {errors}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request Validation Failed",
            "diagnosis": "Schema mismatch or invalid data detected.",
            "errors": errors,
            "example_correct_payload": {
                "text": "The Earth revolves around the Sun."
            }
        }
    )

# ---------------- AGENT ----------------
agent = VerificationAgent()

# ---------------- REQUEST MODEL ----------------
class VerifyRequest(BaseModel):
    text: str = Field(
        ...,
        description="The text content to be verified.",
        min_length=5,
        examples=["The Earth revolves around the Sun."]
    )

# ---------------- ROUTE ----------------

@app.post("/api/verify")
async def verify_content(request: VerifyRequest):
    """
    Verifies the provided text content for hallucinations and citations.
    
    """
    try:
        logger.info(f"Verifying content: {len(request.text)} chars")
        result = await agent.verify(request.text)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Verification failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- RUN ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
