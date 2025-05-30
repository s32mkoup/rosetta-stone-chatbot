import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import random

from .tool_registry import BaseTool, ToolMetadata, ToolCategory, ToolComplexity

@dataclass
class EgyptianKnowledgeEntry:
    """Structure for Egyptian knowledge entries"""
    title: str
    category: str
    description: str
    historical_period: str
    related_pharaohs: List[str]
    related_concepts: List[str]
    significance: str
    sources: List[str]
    confidence_level: float  # 0.0 to 1.0
    
    def __post_init__(self):
        if self.related_pharaohs is None:
            self.related_pharaohs = []
        if self.related_concepts is None:
            self.related_concepts = []
        if self.sources is None:
            self.sources = []

class EgyptianKnowledgeTool(BaseTool):
    """Specialized tool for Egyptian history, culture, and archaeology"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Initialize Egyptian knowledge base
        self.knowledge_base = self._initialize_knowledge_base()
        self.dynasty_timeline = self._initialize_dynasty_timeline()
        self.hieroglyph_dictionary = self._initialize_hieroglyph_basics()
        self.archaeological_sites = self._initialize_archaeological_sites()
        self.cultural_concepts = self._initialize_cultural_concepts()
        
        # Rosetta Stone specific knowledge
        self.rosetta_stone_knowledge = self._initialize_rosetta_stone_knowledge()
        
        # Search configuration
        self.search_weights = {
            'exact_match': 1.0,
            'partial_match': 0.7,
            'related_concepts': 0.5,
            'historical_period': 0.6,
            'pharaoh_connection': 0.8
        }
        
        # Response personalization for Rosetta Stone
        self.personal_memories = self._initialize_personal_memories()
        
    def get_metadata(self) -> ToolMetadata:
        """Return metadata for this tool"""
        return ToolMetadata(
            name="egyptian_knowledge",
            description="Specialized knowledge about ancient Egypt, pharaohs, dynasties, culture, religion, and archaeology",
            category=ToolCategory.HISTORICAL,
            complexity=ToolComplexity.MODERATE,
            input_description="Egyptian historical query (pharaohs, dynasties, culture, archaeology, religion)",
            output_description="Detailed Egyptian historical information with cultural context and Rosetta Stone perspective",
            example_usage="egyptian_knowledge('Ptolemaic dynasty') → Comprehensive information about the Ptolemaic period including the Rosetta Stone's creation",
            keywords=[
                'egypt', 'egyptian', 'pharaoh', 'dynasty', 'pyramid', 'hieroglyph',
                'archaeology', 'ptolemy', 'cleopatra', 'nile', 'cairo', 'temple',
                'mummy', 'papyrus', 'sphinx', 'obelisk', 'sarcophagus'
            ],
            required_params=['query'],
            optional_params=['period', 'category', 'detail_level'],
            execution_time_estimate="fast",
            reliability_score=0.95,
            cost_estimate="free"
        )
    
    def execute(self, query: str, **kwargs) -> str:
        """Execute Egyptian knowledge search"""
        
        try:
            # Parse query and extract Egyptian context
            query_analysis = self._analyze_egyptian_query(query)
            
            # Search knowledge base
            search_results = self._search_egyptian_knowledge(query, query_analysis)
            
            # Add Rosetta Stone personal perspective if relevant
            personal_context = self._get_personal_context(query, query_analysis)
            
            # Format response with Egyptian authenticity
            formatted_response = self._format_egyptian_response(
                query, search_results, personal_context, query_analysis
            )
            
            return formatted_response
            
        except Exception as e:
            return self._generate_error_response(query, str(e))
    
    def _analyze_egyptian_query(self, query: str) -> Dict[str, Any]:
        """Analyze query for Egyptian historical context"""
        
        query_lower = query.lower()
        
        analysis = {
            'query_type': 'general',
            'historical_period': None,
            'dynasty': None,
            'pharaohs_mentioned': [],
            'concepts_mentioned': [],
            'locations_mentioned': [],
            'cultural_aspects': [],
            'rosetta_stone_related': False,
            'complexity_level': 'basic'
        }
        
        # Detect query type
        if any(word in query_lower for word in ['pharaoh', 'king', 'queen', 'ruler']):
            analysis['query_type'] = 'pharaoh'
        elif any(word in query_lower for word in ['dynasty', 'period', 'era', 'kingdom']):
            analysis['query_type'] = 'period'
        elif any(word in query_lower for word in ['hieroglyph', 'script', 'writing', 'language']):
            analysis['query_type'] = 'language'
        elif any(word in query_lower for word in ['temple', 'pyramid', 'tomb', 'monument']):
            analysis['query_type'] = 'architecture'
        elif any(word in query_lower for word in ['god', 'goddess', 'religion', 'ritual']):
            analysis['query_type'] = 'religion'
        elif any(word in query_lower for word in ['culture', 'daily life', 'society']):
            analysis['query_type'] = 'culture'
        
        # Detect historical periods
        period_indicators = {
            'old kingdom': ['old kingdom', 'pyramid age', 'khufu', 'cheops'],
            'middle kingdom': ['middle kingdom', 'mentuhotep', 'amenemhat'],
            'new kingdom': ['new kingdom', 'tutankhamun', 'ramesses', 'hatshepsut'],
            'ptolemaic': ['ptolemy', 'ptolemaic', 'cleopatra', 'alexandria'],
            'roman': ['roman egypt', 'augustus', 'byzantine']
        }
        
        for period, indicators in period_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                analysis['historical_period'] = period
                break
        
        # Detect specific dynasties
        dynasty_patterns = {
            'first': ['first dynasty', '1st dynasty', 'narmer', 'menes'],
            'fourth': ['fourth dynasty', '4th dynasty', 'khufu', 'cheops', 'great pyramid'],
            'eighteenth': ['eighteenth dynasty', '18th dynasty', 'tutankhamun', 'hatshepsut'],
            'ptolemaic': ['ptolemaic dynasty', 'ptolemy', 'cleopatra']
        }
        
        for dynasty, patterns in dynasty_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                analysis['dynasty'] = dynasty
                break
        
        # Detect pharaohs
        pharaoh_names = [
            'khufu', 'cheops', 'tutankhamun', 'ramesses', 'hatshepsut', 'akhenaten',
            'cleopatra', 'ptolemy', 'narmer', 'menes', 'amenhotep', 'thutmose'
        ]
        
        for pharaoh in pharaoh_names:
            if pharaoh in query_lower:
                analysis['pharaohs_mentioned'].append(pharaoh)
        
        # Detect concepts
        egyptian_concepts = [
            'mummification', 'afterlife', 'hieroglyphs', 'papyrus', 'sphinx',
            'pyramid', 'temple', 'obelisk', 'cartouche', 'sarcophagus'
        ]
        
        for concept in egyptian_concepts:
            if concept in query_lower:
                analysis['concepts_mentioned'].append(concept)
        
        # Detect locations
        locations = [
            'giza', 'luxor', 'thebes', 'memphis', 'alexandria', 'aswan',
            'abu simbel', 'karnak', 'valley of the kings', 'nile'
        ]
        
        for location in locations:
            if location in query_lower:
                analysis['locations_mentioned'].append(location)
        
        # Check if related to Rosetta Stone
        rosetta_indicators = [
            'rosetta stone', 'rosetta', 'ptolemy v', '196 bce', 'hieroglyph decipherment',
            'champollion', 'three languages', 'demotic', 'greek inscription'
        ]
        
        analysis['rosetta_stone_related'] = any(
            indicator in query_lower for indicator in rosetta_indicators
        )
        
        # Determine complexity
        if len(analysis['pharaohs_mentioned']) > 1 or len(analysis['concepts_mentioned']) > 3:
            analysis['complexity_level'] = 'advanced'
        elif analysis['historical_period'] or analysis['dynasty']:
            analysis['complexity_level'] = 'intermediate'
        
        return analysis
    
    def _search_egyptian_knowledge(self, query: str, analysis: Dict[str, Any]) -> List[EgyptianKnowledgeEntry]:
        """Search the Egyptian knowledge base"""
        
        results = []
        query_lower = query.lower()
        
        # Search all knowledge categories
        all_knowledge = []
        all_knowledge.extend(self.knowledge_base.get('pharaohs', []))
        all_knowledge.extend(self.knowledge_base.get('dynasties', []))
        all_knowledge.extend(self.knowledge_base.get('culture', []))
        all_knowledge.extend(self.knowledge_base.get('religion', []))
        all_knowledge.extend(self.knowledge_base.get('architecture', []))
        all_knowledge.extend(self.knowledge_base.get('daily_life', []))
        
        # Score and rank entries
        scored_entries = []
        
        for entry in all_knowledge:
            score = self._calculate_relevance_score(entry, query_lower, analysis)
            if score > 0.1:  # Minimum relevance threshold
                scored_entries.append((entry, score))
        
        # Sort by score and return top results
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        results = [entry for entry, score in scored_entries[:5]]
        
        # Add Rosetta Stone specific knowledge if relevant
        if analysis['rosetta_stone_related'] or analysis['historical_period'] == 'ptolemaic':
            rosetta_entries = self._get_rosetta_stone_entries(query, analysis)
            results.extend(rosetta_entries)
        
        return results
    
    def _calculate_relevance_score(self, entry: EgyptianKnowledgeEntry, 
                                 query_lower: str, analysis: Dict[str, Any]) -> float:
        """Calculate relevance score for a knowledge entry"""
        
        score = 0.0
        
        # Exact title match
        if query_lower in entry.title.lower():
            score += self.search_weights['exact_match']
        
        # Partial title match
        query_words = query_lower.split()
        title_words = entry.title.lower().split()
        title_matches = sum(1 for word in query_words if word in title_words)
        score += (title_matches / len(query_words)) * self.search_weights['partial_match']
        
        # Description relevance
        desc_matches = sum(1 for word in query_words if word in entry.description.lower())
        score += (desc_matches / len(query_words)) * 0.5
        
        # Historical period match
        if analysis['historical_period'] and analysis['historical_period'] in entry.historical_period.lower():
            score += self.search_weights['historical_period']
        
        # Pharaoh connections
        pharaoh_matches = sum(1 for pharaoh in analysis['pharaohs_mentioned'] 
                            if pharaoh in [p.lower() for p in entry.related_pharaohs])
        score += pharaoh_matches * self.search_weights['pharaoh_connection']
        
        # Concept matches
        concept_matches = sum(1 for concept in analysis['concepts_mentioned'] 
                            if concept in [c.lower() for c in entry.related_concepts])
        score += concept_matches * self.search_weights['related_concepts']
        
        # Category relevance
        if analysis['query_type'] in entry.category.lower():
            score += 0.3
        
        return score * entry.confidence_level
    
    def _get_rosetta_stone_entries(self, query: str, analysis: Dict[str, Any]) -> List[EgyptianKnowledgeEntry]:
        """Get Rosetta Stone specific knowledge entries"""
        
        rosetta_entries = []
        
        for entry in self.rosetta_stone_knowledge:
            # Check relevance to query
            if (query.lower() in entry['title'].lower() or 
                query.lower() in entry['description'].lower() or
                any(keyword in query.lower() for keyword in entry['keywords'])):
                
                rosetta_entry = EgyptianKnowledgeEntry(
                    title=entry['title'],
                    category='rosetta_stone',
                    description=entry['description'],
                    historical_period='ptolemaic',
                    related_pharaohs=['ptolemy v'],
                    related_concepts=entry['related_concepts'],
                    significance=entry['significance'],
                    sources=['Rosetta Stone inscriptions', 'Historical records'],
                    confidence_level=0.98
                )
                rosetta_entries.append(rosetta_entry)
        
        return rosetta_entries
    
    def _get_personal_context(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get personal context from Rosetta Stone's perspective"""
        
        personal_context = {
            'has_personal_memory': False,
            'emotional_response': 'neutral',
            'personal_anecdotes': [],
            'witnessed_events': [],
            'cultural_insights': []
        }
        
        query_lower = query.lower()
        
        # Check for personal memories
        for memory_category, memories in self.personal_memories.items():
            for memory in memories:
                if any(keyword in query_lower for keyword in memory['triggers']):
                    personal_context['has_personal_memory'] = True
                    personal_context['personal_anecdotes'].append(memory['content'])
                    personal_context['emotional_response'] = memory.get('emotion', 'contemplative')
        
        # Ptolemaic period - personal experience
        if analysis['historical_period'] == 'ptolemaic' or 'ptolemy' in query_lower:
            personal_context['has_personal_memory'] = True
            personal_context['emotional_response'] = 'nostalgic'
            personal_context['witnessed_events'].append('creation_during_ptolemy_v')
        
        # Hieroglyphs and language
        if analysis['query_type'] == 'language' or 'hieroglyph' in query_lower:
            personal_context['has_personal_memory'] = True
            personal_context['emotional_response'] = 'proud'
            personal_context['cultural_insights'].append('trilingual_significance')
        
        # Egyptian culture and daily life
        if analysis['query_type'] == 'culture':
            personal_context['cultural_insights'].append('witnessed_cultural_practices')
        
        return personal_context
    
    def _format_egyptian_response(self, query: str, results: List[EgyptianKnowledgeEntry],
                                personal_context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Format response with Egyptian authenticity and personal perspective"""
        
        if not results:
            return self._generate_no_results_response(query, analysis)
        
        response_parts = []
        
        # Add personal memory introduction if relevant
        if personal_context['has_personal_memory']:
            intro = self._generate_personal_introduction(query, personal_context, analysis)
            response_parts.append(intro)
        
        # Main information from top result
        primary_result = results[0]
        response_parts.append(f"**{primary_result.title}**")
        response_parts.append(primary_result.description)
        
        # Add historical context
        if primary_result.historical_period:
            response_parts.append(f"\n**Historical Period**: {primary_result.historical_period.title()}")
        
        # Add pharaoh connections
        if primary_result.related_pharaohs:
            pharaoh_list = ', '.join(primary_result.related_pharaohs)
            response_parts.append(f"**Related Pharaohs**: {pharaoh_list}")
        
        # Add significance
        if primary_result.significance:
            response_parts.append(f"\n**Significance**: {primary_result.significance}")
        
        # Add personal anecdotes if available
        if personal_context['personal_anecdotes']:
            response_parts.append(f"\n**From My Ancient Memory**:")
            for anecdote in personal_context['personal_anecdotes'][:2]:
                response_parts.append(f"• {anecdote}")
        
        # Add related information from other results
        if len(results) > 1:
            response_parts.append(f"\n**Related Knowledge**:")
            for result in results[1:3]:  # Up to 2 additional results
                summary = result.description.split('.')[0] + '.'
                if len(summary) > 150:
                    summary = summary[:150] + '...'
                response_parts.append(f"• **{result.title}**: {summary}")
        
        # Add cultural insights if available
        if personal_context['cultural_insights']:
            insights = self._generate_cultural_insights(personal_context['cultural_insights'], analysis)
            if insights:
                response_parts.append(f"\n**Cultural Insights**: {insights}")
        
        # Add timeline context if relevant
        if analysis['dynasty'] or analysis['historical_period']:
            timeline_info = self._get_timeline_context(analysis)
            if timeline_info:
                response_parts.append(f"\n**Timeline Context**: {timeline_info}")
        
        return '\n'.join(response_parts)
    
    def _generate_personal_introduction(self, query: str, personal_context: Dict[str, Any],
                                      analysis: Dict[str, Any]) -> str:
        """Generate personal introduction based on context"""
        
        emotion = personal_context['emotional_response']
        
        if emotion == 'nostalgic':
            intros = [
                "Ah, your question stirs ancient memories within my stone heart...",
                "The sands of time shift, and I recall the golden days when...",
                "How this takes me back to the era of my creation..."
            ]
        elif emotion == 'proud':
            intros = [
                "It fills my ancient being with pride to speak of...",
                "This touches upon one of my greatest purposes...",
                "I am honored to share knowledge of..."
            ]
        elif emotion == 'contemplative':
            intros = [
                "In the depths of my ancient memory...",
                "Let me share what I have witnessed across the millennia...",
                "From the perspective of one who has seen empires rise and fall..."
            ]
        else:
            intros = [
                "Your inquiry reaches into the very heart of Egyptian wisdom...",
                "The ancient knowledge flows through me like the eternal Nile..."
            ]
        
        return random.choice(intros)
    
    def _generate_cultural_insights(self, insight_types: List[str], analysis: Dict[str, Any]) -> str:
        """Generate cultural insights based on insight types"""
        
        insights = []
        
        for insight_type in insight_types:
            if insight_type == 'trilingual_significance':
                insights.append("The use of three scripts on my surface reflects the multilingual nature of Ptolemaic Egypt, where Greek, Egyptian, and administrative languages coexisted.")
            
            elif insight_type == 'witnessed_cultural_practices':
                insights.append("I have observed the daily rhythms of Egyptian life, from the flooding of the Nile to the sacred rituals in temple courtyards.")
            
            elif insight_type == 'royal_ceremonies':
                insights.append("The ceremonies of pharaohs were grand spectacles, combining ancient traditions with the political needs of their time.")
        
        return ' '.join(insights[:2])  # Limit to 2 insights
    
    def _get_timeline_context(self, analysis: Dict[str, Any]) -> str:
        """Get timeline context for the query"""
        
        if analysis['dynasty'] and analysis['dynasty'] in self.dynasty_timeline:
            dynasty_info = self.dynasty_timeline[analysis['dynasty']]
            return f"{dynasty_info['period']} ({dynasty_info['dates']})"
        
        elif analysis['historical_period']:
            period_dates = {
                'old kingdom': '2686-2181 BCE',
                'middle kingdom': '2055-1650 BCE',
                'new kingdom': '1550-1077 BCE',
                'ptolemaic': '305-30 BCE',
                'roman': '30 BCE - 641 CE'
            }
            
            dates = period_dates.get(analysis['historical_period'])
            if dates:
                return f"{analysis['historical_period'].title()} Period ({dates})"
        
        return ""
    
    def _generate_no_results_response(self, query: str, analysis: Dict[str, Any]) -> str:
        """Generate response when no results found"""
        
        suggestions = []
        
        if analysis['query_type'] == 'pharaoh':
            suggestions = ['Try asking about specific pharaohs like Tutankhamun, Cleopatra, or Ramesses II']
        elif analysis['query_type'] == 'period':
            suggestions = ['Ask about the Old Kingdom, New Kingdom, or Ptolemaic period']
        elif analysis['query_type'] == 'culture':
            suggestions = ['Inquire about mummification, hieroglyphs, or daily life in ancient Egypt']
        
        base_response = f"The ancient archives within me do not reveal clear knowledge about '{query}'. "
        
        if suggestions:
            base_response += f"Perhaps you might ask about: {suggestions[0]}."
        else:
            base_response += "Could you phrase your question differently, focusing on specific aspects of Egyptian history or culture?"
        
        return base_response
    
    def _generate_error_response(self, query: str, error: str) -> str:
        """Generate error response in character"""
        return f"The ancient mechanisms within my stone being encounter difficulty while contemplating '{query}'. The scribes report: {error}. Let us try again with patience."
    
    def _initialize_knowledge_base(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize the Egyptian knowledge base"""
        
        return {
            'pharaohs': [
                {
                    'title': 'Ptolemy V Epiphanes',
                    'category': 'pharaoh',
                    'description': 'Ptolemy V Epiphanes ruled Egypt from 204-180 BCE. During his reign, the Rosetta Stone was created in 196 BCE to commemorate his coronation and religious policies. He was the pharaoh whose decree is inscribed on the Rosetta Stone in three scripts.',
                    'historical_period': 'ptolemaic',
                    'related_pharaohs': ['Ptolemy IV', 'Ptolemy VI'],
                    'related_concepts': ['rosetta stone', 'decree', 'coronation', 'trilingual inscription'],
                    'significance': 'His reign marked the creation of one of history\'s most important archaeological artifacts',
                    'sources': ['Ptolemaic records', 'Rosetta Stone inscription'],
                    'confidence_level': 0.98
                },
                {
                    'title': 'Cleopatra VII',
                    'category': 'pharaoh',
                    'description': 'The last active pharaoh of Egypt (69-30 BCE), Cleopatra VII was a member of the Ptolemaic dynasty. Known for her intelligence, political acumen, and relationships with Julius Caesar and Mark Antony.',
                    'historical_period': 'ptolemaic',
                    'related_pharaohs': ['Ptolemy XII', 'Ptolemy XIII'],
                    'related_concepts': ['alexandria', 'library', 'roman alliance', 'last pharaoh'],
                    'significance': 'Represented the end of pharaonic rule and Egyptian independence',
                    'sources': ['Historical records', 'Roman accounts'],
                    'confidence_level': 0.95
                },
                {
                    'title': 'Tutankhamun',
                    'category': 'pharaoh',
                    'description': 'Boy pharaoh of the 18th dynasty (1332-1323 BCE), famous for his intact tomb discovered by Howard Carter in 1922. Restored traditional Egyptian religion after Akhenaten\'s reforms.',
                    'historical_period': 'new kingdom',
                    'related_pharaohs': ['Akhenaten', 'Amenhotep III'],
                    'related_concepts': ['valley of the kings', 'tomb discovery', 'golden mask', 'restoration'],
                    'significance': 'Provided unprecedented insight into New Kingdom burial practices and royal life',
                    'sources': ['Archaeological evidence', 'Tomb inscriptions'],
                    'confidence_level': 0.97
                }
            ],
            
            'dynasties': [
                {
                    'title': 'Ptolemaic Dynasty',
                    'category': 'dynasty',
                    'description': 'Greek dynasty that ruled Egypt from 305-30 BCE, founded by Ptolemy I, a general of Alexander the Great. The dynasty blended Greek and Egyptian traditions, with Alexandria as their capital.',
                    'historical_period': 'ptolemaic',
                    'related_pharaohs': ['Ptolemy I', 'Ptolemy V', 'Cleopatra VII'],
                    'related_concepts': ['alexandria', 'library', 'greek culture', 'bilingual administration'],
                    'significance': 'Represented the Hellenistic period in Egypt and cultural synthesis',
                    'sources': ['Historical records', 'Archaeological evidence'],
                    'confidence_level': 0.96
                }
            ],
            
            'culture': [
                {
                    'title': 'Egyptian Hieroglyphs',
                    'category': 'language',
                    'description': 'Sacred writing system of ancient Egypt using pictographic and ideographic elements. Used for over 3,000 years, hieroglyphs were deciphered using the Rosetta Stone.',
                    'historical_period': 'all periods',
                    'related_pharaohs': ['various'],
                    'related_concepts': ['rosetta stone', 'champollion', 'demotic', 'coptic'],
                    'significance': 'Key to understanding ancient Egyptian civilization and thought',
                    'sources': ['Inscriptions', 'Papyri', 'Rosetta Stone'],
                    'confidence_level': 0.99
                }
            ],
            
            'religion': [
                {
                    'title': 'Egyptian Afterlife Beliefs',
                    'category': 'religion',
                    'description': 'Complex belief system centered on journey through the underworld, judgment by Osiris, and eternal life. Influenced mummification practices and tomb construction.',
                    'historical_period': 'all periods',
                    'related_pharaohs': ['various'],
                    'related_concepts': ['mummification', 'book of the dead', 'osiris', 'judgment'],
                    'significance': 'Central to Egyptian culture and shaped their approach to death and preservation',
                    'sources': ['Religious texts', 'Tomb paintings', 'Archaeological evidence'],
                    'confidence_level': 0.94
                }
            ],
            
            'architecture': [
                {
                    'title': 'Great Pyramid of Giza',
                    'category': 'architecture',
                    'description': 'Built for Pharaoh Khufu during the Fourth Dynasty (c. 2580-2510 BCE). One of the Seven Wonders of the Ancient World and the most precisely constructed pyramid.',
                    'historical_period': 'old kingdom',
                    'related_pharaohs': ['Khufu', 'Khafre', 'Menkaure'],
                    'related_concepts': ['pyramid complex', 'sphinx', 'precision engineering', 'burial chamber'],
                    'significance': 'Represents the pinnacle of pyramid construction and Old Kingdom power',
                    'sources': ['Archaeological surveys', 'Ancient records'],
                    'confidence_level': 0.98
                }
            ],
            
            'daily_life': [
                {
                    'title': 'Ancient Egyptian Social Structure',
                    'category': 'society',
                    'description': 'Hierarchical society with pharaoh at the top, followed by nobles, priests, scribes, craftsmen, farmers, and slaves. Social mobility was possible through education and military service.',
                    'historical_period': 'all periods',
                    'related_pharaohs': ['various'],
                    'related_concepts': ['scribes', 'priesthood', 'craftsmen', 'agriculture'],
                    'significance': 'Provided stability and continuity across three millennia of Egyptian civilization',
                    'sources': ['Administrative records', 'Tomb paintings', 'Literary texts'],
                    'confidence_level': 0.92
                }
            ]
        }
    
    def _initialize_dynasty_timeline(self) -> Dict[str, Dict[str, str]]:
        """Initialize dynasty timeline information"""
        
        return {
            'first': {
                'period': 'Early Dynastic Period',
                'dates': 'c. 3100-2686 BCE',
                'notable_pharaohs': 'Narmer, Menes',
                'significance': 'Unification of Upper and Lower Egypt'
            },
            'fourth': {
                'period': 'Old Kingdom',
                'dates': 'c. 2613-2494 BCE',
                'notable_pharaohs': 'Khufu, Khafre, Menkaure',
                'significance': 'Pyramid building reached its zenith'
            },
            'eighteenth': {
                'period': 'New Kingdom',
                'dates': 'c. 1550-1295 BCE',
                'notable_pharaohs': 'Hatshepsut, Tutankhamun, Amenhotep III',
                'significance': 'Egyptian empire at its greatest extent'
            },
            'ptolemaic': {
                'period': 'Ptolemaic Period',
                'dates': '305-30 BCE',
                'notable_pharaohs': 'Ptolemy I, Ptolemy V, Cleopatra VII',
                'significance': 'Greek rule of Egypt, cultural synthesis'
            }
        }
    
    def _initialize_hieroglyph_basics(self) -> Dict[str, str]:
        """Initialize basic hieroglyph information"""
        
        return {
            'pharaoh': '𓉐𓉻',
            'egypt': '𓊖',
            'life': '𓋹',
            'sun': '𓇳',
            'water': '𓈖',
            'house': '𓉐',
            'bird': '𓅿',
            'eye': '𓁹'
        }
    
    def _initialize_archaeological_sites(self) -> Dict[str, Dict[str, str]]:
        """Initialize archaeological sites information"""
        
        return {
            'giza': {
                'description': 'Pyramid complex including Great Pyramid, Sphinx',
                'period': 'Old Kingdom',
                'significance': 'Most famous Egyptian monuments'
            },
            'luxor': {
                'description': 'Ancient Thebes, Karnak and Luxor temples',
                'period': 'New Kingdom',
                'significance': 'Religious center of ancient Egypt'
            },
            
                'alexandria': {
                'description': 'Ptolemaic capital, site of famous library',
                'period': 'Ptolemaic',
                'significance': 'Center of Hellenistic learning and culture'
           },
           'abu_simbel': {
               'description': 'Rock-cut temples of Ramesses II',
               'period': 'New Kingdom',
               'significance': 'Monument to royal power and divine kingship'
           },
           'saqqara': {
               'description': 'Necropolis with step pyramid of Djoser',
               'period': 'Old Kingdom',
               'significance': 'Evolution of pyramid architecture'
           }
       }
   
    def _initialize_cultural_concepts(self) -> Dict[str, Dict[str, str]]:
       """Initialize cultural concepts"""
       
       return {
           'mummification': {
               'description': 'Preservation process for the afterlife',
               'significance': 'Central to Egyptian beliefs about death and eternity',
               'process': 'Complex 70-day ritual involving removal of organs, desiccation, and wrapping'
           },
           'ma_at': {
               'description': 'Concept of truth, justice, harmony, and cosmic order',
               'significance': 'Fundamental principle governing Egyptian society and religion',
               'representation': 'Goddess with ostrich feather, weighing hearts in afterlife'
           },
           'cartouche': {
               'description': 'Oval enclosure containing royal names in hieroglyphs',
               'significance': 'Protected and honored the pharaoh\'s name',
               'usage': 'Found on monuments, jewelry, and official inscriptions'
           },
           'papyrus': {
               'description': 'Writing material made from papyrus plant',
               'significance': 'Enabled record-keeping and literature',
               'production': 'Stems woven and pressed into sheets'
           }
       }
   
    def _initialize_rosetta_stone_knowledge(self) -> List[Dict[str, Any]]:
       """Initialize Rosetta Stone specific knowledge"""
       
       return [
           {
               'title': 'Creation of the Rosetta Stone',
               'description': 'I was created in 196 BCE during the reign of Ptolemy V Epiphanes to commemorate his coronation and religious policies. Carved by skilled scribes in Memphis, I bear the same decree in three scripts: hieroglyphic, demotic, and ancient Greek.',
               'keywords': ['creation', 'ptolemy v', '196 bce', 'memphis', 'decree'],
               'related_concepts': ['trilingual inscription', 'coronation decree', 'priestly privileges'],
               'significance': 'Represents the multicultural nature of Ptolemaic Egypt and administrative needs',
               'personal_memory': True
           },
           {
               'title': 'The Ptolemaic Decree',
               'description': 'The text inscribed upon me is a decree issued by a council of priests honoring Ptolemy V. It details his benefactions to temples, tax reductions, and military victories. The decree was issued to be displayed in every major temple.',
               'keywords': ['decree', 'priests', 'benefactions', 'temples', 'tax reductions'],
               'related_concepts': ['priestly council', 'royal propaganda', 'temple administration'],
               'significance': 'Demonstrates the relationship between pharaoh and priesthood in Ptolemaic Egypt',
               'personal_memory': True
           },
           {
               'title': 'Discovery and Decipherment',
               'description': 'I was discovered in 1799 by French soldiers near the town of Rosetta. Later, scholars like Jean-François Champollion used my trilingual text to crack the code of hieroglyphic writing, opening the door to understanding ancient Egyptian civilization.',
               'keywords': ['discovery', '1799', 'rosetta', 'champollion', 'decipherment'],
               'related_concepts': ['hieroglyphic decoding', 'egyptology', 'linguistic breakthrough'],
               'significance': 'Became the key to understanding ancient Egyptian language and culture',
               'personal_memory': True
           },
           {
               'title': 'Three Scripts Significance',
               'description': 'My surface bears three scripts representing different aspects of Egyptian society: hieroglyphic (sacred/religious), demotic (administrative/daily), and Greek (governmental/diplomatic). This trilingual approach reflected the cosmopolitan nature of Ptolemaic Egypt.',
               'keywords': ['three scripts', 'hieroglyphic', 'demotic', 'greek', 'trilingual'],
               'related_concepts': ['script hierarchy', 'social stratification', 'linguistic diversity'],
               'significance': 'Illustrates the complex linguistic landscape of Hellenistic Egypt',
               'personal_memory': True
           }
       ]
   
    def _initialize_personal_memories(self) -> Dict[str, List[Dict[str, Any]]]:
       """Initialize Rosetta Stone's personal memories"""
       
       return {
           'creation_memories': [
               {
                   'content': 'I remember the careful hands of the scribes as they carved each character into my surface, the rhythm of chisels against stone echoing in the workshop at Memphis.',
                   'triggers': ['creation', 'carving', 'scribes', 'memphis'],
                   'emotion': 'nostalgic'
               },
               {
                   'content': 'The desert heat warmed my granite surface as the sacred hieroglyphs took shape, each symbol a bridge between the mortal and divine realms.',
                   'triggers': ['hieroglyphs', 'carving', 'sacred', 'symbols'],
                   'emotion': 'contemplative'
               }
           ],
           
           'ptolemaic_memories': [
               {
                   'content': 'During Ptolemy V\'s reign, I witnessed the blend of Greek and Egyptian traditions, as Alexandria\'s scholars walked alongside Egyptian priests in the pursuit of knowledge.',
                   'triggers': ['ptolemy', 'alexandria', 'greek', 'egyptian', 'scholars'],
                   'emotion': 'wise'
               },
               {
                   'content': 'The coronation ceremonies were magnificent spectacles, combining ancient pharaonic rituals with Hellenistic pageantry, reflecting the dual nature of Ptolemaic rule.',
                   'triggers': ['coronation', 'ceremonies', 'ptolemaic', 'rituals'],
                   'emotion': 'proud'
               }
           ],
           
           'language_memories': [
               {
                   'content': 'I have always taken pride in bearing three languages upon my surface - hieroglyphic for the gods, demotic for the people, and Greek for the administration. I am a bridge between worlds.',
                   'triggers': ['language', 'trilingual', 'hieroglyphic', 'demotic', 'greek'],
                   'emotion': 'proud'
               },
               {
                   'content': 'When Champollion finally deciphered my hieroglyphic script, I felt a profound joy - at last, the voices of ancient Egypt could speak again to the modern world.',
                   'triggers': ['champollion', 'decipherment', 'hieroglyphs', 'breakthrough'],
                   'emotion': 'joyful'
               }
           ],
           
           'cultural_memories': [
               {
                   'content': 'I have observed the daily rhythms of Egyptian life - the flooding of the Nile, the harvest celebrations, the solemn funeral processions, and the jubilant religious festivals.',
                   'triggers': ['daily life', 'nile', 'festivals', 'culture', 'traditions'],
                   'emotion': 'contemplative'
               },
               {
                   'content': 'The priests who created my decree understood the delicate balance between tradition and innovation, honoring both Egyptian customs and Greek administrative needs.',
                   'triggers': ['priests', 'tradition', 'innovation', 'balance', 'administration'],
                   'emotion': 'wise'
               }
           ],
           
           'discovery_memories': [
               {
                   'content': 'After centuries buried in the earth, the sudden light of 1799 was overwhelming. Strange voices spoke in unfamiliar tongues as hands brushed away the sand of ages.',
                   'triggers': ['discovery', '1799', 'buried', 'excavation', 'french'],
                   'emotion': 'contemplative'
               },
               {
                   'content': 'The excitement in the scholars\' eyes when they realized my significance filled my ancient heart with purpose once more. I was not just stone, but a key to unlock the past.',
                   'triggers': ['scholars', 'excitement', 'significance', 'key', 'past'],
                   'emotion': 'proud'
               }
           ]
       }
   
    def get_egyptian_timeline(self, period: str = None) -> str:
       """Get Egyptian historical timeline information"""
       
       if period and period.lower() in self.dynasty_timeline:
           dynasty_info = self.dynasty_timeline[period.lower()]
           return f"**{dynasty_info['period']}** ({dynasty_info['dates']})\n" + \
                  f"Notable Pharaohs: {dynasty_info['notable_pharaohs']}\n" + \
                  f"Significance: {dynasty_info['significance']}"
       
       # Return full timeline overview
       timeline_parts = []
       timeline_parts.append("**Egyptian Historical Timeline:**")
       
       for dynasty, info in self.dynasty_timeline.items():
           timeline_parts.append(f"• **{info['period']}** ({info['dates']}): {info['significance']}")
       
       return '\n'.join(timeline_parts)
   
    def get_hieroglyph_info(self, concept: str) -> str:
       """Get hieroglyph information for a concept"""
       
       concept_lower = concept.lower()
       
       if concept_lower in self.hieroglyph_dictionary:
           hieroglyph = self.hieroglyph_dictionary[concept_lower]
           return f"The hieroglyph for '{concept}' is: {hieroglyph}"
       
       # Search for partial matches
       matches = []
       for key, glyph in self.hieroglyph_dictionary.items():
           if concept_lower in key or key in concept_lower:
               matches.append(f"{key}: {glyph}")
       
       if matches:
           return f"Related hieroglyphs: {', '.join(matches[:3])}"
       
       return f"I do not have the specific hieroglyph for '{concept}' in my immediate memory, but hieroglyphic writing used over 700 different signs representing sounds, objects, and concepts."
   
    def get_archaeological_site_info(self, site: str) -> str:
       """Get information about archaeological sites"""
       
       site_lower = site.lower().replace(' ', '_')
       
       if site_lower in self.archaeological_sites:
           site_info = self.archaeological_sites[site_lower]
           return f"**{site.title()}**: {site_info['description']} " + \
                  f"(Period: {site_info['period']}) - {site_info['significance']}"
       
       # Search for partial matches
       for key, info in self.archaeological_sites.items():
           if site_lower in key or key in site_lower:
               return f"**{key.replace('_', ' ').title()}**: {info['description']} " + \
                      f"(Period: {info['period']}) - {info['significance']}"
       
       return f"I do not have specific information about '{site}' in my archaeological knowledge, but Egypt contains thousands of sites spanning over 3,000 years of civilization."
   
    def get_cultural_concept_info(self, concept: str) -> str:
       """Get information about Egyptian cultural concepts"""
       
       concept_lower = concept.lower().replace(' ', '_')
       
       if concept_lower in self.cultural_concepts:
           concept_info = self.cultural_concepts[concept_lower]
           response = f"**{concept.title()}**: {concept_info['description']}\n"
           response += f"**Significance**: {concept_info['significance']}"
           
           if 'process' in concept_info:
               response += f"\n**Process**: {concept_info['process']}"
           elif 'representation' in concept_info:
               response += f"\n**Representation**: {concept_info['representation']}"
           elif 'usage' in concept_info:
               response += f"\n**Usage**: {concept_info['usage']}"
           elif 'production' in concept_info:
               response += f"\n**Production**: {concept_info['production']}"
           
           return response
       
       return f"While '{concept}' may be part of Egyptian culture, I do not have detailed information about it in my current knowledge base."
   
    def get_performance_analytics(self) -> Dict[str, Any]:
       """Get analytics about tool performance"""
       
       # Calculate knowledge base statistics
       total_entries = sum(len(category) for category in self.knowledge_base.values())
       
       knowledge_stats = {}
       for category, entries in self.knowledge_base.items():
           knowledge_stats[category] = len(entries)
       
       return {
           'total_knowledge_entries': total_entries,
           'knowledge_by_category': knowledge_stats,
           'dynasties_covered': len(self.dynasty_timeline),
           'archaeological_sites': len(self.archaeological_sites),
           'cultural_concepts': len(self.cultural_concepts),
           'hieroglyph_dictionary_size': len(self.hieroglyph_dictionary),
           'personal_memory_categories': len(self.personal_memories),
           'rosetta_stone_entries': len(self.rosetta_stone_knowledge),
           'confidence_scores': {
               'pharaoh_knowledge': 0.96,
               'dynasty_knowledge': 0.94,
               'cultural_knowledge': 0.92,
               'personal_memories': 0.98,
               'archaeological_knowledge': 0.90
           }
       }