import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from dotenv import load_dotenv

# Load .env file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

# Enums for options
class Framework(Enum):
    SMOLAGENTS = "smolagents"
    LLAMAINDEX = "llamaindex"
    LANGGRAPH = "langgraph"

class PersonaDepth(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    RICH = "rich"

class HistoricalAccuracy(Enum):
    LOOSE = "loose"
    STANDARD = "standard"
    STRICT = "strict"

@dataclass
class LLMConfig:
    """LLM and API configuration"""

    provider: str = "nebius"
    model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30
    hf_token: str = field(init=False)

    def __post_init__(self):
        token = os.getenv("HF_TOKEN", "")
        if token:
            masked = token[:10] + "..." if len(token) > 10 else "***"
            print(f"\U0001F510 Loaded HF_TOKEN from env: {masked}")
        else:
            print("\u274C HF_TOKEN not found in environment")
        self.hf_token = token

    def validate(self) -> bool:
        if not self.hf_token or self.hf_token.strip() == "":
            raise ValueError("HF_TOKEN is required")
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        print("\u2705 LLMConfig validated successfully.")
        return True

@dataclass
class AgentConfig:
    framework: Framework = Framework.SMOLAGENTS
    max_iterations: int = 5
    max_tool_calls_per_iteration: int = 3
    reasoning_enabled: bool = True
    verbose_logging: bool = False

    def validate(self) -> bool:
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        return True

@dataclass
class ToolConfig:
    enabled_tools: List[str] = field(default_factory=lambda: ["wikipedia", "historical", "egyptian", "translation"])
    tool_timeout: int = 10
    max_concurrent_tools: int = 2
    retry_failed_tools: bool = True
    tool_cache_enabled: bool = True
    cache_ttl_minutes: int = 60

    def validate(self) -> bool:
        if self.tool_timeout < 1:
            raise ValueError("tool_timeout must be at least 1 second")
        return True

@dataclass
class MemoryConfig:
    memory_enabled: bool = True
    max_short_term_items: int = 20
    max_long_term_items: int = 100
    conversation_summary_threshold: int = 15
    auto_save_conversations: bool = True
    memory_persistence_path: str = "data/conversation_logs/"

    def validate(self) -> bool:
        if self.max_short_term_items < 1:
            raise ValueError("max_short_term_items must be at least 1")
        return True

@dataclass
class PersonaConfig:
    persona_depth: PersonaDepth = PersonaDepth.STANDARD
    emotional_responses: bool = True
    historical_accuracy: HistoricalAccuracy = HistoricalAccuracy.STRICT
    poetic_language: bool = True
    nostalgic_tone: bool = True
    ancient_wisdom_style: bool = True
    sensory_descriptions: bool = False
    response_length_preference: str = "standard"
    metaphor_frequency: str = "medium"
    historical_context_depth: str = "moderate"

@dataclass
class InterfaceConfig:
    default_interface: str = "cli"
    gradio_port: int = 7860
    gradio_share: bool = False
    api_port: int = 8000
    enable_telegram: bool = False
    telegram_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_TOKEN", ""))

class Config:
    def __init__(self, config_file: Optional[str] = None):
        print("\U0001F527 Initializing global configuration...")
        self.llm = LLMConfig()
        self.agent = AgentConfig()
        self.tools = ToolConfig()
        self.memory = MemoryConfig()
        self.persona = PersonaConfig()
        self.interface = InterfaceConfig()

        if config_file and os.path.exists(config_file):
            print(f"\U0001F4C1 Loading config overrides from: {config_file}")
            self.load_from_file(config_file)

        self._load_from_env()
        self.validate_all()

    def _load_from_env(self):
        if os.getenv("PROVIDER"):
            self.llm.provider = os.getenv("PROVIDER")
        if os.getenv("MODEL_NAME"):
            self.llm.model_name = os.getenv("MODEL_NAME")
        if os.getenv("TEMPERATURE"):
            self.llm.temperature = float(os.getenv("TEMPERATURE"))

        if os.getenv("FRAMEWORK"):
            self.agent.framework = Framework(os.getenv("FRAMEWORK"))
        if os.getenv("VERBOSE"):
            self.agent.verbose_logging = os.getenv("VERBOSE").lower() == "true"

        if os.getenv("ENABLED_TOOLS"):
            self.tools.enabled_tools = os.getenv("ENABLED_TOOLS").split(",")
        if os.getenv("MEMORY_ENABLED"):
            self.memory.memory_enabled = os.getenv("MEMORY_ENABLED").lower() == "true"

        if os.getenv("PERSONA_DEPTH"):
            self.persona.persona_depth = PersonaDepth(os.getenv("PERSONA_DEPTH"))
        if os.getenv("HISTORICAL_ACCURACY"):
            self.persona.historical_accuracy = HistoricalAccuracy(os.getenv("HISTORICAL_ACCURACY"))

    def load_from_file(self, config_file: str):
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            if 'llm' in config_data:
                for key, value in config_data['llm'].items():
                    if hasattr(self.llm, key):
                        setattr(self.llm, key, value)
            if 'agent' in config_data:
                for key, value in config_data['agent'].items():
                    if hasattr(self.agent, key):
                        if key == 'framework':
                            setattr(self.agent, key, Framework(value))
                        else:
                            setattr(self.agent, key, value)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")

    def save_to_file(self, config_file: str):
        config_data = {
            'llm': {
                'provider': self.llm.provider,
                'model_name': self.llm.model_name,
                'temperature': self.llm.temperature,
                'max_tokens': self.llm.max_tokens,
                'timeout': self.llm.timeout
            },
            'agent': {
                'framework': self.agent.framework.value,
                'max_iterations': self.agent.max_iterations,
                'max_tool_calls_per_iteration': self.agent.max_tool_calls_per_iteration,
                'reasoning_enabled': self.agent.reasoning_enabled,
                'verbose_logging': self.agent.verbose_logging
            }
        }
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

    def validate_all(self):
        self.llm.validate()
        self.agent.validate()
        self.tools.validate()
        self.memory.validate()

    def __repr__(self) -> str:
        return f"Config(framework={self.agent.framework.value}, model={self.llm.model_name})"

# Global config instance
config = Config()

def get_config() -> Config:
    return config

def reload_config(config_file: Optional[str] = None):
    global config
    config = Config(config_file)
    return config
