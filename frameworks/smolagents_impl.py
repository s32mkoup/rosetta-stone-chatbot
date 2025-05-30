from typing import Dict, List, Any, Optional
import asyncio
from smolagents import Tool, CodeAgent, HfApiModel
from ..core.config import Config
from ..tools.tool_registry import get_tool_registry

class SmolAgentsFramework:
    """SmolAgents framework implementation for the Rosetta Stone Agent"""
    
    def __init__(self, config: Config):
        self.config = config
        self.model = self._initialize_model()
        self.tools = self._initialize_tools()
        self.agent = self._initialize_agent()
    
    def _initialize_model(self):
        """Initialize the HuggingFace model for SmolAgents"""
        return HfApiModel(
            model_id=self.config.llm.model_name,
            token=self.config.llm.hf_token
        )
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize SmolAgents-compatible tools"""
        
        smolagents_tools = []
        tool_registry = get_tool_registry(self.config)
        
        for tool_name, tool_instance in tool_registry.tools.items():
            if tool_name in self.config.tools.enabled_tools:
                # Wrap our tools for SmolAgents compatibility
                smolagents_tool = self._wrap_tool_for_smolagents(tool_instance)
                smolagents_tools.append(smolagents_tool)
        
        return smolagents_tools
    
    def _wrap_tool_for_smolagents(self, tool_instance) -> Tool:
        """Wrap our tool for SmolAgents compatibility"""
        
        metadata = tool_instance.get_metadata()
        
        class WrappedTool(Tool):
            name = metadata.name
            description = metadata.description
            
            def __call__(self, query: str) -> str:
                return tool_instance.execute(query)
        
        return WrappedTool()
    
    def _initialize_agent(self):
        """Initialize the SmolAgents CodeAgent"""
        
        return CodeAgent(
            tools=self.tools,
            model=self.model,
            max_steps=self.config.agent.max_iterations
        )
    
    async def process_message(self, user_input: str, context: Dict[str, Any]) -> str:
        """Process message using SmolAgents framework"""
        
        # Enhance user input with Rosetta Stone context
        enhanced_prompt = self._enhance_prompt_with_context(user_input, context)
        
        # Run the agent
        result = self.agent.run(enhanced_prompt)
        
        return result
    
    def _enhance_prompt_with_context(self, user_input: str, context: Dict[str, Any]) -> str:
        """Enhance user prompt with Rosetta Stone context"""
        
        from ..persona.rosetta_persona import RosettaPersona
        
        persona = RosettaPersona(self.config)
        system_prompt = persona.get_system_prompt(self.config)
        
        enhanced_prompt = f"""
{system_prompt}

Recent conversation context:
{self._format_context(context)}

User input: {user_input}

Respond as the Rosetta Stone with wisdom, personality, and appropriate tool usage.
"""
        return enhanced_prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompt enhancement"""
        
        context_parts = []
        
        if context.get('recent_conversation'):
            recent = context['recent_conversation'][-2:]
            for turn in recent:
                context_parts.append(f"Previous: {turn.user_input} → {turn.agent_response[:100]}...")
        
        if context.get('current_topics'):
            topics = ', '.join(context['current_topics'])
            context_parts.append(f"Current topics: {topics}")
        
        return '\n'.join(context_parts) if context_parts else "No previous context"