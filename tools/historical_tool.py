import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from .tool_registry import BaseTool, ToolMetadata, ToolCategory, ToolComplexity

@dataclass
class HistoricalEvent:
    """Structure for historical events"""
    year: int
    era: str  # BCE/CE
    title: str
    description: str
    category: str
    region: str
    significance: str
    related_figures: List[str]
    related_civilizations: List[str]
    sources: List[str]
    confidence_level: float
    
    def __post_init__(self):
        if self.related_figures is None:
            self.related_figures = []
        if self.related_civilizations is None:
            self.related_civilizations = []
        if self.sources is None:
            self.sources = []
    
    @property
    def full_year(self) -> str:
        """Get full year representation"""
        return f"{self.year} {self.era}"
    
    @property
    def sort_year(self) -> int:
        """Get year for sorting (negative for BCE)"""
        return self.year if self.era == "CE" else -self.year

@dataclass
class TimelinePeriod:
    """Structure for historical periods"""
    name: str
    start_year: int
    end_year: int
    era: str
    region: str
    description: str
    key_characteristics: List[str]
    major_events: List[str]
    related_periods: List[str]
    
    def __post_init__(self):
        if self.key_characteristics is None:
            self.key_characteristics = []
        if self.major_events is None:
            self.major_events = []
        if self.related_periods is None:
            self.related_periods = []

