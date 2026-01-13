import re
import httpx
from typing import List, Dict
from config import config

class CitationAgent:
    """Validates citations in real-time"""
    
    def __init__(self):
        self.crossref_url = "https://api.crossref.org/works"
    
    async def check_citation(self, citation: Dict) -> Dict:
        """Check a single citation"""
        
        citation_type = citation.get('type', 'unknown')
        
        if citation_type == 'apa':
            return await self._check_apa_citation(citation)
        elif citation_type == 'url':
            return await self._check_url_citation(citation)
        elif citation_type == 'doi':
            return await self._check_doi_citation(citation)
        else:
            return self._unknown_citation(citation)
    
    async def _check_apa_citation(self, citation: Dict) -> Dict:
        """Check APA format citation"""
        author = citation.get('author', '')
        year = citation.get('year', 0)
        
        query = f"{author} {year}"
        
        try:
            params = {
                'query': query,
                'rows': 1,
                'mailto': config.CROSSREF_EMAIL
            }
            
            async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
                response = await client.get(self.crossref_url, params=params)
                data = response.json()
            
            items = data.get('message', {}).get('items', [])
            
            if items:
                paper = items
                return {
                    'citation': citation['text'],
                    'status': 'VALID',
                    'found': True,
                    'metadata': {
                        'title': paper.get('title', ['']) if isinstance(paper.get('title'), list) else paper.get('title', ''),
                        'authors': [a.get('family', '') for a in paper.get('author', [])],
                        'year': paper.get('published-online', {}).get('date-parts', []),
                        'doi': paper.get('DOI', ''),
                        'venue': paper.get('container-title', '')
                    },
                    'issues': []
                }
            else:
                return {
                    'citation': citation['text'],
                    'status': 'INVALID',
                    'found': False,
                    'issues': ['Citation not found in CrossRef database']
                }
        
        except Exception as e:
            return {
                'citation': citation['text'],
                'status': 'UNKNOWN',
                'issues': [f'Error checking citation: {str(e)}']
            }
    
    async def _check_url_citation(self, citation: Dict) -> Dict:
        """Check URL citation"""
        url = citation.get('url', '')
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.head(url, allow_redirects=True)
                status = response.status_code
            
            is_valid = status < 400
            status_text = 'VALID' if is_valid else 'INVALID'
            
            issues = []
            if status >= 400:
                issues.append(f'URL returned status code {status}')
            
            return {
                'citation': citation['text'],
                'status': status_text,
                'url': url,
                'status_code': status,
                'issues': issues
            }
        
        except Exception as e:
            return {
                'citation': citation['text'],
                'status': 'INVALID',
                'url': url,
                'issues': [f'URL unreachable: {str(e)}']
            }
    
    async def _check_doi_citation(self, citation: Dict) -> Dict:
        """Check DOI citation"""
        doi = citation.get('doi', '')
        
        # CrossRef can look up by DOI
        try:
            url = f"https://api.crossref.org/works/{doi}"
            
            async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
                response = await client.get(url)
                data = response.json()
            
            if response.status_code == 200:
                message = data.get('message', {})
                return {
                    'citation': citation['text'],
                    'status': 'VALID',
                    'doi': doi,
                    'metadata': {
                        'title': message.get('title', ''),
                        'doi': message.get('DOI', ''),
                        'year': message.get('published-online', {}).get('date-parts', [])
                    },
                    'issues': []
                }
            else:
                return {
                    'citation': citation['text'],
                    'status': 'INVALID',
                    'doi': doi,
                    'issues': ['DOI not found in CrossRef']
                }
        
        except Exception as e:
            return {
                'citation': citation['text'],
                'status': 'UNKNOWN',
                'doi': doi,
                'issues': [f'Error checking DOI: {str(e)}']
            }
    
    def _unknown_citation(self, citation: Dict) -> Dict:
        """Handle unknown citation type"""
        return {
            'citation': citation['text'],
            'status': 'UNKNOWN',
            'issues': ['Unknown citation format']
        }
