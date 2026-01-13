from typing import Dict, List

class RiskScorer:
    """Calculates hallucination risk scores"""
    
    def __init__(self):
        self.weights = {
            'contradicted_claims': 0.40,
            'unverifiable_claims': 0.30,
            'invalid_citations': 0.20,
            'low_confidence': 0.10
        }
    
    def calculate_risk(self, 
                      claims_results: List[Dict], 
                      citations_results: List[Dict]) -> Dict:
        """Calculate overall hallucination risk"""
        
        if not claims_results:
            return {
                'risk_score': 0,
                'risk_level': 'LOW',
                'factors': [],
                'recommendations': []
            }
        
        # Count claim statuses
        total_claims = len(claims_results)
        contradicted = sum(1 for c in claims_results if c['status'] == 'CONTRADICTED')
        unverifiable = sum(1 for c in claims_results if c['status'] == 'UNVERIFIABLE')
        low_conf = sum(1 for c in claims_results if c.get('confidence', 1.0) < 0.6)
        
        # Count citation issues
        invalid_cits = sum(1 for c in citations_results if c['status'] == 'INVALID')
        total_cits = len(citations_results) if citations_results else 1
        
        # Calculate weighted risk
        risk_score = 0
        
        if total_claims > 0:
            risk_score += (contradicted / total_claims) * self.weights['contradicted_claims'] * 100
            risk_score += (unverifiable / total_claims) * self.weights['unverifiable_claims'] * 100
            risk_score += (low_conf / total_claims) * self.weights['low_confidence'] * 100
        
        if total_cits > 0:
            risk_score += (invalid_cits / total_cits) * self.weights['invalid_citations'] * 100
        
        risk_score = min(100, max(0, risk_score))
        risk_level = 'HIGH' if risk_score >= 60 else 'MEDIUM' if risk_score >= 30 else 'LOW'
        
        # Identify factors
        factors = []
        if contradicted > 0:
            factors.append(f"🔴 {contradicted} contradicted claims")
        if unverifiable > 0:
            factors.append(f"🟠 {unverifiable} unverifiable claims")
        if invalid_cits > 0:
            factors.append(f"🔗 {invalid_cits} invalid citations")
        if low_conf > 0:
            factors.append(f"⚠️ {low_conf} low confidence claims")
        
        if not factors:
            factors.append("✅ No major issues detected")
        
        # Recommendations
        recommendations = []
        if risk_level == 'HIGH':
            recommendations.append("🚨 HIGH RISK: Extensive review required")
            recommendations.append("Do not publish without fact-checking")
        elif risk_level == 'MEDIUM':
            recommendations.append("⚠️ MEDIUM RISK: Review problematic claims")
        else:
            recommendations.append("✅ LOW RISK: Content appears reliable")
        
        if contradicted > 0:
            recommendations.append(f"Remove or revise {contradicted} contradicted claims")
        
        if invalid_cits > 0:
            recommendations.append(f"Verify or replace {invalid_cits} invalid citations")
        
        return {
            'risk_score': round(risk_score, 1),
            'risk_level': risk_level,
            'factors': factors,
            'recommendations': recommendations,
            'breakdown': {
                'contradicted_claims': contradicted,
                'unverifiable_claims': unverifiable,
                'invalid_citations': invalid_cits,
                'low_confidence_claims': low_conf
            }
        }