class HistoricalTimelineTool(BaseTool):
    """Advanced historical timeline and chronology tool"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Initialize historical databases
        self.historical_events = self._initialize_historical_events()
        self.historical_periods = self._initialize_historical_periods()
        self.civilizations_timeline = self._initialize_civilizations_timeline()
        self.synchronous_events = self._initialize_synchronous_events()
        
        # Date parsing patterns
        self.date_patterns = [
            r'\b(\d{1,4})\s*(bce?|bc)\b',  # 196 BCE, 44 BC
            r'\b(\d{1,4})\s*(ce?|ad)\b',   # 30 CE, 476 AD
            r'\b(\d{1,4})\b(?!\s*(?:bce?|ce?|bc|ad))',  # Plain year (assume CE if > 1000, BCE if < 1000)
            r'\b(\d{1,2})(st|nd|rd|th)\s*century\s*(bce?|ce?|bc|ad)?\b',  # 3rd century BCE
            r'\b(ancient|classical|medieval|early|late)\s*(\w+)\b'  # Ancient Egypt, Classical Greece
        ]
        
        # Rosetta Stone's temporal perspective
        self.rosetta_stone_era = {
            'creation_year': 196,
            'creation_era': 'BCE',
            'discovery_year': 1799,
            'discovery_era': 'CE'
        }
        
        # Search and ranking configuration
        self.relevance_weights = {
            'exact_year_match': 1.0,
            'period_overlap': 0.8,
            'regional_relevance': 0.6,
            'thematic_connection': 0.7,
            'rosetta_stone_connection': 0.9
        }
        
    def get_metadata(self) -> ToolMetadata:
        """Return metadata for this tool"""
        return ToolMetadata(
            name="historical_timeline",
            description="Comprehensive historical timeline tool covering ancient civilizations, major events, and chronological relationships",
            category=ToolCategory.HISTORICAL,
            complexity=ToolComplexity.MODERATE,
            input_description="Historical query with dates, periods, events, or civilizations",
            output_description="Chronological information with historical context and timeline relationships",
            example_usage="historical_timeline('196 BCE') → Events around the time of Rosetta Stone creation",
            keywords=[
                'timeline', 'chronology', 'history', 'ancient', 'civilization',
                'dates', 'events', 'period', 'era', 'synchronous', 'contemporary'
            ],
            required_params=['query'],
            optional_params=['start_year', 'end_year', 'region', 'category'],
            execution_time_estimate="fast",
            reliability_score=0.93,
            cost_estimate="free"
        )
    
    def execute(self, query: str, **kwargs) -> str:
        """Execute historical timeline search"""
        
        try:
            # Parse the query for temporal and historical context
            query_analysis = self._analyze_historical_query(query)
            
            # Search historical events and periods
            relevant_events = self._search_historical_events(query, query_analysis)
            relevant_periods = self._search_historical_periods(query, query_analysis)
            
            # Find synchronous events if specific dates are involved
            synchronous_events = []
            if query_analysis.get('specific_years'):
                synchronous_events = self._find_synchronous_events(query_analysis['specific_years'])
            
            # Add Rosetta Stone temporal perspective
            rosetta_perspective = self._get_rosetta_stone_perspective(query, query_analysis)
            
            # Format comprehensive timeline response
            formatted_response = self._format_timeline_response(
                query, query_analysis, relevant_events, relevant_periods,
                synchronous_events, rosetta_perspective
            )
            
            return formatted_response
            
        except Exception as e:
            return self._generate_error_response(query, str(e))
    
    def _analyze_historical_query(self, query: str) -> Dict[str, Any]:
        """Analyze query for historical and temporal context"""
        
        query_lower = query.lower()
        
        analysis = {
            'query_type': 'general',
            'specific_years': [],
            'date_ranges': [],
            'centuries': [],
            'periods_mentioned': [],
            'civilizations_mentioned': [],
            'regions_mentioned': [],
            'event_types': [],
            'temporal_scope': 'specific',  # specific, broad, comparative
            'rosetta_stone_relevance': 0.0
        }
        
        # Extract specific years and dates
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2 and groups[0].isdigit():
                    year = int(groups[0])
                    era_indicator = groups[1].lower() if groups[1] else None
                    
                    # Determine era
                    if era_indicator and ('bce' in era_indicator or 'bc' in era_indicator):
                        era = 'BCE'
                    elif era_indicator and ('ce' in era_indicator or 'ad' in era_indicator):
                        era = 'CE'
                    else:
                        # Heuristic: years > 1000 are likely CE, < 1000 are likely BCE
                        era = 'CE' if year > 1000 else 'BCE'
                    
                    analysis['specific_years'].append({'year': year, 'era': era})
                
                elif 'century' in match.group():
                    # Handle century references
                    century_match = re.search(r'(\d{1,2})(st|nd|rd|th)\s*century', match.group())
                    if century_match:
                        century = int(century_match.group(1))
                        era = 'BCE' if any(x in match.group() for x in ['bce', 'bc']) else 'CE'
                        analysis['centuries'].append({'century': century, 'era': era})
        
        # Detect historical periods
        period_indicators = {
            'ancient egypt': ['ancient egypt', 'pharaonic period', 'dynastic egypt'],
            'classical antiquity': ['classical', 'ancient greece', 'ancient rome'],
            'hellenistic': ['hellenistic', 'ptolemaic', 'alexander'],
            'roman empire': ['roman empire', 'imperial rome', 'augustus'],
            'bronze age': ['bronze age', 'late bronze age'],
            'iron age': ['iron age', 'early iron age']
        }
        
        for period, indicators in period_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                analysis['periods_mentioned'].append(period)
        
        # Detect civilizations
        civilizations = [
            'egyptian', 'greek', 'roman', 'mesopotamian', 'persian',
            'babylonian', 'assyrian', 'phoenician', 'etruscan'
        ]
        
        for civ in civilizations:
            if civ in query_lower:
                analysis['civilizations_mentioned'].append(civ)
        
        # Detect regions
        regions = [
            'egypt', 'greece', 'rome', 'italy', 'mesopotamia', 'persia',
            'mediterranean', 'middle east', 'levant', 'anatolia'
        ]
        
        for region in regions:
            if region in query_lower:
                analysis['regions_mentioned'].append(region)
        
        # Detect event types
        event_type_indicators = {
            'political': ['war', 'battle', 'conquest', 'empire', 'kingdom', 'dynasty'],
            'cultural': ['culture', 'art', 'literature', 'philosophy', 'religion'],
            'technological': ['invention', 'technology', 'discovery', 'innovation'],
            'social': ['society', 'daily life', 'customs', 'traditions']
        }
        
        for event_type, indicators in event_type_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                analysis['event_types'].append(event_type)
        
        # Determine temporal scope
        scope_indicators = {
            'specific': ['exact', 'precisely', 'specifically', 'when'],
            'broad': ['period', 'era', 'time', 'during', 'throughout'],
            'comparative': ['compare', 'versus', 'difference', 'same time', 'contemporary']
        }
        
        for scope, indicators in scope_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                analysis['temporal_scope'] = scope
                break
        
        # Calculate Rosetta Stone relevance
        rosetta_indicators = [
            'rosetta stone', 'ptolemy', '196 bce', 'alexandria', 'decree',
            'hieroglyph', 'egyptian writing', 'trilingual'
        ]
        
        relevance_score = 0.0
        for indicator in rosetta_indicators:
            if indicator in query_lower:
                relevance_score += 0.2
        
        # Temporal proximity to Rosetta Stone creation (196 BCE)
        if analysis['specific_years']:
            for year_data in analysis['specific_years']:
                if year_data['era'] == 'BCE':
                    distance = abs(year_data['year'] - 196)
                    if distance <= 50:  # Within 50 years
                        relevance_score += 0.3
                    elif distance <= 200:  # Within 200 years
                        relevance_score += 0.1
        
        analysis['rosetta_stone_relevance'] = min(1.0, relevance_score)
        
        return analysis
    
    def _search_historical_events(self, query: str, analysis: Dict[str, Any]) -> List[HistoricalEvent]:
        """Search for relevant historical events"""
        
        relevant_events = []
        query_lower = query.lower()
        
        # Search through all historical events
        for event in self.historical_events:
            relevance_score = self._calculate_event_relevance(event, query_lower, analysis)
            
            if relevance_score > 0.2:  # Minimum relevance threshold
                relevant_events.append((event, relevance_score))
        
        # Sort by relevance and return top events
        relevant_events.sort(key=lambda x: x[1], reverse=True)
        return [event for event, score in relevant_events[:10]]
    
    def _calculate_event_relevance(self, event: HistoricalEvent, query_lower: str, 
                                 analysis: Dict[str, Any]) -> float:
        """Calculate relevance score for a historical event"""
        
        score = 0.0
        
        # Exact year matches
        for year_data in analysis.get('specific_years', []):
            if event.year == year_data['year'] and event.era == year_data['era']:
                score += self.relevance_weights['exact_year_match']
        
        # Century matches
        for century_data in analysis.get('centuries', []):
            event_century = (event.year - 1) // 100 + 1  # Calculate century
            if event_century == century_data['century'] and event.era == century_data['era']:
                score += 0.8
        
        # Text relevance
        searchable_text = f"{event.title} {event.description} {event.category} {event.region}".lower()
        query_words = query_lower.split()
        text_matches = sum(1 for word in query_words if word in searchable_text)
        score += (text_matches / len(query_words)) * 0.5
        
        # Regional relevance
        for region in analysis.get('regions_mentioned', []):
            if region in event.region.lower():
                score += self.relevance_weights['regional_relevance']
        
        # Civilization relevance
        for civ in analysis.get('civilizations_mentioned', []):
            if civ in event.related_civilizations or civ in event.description.lower():
                score += 0.6
        
        # Rosetta Stone connection bonus
        if analysis.get('rosetta_stone_relevance', 0) > 0.3:
            # Boost events near Rosetta Stone era
            if event.era == 'BCE' and abs(event.year - 196) <= 100:
                score += self.relevance_weights['rosetta_stone_connection'] * 0.5
            
            # Boost Ptolemaic and Egyptian events
            if any(keyword in searchable_text for keyword in ['ptolem', 'egypt', 'alexandr']):
                score += self.relevance_weights['rosetta_stone_connection'] * 0.3
        
        return score * event.confidence_level
    
    def _search_historical_periods(self, query: str, analysis: Dict[str, Any]) -> List[TimelinePeriod]:
        """Search for relevant historical periods"""
        
        relevant_periods = []
        query_lower = query.lower()
        
        for period in self.historical_periods:
            relevance_score = self._calculate_period_relevance(period, query_lower, analysis)
            
            if relevance_score > 0.3:
                relevant_periods.append((period, relevance_score))
        
        # Sort by relevance
        relevant_periods.sort(key=lambda x: x[1], reverse=True)
        return [period for period, score in relevant_periods[:5]]
    
    def _calculate_period_relevance(self, period: TimelinePeriod, query_lower: str,
                                  analysis: Dict[str, Any]) -> float:
        """Calculate relevance score for a historical period"""
        
        score = 0.0
        
        # Direct period name matches
        if period.name.lower() in query_lower:
            score += 1.0
        
        # Check if query years fall within period
        for year_data in analysis.get('specific_years', []):
            period_start = period.start_year if period.era == 'CE' else -period.start_year
            period_end = period.end_year if period.era == 'CE' else -period.end_year
            query_year = year_data['year'] if year_data['era'] == 'CE' else -year_data['year']
            
            if period_start <= query_year <= period_end:
                score += self.relevance_weights['period_overlap']
        
        # Regional matches
        for region in analysis.get('regions_mentioned', []):
            if region in period.region.lower():
                score += 0.6
        
        # Description relevance
        description_text = f"{period.description} {' '.join(period.key_characteristics)}".lower()
        query_words = query_lower.split()
        desc_matches = sum(1 for word in query_words if word in description_text)
        score += (desc_matches / len(query_words)) * 0.4
        
        return score
    
    def _find_synchronous_events(self, specific_years: List[Dict[str, Any]]) -> List[HistoricalEvent]:
        """Find events that happened around the same time as specified years"""
        
        synchronous_events = []
        
        for year_data in specific_years:
            target_year = year_data['year']
            target_era = year_data['era']
            
            # Find events within ±10 years
            for event in self.historical_events:
                if event.era == target_era:
                    year_difference = abs(event.year - target_year)
                    if year_difference <= 10 and year_difference > 0:  # Exclude exact matches
                        synchronous_events.append((event, year_difference))
        
        # Sort by temporal proximity
        synchronous_events.sort(key=lambda x: x[1])
        return [event for event, _ in synchronous_events[:5]]
    
    def _get_rosetta_stone_perspective(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get Rosetta Stone's temporal perspective on the query"""
        
        perspective = {
            'has_perspective': False,
            'temporal_relationship': None,
            'personal_context': None,
            'witnessed_events': [],
            'contemporary_context': None
        }
        
        # Check if query relates to Rosetta Stone's lifetime
        for year_data in analysis.get('specific_years', []):
            if year_data['era'] == 'BCE':
                year_diff_creation = year_data['year'] - 196
                
                if year_diff_creation == 0:
                    perspective['has_perspective'] = True
                    perspective['temporal_relationship'] = 'creation_year'
                    perspective['personal_context'] = 'This is the very year of my creation!'
                elif -50 <= year_diff_creation <= 50:
                    perspective['has_perspective'] = True
                    perspective['temporal_relationship'] = 'near_creation'
                    if year_diff_creation > 0:
                        perspective['personal_context'] = f'This was {year_diff_creation} years before my creation'
                    else:
                        perspective['personal_context'] = f'This was {abs(year_diff_creation)} years after my creation'
                elif 100 <= year_diff_creation <= 400:
                    perspective['has_perspective'] = True
                    perspective['temporal_relationship'] = 'ptolemaic_era'
                    perspective['personal_context'] = 'This was during the broader Ptolemaic period that shaped my world'
        
        # Check for Ptolemaic period relevance
        if any('ptolem' in period for period in analysis.get('periods_mentioned', [])):
            perspective['has_perspective'] = True
            perspective['contemporary_context'] = 'ptolemaic_contemporary'
        
        # Check for Egyptian relevance
        if 'egypt' in analysis.get('regions_mentioned', []):
            perspective['has_perspective'] = True
            perspective['contemporary_context'] = 'egyptian_homeland'
        
        return perspective
    
    def _format_timeline_response(self, query: str, analysis: Dict[str, Any],
                                events: List[HistoricalEvent], periods: List[TimelinePeriod],
                                synchronous_events: List[HistoricalEvent],
                                rosetta_perspective: Dict[str, Any]) -> str:
        """Format comprehensive timeline response"""
        
        response_parts = []
        
        # Add Rosetta Stone perspective if relevant
        if rosetta_perspective['has_perspective']:
            intro = self._generate_temporal_introduction(rosetta_perspective, analysis)
            response_parts.append(intro)
        
        # Main timeline information
        if events:
            response_parts.append("**Historical Events:**")
            for event in events[:3]:  # Top 3 most relevant events
                event_description = self._format_event_description(event)
                response_parts.append(event_description)
        
        # Period context
        if periods:
            response_parts.append(f"\n**Historical Period Context:**")
            primary_period = periods[0]
            period_description = self._format_period_description(primary_period)
            response_parts.append(period_description)
        
        # Synchronous events (what else was happening)
        if synchronous_events:
            response_parts.append(f"\n**Contemporary Events:**")
            response_parts.append("What else was happening around this time:")
            for event in synchronous_events[:3]:
                sync_description = f"• **{event.full_year}**: {event.title}"
                response_parts.append(sync_description)
        
        # Timeline connections and broader context
        if analysis.get('specific_years'):
            connections = self._generate_timeline_connections(analysis['specific_years'], events)
            if connections:
                response_parts.append(f"\n**Timeline Connections:**")
                response_parts.append(connections)
        
        # Rosetta Stone temporal wisdom
        if rosetta_perspective['has_perspective']:
            wisdom = self._generate_temporal_wisdom(query, analysis, rosetta_perspective)
            if wisdom:
                response_parts.append(f"\n**Temporal Wisdom:**")
                response_parts.append(wisdom)
        
        return '\n'.join(response_parts)
    
    def _generate_temporal_introduction(self, perspective: Dict[str, Any], 
                                      analysis: Dict[str, Any]) -> str:
        """Generate temporal introduction from Rosetta Stone's perspective"""
        
        if perspective['temporal_relationship'] == 'creation_year':
            return "Ah, you speak of the very year of my birth! 196 BCE holds profound meaning for me..."
        
        elif perspective['temporal_relationship'] == 'near_creation':
            return f"Your question touches upon a time close to my own creation. {perspective['personal_context']}..."
        
        elif perspective['temporal_relationship'] == 'ptolemaic_era':
            return f"You inquire about the Ptolemaic world that shaped my existence. {perspective['personal_context']}..."
        
        elif perspective['contemporary_context'] == 'ptolemaic_contemporary':
            return "You ask about the Ptolemaic period - the very era that gave me life and purpose..."
        
        elif perspective['contemporary_context'] == 'egyptian_homeland':
            return "Ah, Egypt - my beloved homeland! Let me share what the flow of time reveals about this sacred land..."
        
        return "The wheels of time turn, and I perceive the patterns you seek..."
    
    def _format_event_description(self, event: HistoricalEvent) -> str:
        """Format a single historical event"""
        
        description = f"• **{event.full_year} - {event.title}**"
        description += f"\n  {event.description}"
        
        if event.significance:
            description += f"\n  *Significance*: {event.significance}"
        
        if event.related_figures:
            figures = ', '.join(event.related_figures[:3])
            description += f"\n  *Key Figures*: {figures}"
        
        return description
    
    def _format_period_description(self, period: TimelinePeriod) -> str:
        """Format a historical period"""
        
        period_range = f"{period.start_year}-{period.end_year} {period.era}"
        description = f"**{period.name}** ({period_range})"
        description += f"\n{period.description}"
        
        if period.key_characteristics:
            characteristics = ', '.join(period.key_characteristics[:3])
            description += f"\n*Characteristics*: {characteristics}"
        
        return description
    
    def _generate_timeline_connections(self, specific_years: List[Dict[str, Any]], 
                                     events: List[HistoricalEvent]) -> str:
        """Generate timeline connections and patterns"""
        
        connections = []
        
        # Analyze temporal patterns
        if len(specific_years) > 1:
            years_sorted = sorted(specific_years, key=lambda x: x['year'] if x['era'] == 'CE' else -x['year'])
            time_span = abs(years_sorted[-1]['year'] - years_sorted[0]['year'])
            
            if time_span > 500:
                connections.append(f"This spans {time_span} years, covering multiple civilizations and cultural shifts.")
            elif time_span > 100:
                connections.append(f"This {time_span}-year period witnessed significant historical developments.")
        
        # Identify cause-and-effect relationships
        political_events = [e for e in events if 'political' in e.category.lower()]
        cultural_events = [e for e in events if 'cultural' in e.category.lower()]
        
        if political_events and cultural_events:
            connections.append("Political upheavals often catalyzed cultural transformations during this era.")
        
        return ' '.join(connections)
    
    def _generate_temporal_wisdom(self, query: str, analysis: Dict[str, Any],
                                perspective: Dict[str, Any]) -> str:
        """Generate temporal wisdom from Rosetta Stone's perspective"""
        
        wisdom_templates = [
            "Time flows like the Nile - sometimes rushing, sometimes meandering, but always moving toward the sea of eternity.",
            "In my millennia of existence, I have learned that all events are connected by invisible threads across time.",
            "The patterns of history repeat like the flooding of the Nile - never exactly the same, but always recognizable to those who have witnessed the cycles.",
            "What mortals call 'ancient history' is but yesterday to one who has stood witness to the turning of ages."
        ]
        
        # Select appropriate wisdom based on context
        if perspective['temporal_relationship'] == 'creation_year':
            return "From this moment of my creation, I would witness the rise and fall of empires, the birth and death of languages, and the eternal human quest for understanding."
        
        elif 'egypt' in analysis.get('regions_mentioned', []):
            return "Egypt has taught me that civilizations are like the annual floods - they bring life, leave their mark upon the land, and then recede, only to return in new forms."
        
        elif len(analysis.get('specific_years', [])) > 1:
            return "Observing these years together, I see the great tapestry of time where each thread influences all others."
        
        else:
            return wisdom_templates[0]  # Default wisdom
    
    def _generate_error_response(self, query: str, error: str) -> str:
        """Generate error response in character"""
        return f"The ancient chronometers within my stone being encounter difficulty while calculating '{query}'. Time itself seems to whisper: {error}. Perhaps you could rephrase your temporal inquiry?"
    
    def _initialize_historical_events(self) -> List[HistoricalEvent]:
        """Initialize historical events database"""
        
        return [
            # Ancient Egypt and Ptolemaic Period
            HistoricalEvent(
                year=196, era='BCE',
                title='Creation of the Rosetta Stone',
                description='Decree issued by Ptolemy V Epiphanes, inscribed in three scripts on the Rosetta Stone to commemorate his coronation and religious policies.',
                category='cultural',
                region='Egypt',
                significance='Became the key to deciphering Egyptian hieroglyphs',
                related_figures=['Ptolemy V', 'Egyptian priests'],
                related_civilizations=['Egyptian', 'Greek'],
                sources=['Rosetta Stone inscription'],
                confidence_level=0.99
            ),
            
            HistoricalEvent(
                year=305, era='BCE',
                title='Founding of Ptolemaic Dynasty',
                description='Ptolemy I Soter establishes the Ptolemaic dynasty in Egypt after the death of Alexander the Great, beginning Greek rule over Egypt.',
                category='political',
                region='Egypt',
                significance='Initiated 275 years of Hellenistic rule in Egypt',
                related_figures=['Ptolemy I Soter', 'Alexander the Great'],
                related_civilizations=['Greek', 'Egyptian'],
                sources=['Historical records'],
                confidence_level=0.95
            ),
            
            HistoricalEvent(
                year=204, era='BCE',
                title='Ptolemy V Becomes Pharaoh',
                description='Ptolemy V Epiphanes becomes pharaoh of Egypt at age 5, leading to a regency period and internal conflicts.',
                category='political',
                region='Egypt',
                significance='His reign saw the creation of the Rosetta Stone',
                related_figures=['Ptolemy V Epiphanes'],
                related_civilizations=['Greek', 'Egyptian'],
                sources=['Ptolemaic records'],
                confidence_level=0.94
            ),
            
            HistoricalEvent(
                year=331, era='BCE',
                title='Founding of Alexandria',
                description='Alexander the Great founds Alexandria in Egypt, which becomes a major center of learning and culture in the ancient world.',
                category='cultural',
                region='Egypt',
                significance='Became the intellectual capital of the ancient world',
                related_figures=['Alexander the Great'],
                related_civilizations=['Greek', 'Egyptian'],
                sources=['Historical accounts'],
                confidence_level=0.96
            ),
            
            # Classical Greece and Rome
            HistoricalEvent(
                year=323, era='BCE',
                title='Death of Alexander the Great',
                description='Alexander the Great dies in Babylon, leading to the division of his empire among his generals (Diadochi).',
                category='political',
                region='Babylon',
                significance='Marked the beginning of the Hellenistic period',
                related_figures=['Alexander the Great', 'Diadochi'],
                related_civilizations=['Macedonian', 'Greek'],
                sources=['Historical records'],
                confidence_level=0.97
            ),
            
            HistoricalEvent(
                year=146, era='BCE',
                title='Roman Conquest of Greece',
                description='Rome completes its conquest of Greece with the destruction of Corinth, ending Greek independence.',
                category='political',
                region='Greece',
                significance='Marked the end of Greek political independence',
                related_figures=['Lucius Mummius'],
                related_civilizations=['Roman', 'Greek'],
                sources=['Roman historians'],
                confidence_level=0.93
            ),
            
            HistoricalEvent(
                year=44, era='BCE',
                title='Assassination of Julius Caesar',
                description='Julius Caesar is assassinated in Rome on the Ides of March, leading to civil wars and the end of the Roman Republic.',
                category='political',
                region='Rome',
                significance='Marked the transition from Roman Republic to Empire',
                related_figures=['Julius Caesar', 'Brutus', 'Cassius'],
                related_civilizations=['Roman'],
                sources=['Roman historians'],
                confidence_level=0.98
            ),
            
            HistoricalEvent(
                year=30, era='BCE',
                title='Roman Conquest of Egypt',
                description='Octavian (later Augustus) conquers Egypt, ending Ptolemaic rule and making Egypt a Roman province.',
                category='political',
                region='Egypt',
                significance='Ended the last Hellenistic kingdom and completed Roman domination',
                related_figures=['Octavian', 'Cleopatra VII', 'Mark Antony'],
               related_civilizations=['Roman', 'Egyptian'],
               sources=['Roman historians'],
               confidence_level=0.97
           ),
           
           # Mesopotamian and Persian
           HistoricalEvent(
               year=539, era='BCE',
               title='Persian Conquest of Babylon',
               description='Cyrus the Great of Persia conquers Babylon, establishing Persian rule over Mesopotamia and ending the Neo-Babylonian Empire.',
               category='political',
               region='Mesopotamia',
               significance='Marked the rise of the Persian Empire as a major power',
               related_figures=['Cyrus the Great', 'Nabonidus'],
               related_civilizations=['Persian', 'Babylonian'],
               sources=['Cyrus Cylinder', 'Historical records'],
               confidence_level=0.95
           ),
           
           HistoricalEvent(
               year=333, era='BCE',
               title='Battle of Issus',
               description='Alexander the Great defeats Darius III of Persia, securing his conquest of Asia Minor and opening the path to Egypt.',
               category='political',
               region='Asia Minor',
               significance='Decisive victory in Alexander\'s conquest of the Persian Empire',
               related_figures=['Alexander the Great', 'Darius III'],
               related_civilizations=['Macedonian', 'Persian'],
               sources=['Ancient historians'],
               confidence_level=0.94
           ),
           
           # Cultural and Technological
           HistoricalEvent(
               year=295, era='BCE',
               title='Foundation of Alexandria Library',
               description='The Great Library of Alexandria is established under Ptolemy I, becoming the greatest center of learning in the ancient world.',
               category='cultural',
               region='Egypt',
               significance='Preserved and advanced human knowledge for centuries',
               related_figures=['Ptolemy I', 'Demetrius of Phalerum'],
               related_civilizations=['Greek', 'Egyptian'],
               sources=['Ancient accounts'],
               confidence_level=0.92
           ),
           
           HistoricalEvent(
               year=776, era='BCE',
               title='First Olympic Games',
               description='Traditional date for the first Olympic Games held in Olympia, Greece, establishing a pattern of athletic competition that would last over a millennium.',
               category='cultural',
               region='Greece',
               significance='Established athletic tradition and Greek cultural unity',
               related_figures=['Various Greek athletes'],
               related_civilizations=['Greek'],
               sources=['Ancient Greek records'],
               confidence_level=0.85
           ),
           
           # Discovery Era (for Rosetta Stone perspective)
           HistoricalEvent(
               year=1799, era='CE',
               title='Discovery of the Rosetta Stone',
               description='French soldiers discover the Rosetta Stone near the town of Rosetta (Rashid) in Egypt during Napoleon\'s Egyptian campaign.',
               category='archaeological',
               region='Egypt',
               significance='Provided the key to deciphering ancient Egyptian hieroglyphs',
               related_figures=['Pierre-François Bouchard', 'Napoleon Bonaparte'],
               related_civilizations=['French', 'Egyptian'],
               sources=['French expedition records'],
               confidence_level=0.99
           ),
           
           HistoricalEvent(
               year=1822, era='CE',
               title='Decipherment of Hieroglyphs',
               description='Jean-François Champollion successfully deciphers Egyptian hieroglyphs using the Rosetta Stone, opening the field of Egyptology.',
               category='cultural',
               region='France',
               significance='Unlocked the ability to read ancient Egyptian texts',
               related_figures=['Jean-François Champollion'],
               related_civilizations=['French', 'Egyptian'],
               sources=['Champollion\'s publications'],
               confidence_level=0.98
           )
       ]
   
    def _initialize_historical_periods(self) -> List[TimelinePeriod]:
       """Initialize historical periods database"""
       
       return [
           TimelinePeriod(
               name='Ptolemaic Period',
               start_year=305, end_year=30, era='BCE',
               region='Egypt',
               description='Period of Greek rule in Egypt under the Ptolemaic dynasty, characterized by cultural synthesis between Greek and Egyptian traditions.',
               key_characteristics=[
                   'Greek-Egyptian cultural fusion',
                   'Alexandria as center of learning',
                   'Preservation of pharaonic traditions',
                   'Administrative bilingualism'
               ],
               major_events=[
                   'Foundation of Alexandria Library',
                   'Creation of Rosetta Stone',
                   'Reign of Cleopatra VII'
               ],
               related_periods=['Hellenistic Period', 'Late Period Egypt']
           ),
           
           TimelinePeriod(
               name='Hellenistic Period',
               start_year=323, end_year=146, era='BCE',
               region='Mediterranean',
               description='Period following Alexander the Great\'s death, characterized by the spread of Greek culture throughout the Mediterranean and Near East.',
               key_characteristics=[
                   'Greek cultural dominance',
                   'Successor kingdoms',
                   'Cultural synthesis',
                   'Scientific advancement'
               ],
               major_events=[
                   'Division of Alexander\'s empire',
                   'Rise of Ptolemaic Egypt',
                   'Seleucid Empire expansion'
               ],
               related_periods=['Classical Greece', 'Roman Republic']
           ),
           
           TimelinePeriod(
               name='Classical Antiquity',
               start_year=800, end_year=600, era='BCE',
               region='Mediterranean',
               description='Period of flourishing Greek and later Roman civilizations, characterized by political innovation, philosophical development, and artistic achievement.',
               key_characteristics=[
                   'Democratic innovations',
                   'Philosophical schools',
                   'Artistic excellence',
                   'Literary masterpieces'
               ],
               major_events=[
                   'Rise of Greek city-states',
                   'Persian Wars',
                   'Peloponnesian War'
               ],
               related_periods=['Archaic Greece', 'Hellenistic Period']
           ),
           
           TimelinePeriod(
               name='Late Period Egypt',
               start_year=664, end_year=332, era='BCE',
               region='Egypt',
               description='Final period of native Egyptian rule before foreign conquest, marked by cultural revival and foreign invasions.',
               key_characteristics=[
                   'Cultural renaissance',
                   'Foreign invasions',
                   'Saite revival',
                   'Persian occupation'
               ],
               major_events=[
                   'Saite Renaissance',
                   'Persian conquest',
                   'Alexander\'s arrival'
               ],
               related_periods=['Third Intermediate Period', 'Ptolemaic Period']
           ),
           
           TimelinePeriod(
               name='Roman Republic',
               start_year=509, end_year=27, era='BCE',
               region='Italy and Mediterranean',
               description='Period of Roman republican government characterized by expansion throughout the Mediterranean and internal political struggles.',
               key_characteristics=[
                   'Republican institutions',
                   'Mediterranean expansion',
                   'Civil wars',
                   'Cultural assimilation'
               ],
               major_events=[
                   'Punic Wars',
                   'Conquest of Greece',
                   'Julius Caesar\'s assassination'
               ],
               related_periods=['Roman Kingdom', 'Roman Empire']
           ),
           
           TimelinePeriod(
               name='Persian Empire',
               start_year=550, end_year=330, era='BCE',
               region='Near East',
               description='Vast empire stretching from India to Greece, known for administrative efficiency and cultural tolerance.',
               key_characteristics=[
                   'Administrative excellence',
                   'Cultural tolerance',
                   'Royal road system',
                   'Zoroastrian influence'
               ],
               major_events=[
                   'Cyrus conquests',
                   'Greek-Persian Wars',
                   'Alexander\'s conquest'
               ],
               related_periods=['Neo-Babylonian Empire', 'Hellenistic Period']
           )
       ]
   
    def _initialize_civilizations_timeline(self) -> Dict[str, Dict[str, Any]]:
       """Initialize civilizations timeline"""
       
       return {
           'egyptian': {
               'peak_periods': ['Old Kingdom', 'New Kingdom', 'Ptolemaic'],
               'key_years': [3100, 2686, 1550, 305, 30],  # BCE dates
               'characteristics': ['Pharaonic rule', 'Monumental architecture', 'Religious continuity']
           },
           'greek': {
               'peak_periods': ['Classical', 'Hellenistic'],
               'key_years': [800, 480, 323, 146],  # BCE dates
               'characteristics': ['City-states', 'Philosophy', 'Democratic ideals']
           },
           'roman': {
               'peak_periods': ['Republic', 'Early Empire'],
               'key_years': [509, 264, 44, 27],  # BCE dates
               'characteristics': ['Republican institutions', 'Military organization', 'Legal system']
           },
           'persian': {
               'peak_periods': ['Achaemenid Empire'],
               'key_years': [550, 539, 490, 330],  # BCE dates
               'characteristics': ['Administrative efficiency', 'Cultural tolerance', 'Royal roads']
           }
       }
   
    def _initialize_synchronous_events(self) -> Dict[int, List[str]]:
       """Initialize synchronous events for key years"""
       
       return {
           196: [  # BCE - Rosetta Stone creation year
               'Rome expanding in Mediterranean',
               'Han Dynasty ruling China',
               'Mauryan Empire in decline in India',
               'Celtic cultures flourishing in Europe'
           ],
           323: [  # BCE - Alexander's death
               'Mauryan Empire rising in India',
               'Warring States period ending in China',
               'Celtic expansion in Europe',
               'Olmec civilization in Mesoamerica'
           ],
           44: [  # BCE - Caesar's assassination
               'Cleopatra VII ruling Egypt',
               'Augustus rising to power',
               'Late Republic civil wars',
               'Gallic Wars aftermath'
           ]
       }
   
