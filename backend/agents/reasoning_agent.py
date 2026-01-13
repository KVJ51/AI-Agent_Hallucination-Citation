import json
import logging
from typing import List, Dict
import asyncio
from google import genai
from config import config

logger = logging.getLogger(__name__)


class ReasoningAgent:
    """LLM-based reasoning using Google Gemini (new SDK)"""

    def __init__(self):
        # ✅ Correct way to authenticate
        self.client = genai.Client(
            api_key=config.GOOGLE_API_KEY
        )

        self.model_name = "gemini-pro"

    async def judge_claim(self, claim: str, evidence_snippets: List[str]) -> Dict:

        if not evidence_snippets:
            return {
                "claim": claim,
                "status": "UNVERIFIABLE",
                "confidence": 0.0,
                "explanation": "No evidence provided",
                "best_evidence": None
            }

        evidence_text = "\n\n".join(
            f"Evidence {i + 1}: {snippet[:250]}"
            for i, snippet in enumerate(evidence_snippets[:3])
        )

        prompt = f"""
You are an expert fact-checker.

Claim:
{claim}

Evidence:
{evidence_text}

Respond ONLY in JSON with this schema:
{{
  "status": "SUPPORTED" | "CONTRADICTED" | "UNVERIFIABLE",
  "confidence": 0.0-1.0,
  "explanation": "1-2 sentence justification",
  "best_evidence_idx": 0
}}
"""

        try:
            # ✅ Async-safe call using thread executor
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )
            

            content = response.text.strip()

            # Remove code fences if present
            if "```" in content:
                content = (
                    content.replace("```json", "")
                           .replace("```", "")
                           .strip()
                )

            result = json.loads(content)
            result["claim"] = claim

            idx = result.get("best_evidence_idx", 0)
            if isinstance(idx, int) and idx < len(evidence_snippets):
                result["best_evidence"] = evidence_snippets[idx]
            else:
                result["best_evidence"] = evidence_snippets[0]

            return result
        
        

        except Exception as e:
            logger.error(
                f"Reasoning error for claim '{claim}': {e}",
                exc_info=True
            )
            return {
                "claim": claim,
                "status": "UNVERIFIABLE",
                "confidence": 0.0,
                "explanation": f"Analysis error: {str(e)}",
                "best_evidence": None
            }