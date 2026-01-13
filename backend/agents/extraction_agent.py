import re
from typing import List, Dict

import nltk
import spacy
from nltk.tokenize import sent_tokenize
from spacy.util import is_package


# Ensure NLTK punkt is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


class ExtractionAgent:
    """Extracts claims and citations from text"""

    def __init__(self):
        # ❌ Do NOT auto-install models at runtime
        if not is_package("en_core_web_sm"):
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' is not installed.\n"
                "Run this command once:\n"
                "python -m spacy download en_core_web_sm"
            )

        self.nlp = spacy.load("en_core_web_sm")

    def extract_claims(self, text: str) -> List[Dict]:
        """Extract atomic factual claims"""
        if not text or not text.strip():
            return []

        sentences = sent_tokenize(text)
        claims = []

        for sent_idx, sentence in enumerate(sentences):
            doc = self.nlp(sentence)

            if self._is_factual_claim(sentence):
                claims.append({
                    "id": f"claim_{sent_idx}",
                    "text": sentence.strip(),
                    "entities": [(ent.text, ent.label_) for ent in doc.ents],
                    "tokens": [token.text for token in doc]
                })

        return claims

    def extract_citations(self, text: str) -> List[Dict]:
        """Extract citations from text"""
        citations = []

        # APA: Smith et al. (2023)
        apa_pattern = r'(\w+(?:\s+et al\.)?)\s*\((\d{4})\)'
        for match in re.finditer(apa_pattern, text):
            citations.append({
                "type": "apa",
                "text": match.group(0),
                "author": match.group(1),
                "year": int(match.group(2))
            })

        # IEEE: [1]
        for match in re.finditer(r'\[(\d+)\]', text):
            citations.append({
                "type": "ieee",
                "text": match.group(0),
                "reference_id": match.group(1)
            })

        # URLs
        for match in re.finditer(r'https?://[^\s]+', text):
            citations.append({
                "type": "url",
                "text": match.group(0),
                "url": match.group(0)
            })

        # DOI
        doi_pattern = r'(?:doi:|DOI\s+)([^\s]+)'
        for match in re.finditer(doi_pattern, text, re.IGNORECASE):
            citations.append({
                "type": "doi",
                "text": match.group(0),
                "doi": match.group(1)
            })

        return citations

    def _is_factual_claim(self, sentence: str) -> bool:
        """Check if sentence is a factual claim"""
        sentence = sentence.strip()

        if sentence.endswith("?"):
            return False
        if sentence.endswith("!"):
            return False
        if len(sentence.split()) < 3:
            return False

        return True
