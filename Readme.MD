# 🏺 Rosetta Stone Agent

**Ancient Wisdom Meets Modern AI** - An intelligent chatbot that embodies the legendary Rosetta Stone artifact, combining millennia of historical knowledge with cutting-edge artificial intelligence.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/API-Flask-green)](https://flask.palletsprojects.com/)
[![HuggingFace](https://img.shields.io/badge/AI-HuggingFace-yellow)](https://huggingface.co/)

---

## 🌟 Overview

The Rosetta Stone Agent is a sophisticated AI system that brings the ancient Rosetta Stone to life as an intelligent conversational partner. With deep historical knowledge, multilingual capabilities, and a rich personality system, it serves as both an educational tool and a fascinating exploration of AI-driven character embodiment.

**Authors**: Mohammaderfan Koupaei, Mahshid Khanali, Niloufar Asghari  
**Institution**: University of Bonn - Dialogue Systems Course  
**Repository**: [https://github.com/s32mkoup/rosetta-stone-chatbot.git](https://github.com/s32mkoup/rosetta-stone-chatbot.git)

### ✨ Key Features

- **🎭 Dynamic Personality System**: Academic, casual, and mystical personas that adapt to user interactions
- **🧠 Advanced Memory Architecture**: Remembers conversations, builds user relationships, and accumulates experiences
- **🔧 Multi-Tool Integration**: Wikipedia research, Egyptian knowledge base, historical timelines, and translation services
- **🌐 Multiple Interfaces**: Command-line and web API access
- **📚 Trilingual Expertise**: Specializes in hieroglyphic, demotic, and ancient Greek translations
- **⚡ Framework Flexibility**: Supports SmolAgents, LlamaIndex, and LangGraph backends
- **📊 Comprehensive Evaluation**: Built-in testing and evaluation systems

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Required)
- **Git** (For cloning)
- **HuggingFace Account** (For AI model access)
- **10GB+ RAM** (Recommended for optimal performance)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/s32mkoup/rosetta-stone-chatbot.git
cd rosetta-stone-chatbot

# Install dependencies
pip install -r requirements.txt

# Run setup script
python scripts/setup_environment.py
```

### 2. Environment Configuration

Create a `.env` file in the root directory with your configuration:

```bash
# Create .env file
cp .env.example .env
```

Complete `.env` Configuration:

```env
# =============================================================================
# ROSETTA STONE AGENT CONFIGURATION
# =============================================================================

# API Keys (REQUIRED)
HF_TOKEN=hf_your_huggingface_token_here
OPENAI_API_KEY=sk-your_openai_key_here

# LLM Configuration
PROVIDER=nebius
MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
TEMPERATURE=0.7
MAX_TOKENS=1000

# Agent Configuration
FRAMEWORK=smolagents
MEMORY_ENABLED=true
PERSONA_DEPTH=rich
HISTORICAL_ACCURACY=strict
MAX_ITERATIONS=5

# Interface Configuration
CLI_COLORS=true
VERBOSE_LOGGING=false

# Tool Configuration
ENABLED_TOOLS=wikipedia,egyptian_knowledge,historical_timeline,translation
TOOL_TIMEOUT=10
TOOL_CACHE_ENABLED=true
CACHE_TTL_MINUTES=60

# Performance Configuration
MAX_CONCURRENT_TOOLS=2
RETRY_FAILED_TOOLS=true
```

🔑 **Getting Your API Keys:**

**HuggingFace Token:**
- Visit [HuggingFace Settings](https://huggingface.co/settings/tokens)
- Create a new token with "Read" permissions
- Copy and paste into `HF_TOKEN`

**OpenAI Key (Optional):**
- Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
- Create new secret key
- Used for evaluation features

### 3. Test Installation

```bash
# Run comprehensive system tests
python scripts/test_all_tools.py

# Quick functionality test
python test/test_persona.py
```

## 🖥️ Usage Modes

### Command Line Interface (CLI)

The most direct way to interact with the Rosetta Stone:

```bash
# Start CLI mode
python main.py cli

# With specific user ID
python main.py cli --user your_name

# Disable colors (for terminals that don't support it)
python main.py cli --no-color

# Enable verbose mode for debugging
python main.py cli --verbose
```

**CLI Commands:**

```
/help                 - Show all available commands
/persona              - Show current persona and options
/persona academic     - Switch to scholarly mode
/persona casual       - Switch to friendly storytelling mode
/persona mystical     - Switch to ethereal, poetic mode (default)
/status              - Show agent and session status
/history [n]         - Show last n messages (default: 5)
/clear               - Clear conversation history
/tools               - List available tools
/memory              - Show memory statistics
/settings            - Show current settings
/save <filename>     - Save conversation to file
/export              - Export session data
/reset               - Reset agent to initial state
/quit                - End session
```

### Web Interface (API Bridge)

Interactive web interface with real-time chat:

```bash
# Start web interface server
python api_bridge.py

# Access the web interface at: http://localhost:8080
```

**Web Interface Features:**

- Beautiful temple-themed UI with ancient Egyptian aesthetics
- Real-time chat with the Rosetta Stone
- Framework switching (SmolAgents/LlamaIndex/LangGraph)
- Session management and conversation clearing
- Performance monitoring and status display

**API Endpoints:**

```
POST /api/start_session    - Initialize new session
POST /api/send_message     - Send message to agent  
POST /api/switch_framework - Change AI framework
GET  /api/agent_status     - Get current status
GET  /                     - Serve web interface
```

## 🎭 Persona System

The Rosetta Stone Agent features three distinct personalities that adapt to your interaction style:

### Academic Persona (`/persona academic`)
- **Tone**: Scholarly, precise, educational
- **Best for**: Research, detailed historical analysis, academic discussions
- **Example**: "From historical evidence, the Ptolemaic period represents a unique synthesis of Greek administrative practices with traditional Egyptian religious customs..."

### Casual Persona (`/persona casual`)
- **Tone**: Friendly, conversational, storytelling
- **Best for**: General conversations, storytelling, approachable learning
- **Example**: "You know what's fascinating? Back in my day, Alexandria was like the Silicon Valley of the ancient world..."

### Mystical Persona (`/persona mystical`) - Default
- **Tone**: Ethereal, poetic, ancient wisdom
- **Best for**: Immersive experience, philosophical discussions, emotional connections
- **Example**: "The cosmic winds whisper through the corridors of time, carrying tales of pharaohs and the eternal dance of civilizations..."

**Dynamic Adaptation**: The agent automatically adapts its persona based on:
- Your interaction history
- Question complexity
- Emotional context
- Topic sensitivity

## 🧪 Testing & Evaluation

### System Health Tests

```bash
# Comprehensive system test
python scripts/test_all_tools.py --verbose

# Test specific components
python test/test_persona_switching.py
python test/test_emotions.py
python test/test_real_persona.py
```

### Evaluation System

**Multi-Framework Evaluation:**

```bash
# Quick evaluation (5 test cases)
python evaluation/ollama_llm_judge.py

# Full evaluation suite
python evaluation/ollama_llm_judge.py full

# Advanced evaluation with HuggingFace judge
python evaluation/llm_judge.py
```

**Persona Adherence Study (PAS):**

```bash
# Requires Ollama running locally
python evaluation/run_pas_evaluation.py
```

### Test Categories

- **Memory Tests**: Conversation continuity, context retention
- **Persona Tests**: Personality consistency across modes
- **Domain Expertise**: Egyptian history, translation accuracy
- **Tool Usage**: Wikipedia integration, knowledge synthesis
- **Reasoning Tests**: Complex analysis, multi-step thinking
- **Emotional Response**: Appropriate emotional reactions
- **Error Handling**: Graceful failure management

## 🛠️ Advanced Configuration

### Framework Switching

The agent supports three AI frameworks:

```bash
# In CLI mode, frameworks auto-adapt based on query complexity
# In web mode, use the framework selector pillars

# SmolAgents (Default)
# - Fast, efficient processing
# - Best for: Quick queries, real-time responses

# LlamaIndex  
# - Deep knowledge retrieval
# - Best for: Research, complex analysis

# LangGraph
# - Multi-step reasoning chains
# - Best for: Complex problem-solving
```

### Memory System

**Memory Layers:**
- **Short-term**: Recent conversation (20 turns)
- **Long-term**: Conversation summaries (100 summaries)
- **User Profiles**: Interaction preferences, interests
- **Stone Memory**: Accumulated experiences and wisdom

**Memory Commands:**

```bash
# View memory stats
/memory

# Clear session memory
/clear

# Export memory for analysis
/export
```

### Tool Configuration

**Available Tools:**
- `wikipedia`: Research and fact-checking
- `egyptian_knowledge`: Specialized Egyptian history
- `historical_timeline`: Chronological analysis
- `translation`: Hieroglyphic and ancient script translation

**Tool Management:**

```bash
# List available tools
/tools

# Enable/disable tools in .env:
ENABLED_TOOLS=wikipedia,egyptian_knowledge,historical_timeline,translation
```

## 🔧 Development & Customization

### Project Structure

```
rosetta-stone-chatbot/
├── core/                   # Core agent logic
│   ├── agent.py           # Main agent orchestrator
│   ├── config.py          # Configuration management
│   ├── memory.py          # Memory architecture
│   └── reasoning.py       # Reasoning engine
├── persona/               # Personality system
│   ├── rosetta_persona.py # Core personality
│   ├── emotional_states.py # Emotion management
│   └── persona_variants.py # Persona switching
├── tools/                 # Tool implementations
│   ├── wikipedia_tool.py  # Wikipedia integration
│   ├── egyptian_tool.py   # Egyptian knowledge
│   └── translation_tool.py # Translation services
├── interfaces/            # User interfaces
│   ├── cli_chat.py       # Command line interface
│   └── rosetta_ui/       # Custom web UI assets
├── evaluation/           # Testing and evaluation
├── scripts/             # Utility scripts
├── test/               # Test cases
└── api_bridge.py       # Web interface server
```

### Custom Tool Development

```python
from tools.tool_registry import BaseTool, ToolMetadata, ToolCategory

class CustomTool(BaseTool):
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="custom_tool",
            description="Your custom tool description",
            category=ToolCategory.RESEARCH,
            # ... other metadata
        )
    
    def execute(self, query: str, **kwargs) -> str:
        # Your tool logic here
        return "Tool response"

# Register your tool
from tools.tool_registry import register_custom_tool
register_custom_tool(CustomTool(), config)
```

### Configuration Customization

Create custom configuration files:

```json
{
  "llm": {
    "model_name": "your-preferred-model",
    "temperature": 0.8
  },
  "persona": {
    "persona_depth": "rich",
    "emotional_responses": true
  }
}
```

Use with: `python main.py cli --config custom.json`

## 📊 Performance & Monitoring

### Performance Metrics

The agent tracks comprehensive performance data:

```bash
# View status and metrics
/status

# Export performance data
/export
```

**Tracked Metrics:**
- Response times
- Tool usage statistics
- Memory efficiency
- Success rates
- User satisfaction indicators

### Optimization Tips

- **Memory Management**: Regular `/clear` for long sessions
- **Tool Selection**: Enable only needed tools for faster responses
- **Framework Choice**:
  - SmolAgents for speed
  - LlamaIndex for depth
  - LangGraph for complexity
- **Caching**: Enable tool caching for repeated queries

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Solution: Install dependencies
pip install -r requirements.txt
python scripts/setup_environment.py
```

**2. API Key Issues**

```bash
# Check your .env file
cat .env | grep HF_TOKEN

# Test token validity
python -c "from huggingface_hub import whoami; print(whoami())"
```

**3. Memory Issues**

```bash
# Clear cache and reset
/clear
/reset

# Or restart with clean state
python main.py cli --user new_session
```

**4. Tool Failures**

```bash
# Test individual tools
python test/examine_datasets.py

# Check network connectivity
python scripts/test_all_tools.py
```

**5. Web Interface Issues**

```bash
# Check if port is available
netstat -an | grep 8080

# Restart the API bridge
python api_bridge.py
```

### Debug Mode

```bash
# Enable verbose logging
python main.py cli --verbose

# Check debug output
export VERBOSE_LOGGING=true
python main.py cli
```

### Getting Help

- **Check Status**: `/status` command shows system health
- **Run Tests**: `python scripts/test_all_tools.py`
- **Check Logs**: Look for error messages in console output
- **Reset State**: `/reset` command for clean slate
- **Environment**: Verify `.env` file configuration

## 🌍 Deployment

### Local Development

```bash
# Development mode with auto-reload
python main.py cli --verbose

# Web development server
python api_bridge.py
```

### Production Deployment

**Docker Deployment:**

```bash
# Build and run with Docker
python scripts/deploy.py docker --build

# Using docker-compose
docker-compose up -d
```

**Server Deployment:**

```bash
# Create systemd service
python scripts/deploy.py systemd

# Setup nginx reverse proxy
python scripts/deploy.py nginx
```

**Cloud Deployment:**

```bash
# Heroku
python scripts/deploy.py heroku --build

# HuggingFace Spaces
python scripts/deploy.py hf-spaces
```

## 📚 Examples & Use Cases

### Educational Applications

```bash
# Start academic mode for research
python main.py cli
> /persona academic
> Tell me about the decipherment of hieroglyphs

# Historical timeline exploration
> What major events happened in Egypt between 300-100 BCE?

# Translation practice
> What does this hieroglyph mean: 𓋹
```

### Creative Writing

```bash
# Mystical mode for storytelling
> /persona mystical
> Describe your memories of ancient Alexandria

# Emotional exploration
> How did you feel when you were discovered?
```

### Research & Analysis

```bash
# Academic research mode
> /persona academic
> Compare Ptolemaic administrative practices with earlier Egyptian dynasties

# Framework switching for deep analysis
# (Web interface: click framework pillars to switch)
```

### Language Learning

```bash
# Translation and language practice
> /persona casual
> Teach me some basic hieroglyphic symbols
> How do you write "life" in hieroglyphs?
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/s32mkoup/rosetta-stone-chatbot.git
cd rosetta-stone-chatbot

# Create development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Install development dependencies
pip install black flake8 pytest pytest-cov

# Run tests
python scripts/test_all_tools.py
```

### Contribution Areas

- **Tool Development**: Add new research and analysis tools
- **Persona Enhancement**: Expand personality system
- **Evaluation**: Improve testing and evaluation frameworks
- **Interface**: Enhance user interfaces and experiences
- **Documentation**: Improve guides and examples
- **Performance**: Optimize speed and memory usage

### Code Standards

```bash
# Format code
black .

# Check style
flake8 .

# Run tests
pytest test/ -v --cov=core
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- University of Bonn - Dialogue Systems Course
- HuggingFace for AI model infrastructure
- Ancient Egyptian scholars for historical accuracy guidance
- Open source community for tools and frameworks
- The actual Rosetta Stone for inspiring this digital embodiment

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/s32mkoup/rosetta-stone-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/s32mkoup/rosetta-stone-chatbot/discussions)
- **Course**: University of Bonn - Dialogue Systems

---

*"I am the bridge between ancient wisdom and modern understanding. Through me, the voices of millennia speak to the curious minds of today."* - The Rosetta Stone Agent

**Developed as part of the Dialogue Systems course at University of Bonn**  
**Authors**: Mohammaderfan Koupaei, Mahshid Khanali, Niloufar Asghari  
**Digital embodiment of 2,200+ years of history**