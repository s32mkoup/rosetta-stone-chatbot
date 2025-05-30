from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from ..core.config import Config

class AgentState(TypedDict):
    """State definition for LangGraph agent"""
    user_input: str
    context: Dict[str, Any]
    reasoning_steps: List[str]
    tool_results: Dict[str, Any]
    response: str
    iteration_count: int
    finished: bool

class LangGraphFramework:
    """LangGraph framework implementation for complex workflows"""
    
    def __init__(self, config: Config):
        self.config = config
        self.graph = self._create_workflow_graph()
        self.memory = SqliteSaver.from_conn_string(":memory:")
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the workflow graph for complex agent interactions"""
        
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_input", self._analyze_input)
        workflow.add_node("plan_response", self._plan_response)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("synthesize_response", self._synthesize_response)
        workflow.add_node("apply_persona", self._apply_persona)
        
        # Add edges
        workflow.add_edge("analyze_input", "plan_response")
        workflow.add_edge("plan_response", "execute_tools")
        workflow.add_edge("execute_tools", "synthesize_response")
        workflow.add_edge("synthesize_response", "apply_persona")
        workflow.add_edge("apply_persona", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_input")
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _analyze_input(self, state: AgentState) -> AgentState:
        """Analyze user input and determine intent"""
        
        user_input = state["user_input"]
        
        # Simple intent analysis (can be enhanced)
        intent = "general"
        if any(word in user_input.lower() for word in ['translate', 'hieroglyph', 'script']):
            intent = "translation"
        elif any(word in user_input.lower() for word in ['history', 'pharaoh', 'ancient']):
            intent = "historical"
        elif any(word in user_input.lower() for word in ['who are you', 'tell me about yourself']):
            intent = "personal"
        
        state["reasoning_steps"].append(f"Analyzed input, detected intent: {intent}")
        return state
    
    async def _plan_response(self, state: AgentState) -> AgentState:
        """Plan the response strategy"""
        
        # Determine what tools are needed
        tools_needed = []
        
        user_input = state["user_input"].lower()
        
        if any(word in user_input for word in ['history', 'when', 'what happened']):
            tools_needed.append('historical_timeline')
        
        if any(word in user_input for word in ['egypt', 'pharaoh', 'pyramid']):
            tools_needed.append('egyptian_knowledge')
        
        if any(word in user_input for word in ['translate', 'hieroglyph', 'demotic']):
            tools_needed.append('translation')
        
        if not tools_needed:
            tools_needed.append('wikipedia')  # Default research tool
        
        state["tool_results"] = {tool: None for tool in tools_needed}
        state["reasoning_steps"].append(f"Planned to use tools: {', '.join(tools_needed)}")
        
        return state
    
    async def _execute_tools(self, state: AgentState) -> AgentState:
        """Execute the planned tools"""
        
        from ..tools.tool_registry import get_tool_registry
        
        registry = get_tool_registry(self.config)
        user_input = state["user_input"]
        
        for tool_name in state["tool_results"].keys():
            if tool_name in registry.tools:
                try:
                    tool = registry.tools[tool_name]
                    result = tool.execute(user_input)
                    state["tool_results"][tool_name] = result
                    state["reasoning_steps"].append(f"Executed {tool_name}: success")
                except Exception as e:
                    state["tool_results"][tool_name] = f"Error: {str(e)}"
                    state["reasoning_steps"].append(f"Executed {tool_name}: failed - {str(e)}")
        
        return state
    
    async def _synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize information from tools into coherent response"""
        
        # Combine tool results
        successful_results = []
        for tool_name, result in state["tool_results"].items():
            if result and not result.startswith("Error:"):
                successful_results.append(f"From {tool_name}: {result[:200]}...")
        
        if successful_results:
            synthesized = "Based on my ancient knowledge: " + " Additionally, ".join(successful_results)
        else:
            synthesized = "Drawing from my millennia of experience, I can share this wisdom about your inquiry."
        
        state["response"] = synthesized
        state["reasoning_steps"].append("Synthesized information from available sources")
        
        return state
    
    async def _apply_persona(self, state: AgentState) -> AgentState:
        """Apply Rosetta Stone personality to the response"""
        
        from ..persona.rosetta_persona import RosettaPersona
        from ..persona.emotional_states import EmotionalStateManager
        
        # Initialize persona components
        persona = RosettaPersona(self.config)
        emotion_manager = EmotionalStateManager()
        
        # Analyze emotional triggers
        triggered_emotion = emotion_manager.analyze_emotional_triggers(
            state["user_input"], 
            state["context"]
        )
        
        # Apply emotional context
        emotion_manager.transition_emotional_state(triggered_emotion)
        
        # Get emotional expressions
        expressions = emotion_manager.get_emotional_expressions()
        
        # Enhance response with personality
        base_response = state["response"]
        
        # Add opening flourish
        if expressions.get('openings'):
            import random
            opening = random.choice(expressions['openings'])
            enhanced_response = f"{opening} {base_response}"
        else:
            enhanced_response = base_response
        
        # Add emotional modifier
        modifier = emotion_manager.get_emotional_modifier()
        enhanced_response = f"*Speaking {modifier}* {enhanced_response}"
        
        # Add closing reflection if appropriate
        if expressions.get('closings') and len(enhanced_response) > 200:
            import random
            closing = random.choice(expressions['closings'])
            enhanced_response += f" {closing}"
        
        state["response"] = enhanced_response
        state["reasoning_steps"].append(f"Applied persona with emotional state: {triggered_emotion.value}")
        state["finished"] = True
        
        return state
    
    async def process_message(self, user_input: str, context: Dict[str, Any]) -> str:
        """Process message using LangGraph workflow"""
        
        # Initialize state
        initial_state = AgentState(
            user_input=user_input,
            context=context,
            reasoning_steps=[],
            tool_results={},
            response="",
            iteration_count=0,
            finished=False
        )
        
        # Run the workflow
        config = {"thread_id": "rosetta_conversation"}
        final_state = await self.graph.ainvoke(initial_state, config=config)
        
        return final_state["response"]
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about workflow execution"""
        
        return {
            "framework": "LangGraph",
            "nodes": ["analyze_input", "plan_response", "execute_tools", "synthesize_response", "apply_persona"],
            "features": ["State management", "Workflow orchestration", "Memory persistence", "Complex reasoning"],
            "capabilities": ["Multi-step reasoning", "Tool orchestration", "Error recovery", "State persistence"]
        }