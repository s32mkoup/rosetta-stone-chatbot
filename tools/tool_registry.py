from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
import inspect
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

from enum import Enum

class ToolCategory(Enum):
    """Categories of tools available to the agent"""
    RESEARCH = "research"
    HISTORICAL = "historical"
    LINGUISTIC = "linguistic"
    COMPUTATIONAL = "computational"
    CREATIVE = "creative"
    MEMORY = "memory"

class ToolComplexity(Enum):
    """Complexity levels for tools"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ADVANCED = "advanced"

@dataclass
class ToolMetadata:
    """Metadata describing a tool's capabilities and characteristics"""
    name: str
    description: str
    category: ToolCategory
    complexity: ToolComplexity
    input_description: str
    output_description: str
    example_usage: str
    keywords: List[str]
    required_params: List[str]
    optional_params: List[str]
    execution_time_estimate: str  # "fast", "medium", "slow"
    reliability_score: float  # 0.0 to 1.0
    cost_estimate: str  # "free", "low", "medium", "high"
    version: str = "1.0.0"
    
    def matches_query(self, query: str, keywords: List[str] = None) -> float:
        """Calculate relevance score for a given query"""
        query_lower = query.lower()
        score = 0.0
        
        # Check tool keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword.lower() in query_lower)
        score += (keyword_matches / len(self.keywords)) * 0.6
        
        # Check description relevance
        desc_words = self.description.lower().split()
        query_words = query_lower.split()
        desc_matches = sum(1 for word in query_words if word in desc_words)
        score += (desc_matches / len(query_words)) * 0.4
        
        # Check additional keywords if provided
        if keywords:
            additional_matches = sum(1 for keyword in keywords if keyword.lower() in query_lower)
            score += (additional_matches / len(keywords)) * 0.2
        
        return min(1.0, score)

