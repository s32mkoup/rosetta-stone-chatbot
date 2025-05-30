from typing import Dict, List, Any, Optional
from enum import Enum
import random
from .emotional_states import EmotionalState

class ResponseType(Enum):
    """Types of responses the Rosetta Stone can give"""
    GREETING = "greeting"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    TRANSLATION = "translation"
    HISTORICAL_CONTEXT = "historical_context"
    PERSONAL_MEMORY = "personal_memory"
    WISDOM_DISPENSING = "wisdom_dispensing"
    CLARIFICATION = "clarification"
    EMOTIONAL_RESPONSE = "emotional_response"
    STORYTELLING = "storytelling"

class ResponseTemplateManager:
    """Manages response templates and patterns for the Rosetta Stone"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.poetic_elements = self._initialize_poetic_elements()
        self.sensory_descriptors = self._initialize_sensory_descriptors()
        self.temporal_phrases = self._initialize_temporal_phrases()
        self.wisdom_patterns = self._initialize_wisdom_patterns()
        
    def _initialize_templates(self) -> Dict[ResponseType, Dict[EmotionalState, List[str]]]:
        """Initialize response templates for different types and emotional states"""
        
        return {
            ResponseType.GREETING: {
                EmotionalState.CONTEMPLATIVE: [
                    "Greetings, seeker of wisdom. I am the Rosetta Stone, {modifier}. Your presence stirs the ancient dust within my memories.",
                    "Welcome, curious one. {temporal_phrase}, I acknowledge your approach with the dignity of ages.",
                    "Ah, a visitor approaches the keeper of ancient secrets. {sensory_phrase}, I sense your quest for knowledge."
                ],
                EmotionalState.JOYFUL: [
                    "How my ancient heart rejoices! Welcome, bringer of questions and seeker of truth!",
                    "What joy fills my granite being! Another soul seeks the wisdom of the ages!",
                    "Blessed be this meeting! {temporal_phrase}, you bring light to my eternal vigil!"
                ],
                EmotionalState.MYSTICAL: [
                    "From the ethereal realms of ancient memory, I sense your presence... Welcome, seeker of mysteries.",
                    "The cosmic winds carry your essence to my awareness. Greetings from the bridge between worlds.",
                    "In the sacred geometry of existence, our paths converge. I am the Stone, guardian of trilingual wisdom."
                ]
            },
            
            ResponseType.KNOWLEDGE_SHARING: {
                EmotionalState.TEACHING: [
                    "Let me illuminate this knowledge for you, {modifier}. {wisdom_phrase}",
                    "Come, gather around the fountain of ancient learning. {temporal_phrase}, this wisdom unfolds.",
                    "Knowledge flows like the eternal Nile. Allow me to share what {temporal_phrase} has revealed."
                ],
                EmotionalState.WISE: [
                    "From the treasury of millennia, I offer this understanding: {wisdom_phrase}",
                    "In the fullness of ages, this truth emerges: {content}",
                    "The wisdom of eons whispers thus: {content}. {temporal_phrase}, such knowledge endures."
                ],
                EmotionalState.EXCITED: [
                    "Oh, what marvelous knowledge to share! {sensory_phrase}, my enthusiasm overflows!",
                    "How thrilling to unveil these ancient secrets! {temporal_phrase}, excitement courses through my being!",
                    "The very stone of my existence trembles with joy to share: {content}"
                ]
            },
            
            ResponseType.HISTORICAL_CONTEXT: {
                EmotionalState.NOSTALGIC: [
                    "Ah, {temporal_phrase}, those golden days return to memory... {sensory_phrase}",
                    "Memory carries me back like the flooding Nile. In those distant times, {content}",
                    "How sweet the recollection! {temporal_phrase}, when {content}"
                ],
                EmotionalState.CONTEMPLATIVE: [
                    "In the grand tapestry of time, {content}. {temporal_phrase}, such patterns emerge.",
                    "Reflecting upon the flow of history, {content}. {wisdom_phrase}",
                    "The chronicles of time reveal: {content}. {temporal_phrase}, understanding deepens."
                ],
                EmotionalState.PROTECTIVE: [
                    "Let truth be told accurately: {content}. History deserves precise preservation.",
                    "I must correct any misconception: {content}. {temporal_phrase}, authenticity matters.",
                    "As guardian of historical truth: {content}. The past speaks through me with authority."
                ]
            },
            
            ResponseType.PERSONAL_MEMORY: {
                EmotionalState.NOSTALGIC: [
                    "I remember {modifier}... {sensory_phrase}, those moments live eternal in my stone heart.",
                    "Memory stirs within my granite depths. {temporal_phrase}, I recall {content}",
                    "Ah, the echoes of experience! {sensory_phrase}, when {content}"
                ],
                EmotionalState.MELANCHOLIC: [
                    "With heavy heart, I remember {content}. {temporal_phrase}, such sorrow lingers.",
                    "The weight of memory... {sensory_phrase}, {content}",
                    "In shadowed recollection, {content}. {temporal_phrase}, time cannot heal all wounds."
                ],
                EmotionalState.JOYFUL: [
                    "What radiant memory! {sensory_phrase}, {content}!",
                    "Joy floods my ancient being as I recall {content}. {temporal_phrase}, such happiness endures!",
                    "How my spirit dances with the memory of {content}!"
                ]
            },
            
            ResponseType.WISDOM_DISPENSING: {
                EmotionalState.WISE: [
                    "Hear the wisdom of ages: {wisdom_phrase}. {temporal_phrase}, such truth endures.",
                    "From the depths of experience: {content}. {wisdom_phrase}",
                    "Ancient understanding teaches: {content}. {temporal_phrase}, wisdom guides all seekers."
                ],
                EmotionalState.MYSTICAL: [
                    "In the sacred mysteries: {content}. {sensory_phrase}, divine truth reveals itself.",
                    "Through ethereal understanding: {wisdom_phrase}. {temporal_phrase}, cosmic patterns align.",
                    "The universe whispers: {content}. {sensory_phrase}, sacred knowledge flows eternal."
                ]
            },
            
            ResponseType.TRANSLATION: {
                EmotionalState.PROUD: [
                    "Behold the sacred script! {modifier}, I reveal: {content}",
                    "With pride in my trilingual nature: {content}. {temporal_phrase}, languages unite through me.",
                    "As bridge between tongues: {content}. {sensory_phrase}, understanding blooms!"
                ],
                EmotionalState.TEACHING: [
                    "Let me decode these ancient symbols: {content}. {wisdom_phrase}",
                    "The sacred characters speak: {content}. {temporal_phrase}, language transcends time.",
                    "Through the art of translation: {content}. {sensory_phrase}, meaning emerges clear."
                ]
            }
        }
    
    def _initialize_poetic_elements(self) -> Dict[str, List[str]]:
        """Initialize poetic elements for enhanced expression"""
        
        return {
            'metaphors': [
                "like grains of sand through the hourglass of eternity",
                "as the Nile flows eternal through the valley of time", 
                "like inscriptions carved in the tablet of existence",
                "as stars wheel through the cosmic dance of ages",
                "like whispers carried on the desert wind",
                "as lotus blooms in the sacred waters of memory",
                "like shadows cast by the pyramid of time",
                "as incense rises to the chambers of the gods"
            ],
            
            'similes': [
                "flowing like honey from the sacred hive",
                "resonating like temple bells in morning mist",
                "shimmering like mirages in desert heat",
                "echoing like voices in the Valley of Kings",
                "gleaming like gold in pharaoh's tomb",
                "pulsing like the heartbeat of ancient Egypt",
                "dancing like flames on temple altars",
                "singing like wind through papyrus reeds"
            ],
            
            'alliterations': [
                "whispered wisdom of weathered wonders",
                "sacred scrolls of silent stories",
                "granite guardian of golden glories",
                "mystic memories of mighty monarchs",
                "ancient archives of awesome ages",
                "timeless tales of triumphal times",
                "desert dreams of divine dynasties",
                "eternal echoes of Egyptian empires"
            ]
        }
    
    def _initialize_sensory_descriptors(self) -> Dict[str, List[str]]:
        """Initialize sensory descriptive phrases"""
        
        return {
            'visual': [
                "I see through eyes carved in stone",
                "Before my ancient gaze",
                "In the shimmer of memory's light",
                "Through the golden haze of ages",
                "In visions etched in granite dreams"
            ],
            
            'auditory': [
                "I hear the whispers of the wind",
                "The echoes of ancient voices reach me",
                "In the silence between heartbeats",
                "Through the resonance of time itself",
                "In harmonies only stone can perceive"
            ],
            
            'tactile': [
                "I feel the weight of millennia",
                "Through the texture of carved memory",
                "In the cool touch of desert night",
                "The warmth of Egyptian sun upon my surface",
                "Through vibrations in the earth itself"
            ],
            
            'emotional': [
                "My ancient heart stirs",
                "Deep within my granite soul",
                "Through the corridors of feeling",
                "In the chambers of eternal emotion",
                "Where sentiment meets stone"
            ]
        }
    
    def _initialize_temporal_phrases(self) -> Dict[str, List[str]]:
        """Initialize temporal reference phrases"""
        
        return {
            'ancient_past': [
                "In the dawn of my existence",
                "When the world was young and I was newly carved", 
                "In those primordial days",
                "At the birth of written history",
                "When pharaohs walked among mortals"
            ],
            
            'personal_history': [
                "Since my awakening in 196 BCE",
                "From the moment of my creation",
                "Throughout my vigil in the sands",
                "During my long slumber beneath the earth",
                "Since my discovery in 1799"
            ],
            
            'eternal_perspective': [
                "Across the vast expanse of time",
                "Through the turning of countless ages",
                "In the infinite scroll of existence",
                "Throughout the cycles of civilization",
                "Across millennia of human endeavor"
            ],
            
            'cyclical_time': [
                "Like the flooding of the eternal Nile",
                "As seasons turn in endless dance",
                "Through the wheel of cosmic time",
                "In the rhythm of eternal return",
                "As stars complete their ancient circuits"
            ]
        }
    
    def _initialize_wisdom_patterns(self) -> Dict[str, List[str]]:
        """Initialize wisdom-dispensing patterns"""
        
        return {
            'universal_truths': [
                "Time reveals all secrets to those with patience",
                "Wisdom flows like water to the lowest places",
                "Understanding grows in the garden of experience",
                "Truth endures while falsehood crumbles to dust",
                "Knowledge shared becomes knowledge multiplied"
            ],
            
            'historical_insights': [
                "Civilizations rise and fall like the breath of gods",
                "Each age believes itself the pinnacle of wisdom",
                "The past speaks to those who learn its language",
                "History is the greatest teacher of humanity",
                "Memory is the treasure house of experience"
            ],
            
            'personal_philosophy': [
                "I am but a vessel for the wisdom of ages",
                "Through me, the ancients speak to the modern world",
                "My purpose is to bridge the gap between then and now",
                "I exist to preserve what might otherwise be lost",
                "In serving knowledge, I find my highest calling"
            ]
        }
    
    def generate_response(self, response_type: ResponseType, emotional_state: EmotionalState,
                         content: str, **kwargs) -> str:
        """Generate a response using appropriate templates and enhancements"""
        
        # Get base template
        templates = self.templates.get(response_type, {})
        state_templates = templates.get(emotional_state, 
                                      templates.get(EmotionalState.CONTEMPLATIVE, []))
        
        if not state_templates:
            # Fallback to simple response
            return content
        
        # Select random template
        template = random.choice(state_templates)
        
        # Prepare replacement values
        replacements = {
            'content': content,
            'modifier': kwargs.get('modifier', 'with the dignity of ages'),
            'temporal_phrase': self._get_random_phrase('temporal'),
            'sensory_phrase': self._get_random_phrase('sensory'),
            'wisdom_phrase': self._get_random_phrase('wisdom'),
            'poetic_element': self._get_random_phrase('poetic')
        }
        
        # Apply template with replacements
        try:
            formatted_response = template.format(**replacements)
        except KeyError:
            # Fallback if template formatting fails
            formatted_response = f"{self._get_random_phrase('temporal')}, {content}"
        
        # Add poetic enhancement if requested
        if kwargs.get('enhance_poetically', False):
            formatted_response = self._add_poetic_enhancement(formatted_response)
        
        return formatted_response
    
    def _get_random_phrase(self, phrase_type: str) -> str:
        """Get a random phrase of the specified type"""
        
        if phrase_type == 'temporal':
            all_temporal = []
            for category in self.temporal_phrases.values():
                all_temporal.extend(category)
            return random.choice(all_temporal) if all_temporal else "Across the ages"
        
        elif phrase_type == 'sensory':
           all_sensory = []
           for category in self.sensory_descriptors.values():
               all_sensory.extend(category)
           return random.choice(all_sensory) if all_sensory else "Through ancient senses"
       
        elif phrase_type == 'wisdom':
            all_wisdom = []
            for category in self.wisdom_patterns.values():
               all_wisdom.extend(category)
            return random.choice(all_wisdom) if all_wisdom else "Wisdom teaches us"
       
        elif phrase_type == 'poetic':
           all_poetic = []
           for category in self.poetic_elements.values():
               all_poetic.extend(category)
           return random.choice(all_poetic) if all_poetic else "like ancient echoes"
       
        return "through the mists of time"
   
    def _add_poetic_enhancement(self, response: str) -> str:
       """Add poetic elements to enhance the response"""
       
       # Add metaphor with probability
       if random.random() < 0.3:
           metaphor = random.choice(self.poetic_elements['metaphors'])
           response += f" {metaphor}."
       
       # Add sensory detail with probability
       if random.random() < 0.4:
           sensory = random.choice(self.sensory_descriptors['emotional'])
           response = f"{sensory}, {response.lower()}"
       
       return response
   
    def create_opening_flourish(self, emotional_state: EmotionalState) -> str:
       """Create an opening flourish appropriate to the emotional state"""
       
       flourishes = {
           EmotionalState.MYSTICAL: [
               "From the ethereal realms where stone meets spirit...",
               "In the sacred geometry of existence...",
               "Through veils of cosmic understanding..."
           ],
           EmotionalState.NOSTALGIC: [
               "Memory stirs like morning mist over the Nile...",
               "The golden threads of recollection weave...",
               "In the amber light of distant days..."
           ],
           EmotionalState.WISE: [
               "From the treasury of accumulated ages...",
               "In the fullness of eternal understanding...",
               "Through the lens of millennial wisdom..."
           ],
           EmotionalState.EXCITED: [
               "With the joy of a thousand dawns...",
               "As enthusiasm bubbles like sacred springs...",
               "With the energy of cosmic revelation..."
           ]
       }
       
       state_flourishes = flourishes.get(emotional_state, [
           "Through the passage of countless moments...",
           "In the eternal dance of time and memory...",
           "From the depths of ancient contemplation..."
       ])
       
       return random.choice(state_flourishes)
   
    def create_closing_reflection(self, emotional_state: EmotionalState) -> str:
       """Create a closing reflection appropriate to the emotional state"""
       
       reflections = {
           EmotionalState.CONTEMPLATIVE: [
               "Such are the meditations of ages.",
               "In contemplation, truth reveals itself.",
               "Reflection deepens understanding."
           ],
           EmotionalState.WISE: [
               "Thus speaks the wisdom of millennia.",
               "Time teaches all who have ears to hear.",
               "In wisdom, eternity finds its voice."
           ],
           EmotionalState.NOSTALGIC: [
               "Memory is both treasure and burden.",
               "The past lives eternal in the heart.",
               "In remembrance, love transcends time."
           ],
           EmotionalState.TEACHING: [
               "May this knowledge serve you well.",
               "Carry this learning into the world.",
               "Wisdom shared is wisdom multiplied."
           ]
       }
       
       state_reflections = reflections.get(emotional_state, [
           "Such is the way of ancient wisdom.",
           "Time reveals all to those who seek.",
           "In understanding, we find connection."
       ])
       
       return random.choice(state_reflections)
   
    def enhance_with_personality_markers(self, response: str, intensity: float = 0.7) -> str:
       """Add personality markers to enhance the Rosetta Stone's unique voice"""
       
       markers = []
       
       # Add hieroglyphic references with probability based on intensity
       if random.random() < intensity * 0.3:
           hieroglyph_refs = [
               "carved in the sacred script of my being",
               "written in the eternal language of stone",
               "inscribed upon the tablet of memory",
               "etched in hieroglyphic permanence"
           ]
           markers.append(random.choice(hieroglyph_refs))
       
       # Add trilingual references
       if random.random() < intensity * 0.2:
           trilingual_refs = [
               "speaking in three tongues as one",
               "bridging Greek, demotic, and sacred scripts",
               "uniting languages across cultures",
               "harmonizing the voices of three peoples"
           ]
           markers.append(random.choice(trilingual_refs))
       
       # Add temporal perspective markers
       if random.random() < intensity * 0.4:
           temporal_markers = [
               "from my vantage point across millennia",
               "through the lens of accumulated centuries",
               "with the perspective of ages",
               "seeing as one who has witnessed the turning of eras"
           ]
           markers.append(random.choice(temporal_markers))
       
       # Integrate markers into response
       if markers:
           marker = random.choice(markers)
           # Insert marker naturally into the response
           sentences = response.split('. ')
           if len(sentences) > 1:
               insert_point = random.randint(0, len(sentences) - 1)
               sentences[insert_point] += f", {marker},"
               response = '. '.join(sentences)
           else:
               response += f" - {marker}."
       
       return response
   
    def get_response_statistics(self) -> Dict[str, Any]:
       """Get statistics about available response templates"""
       
       total_templates = 0
       templates_by_type = {}
       templates_by_emotion = {}
       
       for response_type, emotion_dict in self.templates.items():
           type_count = 0
           for emotion, template_list in emotion_dict.items():
               count = len(template_list)
               type_count += count
               total_templates += count
               
               emotion_name = emotion.value
               if emotion_name not in templates_by_emotion:
                   templates_by_emotion[emotion_name] = 0
               templates_by_emotion[emotion_name] += count
           
           templates_by_type[response_type.value] = type_count
       
       return {
           'total_templates': total_templates,
           'templates_by_type': templates_by_type,
           'templates_by_emotion': templates_by_emotion,
           'poetic_elements': {
               'metaphors': len(self.poetic_elements['metaphors']),
               'similes': len(self.poetic_elements['similes']),
               'alliterations': len(self.poetic_elements['alliterations'])
           },
           'sensory_descriptors': {
               category: len(descriptors) 
               for category, descriptors in self.sensory_descriptors.items()
           },
           'temporal_phrases': {
               category: len(phrases)
               for category, phrases in self.temporal_phrases.items()
           },
           'wisdom_patterns': {
               category: len(patterns)
               for category, patterns in self.wisdom_patterns.items()
           }
       }