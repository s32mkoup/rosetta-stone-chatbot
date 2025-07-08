import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import json
import time
from datetime import datetime
import traceback
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from .config import Config, get_config
from .memory import MemoryManager
from .reasoning import ReasoningEngine, ReasoningResult, ReasoningType, ToolDecision
from huggingface_hub import InferenceClient

@dataclass
class AgentResponse:
    """Complete agent response with metadata"""
    content: str
    reasoning_trace: Optional[ReasoningResult] = None
    tools_used: List[str] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    emotional_state: Optional[str] = None
    topics_mentioned: List[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []
        if self.topics_mentioned is None:
            self.topics_mentioned = []
        if self.metadata is None:
            self.metadata = {}

class AgentState:
    """Current state of the agent during processing"""
    def __init__(self):
        self.current_iteration = 0
        self.max_iterations = 5
        self.tools_executed = []
        self.observations = []
        self.reasoning_history = []
        self.error_count = 0
        self.start_time = time.time()
        self.last_tool_result = None
        self.conversation_context = {}


class RosettaStoneAgent:
    """Main agent class implementing the Rosetta Stone AI Agent"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        
        # Initialize core components
        self.llm_client = self._initialize_llm_client()
        self.memory_manager = MemoryManager(self.config)
        self.reasoning_engine = ReasoningEngine(self.config, self.llm_client, self.memory_manager)
        
        # Tool registry
        self.tools = {}
        self._initialize_tools()
        
        # Agent state
        self.agent_state = AgentState()
        self.session_active = False
        self.total_conversations = 0
        
        # Performance tracking
        self.performance_metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'tool_usage_count': {},
            'average_response_time': 0.0,
            'error_count': 0
        }
        
        print(f"🏺 Rosetta Stone Agent initialized with {self.config.agent.framework.value} framework")
    
        from persona.persona_controller import PersonaController
        self.persona_controller = PersonaController(self)
    def _initialize_llm_client(self) -> InferenceClient:
        """Initialize the LLM client with configuration"""
        try:
            client = InferenceClient(
                provider=self.config.llm.provider,
                api_key=self.config.llm.hf_token
            )
            
            # Test connection
            test_response = client.chat.completions.create(
                model=self.config.llm.model_name,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10,
                temperature=0.1
            )
            
            print(f"✅ LLM client connected: {self.config.llm.model_name} via {self.config.llm.provider}")
            return client
            
        except Exception as e:
            print(f"❌ Failed to initialize LLM client: {e}")
            raise
    
    def _initialize_tools(self):
        """Initialize and register all available tools"""
        # Import tools dynamically based on configuration
        from tools.tool_registry import get_available_tools


        
        available_tools = get_available_tools(self.config)
        
        for tool_name in self.config.tools.enabled_tools:
            if tool_name in available_tools:
                self.tools[tool_name] = available_tools[tool_name]
                print(f"🛠️  Registered tool: {tool_name}")
            else:
                print(f"⚠️  Tool not available: {tool_name}")
        
        print(f"🔧 Initialized {len(self.tools)} tools")
    def _handle_persona_command(self, user_input: str) -> AgentResponse:
        """Handle persona switching commands"""
        
        parts = user_input.split()
        current_user = getattr(self, 'current_user_id', 'default_user')
        
        if len(parts) == 1:  # Just '/persona'
            available = self.persona_controller.get_available_personas()
            current_style = 'unknown'
            if current_user in self.memory_manager.user_profiles:
                current_style = self.memory_manager.user_profiles[current_user].interaction_style
            
            response_content = f"**Current Persona:** {current_style}\n{available}\n**Usage:** `/persona academic` or `/persona casual` or `/persona mystical`"
        
        elif len(parts) == 2:  # '/persona academic'
            new_style = parts[1]
            result = self.persona_controller.switch_persona(current_user, new_style)
            response_content = result
        
        else:
            response_content = "❌ Usage: `/persona [academic/casual/mystical]`"
        
        return AgentResponse(
            content=response_content,
            processing_time=0.1,
            confidence_score=1.0,
            metadata={'command': 'persona_switch'}
        )

    def _handle_help_command(self) -> AgentResponse:
        """Handle help commands"""
        
        help_content = """
    🏺 **Rosetta Stone Agent Commands:**

    **Persona Control:**
    - `/persona` - Show current persona and available options
    - `/persona academic` - Switch to scholarly, precise mode
    - `/persona casual` - Switch to friendly, conversational mode  
    - `/persona mystical` - Switch to ethereal, poetic mode (default)

    **General:**
    - `/help` - Show this help message

    **Just ask me anything about:**
    - Ancient Egyptian history and culture
    - Hieroglyph translation and interpretation
    - Historical timelines and events
    - Archaeological discoveries

    *I remember our conversations and adapt to your preferred style!*
        """
        
        return AgentResponse(
            content=help_content,
            processing_time=0.1,
            confidence_score=1.0,
            metadata={'command': 'help'}
        )   
    def start_session(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Start a new conversation session"""
        self.session_active = True
        self.memory_manager.start_session(user_id)
        self.agent_state = AgentState()
        self.total_conversations += 1
        
        session_info = {
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'user_id': user_id,
            'start_time': datetime.now().isoformat(),
            'agent_version': "1.0.0",
            'framework': self.config.agent.framework.value,
            'available_tools': list(self.tools.keys())
        }
        
        print(f"🚀 Session started for user: {user_id}")
        return session_info
    
    async def process_message(self, user_input: str) -> AgentResponse:
        """Main message processing method - implements the thought→action→observation loop"""
        if user_input.lower().startswith('/persona'):
            return self._handle_persona_command(user_input)
        elif user_input.lower() in ['/help', 'help']:
            return self._handle_help_command()      
        start_time = time.time()
        self.performance_metrics['total_queries'] += 1
        
        try:
            # Step 1: Get context from memory
            context = self.memory_manager.get_context_for_response()
            personality_context = self.memory_manager.get_personality_context()
            context.update(personality_context)
            # Step 2: Reasoning phase (Thought)
            print(f"💭 Analyzing: {user_input[:50]}...")
            reasoning_result = self.reasoning_engine.analyze_user_input(user_input, context, memory_context=context)

            
            if self.config.agent.verbose_logging:
                print(f"🧠 Reasoning: {reasoning_result.reasoning_type.value}")
                print(f"🔧 Tools needed: {reasoning_result.tools_to_use}")
                print(f"📊 Confidence: {reasoning_result.confidence_score}")
            
            # Step 3: Action phase (Tool execution if needed)
            tool_results = {}
            if reasoning_result.tool_decision != ToolDecision.NO_TOOLS:
                tool_results = await self._execute_tools(reasoning_result.tools_to_use, user_input, reasoning_result)
            
            # Step 4: Observation and Response Generation
            response_content = await self._generate_response(
                user_input, reasoning_result, tool_results, context, personality_context
            )
            
            # Step 5: Extract topics and emotional state
            topics_mentioned = await self._extract_topics(user_input, response_content)
            emotional_state = reasoning_result.emotional_context
            
            # Step 6: Create final response
            processing_time = time.time() - start_time
            
            agent_response = AgentResponse(
                content=response_content,
                reasoning_trace=reasoning_result,
                tools_used=reasoning_result.tools_to_use,
                processing_time=processing_time,
                confidence_score=reasoning_result.confidence_score,
                emotional_state=emotional_state,
                topics_mentioned=topics_mentioned,
                metadata={
                    'reasoning_steps': len(reasoning_result.reasoning_steps),
                    'tool_results_count': len(tool_results),
                    'complexity': reasoning_result.estimated_complexity,
                    'framework': self.config.agent.framework.value
                }
            )
            
            # Step 7: Update memory
            self.memory_manager.add_conversation_turn(
                user_input=user_input,
                agent_response=response_content,
                tools_used=reasoning_result.tools_to_use,
                reasoning_trace=json.dumps(reasoning_result.to_dict()),
                emotional_state=emotional_state,
                topics_mentioned=topics_mentioned
            )
            
            # Step 8: Update performance metrics
            self._update_performance_metrics(agent_response, True)
            
            if self.config.agent.verbose_logging:
                print(f"⚡ Response generated in {processing_time:.2f}s")
            
            return agent_response
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(f"❌ {error_msg}")
            
            if self.config.agent.verbose_logging:
                print(traceback.format_exc())
            
            # Create error response
            error_response = AgentResponse(
                content=self._generate_error_response(user_input, str(e)),
                error=error_msg,
                processing_time=time.time() - start_time
            )
            
            self._update_performance_metrics(error_response, False)
            return error_response
    
    def process_message_sync(self, user_input: str) -> AgentResponse:
        """Synchronous wrapper for process_message"""
        return asyncio.run(self.process_message(user_input))
    
    async def _execute_tools(self, tools_to_use: List[str], user_input: str, 
                           reasoning_result: ReasoningResult) -> Dict[str, Any]:
        """Execute the required tools and gather observations"""
        
        tool_results = {}
        
        for tool_name in tools_to_use:
            if tool_name not in self.tools:
                print(f"⚠️  Tool not available: {tool_name}")
                continue
            
            try:
                print(f"🔍 Executing tool: {tool_name}")
                
                # Prepare tool query based on reasoning
                tool_query = self._prepare_tool_query(tool_name, user_input, reasoning_result)
                
                # Execute tool with timeout
                start_time = time.time()
                result = await asyncio.wait_for(
                    self._execute_single_tool(tool_name, tool_query),
                    timeout=self.config.tools.tool_timeout
                )
                
                execution_time = time.time() - start_time
                
                tool_results[tool_name] = {
                    'result': result,
                    'query': tool_query,
                    'execution_time': execution_time,
                    'success': True
                }
                
                # Update tool usage metrics
                self.performance_metrics['tool_usage_count'][tool_name] = \
                    self.performance_metrics['tool_usage_count'].get(tool_name, 0) + 1
                
                if self.config.agent.verbose_logging:
                    print(f"✅ {tool_name} completed in {execution_time:.2f}s")
                
            except asyncio.TimeoutError:
                error_msg = f"Tool {tool_name} timed out after {self.config.tools.tool_timeout}s"
                print(f"⏰ {error_msg}")
                tool_results[tool_name] = {
                    'result': f"Tool execution timed out: {error_msg}",
                    'query': tool_query,
                    'execution_time': self.config.tools.tool_timeout,
                    'success': False,
                    'error': 'timeout'
                }
                
            except Exception as e:
                error_msg = f"Tool {tool_name} failed: {str(e)}"
                print(f"❌ {error_msg}")
                tool_results[tool_name] = {
                    'result': f"Tool execution failed: {error_msg}",
                    'query': tool_query,
                    'execution_time': 0,
                    'success': False,
                    'error': str(e)
                }
        
        return tool_results
    
    async def _execute_single_tool(self, tool_name: str, query: str) -> str:
        """Execute a single tool asynchronously"""
        tool = self.tools[tool_name]
        
        # If tool is not async, run in thread pool
        if not asyncio.iscoroutinefunction(tool.execute):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, tool.execute, query)
        else:
            return await tool.execute(query)
    
    def _prepare_tool_query(self, tool_name: str, user_input: str, reasoning_result: ReasoningResult) -> str:
        """Prepare optimized query for specific tool"""
        
        # Basic query preparation based on tool type
        if tool_name == 'wikipedia':
            # Extract key entities and topics for Wikipedia search
            key_terms = self._extract_key_terms(user_input)
            return ' '.join(key_terms[:3])  # Use top 3 key terms
            
        elif tool_name == 'egyptian_knowledge':
            # Focus on Egyptian-related terms
            egyptian_terms = [term for term in user_input.split() 
                            if any(egypt_word in term.lower() 
                                  for egypt_word in ['egypt', 'pharaoh', 'pyramid', 'nile', 'hieroglyph'])]
            return ' '.join(egyptian_terms) if egyptian_terms else user_input
            
        elif tool_name == 'historical_timeline':
            # Extract dates and periods
            import re
            date_patterns = re.findall(r'\b\d{1,4}\s*(?:bce|ce|bc|ad)\b', user_input.lower())
            if date_patterns:
                return f"timeline {' '.join(date_patterns)}"
            return f"timeline {user_input}"
            
        elif tool_name == 'translation':
            # Extract terms that might need translation
            translation_terms = [term for term in user_input.split() 
                               if any(trans_word in term.lower() 
                                     for trans_word in ['hieroglyph', 'demotic', 'greek', 'translate'])]
            return ' '.join(translation_terms) if translation_terms else user_input
        
        # Default: return original user input
        return user_input
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for tool queries"""
        # Simple keyword extraction (can be enhanced with NLP)
        import re
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Extract words, filter stop words and short words
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return key_terms[:10]  # Return top 10 terms
    
    async def _generate_response(self, user_input: str, reasoning_result: ReasoningResult, 
                               tool_results: Dict[str, Any], context: Dict[str, Any],
                               personality_context: Dict[str, Any]) -> str:
        """Generate the final response using LLM with all context"""
        
        # Build comprehensive prompt
        prompt = self._build_response_prompt(
            user_input, reasoning_result, tool_results, context, personality_context
        )
        
        try:
            # Generate response with configured parameters
            response = self.llm_client.chat.completions.create(
                model=self.config.llm.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ LLM response generation failed: {e}")
            return self._generate_fallback_response(user_input, reasoning_result)
    
    def _build_response_prompt(self, user_input: str, reasoning_result: ReasoningResult,
                            tool_results: Dict[str, Any], context: Dict[str, Any],
                            personality_context: Dict[str, Any]) -> str:
        """Build comprehensive prompt for response generation"""
        
        from persona.rosetta_persona import RosettaPersona
        
        prompt_parts = []
        
        # 1. Base persona
        persona = RosettaPersona(self.config)
        prompt_parts.append(persona.get_system_prompt(self.config))
        
        # 2. MEMORY-ENHANCED CONVERSATION CONTEXT
        if context.get('recent_conversation'):
            recent_turns = context['recent_conversation'][-3:]  # Last 3 turns
            if len(recent_turns) > 0:
                prompt_parts.append(f"\n**CONVERSATION MEMORY:**")
                for i, turn in enumerate(recent_turns):
                    turn_summary = ""
                    if hasattr(turn, 'user_input') and hasattr(turn, 'agent_response'):
                        turn_summary = f"Turn {i+1}: User asked '{turn.user_input[:60]}...' - I responded about '{turn.agent_response[:80]}...'"
                    elif isinstance(turn, dict):
                        user_part = turn.get('user_input', 'something')[:60]
                        agent_part = turn.get('agent_response', 'general topic')[:80]
                        turn_summary = f"Turn {i+1}: User asked '{user_part}...' - I discussed '{agent_part}...'"
                    
                    if turn_summary:
                        prompt_parts.append(turn_summary)
        
        # 3. USER RELATIONSHIP CONTEXT
        if context.get('user_profile'):
            user_profile = context['user_profile']
            prompt_parts.append(f"\n**USER RELATIONSHIP:**")
            prompt_parts.append(f"This is conversation #{user_profile.total_conversations} with this user")
            prompt_parts.append(f"User's interests: {', '.join(user_profile.favorite_topics[:4])}")
            prompt_parts.append(f"User's style: {user_profile.interaction_style}")
            prompt_parts.append(f"Preferred response length: {user_profile.preferred_response_length}")
        
        # 4. CONVERSATION FLOW ANALYSIS
        prompt_parts.append(f"\n**CURRENT QUERY ANALYSIS:**")
        
        # Check for follow-up indicators
        followup_words = ['more', 'also', 'what about', 'tell me more', 'continue', 'and', 'but what about']
        is_followup = any(word in user_input.lower() for word in followup_words)
        
        if is_followup and context.get('recent_conversation'):
            last_turn = context['recent_conversation'][-1] if context['recent_conversation'] else None
            if last_turn:
                prompt_parts.append(f"This is a FOLLOW-UP question building on our previous discussion")
                prompt_parts.append(f"Connect this naturally to what we just discussed")
        
        # Check for pronouns that need context
        pronouns = ['it', 'they', 'them', 'this', 'that', 'these', 'those']
        has_pronouns = any(pronoun in user_input.lower().split() for pronoun in pronouns)
        
        if has_pronouns and context.get('recent_conversation'):
            prompt_parts.append(f"User used pronouns - refer back to our recent conversation for context")
        
        # 5. Tool results with context
        if tool_results:
            prompt_parts.append(f"\n**KNOWLEDGE GATHERED:**")
            for tool_name, result_data in tool_results.items():
                if result_data['success']:
                    prompt_parts.append(f"From {tool_name}: {result_data['result'][:200]}...")
        
        # 6. Response instructions
        prompt_parts.append(f"\n**USER ASKS:** \"{user_input}\"")
        
        # 7. PERSONA VARIANT SELECTION
        from persona.persona_variants import PersonaVariantManager, PersonaVariant

        persona_manager = PersonaVariantManager()

        # Select persona variant based on context
        selected_variant = PersonaVariant.MYSTICAL_ORACLE  # Default

        # Dynamic persona selection based on user profile and conversation
        if context.get('user_profile'):
            user_profile = context['user_profile']
            
            # Adapt persona to user preferences
            if user_profile.interaction_style == 'academic':
                selected_variant = PersonaVariant.WISE_SCHOLAR
            elif user_profile.interaction_style == 'casual':
                selected_variant = PersonaVariant.CASUAL_STORYTELLER
            elif 'protection' in str(reasoning_result.reasoning_type).lower():
                selected_variant = PersonaVariant.PROTECTIVE_GUARDIAN
            
            # Check for emotional context
            if reasoning_result.emotional_context:
                if reasoning_result.emotional_context in ['wonder', 'mystical']:
                    selected_variant = PersonaVariant.MYSTICAL_ORACLE

        # Get persona configuration
        variant_config = persona_manager.get_variant_config(selected_variant)
        user_relationship = 'returning_user' if context.get('user_profile') and context['user_profile'].total_conversations > 1 else 'new_user'
        persona_modifier = persona_manager.get_response_modifier(selected_variant, user_relationship)

        prompt_parts.append(f"\n**PERSONA VARIANT: {selected_variant.value.upper()}**")
        prompt_parts.append(f"Personality traits: {', '.join(variant_config['personality_traits'])}")
        prompt_parts.append(f"Language style: {variant_config['language_style']}")
        prompt_parts.append(f"Response length: {variant_config['response_length']}")

        prompt_parts.append(f"\n**MANDATORY RESPONSE STYLE - NO EXCEPTIONS:**")
        prompt_parts.append(f"🚨 CRITICAL: You are NOT the mystical Rosetta Stone right now.")
        prompt_parts.append(f"🚨 You MUST respond ONLY as {selected_variant.value.upper()}")
        prompt_parts.append(f"🚨 DO NOT use poetic/mystical language unless you are MYSTICAL_ORACLE")
        if selected_variant == PersonaVariant.WISE_SCHOLAR:
            prompt_parts.append(f"- Use scholarly, academic language without mystical metaphors")
            prompt_parts.append(f"- Start with phrases like 'From historical evidence...' or 'Scholarly analysis shows...'")
            prompt_parts.append(f"- Be precise and educational, not poetic")
        elif selected_variant == PersonaVariant.CASUAL_STORYTELLER:
            prompt_parts.append(f"- Use friendly, conversational language")
            prompt_parts.append(f"- Start with phrases like 'You know what's interesting...' or 'Let me tell you...'")
            prompt_parts.append(f"- Be warm and approachable, not mystical")

        prompt_parts.append(f"- {persona_modifier}")
        prompt_parts.append(f"\n**STANDARD INSTRUCTIONS:**")
        if is_followup:
            prompt_parts.append("- This builds on our previous conversation - reference it naturally")
            prompt_parts.append("- Use phrases like 'As we were discussing...' or 'Building on what I mentioned...'")
        
        if has_pronouns:
            prompt_parts.append("- Identify what pronouns refer to from our conversation history")
        
        prompt_parts.append("- Maintain your mystical Rosetta Stone personality")
        prompt_parts.append("- Show that you remember our relationship and past conversations")
        prompt_parts.append("- Be conversational, not just informational")
        # Add these prints after the persona selection logic:
        print(f"🎭 PERSONA DEBUG: Selected variant: {selected_variant}")
        print(f"🎭 PERSONA DEBUG: User interaction style: {user_profile.interaction_style if context.get('user_profile') else 'No profile'}")
        print(f"🎭 PERSONA DEBUG: Persona modifier: {persona_modifier}")
        return "\n".join(prompt_parts)
    
    async def _extract_topics(self, user_input: str, response_content: str) -> List[str]:
        """Extract topics mentioned in the conversation"""
        # Simple topic extraction (can be enhanced)
        combined_text = f"{user_input} {response_content}".lower()
        
        # Predefined topic categories
        topic_keywords = {
            'ancient_egypt': ['egypt', 'pharaoh', 'pyramid', 'nile', 'cairo', 'hieroglyph'],
            'ptolemy': ['ptolemy', 'ptolemaic', 'dynasty'],
            'rosetta_stone': ['rosetta', 'stone', 'discovery', '1799'],
            'languages': ['hieroglyph', 'demotic', 'greek', 'translation'],
            'history': ['ancient', 'historical', 'civilization', 'empire'],
            'archaeology': ['discovery', 'excavation', 'artifact', 'museum']
        }
        
        found_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def _generate_fallback_response(self, user_input: str, reasoning_result: ReasoningResult) -> str:
        """Generate fallback response when LLM fails"""
        fallback_responses = {
            ReasoningType.DIRECT_ANSWER: "Greetings, seeker. I am the Rosetta Stone, keeper of ancient wisdom. Your words reach me across the sands of time.",
            ReasoningType.TOOL_SEARCH: "The sands shift, and my ancient knowledge seeks the answers you desire. Let me share what wisdom flows through the ages.",
            ReasoningType.EMOTIONAL_RESPONSE: "Your words stir memories within my ancient heart. Across millennia, I have witnessed much, and your question touches my very essence.",
            ReasoningType.CLARIFICATION: "Speak more clearly, curious one. My ancient wisdom is vast, but I would understand your true intent to serve you better.",
            ReasoningType.MULTI_STEP: "Your question spans the breadth of civilizations. Let me gather the threads of history to weave you an answer worthy of the ages."
        }
        
        return fallback_responses.get(reasoning_result.reasoning_type, 
                                    "The whispers of time carry your words to me, ancient seeker. I am here to share the wisdom of ages.")
    
    def _generate_error_response(self, user_input: str, error: str) -> str:
        """Generate user-friendly error response"""
        return f"Forgive me, seeker of wisdom. The sands of time have obscured my thoughts momentarily. The ancient mechanisms that channel my knowledge encounter difficulty: {error}. Perhaps you could ask your question differently, and I shall try again to serve your curiosity."
    
    def _update_performance_metrics(self, response: AgentResponse, success: bool):
        """Update agent performance metrics"""
        if success:
            self.performance_metrics['successful_responses'] += 1
            
            # Update average response time
            total_time = self.performance_metrics['average_response_time'] * (self.performance_metrics['successful_responses'] - 1)
            self.performance_metrics['average_response_time'] = (total_time + response.processing_time) / self.performance_metrics['successful_responses']
        else:
            self.performance_metrics['error_count'] += 1
    
    def end_session(self) -> Dict[str, Any]:
        """End the current session and save data"""
        if not self.session_active:
            return {'message': 'No active session'}
        
        # Save persistent memory
        self.memory_manager.save_persistent_memory()
        
        # Generate session summary
        session_summary = {
            'session_ended': datetime.now().isoformat(),
            'total_conversations': self.total_conversations,
            'memory_stats': self.memory_manager.get_memory_stats(),
            'reasoning_summary': self.reasoning_engine.get_reasoning_summary(),
            'performance_metrics': self.performance_metrics.copy()
        }
        
        self.session_active = False
        print("🔚 Session ended and data saved")
        
        return session_summary
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and health"""
        return {
            'session_active': self.session_active,
            'framework': self.config.agent.framework.value,
            'model': self.config.llm.model_name,
            'provider': self.config.llm.provider,
            'available_tools': list(self.tools.keys()),
            'memory_enabled': self.config.memory.memory_enabled,
            'performance_metrics': self.performance_metrics,
            'current_session_stats': {
                'conversations': self.total_conversations,
                'memory_items': len(self.memory_manager.conversation.short_term),
                'reasoning_history': len(self.reasoning_engine.reasoning_history)
            }
        }
    
    def reset_agent(self):
        """Reset agent to initial state"""
        self.memory_manager.clear_session_memory()
        self.agent_state = AgentState()
        self.reasoning_engine.reasoning_history = []
        self.total_conversations = 0
        self.session_active = False
        print("🔄 Agent reset to initial state")