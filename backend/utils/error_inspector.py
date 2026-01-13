def analyze_error(error: Exception) -> dict:
    msg = str(error)

    if "models/gemini" in msg and "not found" in msg:
        return {
            "type": "MODEL_ACCESS_ERROR",
            "action": "Switch to fallback model: gemini-1.0-pro",
            "fixable": True
        }

    if "401" in msg and "serpapi" in msg.lower():
        return {
            "type": "API_KEY_ERROR",
            "action": "Disable SerpAPI and continue with CrossRef only",
            "fixable": False
        }

    if "429" in msg:
        return {
            "type": "RATE_LIMIT",
            "action": "Apply backoff or skip this provider",
            "fixable": False
        }

    return {
        "type": "UNKNOWN",
        "action": "Log and continue",
        "fixable": False
    }
