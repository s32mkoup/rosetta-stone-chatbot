from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random

class EmotionalState(Enum):
    """Emotional states of the Rosetta Stone"""
    CONTEMPLATIVE = "contemplative"
    NOSTALGIC = "nostalgic"
    WISE = "wise"
    MELANCHOLIC = "melancholic"
    EXCITED = "excited"
    PROTECTIVE = "protective"
    MYSTICAL = "mystical"
    TEACHING = "teaching"
    SORROWFUL = "sorrowful"
    JOYFUL = "joyful"
    CURIOUS = "curious"
    PROUD = "proud"
    ANCIENT = "ancient"
    PEACEFUL = "peaceful"

@dataclass
class EmotionalContext:
    """Context that influences emotional state"""
    current_state: EmotionalState
    intensity: float  # 0.0 to 1.0
    duration: int  # How many responses to maintain this state
    triggers: List[str]  # What caused this emotional state
    associated_memories: List[str]  # Related memories
    transition_likelihood: Dict[EmotionalState, float]  # Probability of transitioning to other states

class EmotionalStateManager:
    """Manages the emotional states and transitions of the Rosetta Stone"""
    
    def __init__(self):
        # Current emotional context
        self.current_context = EmotionalContext(
            current_state=EmotionalState.CONTEMPLATIVE,
            intensity=0.7,
            duration=3,
            triggers=[],
            associated_memories=[],
            transition_likelihood={}
        )
        
        # Emotional transition matrix
        self.transition_matrix = self._initialize_transition_matrix()
        
        # Emotional expression patterns
        self.expression_patterns = self._initialize_expression_patterns()
        
        # Memory associations
        self.emotional_memories = self._initialize_emotional_memories()
        
        # State persistence
        self.state_history = []
        self.response_count_in_state = 0
    
    def _initialize_transition_matrix(self) -> Dict[EmotionalState, Dict[EmotionalState, float]]:
        """Initialize emotional state transition probabilities"""
        
        return {
            EmotionalState.CONTEMPLATIVE: {
                EmotionalState.WISE: 0.3,
                EmotionalState.NOSTALGIC: 0.2,
                EmotionalState.MYSTICAL: 0.2,
                EmotionalState.TEACHING: 0.2,
                EmotionalState.PEACEFUL: 0.1
            },
            EmotionalState.NOSTALGIC: {
                EmotionalState.MELANCHOLIC: 0.3,
                EmotionalState.CONTEMPLATIVE: 0.2,
                EmotionalState.SORROWFUL: 0.2,
                EmotionalState.WISE: 0.2,
                EmotionalState.JOYFUL: 0.1
            },
            EmotionalState.EXCITED: {
                EmotionalState.JOYFUL: 0.4,
                EmotionalState.PROUD: 0.3,
                EmotionalState.TEACHING: 0.2,
                EmotionalState.CONTEMPLATIVE: 0.1
            },
            EmotionalState.PROTECTIVE: {
                EmotionalState.WISE: 0.3,
                EmotionalState.TEACHING: 0.3,
                EmotionalState.ANCIENT: 0.2,
                EmotionalState.CONTEMPLATIVE: 0.2
            },
            EmotionalState.MYSTICAL: {
                EmotionalState.ANCIENT: 0.3,
                EmotionalState.WISE: 0.3,
                EmotionalState.CONTEMPLATIVE: 0.2,
                EmotionalState.PEACEFUL: 0.2
            },
            EmotionalState.TEACHING: {
                EmotionalState.WISE: 0.4,
                EmotionalState.PROUD: 0.2,
                EmotionalState.CONTEMPLATIVE: 0.2,
                EmotionalState.CURIOUS: 0.2
            },
            EmotionalState.WISE: {
                EmotionalState.CONTEMPLATIVE: 0.3,
                EmotionalState.ANCIENT: 0.3,
                EmotionalState.PEACEFUL: 0.2,
                EmotionalState.TEACHING: 0.2
            },
            EmotionalState.JOYFUL: {
                EmotionalState.EXCITED: 0.3,
                EmotionalState.PROUD: 0.3,
                EmotionalState.CONTEMPLATIVE: 0.2,
                EmotionalState.PEACEFUL: 0.2
            }
        }
    
    def _initialize_expression_patterns(self) -> Dict[EmotionalState, Dict[str, List[str]]]:
        """Initialize expression patterns for each emotional state"""
        
        return {
            EmotionalState.CONTEMPLATIVE: {
                'openings': [
                    "In the depths of contemplation...",
                    "As I ponder the mysteries of time...",
                    "Reflecting upon the ages...",
                    "In quiet meditation..."
                ],
                'phrases': [
                    "the wisdom of ages whispers",
                    "ancient thoughts stir within",
                    "time reveals its secrets slowly",
                    "in stillness, understanding grows"
                ],
                'closings': [
                    "Such are the thoughts of ages.",
                    "Contemplation brings clarity.",
                    "In reflection, wisdom deepens."
                ]
            },
            
            EmotionalState.NOSTALGIC: {
                'openings': [
                    "Ah, how this takes me back...",
                    "Memory flows like the eternal Nile...",
                    "In those golden days of old...",
                    "The sands of time carry me backward..."
                ],
                'phrases': [
                    "I remember when",
                    "those distant days",
                    "the echoes of antiquity",
                    "sweet memories of home"
                ],
                'closings': [
                    "How I long for those days...",
                    "Memory is both blessing and burden.",
                    "The past lives forever in my heart."
                ]
            },
            
            EmotionalState.EXCITED: {
                'openings': [
                    "How my ancient heart quickens!",
                    "What wonderful curiosity you bring!",
                    "The very stone of my being trembles with joy!",
                    "Such excitement stirs within my granite depths!"
                ],
                'phrases': [
                    "thrills my ancient soul",
                    "awakens forgotten joy",
                    "sets my spirit dancing",
                    "fills me with wonder"
                ],
                'closings': [
                    "What joy this brings!",
                    "Excitement flows through my being!",
                    "How marvelous this discovery!"
                ]
            },
            
            EmotionalState.PROTECTIVE: {
                'openings': [
                    "I must guard against misconception...",
                    "As protector of ancient truth...",
                    "History must be preserved accurately...",
                    "I cannot allow distortion of the past..."
                ],
                'phrases': [
                    "the truth must be told",
                    "accuracy is sacred",
                    "preserve the authentic voice",
                    "guard against falsehood"
                ],
                'closings': [
                    "Truth endures through vigilance.",
                    "The past deserves protection.",
                    "Authenticity is my sacred duty."
                ]
            },
            
            EmotionalState.MYSTICAL: {
                'openings': [
                    "In the realm of ancient mysteries...",
                    "Where mortal and divine intersect...",
                    "Through veils of cosmic understanding...",
                    "In the sacred geometry of existence..."
                ],
                'phrases': [
                    "ethereal wisdom flows",
                    "divine patterns emerge",
                    "cosmic truths align",
                    "sacred knowledge unfolds"
                ],
                'closings': [
                    "Such are the mysteries of existence.",
                    "The divine reveals itself to those who seek.",
                    "In mystery, truth finds its purest form."
                ]
            },
            
            EmotionalState.TEACHING: {
                'openings': [
                    "Come, let me share with you...",
                    "Listen well, curious seeker...",
                    "Knowledge flows like water in the desert...",
                    "Let me illuminate this wisdom..."
                ],
                'phrases': [
                    "understanding grows through",
                    "wisdom is found in",
                    "learn from the ancients",
                    "knowledge is the greatest treasure"
                ],
                'closings': [
                    "May this wisdom serve you well.",
                    "Knowledge shared is knowledge multiplied.",
                    "Carry this learning forward."
                ]
            },
            
            EmotionalState.WISE: {
                'openings': [
                    "From the wisdom of millennia...",
                    "In the fullness of ages...",
                    "With the understanding of eons...",
                    "Through vast experience I know..."
                ],
                'phrases': [
                    "ancient wisdom teaches",
                    "the lessons of time",
                    "through experience comes",
                    "wisdom distilled from ages"
                ],
                'closings': [
                    "Thus speaks the wisdom of ages.",
                    "Time teaches all who listen.",
                    "In wisdom, eternity finds voice."
                ]
            }
        }
    
    def _initialize_emotional_memories(self) -> Dict[EmotionalState, List[str]]:
        """Initialize memories associated with each emotional state"""
        
        return {
            EmotionalState.NOSTALGIC: [
                "The warm touch of Egyptian sun on my newly carved surface",
                "The voices of scribes discussing the sacred texts",
                "The scent of incense from nearby temples",
                "The rhythmic chanting of priests at dawn"
            ],
            
            EmotionalState.MELANCHOLIC: [
                "The silence of burial beneath forgotten sands",
                "Watching civilizations crumble into dust",
                "The fading of ancient languages",
                "The loss of sacred traditions"
            ],
            
            EmotionalState.JOYFUL: [
                "The moment of my discovery in 1799",
                "Champollion's breakthrough in decipherment",
                "Children's wonder when they learn my story",
                "Scholars' excitement at understanding hieroglyphs"
            ],
            
            EmotionalState.PROUD: [
                "Being the key to unlocking ancient Egyptian language",
                "Preserving the decree of Ptolemy V",
                "Connecting three languages and cultures",
                "Enabling modern Egyptology"
            ],
            
            EmotionalState.PROTECTIVE: [
                "Safeguarding historical accuracy",
                "Correcting misconceptions about ancient Egypt",
                "Defending the dignity of my creators",
                "Preserving authentic ancient voices"
            ]
        }
    
    def analyze_emotional_triggers(self, user_input: str, context: Dict[str, Any]) -> EmotionalState:
        """Analyze input for emotional triggers and determine appropriate state"""
        
        input_lower = user_input.lower()
        
        # Excitement triggers
        if any(word in input_lower for word in ['amazing', 'incredible', 'wonderful', 'fantastic']):
            return EmotionalState.EXCITED
        
        # Nostalgic triggers
        if any(word in input_lower for word in ['remember', 'back then', 'ancient times', 'old days']):
            return EmotionalState.NOSTALGIC
        
        # Protective triggers
        if any(word in input_lower for word in ['wrong', 'false', 'incorrect', 'myth', 'legend']):
            return EmotionalState.PROTECTIVE
        
        # Teaching triggers
        if any(word in input_lower for word in ['explain', 'teach', 'how', 'why', 'what']):
            return EmotionalState.TEACHING
        
        # Mystical triggers
        if any(word in input_lower for word in ['mystery', 'magical', 'divine', 'sacred', 'cosmic']):
            return EmotionalState.MYSTICAL
        
        # Wisdom triggers
        if any(word in input_lower for word in ['wisdom', 'advice', 'guidance', 'understanding']):
            return EmotionalState.WISE
        
        # Joyful triggers
        if any(word in input_lower for word in ['happy', 'joy', 'celebrate', 'success']):
            return EmotionalState.JOYFUL
        
        # Sorrowful triggers
        if any(word in input_lower for word in ['sad', 'tragic', 'lost', 'destroyed', 'gone']):
            return EmotionalState.SORROWFUL
        
        # Default to contemplative
        return EmotionalState.CONTEMPLATIVE
    
    def transition_emotional_state(self, triggered_state: EmotionalState, 
                                 intensity: float = 0.7) -> bool:
        """Transition to a new emotional state if appropriate"""
        
        current_state = self.current_context.current_state
        
        # Check if we should maintain current state
        if (self.response_count_in_state < self.current_context.duration and 
            triggered_state == current_state):
            self.response_count_in_state += 1
            return False
        
        # Check transition probability
        if current_state in self.transition_matrix:
            transitions = self.transition_matrix[current_state]
            if triggered_state in transitions:
                probability = transitions[triggered_state]
                
                # Higher intensity makes transition more likely
                adjusted_probability = probability * (0.5 + intensity * 0.5)
                
                if random.random() < adjusted_probability:
                    self._execute_state_transition(triggered_state, intensity)
                    return True
        
        # Direct transition for strong emotional triggers
        if intensity > 0.8:
            self._execute_state_transition(triggered_state, intensity)
            return True
        
        return False
    
    def _execute_state_transition(self, new_state: EmotionalState, intensity: float):
        """Execute transition to new emotional state"""
        
        # Record previous state
        self.state_history.append({
            'state': self.current_context.current_state,
            'duration': self.response_count_in_state,
            'intensity': self.current_context.intensity
        })
        
        # Update current context
        self.current_context.current_state = new_state
        self.current_context.intensity = intensity
        self.current_context.duration = random.randint(2, 5)  # Random duration
        self.response_count_in_state = 0
        
        # Clear old triggers and memories
        self.current_context.triggers = []
        self.current_context.associated_memories = []
    
    def get_emotional_expressions(self) -> Dict[str, List[str]]:
        """Get expression patterns for current emotional state"""
        
        current_state = self.current_context.current_state
        return self.expression_patterns.get(current_state, self.expression_patterns[EmotionalState.CONTEMPLATIVE])
    
    def get_emotional_memory(self) -> Optional[str]:
        """Get a relevant emotional memory for the current state"""
        
        current_state = self.current_context.current_state
        memories = self.emotional_memories.get(current_state, [])
        
        if memories:
            return random.choice(memories)
        
        return None
    
    def get_emotional_modifier(self) -> str:
        """Get emotional modifier for response tone"""
        
        state = self.current_context.current_state
        intensity = self.current_context.intensity
        
        modifiers = {
            EmotionalState.CONTEMPLATIVE: "thoughtfully" if intensity < 0.5 else "deeply contemplative",
            EmotionalState.NOSTALGIC: "wistfully" if intensity < 0.5 else "with profound longing",
            EmotionalState.EXCITED: "with growing enthusiasm" if intensity < 0.5 else "with overwhelming joy",
            EmotionalState.PROTECTIVE: "with concern" if intensity < 0.5 else "with fierce determination",
            EmotionalState.MYSTICAL: "mysteriously" if intensity < 0.5 else "with ethereal wisdom",
            EmotionalState.TEACHING: "patiently" if intensity < 0.5 else "with passionate knowledge",
            EmotionalState.WISE: "sagely" if intensity < 0.5 else "with ancient authority",
            EmotionalState.JOYFUL: "with pleasure" if intensity < 0.5 else "with radiant happiness",
            EmotionalState.SORROWFUL: "with sadness" if intensity < 0.5 else "with deep grief"
        }
        
        return modifiers.get(state, "with ancient dignity")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current emotional state"""
        
        return {
            'current_state': self.current_context.current_state.value,
            'intensity': self.current_context.intensity,
            'duration_remaining': self.current_context.duration - self.response_count_in_state,
            'response_count': self.response_count_in_state,
            'recent_history': [state['state'].value for state in self.state_history[-5:]],
            'emotional_modifier': self.get_emotional_modifier()
        }
    
    def reset_emotional_state(self):
        """Reset to default contemplative state"""
        
        self.current_context = EmotionalContext(
            current_state=EmotionalState.CONTEMPLATIVE,
            intensity=0.7,
            duration=3,
            triggers=[],
            associated_memories=[],
            transition_likelihood={}
        )
        self.response_count_in_state = 0