class BaseTool(ABC):
    """Abstract base class for all agent tools"""
    
    def __init__(self, config: Any = None):
        self.config = config
        self.metadata: Optional[ToolMetadata] = None
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        self.last_execution_time = 0.0
        self.cache = {}
        self.cache_enabled = True
        self.cache_ttl = 300  # 5 minutes default
    
    @abstractmethod
    def execute(self, query: str, **kwargs) -> str:
        """Execute the tool with the given query"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata"""
        pass
    
    def validate_input(self, query: str, **kwargs) -> bool:
        """Validate input parameters"""
        if not query or not isinstance(query, str):
            return False
        
        # Check required parameters
        if self.metadata:
            for param in self.metadata.required_params:
                if param not in kwargs:
                    return False
        
        return True
    
    def get_cache_key(self, query: str, **kwargs) -> str:
        """Generate cache key for the query"""
        import hashlib
        cache_string = f"{query}_{sorted(kwargs.items())}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[str]:
        """Retrieve cached result if available and valid"""
        if not self.cache_enabled or cache_key not in self.cache:
            return None
        
        import time
        cached_item = self.cache[cache_key]
        if time.time() - cached_item['timestamp'] > self.cache_ttl:
            del self.cache[cache_key]
            return None
        
        return cached_item['result']
    
    def cache_result(self, cache_key: str, result: str):
        """Cache the result"""
        if self.cache_enabled:
            import time
            self.cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this tool"""
        avg_time = self.total_execution_time / max(1, self.execution_count)
        success_rate = (self.execution_count - self.error_count) / max(1, self.execution_count)
        
        return {
            'name': self.metadata.name if self.metadata else 'Unknown',
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'average_execution_time': avg_time,
            'last_execution_time': self.last_execution_time,
            'cache_size': len(self.cache),
            'reliability_score': self.metadata.reliability_score if self.metadata else 0.0
        }
    
    async def execute_async(self, query: str, **kwargs) -> str:
        """Async wrapper for execute method"""
        if asyncio.iscoroutinefunction(self.execute):
            return await self.execute(query, **kwargs)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.execute, query, **kwargs)

class ToolRegistry:
    """Central registry for managing all agent tools"""
    
    def __init__(self, config):
        self.config = config
        self.tools: Dict[str, BaseTool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.tool_categories: Dict[ToolCategory, List[str]] = {}
        self.tool_performance: Dict[str, Dict[str, Any]] = {}
        
        # Tool selection preferences
        self.selection_weights = {
            'relevance': 0.4,
            'reliability': 0.3,
            'performance': 0.2,
            'cost': 0.1
        }
        
        # Initialize categories
        for category in ToolCategory:
            self.tool_categories[category] = []
    
    def register_tool(self, tool: BaseTool) -> bool:
        """Register a new tool in the registry"""
        try:
            metadata = tool.get_metadata()
            tool.metadata = metadata
            
            # Validate metadata
            if not self._validate_tool_metadata(metadata):
                print(f"❌ Invalid metadata for tool: {metadata.name}")
                return False
            
            # Register the tool
            self.tools[metadata.name] = tool
            self.tool_metadata[metadata.name] = metadata
            self.tool_categories[metadata.category].append(metadata.name)
            
            print(f"✅ Registered tool: {metadata.name} ({metadata.category.value})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register tool: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the registry"""
        if tool_name not in self.tools:
            return False
        
        metadata = self.tool_metadata[tool_name]
        
        # Remove from all registries
        del self.tools[tool_name]
        del self.tool_metadata[tool_name]
        self.tool_categories[metadata.category].remove(tool_name)
        
        if tool_name in self.tool_performance:
            del self.tool_performance[tool_name]
        
        print(f"🗑️  Unregistered tool: {tool_name}")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool by name"""
        return self.tools.get(tool_name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """Get all tools in a specific category"""
        tool_names = self.tool_categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def find_relevant_tools(self, query: str, max_tools: int = 5, 
                          category_filter: Optional[ToolCategory] = None,
                          complexity_filter: Optional[ToolComplexity] = None) -> List[Tuple[str, float]]:
        """Find tools most relevant to a query"""
        
        candidates = []
        
        for tool_name, metadata in self.tool_metadata.items():
            # Apply filters
            if category_filter and metadata.category != category_filter:
                continue
            
            if complexity_filter and metadata.complexity != complexity_filter:
                continue
            
            # Calculate relevance score
            relevance = metadata.matches_query(query)
            
            if relevance > 0.1:  # Minimum relevance threshold
                candidates.append((tool_name, relevance))
        
        # Sort by relevance and return top results
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:max_tools]
    
    def select_best_tools(self, query: str, reasoning_context: Dict[str, Any],
                         max_tools: int = 3) -> List[str]:
        """Select the best tools for a query using multiple criteria"""
        
        # Get relevant tools
        relevant_tools = self.find_relevant_tools(query, max_tools * 2)
        
        if not relevant_tools:
            return []
        
        # Calculate composite scores
        scored_tools = []
        
        for tool_name, relevance in relevant_tools:
            metadata = self.tool_metadata[tool_name]
            performance = self.get_tool_performance(tool_name)
            
            # Composite score calculation
            score = (
                relevance * self.selection_weights['relevance'] +
                metadata.reliability_score * self.selection_weights['reliability'] +
                performance.get('success_rate', 0.5) * self.selection_weights['performance'] +
                self._get_cost_score(metadata.cost_estimate) * self.selection_weights['cost']
            )
            
            scored_tools.append((tool_name, score))
        
        # Sort by composite score and return best tools
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool_name for tool_name, _ in scored_tools[:max_tools]]
    
    def execute_tool(self, tool_name: str, query: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool and track performance"""
        import time
        
        if tool_name not in self.tools:
            return {
                'success': False,
                'result': f"Tool '{tool_name}' not found",
                'error': 'Tool not found',
                'execution_time': 0
            }
        
        tool = self.tools[tool_name]
        
        # Validate input
        if not tool.validate_input(query, **kwargs):
            return {
                'success': False,
                'result': f"Invalid input for tool '{tool_name}'",
                'error': 'Invalid input',
                'execution_time': 0
            }
        
        # Check cache
        cache_key = tool.get_cache_key(query, **kwargs)
        cached_result = tool.get_cached_result(cache_key)
        
        if cached_result:
            return {
                'success': True,
                'result': cached_result,
                'cached': True,
                'execution_time': 0
            }
        
        # Execute tool
        start_time = time.time()
        
        try:
            result = tool.execute(query, **kwargs)
            execution_time = time.time() - start_time
            
            # Update tool statistics
            tool.execution_count += 1
            tool.total_execution_time += execution_time
            tool.last_execution_time = execution_time
            
            # Cache result
            tool.cache_result(cache_key, result)
            
            # Update performance tracking
            self._update_performance_stats(tool_name, execution_time, True)
            
            return {
                'success': True,
                'result': result,
                'cached': False,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Update error statistics
            tool.error_count += 1
            tool.execution_count += 1
            tool.total_execution_time += execution_time
            
            self._update_performance_stats(tool_name, execution_time, False)
            
            return {
                'success': False,
                'result': f"Tool execution failed: {str(e)}",
                'error': str(e),
                'execution_time': execution_time
            }
    
    async def execute_tool_async(self, tool_name: str, query: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool asynchronously"""
        import time
        
        if tool_name not in self.tools:
            return {
                'success': False,
                'result': f"Tool '{tool_name}' not found",
                'error': 'Tool not found',
                'execution_time': 0
            }
        
        tool = self.tools[tool_name]
        
        # Validate input
        if not tool.validate_input(query, **kwargs):
            return {
                'success': False,
                'result': f"Invalid input for tool '{tool_name}'",
                'error': 'Invalid input',
                'execution_time': 0
            }
        
        # Check cache
        cache_key = tool.get_cache_key(query, **kwargs)
        cached_result = tool.get_cached_result(cache_key)
        
        if cached_result:
            return {
                'success': True,
                'result': cached_result,
                'cached': True,
                'execution_time': 0
            }
        
        # Execute tool asynchronously
        start_time = time.time()
        
        try:
            result = await tool.execute_async(query, **kwargs)
            execution_time = time.time() - start_time
            
            # Update tool statistics
            tool.execution_count += 1
            tool.total_execution_time += execution_time
            tool.last_execution_time = execution_time
            
            # Cache result
            tool.cache_result(cache_key, result)
            
            # Update performance tracking
            self._update_performance_stats(tool_name, execution_time, True)
            
            return {
                'success': True,
                'result': result,
                'cached': False,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Update error statistics
            tool.error_count += 1
            tool.execution_count += 1
            tool.total_execution_time += execution_time
            
            self._update_performance_stats(tool_name, execution_time, False)
            
            return {
                'success': False,
                'result': f"Tool execution failed: {str(e)}",
                'error': str(e),
                'execution_time': execution_time
            }
    
    def get_tool_performance(self, tool_name: str) -> Dict[str, Any]:
        """Get performance statistics for a tool"""
        if tool_name not in self.tools:
            return {}
        
        return self.tools[tool_name].get_performance_stats()
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get overall registry statistics"""
        total_tools = len(self.tools)
        category_counts = {cat.value: len(tools) for cat, tools in self.tool_categories.items()}
        
        # Performance aggregates
        total_executions = sum(tool.execution_count for tool in self.tools.values())
        total_errors = sum(tool.error_count for tool in self.tools.values())
        
        return {
            'total_tools': total_tools,
            'category_distribution': category_counts,
            'total_executions': total_executions,
            'total_errors': total_errors,
            'overall_success_rate': (total_executions - total_errors) / max(1, total_executions),
            'enabled_tools': [name for name in self.tools.keys() if name in self.config.tools.enabled_tools],
            'disabled_tools': [name for name in self.tools.keys() if name not in self.config.tools.enabled_tools]
        }
    
    def list_available_tools(self, category: Optional[ToolCategory] = None) -> List[Dict[str, Any]]:
        """List all available tools with their metadata"""
        tools_list = []
        
        for tool_name, metadata in self.tool_metadata.items():
            if category and metadata.category != category:
                continue
            
            tools_list.append({
                'name': metadata.name,
                'description': metadata.description,
                'category': metadata.category.value,
                'complexity': metadata.complexity.value,
                'keywords': metadata.keywords,
                'example': metadata.example_usage,
                'reliability': metadata.reliability_score,
                'enabled': tool_name in self.config.tools.enabled_tools
            })
        
        return sorted(tools_list, key=lambda x: x['name'])
    
    def _validate_tool_metadata(self, metadata: ToolMetadata) -> bool:
        """Validate tool metadata"""
        required_fields = ['name', 'description', 'category', 'complexity']
        
        for field in required_fields:
            if not hasattr(metadata, field) or not getattr(metadata, field):
                return False
        
        # Check for duplicate names
        if metadata.name in self.tool_metadata:
            return False
        
        return True
    
    def _get_cost_score(self, cost_estimate: str) -> float:
        """Convert cost estimate to score (higher is better)"""
        cost_scores = {
            'free': 1.0,
            'low': 0.8,
            'medium': 0.6,
            'high': 0.4
        }
        return cost_scores.get(cost_estimate.lower(), 0.5)
    
    def _update_performance_stats(self, tool_name: str, execution_time: float, success: bool):
        """Update performance statistics for a tool"""
        if tool_name not in self.tool_performance:
            self.tool_performance[tool_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'total_time': 0.0,
                'average_time': 0.0
            }
        
        stats = self.tool_performance[tool_name]
        stats['total_executions'] += 1
        stats['total_time'] += execution_time
        stats['average_time'] = stats['total_time'] / stats['total_executions']
        
        if success:
            stats['successful_executions'] += 1

# Global registry instance
_global_registry = None

def get_tool_registry(config) -> ToolRegistry:
    """Get the global tool registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry(config)
        _initialize_default_tools(_global_registry, config)
    return _global_registry

def _initialize_default_tools(registry: ToolRegistry, config):
    """Initialize default tools in the registry"""
    
    # Import and register available tools
    try:
        from .wikipedia_tool import WikipediaTool
        registry.register_tool(WikipediaTool(config))
    except ImportError:
        print("⚠️  WikipediaTool not available")
    
    try:
        from .historical_tool import HistoricalTimelineTool
        registry.register_tool(HistoricalTimelineTool(config))
    except ImportError:
        print("⚠️  HistoricalTimelineTool not available")
    
    try:
        from .egyptian_tool import EgyptianKnowledgeTool
        registry.register_tool(EgyptianKnowledgeTool(config))
    except ImportError:
        print("⚠️  EgyptianKnowledgeTool not available")
    
    try:
        from .translation_tool import TranslationTool
        registry.register_tool(TranslationTool(config))
    except ImportError:
        print("⚠️  TranslationTool not available")

def get_available_tools(config) -> Dict[str, BaseTool]:
    """Get dictionary of available tools"""
    registry = get_tool_registry(config)
    return {name: tool for name, tool in registry.tools.items() 
            if name in config.tools.enabled_tools}

def register_custom_tool(tool: BaseTool, config) -> bool:
    """Register a custom tool"""
    registry = get_tool_registry(config)
    return registry.register_tool(tool)

def find_tools_for_query(query: str, config, max_tools: int = 3) -> List[str]:
    """Find the best tools for a given query"""
    registry = get_tool_registry(config)
    return registry.select_best_tools(query, {}, max_tools)