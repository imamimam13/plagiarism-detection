import requests

from typing import List, Dict, Any
from app.core.config import settings
from difflib import SequenceMatcher

class PlagiarismService:
    def __init__(self):
        self.searxng_url = settings.SEARXNG_URL.rstrip('/')
        self.enabled = bool(self.searxng_url)

    def _chunk_text(self, text: str, chunk_size=150) -> List[str]:
        """Split text into chunks of approximately chunk_size words"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def _calculate_similarity(self, a: str, b: str) -> float:
        """Calculate generic similarity ratio between two strings"""
        return SequenceMatcher(None, a, b).ratio()

    def check_plagiarism(self, text: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "SearXNG URL not configured"}

        chunks = self._chunk_text(text)
        sources = {}
        total_similarity = 0.0
        
        # Limit chunks to prevent excessive requests for demo
        max_chunks = 5
        checked_chunks = chunks[:max_chunks]
        
        print(f"Checking {len(checked_chunks)} chunks against SearXNG...")

        for chunk in checked_chunks:
            try:
                # Query SearXNG
                params = {
                    "q": chunk[:200], # Search snippet of the chunk
                    "format": "json",
                    "language": "auto"
                }
                resp = requests.get(f"{self.searxng_url}/search", params=params, timeout=10)
                
                if resp.status_code == 200:
                    results = resp.json().get('results', [])
                    
                    # Check top 3 results for similarity
                    chunk_max_sim = 0.0
                    for res in results[:3]:
                        sim = self._calculate_similarity(chunk, res.get('content', ''))
                        if sim > chunk_max_sim:
                            chunk_max_sim = sim
                            
                        # If similarity is high, record source
                        if sim > 0.1: # Threshold for "relevance"
                            url = res.get('url')
                            if url not in sources:
                                sources[url] = {
                                    "title": res.get('title'),
                                    "count": 1,
                                    "max_similarity": sim
                                }
                            else:
                                sources[url]["count"] += 1
                                sources[url]["max_similarity"] = max(sources[url]["max_similarity"], sim)
                    
                    total_similarity += chunk_max_sim
                    
            except Exception as e:
                print(f"Error querying SearXNG: {e}")
                
        # Calculate overall score
        # Normalize: if every chunk has a perfect match, score is 100%
        # This is a naive heuristic
        plagiarism_score = (total_similarity / len(checked_chunks)) * 100 if checked_chunks else 0.0
        
        sorted_sources = sorted(sources.values(), key=lambda x: x['max_similarity'], reverse=True)

        return {
            "plagiarism_score": min(plagiarism_score, 100.0),
            "sources": sorted_sources,
            "checked_chunks": len(checked_chunks),
            "message": "Scan complete"
        }
