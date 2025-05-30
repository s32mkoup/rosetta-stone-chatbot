import requests
import json
import re
from typing import Dict, List, Any, Optional, Tuple
import time
from urllib.parse import quote, unquote
from dataclasses import dataclass

from .tool_registry import BaseTool, ToolMetadata, ToolCategory, ToolComplexity

@dataclass
class WikipediaSearchResult:
    """Structure for Wikipedia search results"""
    title: str
    extract: str
    url: str
    page_id: int
    thumbnail: Optional[str] = None
    coordinates: Optional[Tuple[float, float]] = None
    categories: List[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []

class WikipediaTool(BaseTool):
    """Advanced Wikipedia search and information retrieval tool"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Wikipedia API configuration
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.search_limit = 10
        self.extract_length = 500
        
        # Request configuration
        self.headers = {
            'User-Agent': 'RosettaStoneAgent/1.0 (Educational Research Tool)',
            'Accept': 'application/json'
        }
        self.timeout = 15
        
        # Historical filtering - prioritize historical content
        self.historical_keywords = [
            'ancient', 'history', 'historical', 'civilization', 'empire', 'dynasty',
            'pharaoh', 'egypt', 'ptolemy', 'hieroglyph', 'archaeology', 'artifact',
            'museum', 'discovery', 'excavation', 'inscription', 'monument',
            'temple', 'pyramid', 'tomb', 'papyrus', 'manuscript', 'scroll'
        ]
        
        # Quality scoring weights
        self.quality_weights = {
            'historical_relevance': 0.3,
            'content_length': 0.2,
            'completeness': 0.2,
            'recency': 0.1,
            'reliability_indicators': 0.2
        }
        
        # Performance tracking
        self.search_history = []
        self.failed_queries = []
        
    def get_metadata(self) -> ToolMetadata:
        """Return metadata for this tool"""
        return ToolMetadata(
            name="wikipedia",
            description="Search Wikipedia for comprehensive information about historical figures, events, places, and concepts",
            category=ToolCategory.RESEARCH,
            complexity=ToolComplexity.SIMPLE,
            input_description="Search query (person, place, event, concept)",
            output_description="Detailed information with summaries, key facts, and historical context",
            example_usage="wikipedia('Cleopatra VII') → Biographical information about the last pharaoh of Egypt",
            keywords=[
                'wikipedia', 'encyclopedia', 'search', 'information', 'facts',
                'biography', 'history', 'research', 'knowledge', 'reference'
            ],
            required_params=['query'],
            optional_params=['language', 'sections', 'max_results'],
            execution_time_estimate="fast",
            reliability_score=0.9,
            cost_estimate="free"
        )
    
    def execute(self, query: str, **kwargs) -> str:
        """Execute Wikipedia search and return formatted results"""
        
        # Track search
        search_start = time.time()
        
        try:
            # Optimize query for Wikipedia search
            optimized_query = self._optimize_search_query(query)
            
            # Perform multi-strategy search
            results = self._multi_strategy_search(optimized_query, **kwargs)
            
            if not results:
                # Fallback search with broader terms
                fallback_results = self._fallback_search(query)
                if fallback_results:
                    results = fallback_results
                else:
                    return self._generate_no_results_message(query)
            
            # Rank and select best results
            ranked_results = self._rank_results(results, query)
            
            # Format comprehensive response
            formatted_response = self._format_comprehensive_response(ranked_results, query)
            
            # Track successful search
            search_time = time.time() - search_start
            self._track_search_success(query, len(results), search_time)
            
            return formatted_response
            
        except Exception as e:
            self._track_search_failure(query, str(e))
            return self._generate_error_message(query, str(e))
    
    def _optimize_search_query(self, query: str) -> str:
        """Optimize search query for better Wikipedia results"""
        
        # Clean and normalize query
        cleaned_query = re.sub(r'[^\w\s\-\(\)]', ' ', query)
        cleaned_query = ' '.join(cleaned_query.split())  # Remove extra spaces
        
        # Historical period detection and enhancement
        historical_patterns = {
            r'\b(\d{1,4})\s*(bce?|ce?|bc|ad)\b': r'\1 \2',
            r'\b(ancient|pharaoh|dynasty|empire)\b': lambda m: m.group(0),
            r'\b(egypt|egyptian|ptolemy|cleopatra)\b': lambda m: m.group(0)
        }
        
        enhanced_query = cleaned_query
        for pattern, replacement in historical_patterns.items():
            if callable(replacement):
                enhanced_query = re.sub(pattern, replacement, enhanced_query, flags=re.IGNORECASE)
            else:
                enhanced_query = re.sub(pattern, replacement, enhanced_query, flags=re.IGNORECASE)
        
        # Add disambiguation hints for common historical terms
        disambiguation_hints = {
            'ptolemy': 'ptolemy egypt pharaoh',
            'cleopatra': 'cleopatra vii egypt pharaoh',
            'alexander': 'alexander great macedonia',
            'caesar': 'julius caesar roman emperor',
            'rosetta stone': 'rosetta stone egypt hieroglyphs'
        }
        
        query_lower = enhanced_query.lower()
        for term, hint in disambiguation_hints.items():
            if term in query_lower and hint not in query_lower:
                enhanced_query = f"{enhanced_query} {hint}"
        
        return enhanced_query
    
    def _multi_strategy_search(self, query: str, **kwargs) -> List[WikipediaSearchResult]:
        """Perform search using multiple strategies"""
        
        all_results = []
        
        # Strategy 1: Direct page lookup
        direct_result = self._direct_page_search(query)
        if direct_result:
            all_results.append(direct_result)
        
        # Strategy 2: Full-text search
        search_results = self._fulltext_search(query, limit=5)
        all_results.extend(search_results)
        
        # Strategy 3: Category-based search (for historical topics)
        if self._is_historical_query(query):
            category_results = self._category_based_search(query)
            all_results.extend(category_results)
        
        # Strategy 4: Related articles search
        if len(all_results) > 0:
            related_results = self._find_related_articles(all_results[0].title, limit=2)
            all_results.extend(related_results)
        
        # Remove duplicates
        seen_titles = set()
        unique_results = []
        for result in all_results:
            if result.title not in seen_titles:
                unique_results.append(result)
                seen_titles.add(result.title)
        
        return unique_results
    
    def _direct_page_search(self, query: str) -> Optional[WikipediaSearchResult]:
        """Try to find a page directly by title"""
        
        try:
            # Try exact title match
            url = f"{self.base_url}/page/summary/{quote(query)}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_summary_response(data)
            
            # Try with common variations
            variations = [
                query.title(),
                query.lower(),
                query.replace(' ', '_'),
                query.replace('-', ' ')
            ]
            
            for variation in variations:
                url = f"{self.base_url}/page/summary/{quote(variation)}"
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_summary_response(data)
            
        except Exception as e:
            print(f"Direct search failed: {e}")
        
        return None
    
    def _fulltext_search(self, query: str, limit: int = 5) -> List[WikipediaSearchResult]:
        """Perform full-text search using Wikipedia API"""
        
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': limit,
                'srprop': 'size|wordcount|timestamp|snippet',
                'srenablerewrites': 1
            }
            
            response = requests.get(self.api_url, params=params, 
                                  headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                search_results = data.get('query', {}).get('search', [])
                
                results = []
                for item in search_results:
                    # Get full summary for each result
                    summary_result = self._get_page_summary(item['title'])
                    if summary_result:
                        results.append(summary_result)
                
                return results
            
        except Exception as e:
            print(f"Fulltext search failed: {e}")
        
        return []
    
    def _category_based_search(self, query: str) -> List[WikipediaSearchResult]:
        """Search within historical categories"""
        
        historical_categories = [
            'Category:Ancient Egypt',
            'Category:Ptolemaic dynasty',
            'Category:Egyptian pharaohs',
            'Category:Ancient Egyptian culture',
            'Category:Egyptian hieroglyphs',
            'Category:Archaeological discoveries'
        ]
        
        results = []
        
        try:
            for category in historical_categories[:2]:  # Limit to avoid too many requests
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'categorymembers',
                    'cmtitle': category,
                    'cmlimit': 10,
                    'cmtype': 'page'
                }
                
                response = requests.get(self.api_url, params=params,
                                      headers=self.headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    members = data.get('query', {}).get('categorymembers', [])
                    
                    for member in members:
                        title = member['title']
                        # Check if title is relevant to query
                        if self._is_title_relevant(title, query):
                            summary_result = self._get_page_summary(title)
                            if summary_result:
                                results.append(summary_result)
                                if len(results) >= 3:  # Limit category results
                                    break
                
                if len(results) >= 3:
                    break
        
        except Exception as e:
            print(f"Category search failed: {e}")
        
        return results
    
    def _find_related_articles(self, title: str, limit: int = 2) -> List[WikipediaSearchResult]:
        """Find articles related to a given title"""
        
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'prop': 'links',
                'titles': title,
                'pllimit': limit * 2  # Get more to filter
            }
            
            response = requests.get(self.api_url, params=params,
                                  headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                
                results = []
                for page_id, page_data in pages.items():
                    links = page_data.get('links', [])
                    
                    for link in links[:limit]:
                        link_title = link['title']
                        # Skip non-article links
                        if not link_title.startswith(('Category:', 'Template:', 'File:')):
                            summary_result = self._get_page_summary(link_title)
                            if summary_result:
                                results.append(summary_result)
                                if len(results) >= limit:
                                    break
                    
                    if len(results) >= limit:
                        break
                
                return results
        
        except Exception as e:
            print(f"Related articles search failed: {e}")
        
        return []
    
    def _get_page_summary(self, title: str) -> Optional[WikipediaSearchResult]:
        """Get page summary using REST API"""
        
        try:
            url = f"{self.base_url}/page/summary/{quote(title)}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_summary_response(data)
        
        except Exception as e:
            print(f"Failed to get summary for {title}: {e}")
        
        return None
    
    def _parse_summary_response(self, data: Dict[str, Any]) -> WikipediaSearchResult:
        """Parse Wikipedia summary API response"""
        
        return WikipediaSearchResult(
            title=data.get('title', ''),
            extract=data.get('extract', ''),
            url=data.get('content_urls', {}).get('desktop', {}).get('page', ''),
            page_id=data.get('pageid', 0),
            thumbnail=data.get('thumbnail', {}).get('source') if 'thumbnail' in data else None,
            coordinates=self._extract_coordinates(data),
            categories=[]  # Would need additional API call
        )
    
    def _extract_coordinates(self, data: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Extract coordinates from page data"""
        coordinates = data.get('coordinates')
        if coordinates:
            return (coordinates.get('lat'), coordinates.get('lon'))
        return None
    
    def _rank_results(self, results: List[WikipediaSearchResult], query: str) -> List[WikipediaSearchResult]:
        """Rank search results by relevance and quality"""
        
        scored_results = []
        
        for result in results:
            score = self._calculate_result_score(result, query)
            scored_results.append((result, score))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        return [result for result, score in scored_results]
    
    def _calculate_result_score(self, result: WikipediaSearchResult, query: str) -> float:
        """Calculate relevance score for a search result"""
        
        score = 0.0
        query_lower = query.lower()
        title_lower = result.title.lower()
        extract_lower = result.extract.lower()
        
        # Title relevance (exact match gets highest score)
        if query_lower == title_lower:
            score += 100
        elif query_lower in title_lower:
            score += 50
        elif any(word in title_lower for word in query_lower.split()):
            score += 25
        
        # Content relevance
        query_words = set(query_lower.split())
        title_words = set(title_lower.split())
        extract_words = set(extract_lower.split())
        
        # Word overlap in title
        title_overlap = len(query_words.intersection(title_words))
        score += title_overlap * 10
        
        # Word overlap in extract
        extract_overlap = len(query_words.intersection(extract_words))
        score += extract_overlap * 5
        
        # Historical relevance bonus
        historical_score = sum(1 for keyword in self.historical_keywords 
                             if keyword in title_lower or keyword in extract_lower)
        score += historical_score * self.quality_weights['historical_relevance'] * 20
        
        # Content quality indicators
        if len(result.extract) > 200:
            score += self.quality_weights['content_length'] * 10
        
        if result.thumbnail:
            score += 5  # Has image
        
        if result.coordinates:
            score += 3  # Has location data
        
        return score
    
    def _format_comprehensive_response(self, results: List[WikipediaSearchResult], query: str) -> str:
        """Format search results into comprehensive response"""
        
        if not results:
            return self._generate_no_results_message(query)
        
        # Primary result (highest scored)
        primary = results[0]
        
        # Build response
        response_parts = []
        
        # Main information
        response_parts.append(f"**{primary.title}**")
        response_parts.append(primary.extract)
        
        # Additional context from other results
        if len(results) > 1:
            response_parts.append("\n**Related Information:**")
            
            for result in results[1:3]:  # Include up to 2 additional results
                if result.extract and len(result.extract) > 50:
                    # Get first sentence or first 150 characters
                    summary = result.extract.split('.')[0]
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                    response_parts.append(f"• **{result.title}**: {summary}")
        
        # Historical connections (if applicable)
        historical_connections = self._find_historical_connections(results, query)
        if historical_connections:
            response_parts.append(f"\n**Historical Context:**")
            response_parts.append(historical_connections)
        
        # Source information
        response_parts.append(f"\n**Sources**: Wikipedia")
        if primary.url:
            response_parts.append(f"Primary source: {primary.url}")
        
        return "\n".join(response_parts)
    
    def _find_historical_connections(self, results: List[WikipediaSearchResult], query: str) -> str:
        """Find and format historical connections in the results"""
        
        connections = []
        
        # Look for dates, periods, and historical context
        for result in results:
            text = f"{result.title} {result.extract}".lower()
            
            # Extract dates
            date_patterns = [
                r'\b(\d{1,4})\s*(bce?|ce?|bc|ad)\b',
                r'\b(\d{1,2})(st|nd|rd|th)\s*century\b',
                r'\b(ancient|classical|medieval|modern)\s*(egypt|rome|greece)\b'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        date_ref = ' '.join(match)
                    else:
                        date_ref = match
                    
                    if date_ref and date_ref not in connections:
                        connections.append(date_ref)
        
        if connections:
            unique_connections = list(set(connections))[:3]  # Limit to 3
            return f"Time period: {', '.join(unique_connections)}"
        
        return ""
    
    def _fallback_search(self, query: str) -> List[WikipediaSearchResult]:
        """Fallback search with broader terms"""
        
        # Extract key terms and try broader searches
        key_terms = self._extract_key_terms(query)
        
        for term in key_terms:
            if len(term) > 3:  # Skip very short terms
                results = self._fulltext_search(term, limit=3)
                if results:
                    return results
        
        # Last resort: search for just historical terms
        historical_terms = [term for term in key_terms 
                           if term.lower() in self.historical_keywords]
        
        if historical_terms:
            return self._fulltext_search(' '.join(historical_terms[:2]), limit=2)
        
        return []
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for fallback search"""
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'about', 'tell', 'me'
        }
        
        words = re.findall(r'\b\w+\b', query.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def _is_historical_query(self, query: str) -> bool:
        """Check if query is related to historical topics"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.historical_keywords)
    
    def _is_title_relevant(self, title: str, query: str) -> bool:
        """Check if a title is relevant to the query"""
        title_lower = title.lower()
        query_lower = query.lower()
        
        # Check for direct word matches
        query_words = query_lower.split()
        return any(word in title_lower for word in query_words if len(word) > 2)
    
    def _generate_no_results_message(self, query: str) -> str:
        """Generate message when no results are found"""
        return f"I searched the vast archives of Wikipedia for '{query}', but the sands of knowledge did not reveal what you seek. Perhaps you could rephrase your question, or ask about a related topic?"
    
    def _generate_error_message(self, query: str, error: str) -> str:
        """Generate user-friendly error message"""
        return f"The ancient pathways to Wikipedia's knowledge encountered an obstacle while searching for '{query}'. The scribes report: {error}. Let us try again, perhaps with different words."
    
    def _track_search_success(self, query: str, result_count: int, execution_time: float):
        """Track successful search for analytics"""
        self.search_history.append({
            'query': query,
            'result_count': result_count,
            'execution_time': execution_time,
            'timestamp': time.time(),
            'success': True
        })
        
        # Keep only recent history
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    def _track_search_failure(self, query: str, error: str):
        """Track failed search for analytics"""
        self.failed_queries.append({
            'query': query,
            'error': error,
            'timestamp': time.time()
        })
        
        # Keep only recent failures
        if len(self.failed_queries) > 50:
            self.failed_queries = self.failed_queries[-50:]
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get analytics about search performance"""
        total_searches = len(self.search_history)
        failed_searches = len(self.failed_queries)
        
        if total_searches == 0:
            return {'message': 'No search history available'}
        
        avg_results = sum(search['result_count'] for search in self.search_history) / total_searches
        avg_time = sum(search['execution_time'] for search in self.search_history) / total_searches
        
        return {
            'total_searches': total_searches,
            'failed_searches': failed_searches,
            'success_rate': (total_searches - failed_searches) / total_searches,
            'average_results_per_search': avg_results,
            'average_execution_time': avg_time,
            'most_common_failures': self._get_common_failure_patterns()
        }
    
    def _get_common_failure_patterns(self) -> List[str]:
        """Analyze common failure patterns"""
        if not self.failed_queries:
            return []
        
        # Simple pattern analysis
        error_types = {}
        for failure in self.failed_queries:
            error = failure['error'].lower()
            if 'timeout' in error:
                error_types['timeout'] = error_types.get('timeout', 0) + 1
            elif 'not found' in error:
                error_types['not_found'] = error_types.get('not_found', 0) + 1
            else:
                error_types['other'] = error_types.get('other', 0) + 1
        
        return [f"{error_type}: {count}" for error_type, count in error_types.items()]