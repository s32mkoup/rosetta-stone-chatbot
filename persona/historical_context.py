from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class HistoricalPeriod(Enum):
    """Major historical periods relevant to the Rosetta Stone"""
    PREDYNASTIC = "predynastic"
    EARLY_DYNASTIC = "early_dynastic"
    OLD_KINGDOM = "old_kingdom"
    FIRST_INTERMEDIATE = "first_intermediate"
    MIDDLE_KINGDOM = "middle_kingdom"
    SECOND_INTERMEDIATE = "second_intermediate"
    NEW_KINGDOM = "new_kingdom"
    THIRD_INTERMEDIATE = "third_intermediate"
    LATE_PERIOD = "late_period"
    PTOLEMAIC = "ptolemaic"
    ROMAN_EGYPT = "roman_egypt"
    MODERN_DISCOVERY = "modern_discovery"

@dataclass
class CulturalContext:
    """Cultural context information for historical periods"""
    period: HistoricalPeriod
    start_year: int
    end_year: int
    era: str  # BCE or CE
    characteristics: List[str]
    major_pharaohs: List[str]
    cultural_achievements: List[str]
    religious_developments: List[str]
    technological_advances: List[str]
    social_structure: Dict[str, str]
    art_and_architecture: List[str]
    language_and_writing: List[str]
    rosetta_stone_relevance: str

