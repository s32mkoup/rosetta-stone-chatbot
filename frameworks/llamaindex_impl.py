from typing import Dict, List, Any, Optional
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from ..core.config import Config

class LlamaIndexFramework:
    """LlamaIndex framework implementation for knowledge-based queries"""
    
    def __init__(self, config: Config):
        self.config = config
        self._setup_llama_index()
        self.knowledge_index = self._create_knowledge_index()
        self.agent = self._create_agent()
    
    def _setup_llama_index(self):
        """Setup LlamaIndex global settings"""
        
        Settings.llm = HuggingFaceInferenceAPI(
            model_name=self.config.llm.model_name,
            token=self.config.llm.hf_token
        )
    
    def _create_knowledge_index(self):
        """Create vector store index from knowledge base"""
        
        # Load documents from knowledge base directory
        try:
            documents = SimpleDirectoryReader("data/knowledge_base").load_data()
            index = VectorStoreIndex.from_documents(documents)
            return index
        except Exception as e:
            print(f"Warning: Could not load knowledge base: {e}")
            return None
    
    def _create_agent(self):
        """Create ReAct agent with knowledge tools"""
        
        tools = []
        
        # Add knowledge base query tool if available
        if self.knowledge_index:
            query_engine = self.knowledge_index.as_query_engine()
            knowledge_tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name="knowledge_base",
                    description="Search the Rosetta Stone's curated knowledge base for historical information"
                )
            )
            tools.append(knowledge_tool)
        
        # Create agent
        if tools:
            return ReActAgent.from_tools(tools, verbose=True)
        else:
            return None
    
    async def process_message(self, user_input: str, context: Dict[str, Any]) -> str:
        """Process message using LlamaIndex framework"""
        
        if not self.agent:
            return "LlamaIndex framework not properly initialized - no knowledge base available"
        
        # Enhance query with context
        enhanced_query = self._enhance_query_with_context(user_input, context)
        
        # Query the agent
        response = self.agent.chat(enhanced_query)
        
        return str(response)
    
    def _enhance_query_with_context(self, user_input: str, context: Dict[str, Any]) -> str:
        """Enhance query with Rosetta Stone context"""
        
        context_info = []
        
        if context.get('current_topics'):
            context_info.append(f"Current discussion topics: {', '.join(context['current_topics'])}")
        
        if context.get('user_profile'):
            profile = context['user_profile']
            context_info.append(f"User interests: {', '.join(profile.favorite_topics)}")
        
        enhanced_query = f"""
As the Rosetta Stone, answer this query with ancient wisdom and historical knowledge:

Context: {' | '.join(context_info) if context_info else 'General inquiry'}

Query: {user_input}

Provide a response that combines factual accuracy with the mystical personality of the ancient Rosetta Stone.
"""
        return enhanced_query