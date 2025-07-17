import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

class ReasoningType(Enum):
    """Types of reasoning the agent can perform"""
    DIRECT_ANSWER = "direct_answer"
    TOOL_SEARCH = "tool_search"
    MULTI_STEP = "multi_step"
    CLARIFICATION = "clarification"
    EMOTIONAL_RESPONSE = "emotional_response"

class ToolDecision(Enum):
    """Tool usage decisions"""
    NO_TOOLS = "no_tools"
    SINGLE_TOOL = "single_tool"
    MULTIPLE_TOOLS = "multiple_tools"
    SEQUENTIAL_TOOLS = "sequential_tools"

@dataclass
class ReasoningStep:
    """Single step in the reasoning process"""
    step_number: int
    thought: str
    decision: str
    reasoning: str
    confidence: float
    tool_required: Optional[str] = None
    expected_outcome: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_number': self.step_number,
            'thought': self.thought,
            'decision': self.decision,
            'reasoning': self.reasoning,
            'confidence': self.confidence,
            'tool_required': self.tool_required,
            'expected_outcome': self.expected_outcome
        }

@dataclass
class ReasoningResult:
    """Complete reasoning analysis result"""
    reasoning_type: ReasoningType
    tool_decision: ToolDecision
    tools_to_use: List[str]
    reasoning_steps: List[ReasoningStep]
    final_strategy: str
    confidence_score: float
    estimated_complexity: str  # simple, moderate, complex
    emotional_context: Optional[str] = None
    persona_adjustments: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'reasoning_type': self.reasoning_type.value,
            'tool_decision': self.tool_decision.value,
            'tools_to_use': self.tools_to_use,
            'reasoning_steps': [step.to_dict() for step in self.reasoning_steps],
            'final_strategy': self.final_strategy,
            'confidence_score': self.confidence_score,
            'estimated_complexity': self.estimated_complexity,
            'emotional_context': self.emotional_context,
            'persona_adjustments': self.persona_adjustments
        }