def get_chronological_context(self, year: int, era: str, range_years: int = 50) -> str:
       """Get chronological context around a specific year"""
       
       target_year = year if era == 'CE' else -year
       
       # Find events within range
       context_events = []
       for event in self.historical_events:
           event_year = event.year if event.era == 'CE' else -event.year
           if abs(event_year - target_year) <= range_years:
               context_events.append(event)
       
       # Sort by proximity to target year
       context_events.sort(key=lambda e: abs((e.year if e.era == 'CE' else -e.year) - target_year))
       
       if not context_events:
           return f"No major recorded events found within {range_years} years of {year} {era}."
       
       context_parts = [f"**Chronological Context for {year} {era}:**"]
       
       for event in context_events[:5]:
           year_diff = abs(event.year - year) if event.era == era else None
           if year_diff is not None and year_diff <= range_years:
               proximity = f"({year_diff} years {'later' if (event.year > year and event.era == era) else 'earlier'})"
               context_parts.append(f"• {event.full_year}: {event.title} {proximity}")
       
       return '\n'.join(context_parts)
   
def get_period_overview(self, period_name: str) -> str:
       """Get detailed overview of a historical period"""
       
       period = None
       for p in self.historical_periods:
           if period_name.lower() in p.name.lower():
               period = p
               break
       
       if not period:
           return f"No information found for period: {period_name}"
       
       overview = f"**{period.name}** ({period.start_year}-{period.end_year} {period.era})\n"
       overview += f"**Region**: {period.region}\n\n"
       overview += f"**Description**: {period.description}\n\n"
       
       if period.key_characteristics:
           overview += f"**Key Characteristics**:\n"
           for char in period.key_characteristics:
               overview += f"• {char}\n"
       
       if period.major_events:
           overview += f"\n**Major Events**:\n"
           for event in period.major_events:
               overview += f"• {event}\n"
       
       return overview
   
