import asyncio
from typing import Dict, List
from agents.extraction_agent import ExtractionAgent
from agents.reasoning_agent import ReasoningAgent
from agents.citation_agent import CitationAgent
from agents.risk_scorer import RiskScorer
from tools.retrieval_tools import RetrievalTools
from config import config

class VerificationAgent:
    """Main agent that orchestrates all sub-agents"""
    
    def __init__(self):
        self.extractor = ExtractionAgent()
        self.reasoner = ReasoningAgent()
        self.citation_checker = CitationAgent()
        self.risk_scorer = RiskScorer()
        self.retriever = RetrievalTools()
    
    async def verify(self, 
                    content: str,
                    context: str = "") -> Dict:
        """
        Main verification pipeline
        Returns: {claims, citations, risk_assessment}
        """
        
        # Step 1: Extract claims and citations
        claims = self.extractor.extract_claims(content)
        citations = self.extractor.extract_citations(content)
        
        # Step 2: Verify each claim (in parallel)
        verified_claims = await self._verify_claims_parallel(claims)
        
        # Step 3: Check each citation (in parallel)
        verified_citations = await self._check_citations_parallel(citations)
        
        # Step 4: Calculate overall risk
        risk_assessment = self.risk_scorer.calculate_risk(
            verified_claims, 
            verified_citations
        )

        return {
            'claims': verified_claims,
            'citations': verified_citations,
            'risk_assessment': risk_assessment,
            'metadata': {
                'total_claims': len(claims),
                'total_citations': len(citations),
                'processed_at': self._get_timestamp()
            }
        }
    
    async def _verify_claims_parallel(self, claims: List[Dict]) -> List[Dict]:
        """Verify all claims in parallel"""
        tasks = []
        
        for claim in claims:
            task = self._verify_single_claim(claim)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def _verify_single_claim(self, claim: Dict) -> Dict:
        """Verify a single claim"""
        claim_text = claim['text']
        
        # Retrieve evidence
        evidence = await self._retrieve_evidence(claim_text)
        
        if not evidence:
            return {
                'id': claim['id'],
                'text': claim_text,
                'status': 'UNVERIFIABLE',
                'confidence': 0.0,
                'evidence': [],
                'explanation': 'No evidence found',
                'risk_flag': '🟠 Unverifiable'
            }
        
        # Judge the claim
        reasoning = await self.reasoner.judge_claim(
            claim_text,
            [e.get('snippet') or e.get('title', '') for e in evidence]
        )
        
        return {
            'id': claim['id'],
            'text': claim_text,
            'status': reasoning.get('status', 'UNVERIFIABLE'),
            'confidence': reasoning.get('confidence', 0.0),
            'explanation': reasoning.get('explanation', ''),
            'best_evidence': reasoning.get('best_evidence', ''),
            'evidence_sources': [e.get('source', 'unknown') for e in evidence],
            'risk_flag': self._get_risk_flag(reasoning.get('status', 'UNVERIFIABLE'))
        }
    
    async def _retrieve_evidence(self, claim: str) -> List[Dict]:
        """Retrieve evidence for a claim"""
        evidence = []
        
        try:
            # Search web
            web_results = await self.retriever.search_web(claim, num_results=2)
            evidence.extend(web_results)
            
            # Search papers
            paper_results = await self.retriever.search_papers(claim, num_results=2)
            evidence.extend(paper_results)
        
        except Exception as e:
            print(f"Evidence retrieval error: {e}")
        
        return evidence[:config.MAX_EVIDENCE_PER_CLAIM]
    
    async def _check_citations_parallel(self, citations: List[Dict]) -> List[Dict]:
        """Check all citations in parallel"""
        tasks = []
        
        for citation in citations:
            task = self.citation_checker.check_citation(citation)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    def _get_risk_flag(self, status: str) -> str:
        """Get visual risk flag for claim status"""
        flags = {
            'SUPPORTED': '✅ Supported',
            'CONTRADICTED': '🔴 Contradicted',
            'UNVERIFIABLE': '🟠 Unverifiable'
        }
        return flags.get(status, '❓ Unknown')
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