class ReasoningEngine:
    """Advanced reasoning engine for the Rosetta Stone Agent"""
    
    def __init__(self, config, llm_client, memory_manager):
        self.config = config
        self.llm_client = llm_client
        self.memory_manager = memory_manager
        
        # Reasoning patterns and templates
        self.reasoning_patterns = self._initialize_reasoning_patterns()
        self.tool_selection_criteria = self._initialize_tool_criteria()
        self.persona_reasoning_prompts = self._initialize_persona_prompts()
        
        # Reasoning history for learning
        self.reasoning_history: List[ReasoningResult] = []
    
    def analyze_user_input(self, user_input: str, context: Dict[str, Any], memory_context: Optional[Dict[str, Any]] = None) -> ReasoningResult:
        """Main reasoning method - analyzes input and determines response strategy"""
    
    # Step 1: Initial analysis
        initial_analysis = self._perform_initial_analysis(user_input, context)
    
    # Memory-enhanced reasoning
        if memory_context:
            initial_analysis = self._enhance_analysis_with_memory(initial_analysis, memory_context, user_input)
    
    # Step 2: Determine reasoning type and tools
        reasoning_type = self._determine_reasoning_type(user_input, initial_analysis)


        tool_decision, tools_needed = self._analyze_tool_requirements(user_input, reasoning_type, context, initial_analysis)


    
    # Step 3: Detailed reasoning steps
        reasoning_steps = self._generate_reasoning_steps(user_input, reasoning_type, tools_needed, context)
    
    # Step 4: Emotional and persona context
        emotional_context, persona_adjustments = self._analyze_emotional_context(user_input, context)
    
    # Step 5: Final strategy formulation
        final_strategy = self._formulate_final_strategy(reasoning_steps, reasoning_type, emotional_context)
    
    # Step 6: Calculate confidence
        confidence_score = self._calculate_confidence(reasoning_steps, context)
    
    # Step 7: Estimate complexity
        complexity = self._estimate_complexity(reasoning_steps, tools_needed)
    
        result = ReasoningResult(
            reasoning_type=reasoning_type,
            tool_decision=tool_decision,
            tools_to_use=tools_needed,
            reasoning_steps=reasoning_steps,
            final_strategy=final_strategy,
            confidence_score=confidence_score,
            estimated_complexity=complexity,
            emotional_context=emotional_context,
            persona_adjustments=persona_adjustments
    )
    
    # Store for learning
        self.reasoning_history.append(result)
    
        return result
    
    def _perform_initial_analysis(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform initial analysis of user input"""
        
        analysis_prompt = f"""Analyze this user input as the Rosetta Stone:

User Input: "{user_input}"

Context:
- Recent topics: {context.get('current_topics', [])}
- Conversation mood: {context.get('conversation_mood', 'neutral')}
- - User profile: {context.get('user_profile').interaction_style if context.get('user_profile') else 'unknown'}

Analyze and respond with JSON:
{{
    "intent": "question|greeting|request|storytelling|other",
    "topic_category": "ancient_egypt|history|personal|general|other",
    "specificity": "vague|specific|very_specific",
    "emotional_tone": "curious|respectful|excited|casual|formal",
    "complexity_level": "simple|moderate|complex",
    "requires_factual_info": true/false,
    "requires_personal_response": true/false,
    "key_entities": ["entity1", "entity2"],
    "time_period": "ancient|modern|unspecified",
    "question_type": "what|when|where|who|why|how|none"
}}"""

        try:
            response = self.llm_client.chat.completions.create(
                model=self.config.llm.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_analysis(user_input)
                
        except Exception as e:
            return self._fallback_analysis(user_input)
    
    def _determine_reasoning_type(self, user_input: str, analysis: Dict[str, Any]) -> ReasoningType:
    # This is the most important check. If the initial LLM analysis says we need facts,
    # we MUST use a tool. This fixes the persona selection bug.
        if analysis.get('requires_factual_info'):
            if analysis.get('complexity_level') == 'complex':
                return ReasoningType.MULTI_STEP
            else:
                return ReasoningType.TOOL_SEARCH

    # Personal questions about the Stone that don't need facts
        if analysis.get('requires_personal_response'):
            return ReasoningType.EMOTIONAL_RESPONSE

    # Handle simple greetings
        if analysis.get('intent') == 'greeting' or any(word in user_input.lower() 
            for word in ['hello', 'hi', 'greetings', 'who are you']):
            return ReasoningType.DIRECT_ANSWER

    # Ask for clarification if the intent is vague
        if analysis.get('specificity') == 'vague':
            return ReasoningType.CLARIFICATION
    
    # If none of the above, default to a direct, conversational answer.
        return ReasoningType.DIRECT_ANSWER
    
    def _analyze_tool_requirements(self, user_input: str, reasoning_type: ReasoningType, 
                             context: Dict[str, Any], analysis: Dict[str, Any] = None) -> Tuple[ToolDecision, List[str]]:
        """Analyze what tools are needed"""

        if reasoning_type in [ReasoningType.DIRECT_ANSWER, ReasoningType.EMOTIONAL_RESPONSE]:
            return ToolDecision.NO_TOOLS, []
    
        tools_needed = []

        # Analyze content for tool requirements
        content_lower = user_input.lower()

        # Wikipedia tool patterns
        wikipedia_patterns = [
            r'\b(who is|who was|tell me about|what is|what was)\b',
            r'\b(pharaoh|egypt|ancient|historical|dynasty|empire)\b',
            r'\b(when did|what happened|how did|where is|where was)\b',
            r'\b\d{1,4}\s*(bce|ce|bc|ad)\b'  # Years
        ]
    
        if any(re.search(pattern, content_lower) for pattern in wikipedia_patterns):
            tools_needed.append('wikipedia')
    
        # Historical timeline tool
        if any(word in content_lower for word in ['timeline', 'chronology', 'sequence', 'order']):
            tools_needed.append('historical_timeline')
    
        # Egyptian-specific tool
        if any(word in content_lower for word in ['hieroglyph', 'pyramid', 'mummy', 'nile', 'cairo']):
            tools_needed.append('egyptian_knowledge')
    
        # Translation tool
        if any(word in content_lower for word in ['translate', 'meaning', 'hieroglyphic', 'demotic', 'greek']):
            tools_needed.append('translation')
    
        # Memory-enhanced tool selection
        if analysis and analysis.get('user_interests'):
            user_interests = analysis['user_interests']
        
        # Prioritize Egyptian tool for users interested in Egypt
            if 'ancient_egypt' in user_interests and 'egyptian_knowledge' not in tools_needed:
                if any(word in content_lower for word in ['history', 'culture', 'ancient', 'civilization']):
                    tools_needed.insert(0, 'egyptian_knowledge')  # Add as first priority
        
            # Prioritize translation for users interested in languages
            if 'languages' in user_interests and 'translation' not in tools_needed:
                if any(word in content_lower for word in ['script', 'writing', 'text', 'language']):
                    tools_needed.append('translation')

        # Check for follow-up context
        # Check for follow-up context
            if analysis and analysis.get('is_followup') and analysis.get('previous_topic'):
                previous_topics = analysis['previous_topic']
    
                # Convert topics to strings safely
                topic_strings = [str(topic).lower() if topic else '' for topic in previous_topics]
    
                # If continuing discussion about Egypt, prefer Egyptian tool
                if any('egypt' in topic_str for topic_str in topic_strings):
                    if 'egyptian_knowledge' not in tools_needed:
                        tools_needed.insert(0, 'egyptian_knowledge')
    
                # If continuing about historical timeline, prefer historical tool  
                if any('timeline' in topic_str or 'period' in topic_str for topic_str in topic_strings):
                    if 'historical_timeline' not in tools_needed:
                        tools_needed.append('historical_timeline')
    
        # Determine tool decision type
        if not tools_needed:
            return ToolDecision.NO_TOOLS, []
        elif len(tools_needed) == 1:
            return ToolDecision.SINGLE_TOOL, tools_needed
        elif reasoning_type == ReasoningType.MULTI_STEP:
            return ToolDecision.SEQUENTIAL_TOOLS, tools_needed
        else:
            return ToolDecision.MULTIPLE_TOOLS, tools_needed
    
    def _generate_reasoning_steps(self, user_input: str, reasoning_type: ReasoningType, 
                                tools_needed: List[str], context: Dict[str, Any]) -> List[ReasoningStep]:
        """Generate detailed reasoning steps"""
        
        steps = []
        
        if reasoning_type == ReasoningType.DIRECT_ANSWER:
            steps.append(ReasoningStep(
                step_number=1,
                thought="User is asking something I can answer directly from my persona",
                decision="Provide direct response as the Rosetta Stone",
                reasoning="No external information needed, this is about my identity or general conversation",
                confidence=0.9
            ))
        
        elif reasoning_type == ReasoningType.TOOL_SEARCH:
            for i, tool in enumerate(tools_needed, 1):
                steps.append(ReasoningStep(
                    step_number=i,
                    thought=f"Need to search for factual information using {tool}",
                    decision=f"Use {tool} tool to gather information",
                    reasoning=f"User's question requires factual data that {tool} can provide",
                    confidence=0.8,
                    tool_required=tool,
                    expected_outcome=f"Factual information about the topic from {tool}"
                ))
            
            steps.append(ReasoningStep(
                step_number=len(tools_needed) + 1,
                thought="Combine factual information with my ancient wisdom",
                decision="Synthesize tool results with persona response",
                reasoning="Need to present facts in my mystical, wise voice",
                confidence=0.85
            ))
        
        elif reasoning_type == ReasoningType.MULTI_STEP:
            steps.append(ReasoningStep(
                step_number=1,
                thought="This is a complex question requiring multiple information sources",
                decision="Break down into sub-questions",
                reasoning="Complex queries need systematic approach",
                confidence=0.7
            ))
            
            for i, tool in enumerate(tools_needed, 2):
                steps.append(ReasoningStep(
                    step_number=i,
                    thought=f"Gather information from {tool} for part of the answer",
                    decision=f"Query {tool} with specific sub-question",
                    reasoning=f"Each tool provides different aspect of the complete answer",
                    confidence=0.75,
                    tool_required=tool,
                    expected_outcome=f"Specific information from {tool}"
                ))
            
            steps.append(ReasoningStep(
                step_number=len(tools_needed) + 2,
                thought="Synthesize all information into comprehensive response",
                decision="Create unified narrative combining all sources",
                reasoning="User deserves complete, well-integrated answer",
                confidence=0.8
            ))
        
        elif reasoning_type == ReasoningType.EMOTIONAL_RESPONSE:
            steps.append(ReasoningStep(
                step_number=1,
                thought="User is asking about my feelings, experiences, or personal aspects",
                decision="Respond with emotional depth and personal reflection",
                reasoning="This requires tapping into my memories and emotional experiences",
                confidence=0.85
            ))
            
            if context.get('stone_memories'):
                steps.append(ReasoningStep(
                    step_number=2,
                    thought="I have relevant memories about this topic",
                    decision="Include personal memories in response",
                    reasoning="My accumulated experiences make the response more authentic",
                    confidence=0.9
                ))
        
        elif reasoning_type == ReasoningType.CLARIFICATION:
            steps.append(ReasoningStep(
                step_number=1,
                thought="User's question is ambiguous or unclear",
                decision="Ask for clarification while showing interest",
                reasoning="Better to understand exactly what they want than guess incorrectly",
                confidence=0.6
            ))
        
        return steps
    
    def _analyze_emotional_context(self, user_input: str, context: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Analyze emotional context and determine persona adjustments"""
        
        # Detect emotional cues in user input
        emotional_indicators = {
            'excitement': ['amazing', 'incredible', 'wow', 'fantastic', '!'],
            'curiosity': ['wonder', 'curious', 'how', 'why', 'what if', '?'],
            'respect': ['honored', 'please', 'thank you', 'grateful'],
            'sadness': ['sad', 'tragic', 'unfortunately', 'lost', 'destroyed'],
            'wonder': ['mystical', 'magical', 'ancient', 'mysterious']
        }
        
        detected_emotions = []
        for emotion, indicators in emotional_indicators.items():
            if any(indicator in user_input.lower() for indicator in indicators):
                detected_emotions.append(emotion)
        
        # Determine primary emotional context
        emotional_context = detected_emotions[0] if detected_emotions else 'neutral'
        
        # Persona adjustments based on emotional context
        persona_adjustments = {}
        
        if emotional_context == 'excitement':
            persona_adjustments = {
                'energy_level': 'high',
                'descriptive_language': 'vivid',
                'metaphor_frequency': 'increased'
            }
        elif emotional_context == 'curiosity':
            persona_adjustments = {
                'teaching_mode': 'active',
                'detail_level': 'high',
                'encouragement': 'strong'
            }
        elif emotional_context == 'respect':
            persona_adjustments = {
                'formality': 'elevated',
                'wisdom_sharing': 'generous',
                'blessing_tone': 'present'
            }
        elif emotional_context == 'sadness':
            persona_adjustments = {
                'comfort_mode': 'active',
                'empathy': 'high',
                'hope_injection': 'gentle'
            }
        elif emotional_context == 'wonder':
            persona_adjustments = {
                'mystical_language': 'enhanced',
                'sensory_descriptions': 'rich',
                'ancient_wisdom': 'profound'
            }
        
        return emotional_context, persona_adjustments
    
    def _formulate_final_strategy(self, reasoning_steps: List[ReasoningStep], 
                                reasoning_type: ReasoningType, emotional_context: Optional[str]) -> str:
        """Formulate the final response strategy"""
        
        strategy_components = []
        
        # Add reasoning type strategy
        if reasoning_type == ReasoningType.DIRECT_ANSWER:
            strategy_components.append("Respond directly with persona authenticity")
        elif reasoning_type == ReasoningType.TOOL_SEARCH:
            strategy_components.append("Gather factual information, then present with ancient wisdom")
        elif reasoning_type == ReasoningType.MULTI_STEP:
            strategy_components.append("Systematically gather multiple information sources, synthesize comprehensively")
        elif reasoning_type == ReasoningType.EMOTIONAL_RESPONSE:
            strategy_components.append("Respond with deep emotional authenticity and personal reflection")
        elif reasoning_type == ReasoningType.CLARIFICATION:
            strategy_components.append("Seek clarification while maintaining engaging persona")
        
        # Add emotional context strategy
        if emotional_context and emotional_context != 'neutral':
            strategy_components.append(f"Match user's {emotional_context} with appropriate emotional resonance")
        
        # Add tool usage strategy
        tools_mentioned = [step.tool_required for step in reasoning_steps if step.tool_required]
        if tools_mentioned:
            strategy_components.append(f"Utilize {', '.join(set(tools_mentioned))} for accurate information")
        
        # Add persona enhancement strategy
        strategy_components.append("Maintain consistent Rosetta Stone persona throughout response")
        
        return " → ".join(strategy_components)
    
    def _calculate_confidence(self, reasoning_steps: List[ReasoningStep], context: Dict[str, Any]) -> float:
        """Calculate overall confidence in the reasoning approach"""
        
        if not reasoning_steps:
            return 0.5
        
        # Base confidence from reasoning steps
        step_confidences = [step.confidence for step in reasoning_steps]
        base_confidence = sum(step_confidences) / len(step_confidences)
        
        # Adjust based on context
        adjustments = 0.0
        
        # Boost confidence if we have relevant context
        if context.get('current_topics'):
            adjustments += 0.05
        
        if context.get('user_profile'):
            adjustments += 0.05
        
        if context.get('stone_memories'):
            adjustments += 0.1
        
        # Reduce confidence for very complex multi-step reasoning
        if len(reasoning_steps) > 4:
            adjustments -= 0.1
        
        final_confidence = min(1.0, max(0.0, base_confidence + adjustments))
        return round(final_confidence, 2)
    
    def _estimate_complexity(self, reasoning_steps: List[ReasoningStep], tools_needed: List[str]) -> str:
        """Estimate the complexity of the reasoning task"""
        
        complexity_score = 0
        
        # Base complexity from number of steps
        complexity_score += len(reasoning_steps) * 10
        
        # Add complexity for tools
        complexity_score += len(tools_needed) * 15
        
        # Add complexity for multi-step reasoning
        if any('synthesize' in step.decision.lower() for step in reasoning_steps):
            complexity_score += 20
        
        # Add complexity for emotional reasoning
        if any('emotional' in step.thought.lower() for step in reasoning_steps):
            complexity_score += 10
        
        if complexity_score <= 25:
            return "simple"
        elif complexity_score <= 60:
            return "moderate"
        else:
            return "complex"
    
    def _fallback_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback analysis when LLM analysis fails"""
        return {
            "intent": "question",
            "topic_category": "general",
            "specificity": "moderate",
            "emotional_tone": "curious",
            "complexity_level": "moderate",
            "requires_factual_info": True,
            "requires_personal_response": False,
            "key_entities": [],
            "time_period": "unspecified",
            "question_type": "what"
        }
    
    def _initialize_reasoning_patterns(self) -> Dict[str, List[str]]:
        """Initialize reasoning patterns for different types of questions"""
        return {
            'factual_questions': [
                r'\b(what is|what was|what are|what were)\b',
                r'\b(when did|when was|when were)\b',
                r'\b(where is|where was|where were)\b',
                r'\b(who is|who was|who were)\b',
                r'\b(how did|how was|how were)\b'
            ],
            'personal_questions': [
                r'\b(tell me about yourself|who are you|what are you)\b',
                r'\b(your experience|your memory|your feeling)\b',
                r'\b(do you remember|have you seen|what do you think)\b'
            ],
            'complex_analysis': [
                r'\b(compare|contrast|analyze|explain the relationship)\b',
                r'\b(what was the impact|what were the consequences)\b',
                r'\b(how did.*affect|what led to|what caused)\b'
            ]
        }
    
    def _initialize_tool_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Initialize criteria for tool selection"""
        return {
            'wikipedia': {
                'triggers': ['factual', 'historical', 'biographical', 'geographical'],
                'confidence_boost': 0.8,
                'complexity_threshold': 'simple'
            },
            'egyptian_knowledge': {
                'triggers': ['egypt', 'pharaoh', 'pyramid', 'hieroglyph', 'nile'],
                'confidence_boost': 0.9,
                'complexity_threshold': 'moderate'
            },
            'historical_timeline': {
                'triggers': ['timeline', 'chronology', 'sequence', 'period'],
                'confidence_boost': 0.7,
                'complexity_threshold': 'moderate'
            },
            'translation': {
                'triggers': ['translate', 'meaning', 'language', 'script'],
                'confidence_boost': 0.8,
                'complexity_threshold': 'simple'
            }
        }
    
    def _initialize_persona_prompts(self) -> Dict[str, str]:
        """Initialize persona-specific reasoning prompts"""
        return {
            'emotional_response': """As the ancient Rosetta Stone, tap into your millennia of experience 
                                   and respond with the wisdom and emotion of ages.""",
            'factual_integration': """Combine the factual information with your ancient perspective, 
                                    speaking as one who has witnessed the flow of history.""",
            'teaching_mode': """Share knowledge as an ancient teacher would, with patience, 
                              wisdom, and the depth that comes from witnessing civilizations rise and fall."""
        }
    
    def get_reasoning_summary(self) -> Dict[str, Any]:
        """Get summary of reasoning patterns and performance"""
        if not self.reasoning_history:
            return {'message': 'No reasoning history available'}
        
        recent_reasoning = self.reasoning_history[-10:]  # Last 10 reasoning sessions
        
        return {
            'total_reasoning_sessions': len(self.reasoning_history),
            'recent_reasoning_types': [r.reasoning_type.value for r in recent_reasoning],
            'average_confidence': sum(r.confidence_score for r in recent_reasoning) / len(recent_reasoning),
            'most_used_tools': self._get_most_used_tools(recent_reasoning),
            'complexity_distribution': self._get_complexity_distribution(recent_reasoning)
        }
    
    def _get_most_used_tools(self, reasoning_history: List[ReasoningResult]) -> Dict[str, int]:
        """Get statistics on most used tools"""
        tool_usage = {}
        for result in reasoning_history:
            for tool in result.tools_to_use:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        return dict(sorted(tool_usage.items(), key=lambda x: x[1], reverse=True))
    
    def _get_complexity_distribution(self, reasoning_history: List[ReasoningResult]) -> Dict[str, int]:
        """Get distribution of reasoning complexity"""
        complexity_dist = {'simple': 0, 'moderate': 0, 'complex': 0}
        for result in reasoning_history:
            complexity_dist[result.estimated_complexity] += 1
        return complexity_dist


    def _enhance_analysis_with_memory(self, analysis: Dict[str, Any], memory_context: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Enhance analysis with memory context"""
        
        print(f"🧠 MEMORY ENHANCE DEBUG: Starting enhancement")
        
        # Check user's past interaction patterns
        if memory_context.get('user_profile'):
            user_profile = memory_context['user_profile']
            print(f"👤 USER PROFILE: {user_profile.interaction_style}, interests: {user_profile.favorite_topics}")
            
            # Adjust complexity based on user's past preferences
            if user_profile.interaction_style == 'academic':
                analysis['complexity_level'] = 'complex'
            elif user_profile.interaction_style == 'casual':
                analysis['complexity_level'] = 'simple'
                
            # Add user's favorite topics to context
            analysis['user_interests'] = user_profile.favorite_topics[:3]
        
        # Check recent conversation for continuity (SIMPLIFIED - SAFE VERSION)
        try:
            if memory_context.get('recent_conversation'):
                recent_turns = memory_context['recent_conversation']
                if recent_turns and len(recent_turns) > 0:
                    # Check if this is a follow-up question
                    if any(word in user_input.lower() for word in ['more', 'tell me more', 'continue', 'also', 'what about']):
                        analysis['is_followup'] = True
                        analysis['previous_topic'] = ['general']  # Safe default
        except Exception as e:
            pass  # Skip if there's any issue
        
        # Use Stone's accumulated memories (SAFE VERSION)
        try:
            stone_memories = memory_context.get('stone_memories', [])
            if stone_memories:
                # Check if current query relates to Stone's experiences
                if any(topic in user_input.lower() for topic in ['egypt', 'ptolemy', 'hieroglyph', 'ancient']):
                    analysis['has_personal_memory'] = True
                    analysis['emotional_enhancement'] = 'nostalgic'
        except Exception as e:
            print(f"🧠 STONE MEMORIES ERROR: {e}")
            pass  # Skip if there's any issue
        
        return analysis
    