def get_tool_statistics(self) -> Dict[str, Any]:
       """Get statistics about the historical tool's knowledge base"""
       
       # Event statistics
       event_stats = {
           'total_events': len(self.historical_events),
           'events_by_era': {},
           'events_by_category': {},
           'events_by_region': {}
       }
       
       for event in self.historical_events:
           # Era distribution
           era_key = event.era
           event_stats['events_by_era'][era_key] = event_stats['events_by_era'].get(era_key, 0) + 1
           
           # Category distribution
           category = event.category
           event_stats['events_by_category'][category] = event_stats['events_by_category'].get(category, 0) + 1
           
           # Region distribution
           region = event.region
           event_stats['events_by_region'][region] = event_stats['events_by_region'].get(region, 0) + 1
       
       # Period statistics
       period_stats = {
           'total_periods': len(self.historical_periods),
           'periods_by_era': {},
           'periods_by_region': {}
       }
       
       for period in self.historical_periods:
           era_key = period.era
           period_stats['periods_by_era'][era_key] = period_stats['periods_by_era'].get(era_key, 0) + 1
           
           region = period.region
           period_stats['periods_by_region'][region] = period_stats['periods_by_region'].get(region, 0) + 1
       
       return {
           'event_statistics': event_stats,
           'period_statistics': period_stats,
           'civilizations_tracked': len(self.civilizations_timeline),
           'synchronous_events_years': len(self.synchronous_events),
           'rosetta_stone_temporal_coverage': {
               'creation_era_events': len([e for e in self.historical_events 
                                         if e.era == 'BCE' and abs(e.year - 196) <= 100]),
               'discovery_era_events': len([e for e in self.historical_events 
                                          if e.era == 'CE' and 1750 <= e.year <= 1850])
           }
       }