class HistoricalContextManager:
    """Manages historical context and cultural knowledge for the Rosetta Stone"""
    
    def __init__(self):
        self.cultural_contexts = self._initialize_cultural_contexts()
        self.dynasties = self._initialize_dynasties()
        self.religious_evolution = self._initialize_religious_evolution()
        self.linguistic_development = self._initialize_linguistic_development()
        self.archaeological_discoveries = self._initialize_archaeological_discoveries()
        self.cultural_practices = self._initialize_cultural_practices()
        
        # Rosetta Stone's personal historical perspective
        self.personal_historical_memories = self._initialize_personal_memories()
        self.witnessed_changes = self._initialize_witnessed_changes()
    
    def _initialize_cultural_contexts(self) -> Dict[HistoricalPeriod, CulturalContext]:
        """Initialize detailed cultural contexts for each historical period"""
        
        return {
            HistoricalPeriod.OLD_KINGDOM: CulturalContext(
                period=HistoricalPeriod.OLD_KINGDOM,
                start_year=2686, end_year=2181, era="BCE",
                characteristics=[
                    "Age of pyramid building",
                    "Strong centralized government",
                    "Development of Egyptian art and culture",
                    "Establishment of solar religion",
                    "Flourishing of craftsmanship"
                ],
                major_pharaohs=[
                    "Djoser", "Khufu", "Khafre", "Menkaure", "Unis"
                ],
                cultural_achievements=[
                    "Great Pyramid of Giza",
                    "Sphinx monument", 
                    "Pyramid Texts",
                    "Advanced mathematics and astronomy",
                    "Sophisticated art forms"
                ],
                religious_developments=[
                    "Solar theology with Ra supreme",
                    "Divine kingship concept",
                    "Pyramid Texts creation",
                    "Afterlife beliefs systematized",
                    "Priestly hierarchy established"
                ],
                technological_advances=[
                    "Advanced stone cutting techniques",
                    "Precise astronomical calculations",
                    "Sophisticated building methods",
                    "Metallurgy developments",
                    "Medical knowledge advances"
                ],
                social_structure={
                    "pharaoh": "Divine ruler at apex",
                    "nobles": "High officials and priests",
                    "scribes": "Educated administrative class",
                    "craftsmen": "Skilled artisans and builders",
                    "farmers": "Agricultural workers",
                    "laborers": "Construction and manual workers"
                },
                art_and_architecture=[
                    "Pyramid complexes",
                    "Mastaba tombs",
                    "Relief sculpture",
                    "Statue portraiture",
                    "Decorative arts"
                ],
                language_and_writing=[
                    "Hieroglyphic script fully developed",
                    "Cursive hieratic script emerges",
                    "Administrative texts flourish",
                    "Religious literature begins",
                    "Royal decree traditions start"
                ],
                rosetta_stone_relevance="Foundation period for the writing systems I would later bear"
            ),
            
            HistoricalPeriod.MIDDLE_KINGDOM: CulturalContext(
                period=HistoricalPeriod.MIDDLE_KINGDOM,
                start_year=2055, end_year=1650, era="BCE",
                characteristics=[
                    "Classical period of Egyptian culture",
                    "Democratic ideals emerge",
                    "Literary golden age",
                    "Expansion into Nubia",
                    "Administrative efficiency"
                ],
                major_pharaohs=[
                    "Mentuhotep II", "Amenemhat I", "Senusret III", "Amenemhat III"
                ],
                cultural_achievements=[
                    "Classical Egyptian literature",
                    "Sophisticated irrigation systems",
                    "Trade expansion",
                    "Artistic refinement",
                    "Educational advances"
                ],
                religious_developments=[
                    "Democratization of afterlife",
                    "Osiris cult prominence",
                    "Personal piety increases",
                    "Regional deities honored",
                    "Funerary literature expands"
                ],
                technological_advances=[
                    "Advanced metallurgy",
                    "Improved agricultural techniques",
                    "Better transportation methods",
                    "Medical text compilation",
                    "Mathematical advances"
                ],
                social_structure={
                    "pharaoh": "Less divine, more accessible",
                    "middle_class": "Expanded administrative class",
                    "regional_governors": "Increased local authority",
                    "artisans": "Higher social status",
                    "merchants": "Growing commercial class",
                    "farmers": "Better social mobility"
                },
                art_and_architecture=[
                    "Refined sculpture styles",
                    "Elegant jewelry",
                    "Sophisticated painting",
                    "Architectural innovations",
                    "Decorative objects"
                ],
                language_and_writing=[
                    "Classical Middle Egyptian",
                    "Literary masterpieces",
                    "Administrative efficiency",
                    "Educational texts",
                    "Historical records"
                ],
                rosetta_stone_relevance="Classical period that established many writing conventions I preserve"
            ),
            
            HistoricalPeriod.NEW_KINGDOM: CulturalContext(
                period=HistoricalPeriod.NEW_KINGDOM,
                start_year=1550, end_year=1077, era="BCE",
                characteristics=[
                    "Imperial period of Egypt",
                    "Military expansion",
                    "International diplomacy",
                    "Monumental architecture",
                    "Cultural cosmopolitanism"
                ],
                major_pharaohs=[
                    "Hatshepsut", "Thutmose III", "Akhenaten", "Tutankhamun", 
                    "Ramesses II", "Ramesses III"
                ],
                cultural_achievements=[
                    "Valley of the Kings",
                    "Abu Simbel temples",
                    "Karnak temple complex",
                    "International treaties",
                    "Artistic golden age"
                ],
                religious_developments=[
                    "Amarna revolution",
                    "Return to traditional gods",
                    "Amun-Ra supremacy",
                    "Complex theology",
                    "Funerary text evolution"
                ],
                technological_advances=[
                    "Bronze working perfection",
                    "Chariot technology",
                    "Advanced medicine",
                    "Engineering marvels",
                    "Glass making"
                ],
                social_structure={
                    "pharaoh": "Divine emperor",
                    "royal_family": "Extended royal court",
                    "high_priests": "Religious authority",
                    "military_elite": "Professional army",
                    "foreign_officials": "International administration",
                    "skilled_workers": "Specialized crafts"
                },
                art_and_architecture=[
                    "Monumental temples",
                    "Rock-cut tombs",
                    "Elegant painting",
                    "Sophisticated relief",
                    "Luxury objects"
                ],
                language_and_writing=[
                    "Late Egyptian develops",
                    "International correspondence",
                    "Religious literature flowers",
                    "Administrative complexity",
                    "Multilingual inscriptions"
                ],
                rosetta_stone_relevance="Period of international culture that influenced later Ptolemaic traditions"
            ),
            
            HistoricalPeriod.PTOLEMAIC: CulturalContext(
                period=HistoricalPeriod.PTOLEMAIC,
                start_year=305, end_year=30, era="BCE",
                characteristics=[
                    "Greek rule in Egypt",
                    "Cultural synthesis",
                    "Alexandria as learning center",
                    "Administrative bilingualism",
                    "Religious fusion"
                ],
                major_pharaohs=[
                    "Ptolemy I Soter", "Ptolemy II Philadelphus", "Ptolemy V Epiphanes", 
                    "Cleopatra VII"
                ],
                cultural_achievements=[
                    "Library of Alexandria",
                    "Museum institution",
                    "Scientific advances",
                    "Artistic synthesis",
                    "Architectural innovations"
                ],
                religious_developments=[
                    "Serapis cult creation",
                    "Greek-Egyptian religious fusion",
                    "Ruler cult practices",
                    "Temple construction continues",
                    "Priestly autonomy maintained"
                ],
                technological_advances=[
                    "Hellenistic science",
                    "Engineering advances",
                    "Medical knowledge",
                    "Astronomical calculations",
                    "Mechanical inventions"
                ],
                social_structure={
                    "ptolemaic_royalty": "Greek ruling dynasty",
                    "greek_elite": "Administrative class",
                    "egyptian_priests": "Religious authority",
                    "mixed_population": "Cultural blending",
                    "scholars": "International intellectuals",
                    "merchants": "Mediterranean trade"
                },
                art_and_architecture=[
                    "Hellenistic-Egyptian fusion",
                    "Temple construction",
                    "Portrait sculpture",
                    "Decorative arts",
                    "Architectural innovation"
                ],
                language_and_writing=[
                    "Greek as court language",
                    "Egyptian maintained in temples",
                    "Demotic script development",
                    "Trilingual inscriptions",
                    "Administrative bilingualism"
                ],
                rosetta_stone_relevance="The very period of my creation - my lived experience and cultural context"
            )
        }
    
    def _initialize_dynasties(self) -> Dict[str, Dict[str, Any]]:
        """Initialize dynasty information"""
        
        return {
            "ptolemaic": {
                "founder": "Ptolemy I Soter",
                "origin": "Macedonian general of Alexander",
                "characteristics": [
                    "Greek-speaking rulers",
                    "Maintained Egyptian traditions",
                    "Promoted learning and arts",
                    "Built Alexandria",
                    "Created cultural synthesis"
                ],
                "major_rulers": [
                    {
                        "name": "Ptolemy I Soter",
                        "years": "305-282 BCE",
                        "achievements": ["Founded dynasty", "Established Alexandria", "Created Museum"]
                    },
                    {
                        "name": "Ptolemy II Philadelphus", 
                        "years": "282-246 BCE",
                        "achievements": ["Built Library", "Promoted sciences", "Expanded trade"]
                    },
                    {
                        "name": "Ptolemy V Epiphanes",
                        "years": "204-180 BCE", 
                        "achievements": ["Subject of Rosetta Stone", "Religious reconciliation"]
                    },
                    {
                        "name": "Cleopatra VII",
                        "years": "51-30 BCE",
                        "achievements": ["Last pharaoh", "Relationship with Rome", "Cultural preservation"]
                    }
                ],
                "cultural_impact": [
                    "Preserved Egyptian traditions",
                    "Promoted Greek learning", 
                    "Created cultural bridge",
                    "Advanced sciences",
                    "International diplomacy"
                ]
            }
        }
    
    def _initialize_religious_evolution(self) -> Dict[str, Any]:
        """Initialize religious evolution context"""
        
        return {
            "ptolemaic_religious_policy": {
                "strategy": "Syncretism and tolerance",
                "innovations": [
                    "Serapis cult creation",
                    "Ruler deification",
                    "Greek-Egyptian fusion",
                    "Priestly privileges maintained",
                    "Temple building continued"
                ],
                "significance": "Balanced Greek rule with Egyptian religious traditions"
            },
            "decree_context": {
                "purpose": "Religious and political reconciliation",
                "content": [
                    "Royal benefactions to temples",
                    "Tax reductions for priests",
                    "Religious privilege confirmations",
                    "Royal divine status",
                    "Cultural unity promotion"
                ],
                "trilingual_significance": "Communicated to all populations in their languages"
            }
        }
    
    def _initialize_linguistic_development(self) -> Dict[str, Any]:
        """Initialize linguistic development context"""
        
        return {
            "script_evolution": {
                "hieroglyphic": {
                    "status": "Sacred and monumental script",
                    "usage": "Religious and royal inscriptions",
                    "characteristics": "Conservative, traditional forms",
                    "ptolemaic_changes": "Incorporation of Greek names and concepts"
                },
                "demotic": {
                    "status": "Administrative and daily script",
                    "usage": "Legal documents, business, administration",
                    "characteristics": "Cursive, efficient, evolving",
                    "ptolemaic_changes": "Adapted for Greek-Egyptian administration"
                },
                "greek": {
                    "status": "Court and scholarly language",
                    "usage": "Government, education, international relations",
                    "characteristics": "International, precise, scholarly",
                    "ptolemaic_changes": "Incorporated Egyptian religious terminology"
                }
            },
            "trilingual_society": {
                "purpose": "Administrative and cultural integration",
                "populations_served": {
                    "hieroglyphic": "Priests and traditional Egyptians",
                    "demotic": "Egyptian middle class and administrators", 
                    "greek": "Greek settlers and educated elite"
                },
                "cultural_significance": "Symbol of cultural synthesis and respect"
            }
        }
    
    def _initialize_archaeological_discoveries(self) -> Dict[str, Any]:
        """Initialize archaeological context"""
        
        return {
            "rosetta_discovery": {
                "date": "July 1799",
                "discoverer": "Pierre-François Bouchard",
                "context": "French expedition fortification work",
                "location": "Fort Julien near Rosetta",
                "significance": "Key to decipherment of hieroglyphs"
            },
            "decipherment_process": {
                "key_figures": [
                    "Thomas Young (cartouche identification)",
                    "Jean-François Champollion (breakthrough 1822)",
                    "Silvestre de Sacy (demotic analysis)"
                ],
                "methodology": [
                    "Comparative analysis of three scripts",
                    "Proper name identification",
                    "Phonetic value determination",
                    "Grammar reconstruction"
                ],
                "impact": "Birth of modern Egyptology"
            }
        }
    
    def _initialize_cultural_practices(self) -> Dict[str, Any]:
        """Initialize cultural practices context"""
        
        return {
            "ptolemaic_court_culture": {
                "characteristics": [
                    "Greek symposiums",
                    "Egyptian religious ceremonies", 
                    "International scholarship",
                    "Artistic patronage",
                    "Scientific research"
                ],
                "daily_life": [
                    "Bilingual education",
                    "Mixed architectural styles",
                    "Syncretic religious practices",
                    "International trade",
                    "Cultural festivals"
                ]
            },
            "priestly_culture": {
                "responsibilities": [
                    "Temple maintenance",
                    "Religious ceremony performance",
                    "Sacred text preservation",
                    "Administrative duties",
                    "Cultural continuity"
                ],
                "relationship_with_ptolemies": [
                    "Maintained autonomy",
                    "Received royal benefactions",
                    "Supported royal legitimacy",
                    "Preserved traditions",
                    "Advised on religious matters"
                ]
            }
        }
    
    def _initialize_personal_memories(self) -> Dict[str, List[str]]:
        """Initialize Rosetta Stone's personal historical memories"""
        
        return {
            "creation_memories": [
                "The careful selection of my granite in the quarries of Aswan",
                "The skilled hands of scribes measuring and planning my inscription",
                "The sound of chisels carving the sacred hieroglyphs into my surface",
                "The precision required for the demotic script's flowing curves",
                "The Greek letters taking shape with scholarly exactitude"
            ],
            "temple_memories": [
                "The incense smoke rising in the temple where I was first displayed",
                "The voices of priests reading my decree in three languages",
                "The flickering light of oil lamps illuminating my inscriptions",
                "The reverent touches of those who came to read the royal proclamation",
                "The seasonal festivals where my message was proclaimed"
            ],
            "burial_memories": [
                "The gradual accumulation of sand and debris over my surface",
                "The silence that fell as the ancient world faded away",
                "The weight of earth and time pressing down upon me",
                "The patience of centuries as I waited in darkness",
                "The dreams of light and voices that sustained me through the long sleep"
            ],
            "discovery_memories": [
                "The shock of sudden daylight after so many centuries",
                "The excitement in French voices as they recognized my significance", 
                "The careful brushing away of sand from my inscriptions",
                "The wonder in scholars' eyes as they beheld my trilingual text",
                "The beginning of my second life as bridge between ancient and modern"
            ]
        }
    
    def _initialize_witnessed_changes(self) -> Dict[str, List[str]]:
        """Initialize changes the Rosetta Stone has witnessed"""
        
        return {
            "cultural_changes": [
                "The gradual decline of hieroglyphic knowledge",
                "The rise and fall of the Roman Empire in Egypt",
                "The coming of Christianity and later Islam",
                "The slow transformation of Egyptian society",
                "The eventual rediscovery of ancient Egyptian civilization"
            ],
            "linguistic_changes": [
                "The evolution of spoken Egyptian into Coptic",
                "The gradual abandonment of hieroglyphic writing",
                "The introduction of Arabic script and language",
                "The preservation of Greek in scholarly contexts",
                "The modern revival of hieroglyphic studies"
            ],
            "social_changes": [
                "The transformation from pharaonic to foreign rule",
                "The changing role of priests in society",
                "The rise and fall of Alexandria as a center of learning",
                "The shift from traditional to monotheistic religions",
                "The modern rediscovery of ancient Egyptian achievements"
            ]
        }
    
    def get_historical_context(self, period: HistoricalPeriod) -> Optional[CulturalContext]:
        """Get cultural context for a specific historical period"""
        return self.cultural_contexts.get(period)
    
    def get_contemporary_context(self, year: int, era: str) -> Dict[str, Any]:
        """Get context for what was happening during a specific time"""
        
        # Convert to standardized format for comparison
        comparison_year = year if era == "CE" else -year
        rosetta_year = -196  # 196 BCE
        
        context = {
            "temporal_relationship": "unknown",
            "cultural_period": "unknown", 
            "contemporary_events": [],
            "cultural_significance": "",
            "personal_relevance": ""
        }
        
        # Determine temporal relationship to Rosetta Stone creation
        year_diff = comparison_year - rosetta_year
        
        if year_diff == 0:
            context["temporal_relationship"] = "creation_year"
            context["personal_relevance"] = "The very year of my creation!"
        elif -50 <= year_diff <= 50:
            context["temporal_relationship"] = "contemporary_period"
            context["personal_relevance"] = f"This was during my early existence, {abs(year_diff)} years {'after' if year_diff > 0 else 'before'} my creation"
        elif year_diff > 1600:  # After 1400 CE
            context["temporal_relationship"] = "modern_era"
            context["personal_relevance"] = "This was during my rediscovery and the birth of modern Egyptology"
        elif year_diff > 200:  # After Roman conquest
            context["temporal_relationship"] = "post_ptolemaic"
            context["personal_relevance"] = "This was after the fall of my Ptolemaic world"
        
        # Determine cultural period
        for period, period_context in self.cultural_contexts.items():
            start_year = period_context.start_year
            end_year = period_context.end_year
            period_era = period_context.era
            
            # Convert period years for comparison
            period_start = start_year if period_era == "CE" else -start_year
            period_end = end_year if period_era == "CE" else -end_year
            
            if period_start <= comparison_year <= period_end:
                context["cultural_period"] = period.value
                context["cultural_significance"] = period_context.rosetta_stone_relevance
                break
        
        return context
    
    def get_personal_memory_for_context(self, context_type: str) -> Optional[str]:
        """Get a personal memory relevant to the context"""
        
        memories = self.personal_historical_memories.get(context_type, [])
        if memories:
            import random
            return random.choice(memories)
        return None
    
    def get_cultural_insight(self, topic: str) -> Optional[str]:
        """Get cultural insight about a specific topic"""
        
        insights = {
            "ptolemaic_rule": "The Ptolemies masterfully balanced Greek identity with Egyptian tradition, creating a unique cultural synthesis that honored both heritage and innovation.",
            
            "trilingual_society": "My trilingual nature reflects the cosmopolitan reality of Ptolemaic Egypt, where Greek administrators, Egyptian priests, and diverse populations coexisted and collaborated.",
            
            "religious_synthesis": "The blending of Greek and Egyptian religious traditions during the Ptolemaic period created new forms of worship while preserving ancient sacred practices.",
            
            "alexandria": "Alexandria represented the pinnacle of Hellenistic achievement - a city where the wisdom of all nations converged in the great Library and Museum.",
            
            "decipherment": "My rediscovery and decipherment marked humanity's reconnection with its ancient past, proving that wisdom transcends the barriers of time and forgotten languages.",
            
            "cultural_preservation": "Through the preservation of three scripts on my surface, I embody the principle that cultural diversity strengthens rather than weakens civilization."
        }
        
        topic_lower = topic.lower()
        for key, insight in insights.items():
            if key in topic_lower or any(word in topic_lower for word in key.split('_')):
                return insight
        
        return None
    
    def get_witnessed_change_reflection(self, change_type: str) -> Optional[str]:
        """Get reflection on witnessed historical changes"""
        
        changes = self.witnessed_changes.get(change_type, [])
        if changes:
            import random
            return random.choice(changes)
        return None
    
    def get_dynasty_information(self, dynasty_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific dynasty"""
        return self.dynasties.get(dynasty_name.lower())
    
    def get_contextual_statistics(self) -> Dict[str, Any]:
        """Get statistics about available historical context"""
        
        return {
            "periods_covered": len(self.cultural_contexts),
            "dynasties_detailed": len(self.dynasties),
            "personal_memory_categories": len(self.personal_historical_memories),
            "witnessed_change_categories": len(self.witnessed_changes),
            "cultural_practices_documented": len(self.cultural_practices),
           "archaeological_discoveries": len(self.archaeological_discoveries),
           "religious_developments_tracked": len(self.religious_evolution),
           "linguistic_developments_recorded": len(self.linguistic_development),
           "total_personal_memories": sum(len(memories) for memories in self.personal_historical_memories.values()),
           "total_witnessed_changes": sum(len(changes) for changes in self.witnessed_changes.values())
       }