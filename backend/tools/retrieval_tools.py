import httpx
import asyncio
from typing import List, Dict
from config import config

class RetrievalTools:
    """Tools for retrieving evidence from web and academic sources"""
    
    def __init__(self):
        self.serpapi_key = config.SERPAPI_KEY
        self.crossref_url = "https://api.crossref.org/works"
        self.semantic_scholar_url = "https://api.semanticscholar.org/graph/v1"
    
    async def search_web(self, query: str, num_results: int = 3) -> List[Dict]:
        """Search general web for evidence"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "engine": "google"
            }
            
            async with httpx.AsyncClient(timeout=config.SEARCH_TIMEOUT) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    'title': item.get('title'),
                    'url': item.get('link'),
                    'snippet': item.get('snippet'),
                    'source': 'web_search'
                })
            
            return results
        
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    async def search_papers(self, query: str, num_results: int = 3) -> List[Dict]:
        """Search academic papers (CrossRef + Semantic Scholar)"""
        results = []
        
        # CrossRef
        try:
            crossref_results = await self._search_crossref(query, num_results)
            results.extend(crossref_results)
        except Exception as e:
            print(f"CrossRef error: {e}")
        
        # Semantic Scholar
        try:
            scholar_results = await self._search_semantic_scholar(query, num_results)
            results.extend(scholar_results)
        except Exception as e:
            print(f"Semantic Scholar error: {e}")
        
        return results[:num_results]
    
    async def _search_crossref(self, query: str, limit: int = 3) -> List[Dict]:
        """Search CrossRef API"""
        try:
            params = {
                'query': query,
                'rows': limit,
                'mailto': config.CROSSREF_EMAIL
            }
            
            async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
                response = await client.get(self.crossref_url, params=params)
                data = response.json()
            
            results = []
            for item in data.get('message', {}).get('items', [])[:limit]:
                results.append({
                    'title': item.get('title', ['']) if isinstance(item.get('title'), list) else item.get('title', ''),
                    'authors': [a.get('family', '') for a in item.get('author', [])],
                    'year': item.get('published-online', {}).get('date-parts', []),
                    'journal': item.get('container-title', ''),
                    'doi': item.get('DOI', ''),
                    'url': item.get('URL', ''),
                    'source': 'crossref'
                })
            
            return results
        except Exception as e:
            print(f"CrossRef error: {e}")
            return []
    
    async def _search_semantic_scholar(self, query: str, limit: int = 3) -> List[Dict]:
        """Search Semantic Scholar API"""
        try:
            url = f"{self.semantic_scholar_url}/paper/search"
            params = {'query': query, 'limit': limit}
            
            headers = {}
            if config.SEMANTIC_SCHOLAR_API_KEY:
                headers['x-api-key'] = config.SEMANTIC_SCHOLAR_API_KEY
            
            async with httpx.AsyncClient(timeout=config.API_TIMEOUT) as client:
                response = await client.get(url, params=params, headers=headers)
                data = response.json()
            
            results = []
            for item in data.get('data', [])[:limit]:
                results.append({
                    'title': item.get('title', ''),
                    'authors': [a.get('name', '') for a in item.get('authors', [])],
                    'year': item.get('year', 0),
                    'venue': item.get('venue', ''),
                    'doi': item.get('externalIds', {}).get('DOI', ''),
                    'url': item.get('url', ''),
                    'source': 'semantic_scholar'
                })
            
            return results
        except Exception as e:
            print(f"Semantic Scholar error: {e}")
            return []
    
    async def check_url(self, url: str) -> Dict:
        """Check if URL is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.head(url, allow_redirects=True)
                status = response.status_code
            
            return {
                'url': url,
                'is_valid': status < 400,
                'status_code': status
            }
        except Exception as e:
            return {
                'url': url,
                'is_valid': False,
                'error': str(e)
            }
    
    async def validate_citation(self, citation: Dict) -> Dict:
        """Validate a citation by searching for it"""
        query = f"{citation.get('author', '')} {citation.get('year', '')}"
        
        # Search for the paper
        results = await self._search_crossref(query, 1)
        
        if results:
            paper = results
            return {
                'citation': citation,
                'found': True,
                'metadata': paper,
                'confidence': 0.9
            }
        
        return {
            'citation': citation,
            'found': False,
            'confidence': 0.1
        }
