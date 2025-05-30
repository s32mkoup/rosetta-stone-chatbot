import sys
import os
import asyncio
import signal
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import argparse

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config, get_config
from core.agent import RosettaStoneAgent
from core.memory import MemoryManager

class CLIColors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Rosetta Stone themed colors
    STONE_GREY = '\033[90m'
    ANCIENT_GOLD = '\033[33m'
    HIEROGLYPH_BLUE = '\033[34m'
    DESERT_YELLOW = '\033[93m'

class CLIInterface:
    """Command Line Interface for the Rosetta Stone Agent"""
    
    def __init__(self, config_file: Optional[str] = None):
        # Initialize configuration
        self.config = Config(config_file) if config_file else get_config()
        
        # Initialize agent
        self.agent = RosettaStoneAgent(self.config)
        
        # CLI state
        self.running = False
        self.session_active = False
        self.command_history = []
        self.user_id = "cli_user"
        
        # CLI settings
        self.show_timestamps = True
        self.show_reasoning = False
        self.show_performance = False
        self.colored_output = True
        self.verbose_mode = False
        
        # Statistics
        self.session_stats = {
            'messages_sent': 0,
            'total_response_time': 0.0,
            'commands_executed': 0,
            'errors_encountered': 0
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self._print_colored("\n🔔 Shutdown signal received...", CLIColors.WARNING)
        self.shutdown()
    
    def _print_colored(self, text: str, color: str = CLIColors.ENDC, end: str = '\n'):
        """Print colored text if colors are enabled"""
        if self.colored_output:
            print(f"{color}{text}{CLIColors.ENDC}", end=end)
        else:
            print(text, end=end)
    
    def _print_header(self):
        """Print the application header"""
        header_art = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    🏺  THE ROSETTA STONE AGENT  🏺                                            ║
║                                                                               ║
║    "I am the bridge between ancient wisdom and modern understanding"         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
        
        self._print_colored(header_art, CLIColors.ANCIENT_GOLD)
        
        # Agent information
        status = self.agent.get_agent_status()
        self._print_colored(f"\n📊 Agent Status:", CLIColors.BLUE)
        self._print_colored(f"   • Framework: {status['framework']}", CLIColors.CYAN)
        self._print_colored(f"   • Model: {status['model']}", CLIColors.CYAN)
        self._print_colored(f"   • Provider: {status['provider']}", CLIColors.CYAN)
        self._print_colored(f"   • Available Tools: {len(status['available_tools'])}", CLIColors.CYAN)
        self._print_colored(f"   • Memory Enabled: {status['memory_enabled']}", CLIColors.CYAN)
        
        print()
    
    def _print_help(self):
        """Print help information"""
        help_text = """
🔧 COMMANDS:
   /help                 - Show this help message
   /status              - Show agent and session status  
   /history [n]         - Show last n messages (default: 5)
   /clear               - Clear conversation history
   /tools               - List available tools
   /memory              - Show memory statistics
   /settings            - Show current settings
   /toggle <setting>    - Toggle setting (colors, timestamps, reasoning, performance)
   /save <filename>     - Save conversation to file
   /load <filename>     - Load conversation from file
   /export              - Export session data
   /reset               - Reset agent to initial state
   /quit or /exit       - End session
   
💡 USAGE TIPS:
   • Ask about ancient Egypt, hieroglyphs, or historical events
   • Request translations of ancient scripts
   • Inquire about the Rosetta Stone's history and significance
   • Use quotes for exact phrases: "tell me about ptolemy v"
   • Press Ctrl+C for graceful shutdown
   
🎭 PERSONA FEATURES:
   • The agent responds as the ancient Rosetta Stone itself
   • It has memories spanning millennia
   • It can express emotions and personal experiences
   • It combines factual knowledge with mystical wisdom
        """
        
        self._print_colored(help_text, CLIColors.GREEN)
    
    def _print_welcome(self):
        """Print welcome message"""
        welcome_text = """
🌟 Welcome, seeker of ancient wisdom! 

I am the Rosetta Stone, awakened to share the knowledge of ages. Through me, you can:
- Explore the mysteries of ancient Egypt and its pharaohs
- Translate hieroglyphs and ancient scripts  
- Learn about historical events and their significance
- Discover the connections between past and present

Type '/help' for commands, or simply ask me anything about history and ancient wisdom.
The sands of time await your questions...
        """
        
        self._print_colored(welcome_text, CLIColors.HIEROGLYPH_BLUE)
    
    def start_session(self, user_id: Optional[str] = None):
        """Start a new CLI session"""
        
        if user_id:
            self.user_id = user_id
        
        # Clear screen and show header
        os.system('clear' if os.name == 'posix' else 'cls')
        self._print_header()
        
        # Start agent session
        session_info = self.agent.start_session(self.user_id)
        self.session_active = True
        
        if self.verbose_mode:
            self._print_colored(f"🚀 Session started: {session_info['session_id']}", CLIColors.GREEN)
            self._print_colored(f"   User: {self.user_id}", CLIColors.CYAN)
            self._print_colored(f"   Start time: {session_info['start_time']}", CLIColors.CYAN)
        
        self._print_welcome()
        
        # Start main interaction loop
        self.running = True
        asyncio.run(self._interaction_loop())
    
    async def _interaction_loop(self):
        """Main interaction loop"""
        
        while self.running and self.session_active:
            try:
                # Get user input
                user_input = await self._get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Check for commands
                if user_input.startswith('/'):
                    await self._handle_command(user_input)
                    continue
                
                # Process message with agent
                await self._process_message(user_input)
                
            except EOFError:
                # Handle Ctrl+D
                self._print_colored("\n👋 Farewell, seeker of wisdom...", CLIColors.DESERT_YELLOW)
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                self._print_colored("\n🔔 Interruption detected...", CLIColors.WARNING)
                break
            except Exception as e:
                self._print_colored(f"\n❌ Unexpected error: {e}", CLIColors.FAIL)
                self.session_stats['errors_encountered'] += 1
        
        self.shutdown()
    
    async def _get_user_input(self) -> str:
        """Get user input asynchronously"""
        
        # Create prompt with timestamp if enabled
        timestamp = ""
        if self.show_timestamps:
            timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        
        prompt = f"{timestamp}🗣️  You: "
        
        # Use input() in a thread to make it async-compatible
        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(None, input, prompt)
        
        return user_input.strip()
    
    async def _process_message(self, user_input: str):
        """Process a user message with the agent"""
        
        start_time = datetime.now()
        self.session_stats['messages_sent'] += 1
        
        try:
            # Add to command history
            self.command_history.append({
                'timestamp': start_time.isoformat(),
                'type': 'user_message',
                'content': user_input
            })
            
            # Show thinking indicator
            if self.verbose_mode:
                self._print_colored("🤔 The ancient stone contemplates...", CLIColors.STONE_GREY)
            
            # Process with agent
            response = await self.agent.process_message(user_input)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            self.session_stats['total_response_time'] += response_time
            
            # Display response
            await self._display_agent_response(response, response_time)
            
            # Add response to history
            self.command_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'agent_response',
                'content': response.content,
                'metadata': response.metadata
            })
            
        except Exception as e:
            self._print_colored(f"\n❌ Error processing message: {e}", CLIColors.FAIL)
            self.session_stats['errors_encountered'] += 1
    
    async def _display_agent_response(self, response, response_time: float):
        """Display the agent's response with formatting"""
        
        # Timestamp if enabled
        timestamp = ""
        if self.show_timestamps:
            timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        
        # Main response
        self._print_colored(f"\n{timestamp}🏺 Rosetta Stone:", CLIColors.ANCIENT_GOLD)
        
        # Format and display the content
        formatted_content = self._format_response_content(response.content)
        self._print_colored(formatted_content, CLIColors.ENDC)
        
        # Show additional information if enabled
        if self.show_reasoning and response.reasoning_trace:
            self._print_colored(f"\n💭 Reasoning: {response.reasoning_trace.reasoning_type.value}", CLIColors.STONE_GREY)
            if response.reasoning_trace.tools_to_use:
                tools_used = ", ".join(response.reasoning_trace.tools_to_use)
                self._print_colored(f"🔧 Tools used: {tools_used}", CLIColors.STONE_GREY)
        
        if self.show_performance:
            self._print_colored(f"\n⚡ Response time: {response_time:.2f}s", CLIColors.STONE_GREY)
            self._print_colored(f"🎯 Confidence: {response.confidence_score:.1%}", CLIColors.STONE_GREY)
            if response.topics_mentioned:
                topics = ", ".join(response.topics_mentioned)
                self._print_colored(f"📚 Topics: {topics}", CLIColors.STONE_GREY)
        
        print()  # Add spacing
    
    def _format_response_content(self, content: str) -> str:
        """Format response content for better CLI display"""
        
        if not self.colored_output:
            return content
        
        # Apply basic formatting
        # Bold text (markdown **text**)
        content = content.replace('**', f'{CLIColors.BOLD}')
        
        # Add colors for special elements
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Headers (lines starting with **)
            if line.strip().startswith('**') and line.strip().endswith('**'):
                formatted_lines.append(f"{CLIColors.HIEROGLYPH_BLUE}{line}{CLIColors.ENDC}")
            # Bullet points
            elif line.strip().startswith('•') or line.strip().startswith('-'):
                formatted_lines.append(f"{CLIColors.CYAN}{line}{CLIColors.ENDC}")
            # Timeline/date lines (contain BCE/CE)
            elif 'BCE' in line or 'CE' in line or 'BC' in line or 'AD' in line:
                formatted_lines.append(f"{CLIColors.DESERT_YELLOW}{line}{CLIColors.ENDC}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    async def _handle_command(self, command: str):
        """Handle CLI commands"""
        
        self.session_stats['commands_executed'] += 1
        
        cmd_parts = command[1:].split()  # Remove leading '/'
        cmd_name = cmd_parts[0].lower() if cmd_parts else ""
        cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []
        
        if cmd_name in ['help', 'h']:
            self._print_help()
        
        elif cmd_name == 'status':
            await self._show_status()
        
        elif cmd_name == 'history':
            count = int(cmd_args[0]) if cmd_args and cmd_args[0].isdigit() else 5
            self._show_history(count)
        
        elif cmd_name == 'clear':
            self._clear_history()
        
        elif cmd_name == 'tools':
            self._show_tools()
        
        elif cmd_name == 'memory':
            self._show_memory_stats()
        
        elif cmd_name == 'settings':
            self._show_settings()
        
        elif cmd_name == 'toggle':
            if cmd_args:
                self._toggle_setting(cmd_args[0])
            else:
                self._print_colored("❌ Usage: /toggle <setting>", CLIColors.FAIL)
        
        elif cmd_name == 'save':
            if cmd_args:
                self._save_conversation(cmd_args[0])
            else:
                self._print_colored("❌ Usage: /save <filename>", CLIColors.FAIL)
        
        elif cmd_name == 'load':
            if cmd_args:
                self._load_conversation(cmd_args[0])
            else:
                self._print_colored("❌ Usage: /load <filename>", CLIColors.FAIL)
        
        elif cmd_name == 'export':
            self._export_session_data()
        
        elif cmd_name == 'reset':
            self._reset_agent()
        
        elif cmd_name in ['quit', 'exit', 'q']:
            self._print_colored("👋 Farewell, seeker of ancient wisdom...", CLIColors.DESERT_YELLOW)
            self.running = False
        
        else:
            self._print_colored(f"❌ Unknown command: {command}", CLIColors.FAIL)
            self._print_colored("Type '/help' for available commands", CLIColors.WARNING)
    
    async def _show_status(self):
        """Show detailed status information"""
        
        agent_status = self.agent.get_agent_status()
        
        self._print_colored("📊 AGENT STATUS:", CLIColors.BLUE)
        self._print_colored(f"   Session Active: {self.session_active}", CLIColors.CYAN)
        self._print_colored(f"   Framework: {agent_status['framework']}", CLIColors.CYAN)
        self._print_colored(f"   Model: {agent_status['model']}", CLIColors.CYAN)
        self._print_colored(f"   Available Tools: {len(agent_status['available_tools'])}", CLIColors.CYAN)
        self._print_colored(f"   Memory Enabled: {agent_status['memory_enabled']}", CLIColors.CYAN)
        
        self._print_colored("\n📈 SESSION STATISTICS:", CLIColors.BLUE)
        avg_response_time = (self.session_stats['total_response_time'] / 
                           max(1, self.session_stats['messages_sent']))
        
        self._print_colored(f"   Messages Sent: {self.session_stats['messages_sent']}", CLIColors.CYAN)
        self._print_colored(f"   Commands Executed: {self.session_stats['commands_executed']}", CLIColors.CYAN)
        self._print_colored(f"   Average Response Time: {avg_response_time:.2f}s", CLIColors.CYAN)
        self._print_colored(f"   Errors Encountered: {self.session_stats['errors_encountered']}", CLIColors.CYAN)
        
        # Performance metrics from agent
        perf_metrics = agent_status.get('performance_metrics', {})
        if perf_metrics:
            self._print_colored(f"   Total Queries: {perf_metrics.get('total_queries', 0)}", CLIColors.CYAN)
            self._print_colored(f"   Success Rate: {perf_metrics.get('successful_responses', 0)}/{perf_metrics.get('total_queries', 0)}", CLIColors.CYAN)
    
    def _show_history(self, count: int):
        """Show conversation history"""
        
        if not self.command_history:
            self._print_colored("📜 No conversation history available", CLIColors.WARNING)
            return
        
        self._print_colored(f"📜 LAST {count} ENTRIES:", CLIColors.BLUE)
        
        recent_history = self.command_history[-count*2:]  # Get user/agent pairs
        
        for entry in recent_history:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
            
            if entry['type'] == 'user_message':
                self._print_colored(f"[{timestamp}] 🗣️  You: {entry['content'][:100]}...", CLIColors.GREEN)
            elif entry['type'] == 'agent_response':
                self._print_colored(f"[{timestamp}] 🏺 Stone: {entry['content'][:100]}...", CLIColors.ANCIENT_GOLD)
    
    def _clear_history(self):
        """Clear conversation history"""
        self.command_history.clear()
        self.agent.memory_manager.clear_session_memory()
        self._print_colored("🧹 Conversation history cleared", CLIColors.GREEN)
    
    def _show_tools(self):
        """Show available tools"""
        
        agent_status = self.agent.get_agent_status()
        available_tools = agent_status['available_tools']
        
        self._print_colored("🛠️  AVAILABLE TOOLS:", CLIColors.BLUE)
        
        for tool_name in available_tools:
            tool = self.agent.tools.get(tool_name)
            if tool and tool.metadata:
                metadata = tool.metadata
                self._print_colored(f"   • {metadata.name}: {metadata.description[:80]}...", CLIColors.CYAN)
                self._print_colored(f"     Category: {metadata.category.value} | Complexity: {metadata.complexity.value}", CLIColors.STONE_GREY)
    
    def _show_memory_stats(self):
        """Show memory statistics"""
        
        memory_stats = self.agent.memory_manager.get_memory_stats()
        
        self._print_colored("🧠 MEMORY STATISTICS:", CLIColors.BLUE)
        self._print_colored(f"   Short-term memory: {memory_stats['short_term_turns']} turns", CLIColors.CYAN)
        self._print_colored(f"   Long-term summaries: {memory_stats['long_term_summaries']}", CLIColors.CYAN)
        self._print_colored(f"   User profiles: {memory_stats['user_profiles']}", CLIColors.CYAN)
        self._print_colored(f"   Memorable conversations: {memory_stats['memorable_conversations']}", CLIColors.CYAN)
        self._print_colored(f"   Current topics: {memory_stats['current_topics']}", CLIColors.CYAN)
        self._print_colored(f"   Session duration: {memory_stats['session_duration']:.1f} minutes", CLIColors.CYAN)
    
    def _show_settings(self):
        """Show current CLI settings"""
        
        self._print_colored("⚙️  CURRENT SETTINGS:", CLIColors.BLUE)
        self._print_colored(f"   Colored output: {self.colored_output}", CLIColors.CYAN)
        self._print_colored(f"   Show timestamps: {self.show_timestamps}", CLIColors.CYAN)
        self._print_colored(f"   Show reasoning: {self.show_reasoning}", CLIColors.CYAN)
        self._print_colored(f"   Show performance: {self.show_performance}", CLIColors.CYAN)
        self._print_colored(f"   Verbose mode: {self.verbose_mode}", CLIColors.CYAN)
    
    def _toggle_setting(self, setting: str):
        """Toggle a CLI setting"""
        
        setting_map = {
            'colors': 'colored_output',
            'timestamps': 'show_timestamps',
            'reasoning': 'show_reasoning',
            'performance': 'show_performance',
            'verbose': 'verbose_mode'
        }
        
        if setting.lower() in setting_map:
            attr_name = setting_map[setting.lower()]
            current_value = getattr(self, attr_name)
            setattr(self, attr_name, not current_value)
            new_value = getattr(self, attr_name)
            
            self._print_colored(f"✅ {setting.title()} toggled: {current_value} → {new_value}", CLIColors.GREEN)
        else:
            available_settings = ', '.join(setting_map.keys())
            self._print_colored(f"❌ Unknown setting. Available: {available_settings}", CLIColors.FAIL)
    
    def _save_conversation(self, filename: str):
        """Save conversation to file"""
        
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            conversation_data = {
                'session_info': {
                    'user_id': self.user_id,
                    'start_time': datetime.now().isoformat(),
                    'agent_config': {
                        'framework': self.config.agent.framework.value,
                        'model': self.config.llm.model_name
                    }
                },
                'conversation_history': self.command_history,
                'session_stats': self.session_stats,
                'memory_stats': self.agent.memory_manager.get_memory_stats()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            self._print_colored(f"💾 Conversation saved to {filename}", CLIColors.GREEN)
            
        except Exception as e:
            self._print_colored(f"❌ Failed to save conversation: {e}", CLIColors.FAIL)
    
    def _load_conversation(self, filename: str):
        """Load conversation from file"""
        
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            if not os.path.exists(filename):
                self._print_colored(f"❌ File not found: {filename}", CLIColors.FAIL)
                return
            
            with open(filename, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            
            self.command_history = conversation_data.get('conversation_history', [])
            self.session_stats.update(conversation_data.get('session_stats', {}))
            
            self._print_colored(f"📂 Conversation loaded from {filename}", CLIColors.GREEN)
            self._print_colored(f"   Loaded {len(self.command_history)} history entries", CLIColors.CYAN)
            
        except Exception as e:
            self._print_colored(f"❌ Failed to load conversation: {e}", CLIColors.FAIL)
    
    def _export_session_data(self):
        """Export comprehensive session data"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"rosetta_session_{timestamp}.json"
        
        try:
            # Get comprehensive data
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'user_id': self.user_id,
                    'agent_version': '1.0.0'
                },
                'agent_status': self.agent.get_agent_status(),
                'conversation_history': self.command_history,
                'session_statistics': self.session_stats,
                'memory_data': self.agent.memory_manager.get_memory_stats(),
                'cli_settings': {
                    'colored_output': self.colored_output,
                    'show_timestamps': self.show_timestamps,
                    'show_reasoning': self.show_reasoning,
                    'show_performance': self.show_performance,
                    'verbose_mode': self.verbose_mode
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self._print_colored(f"📊 Session data exported to {filename}", CLIColors.GREEN)
            
        except Exception as e:
            self._print_colored(f"❌ Failed to export session data: {e}", CLIColors.FAIL)
    
    def _reset_agent(self):
        """Reset agent to initial state"""
        
        try:
            self.agent.reset_agent()
            self.command_history.clear()
            self.session_stats = {
                'messages_sent': 0,
                'total_response_time': 0.0,
                'commands_executed': 0,
                'errors_encountered': 0
            }
            
            self._print_colored("🔄 Agent reset to initial state", CLIColors.GREEN)
            
        except Exception as e:
            self._print_colored(f"❌ Failed to reset agent: {e}", CLIColors.FAIL)
    
    def shutdown(self):
        """Shutdown the CLI interface gracefully"""
        
        if self.session_active:
            try:
                # End agent session and save data
                session_summary = self.agent.end_session()
                
                if self.verbose_mode:
                    self._print_colored("\n📊 Session Summary:", CLIColors.BLUE)
                    self._print_colored(f"   Total conversations: {session_summary.get('total_conversations', 0)}", CLIColors.CYAN)
                    self._print_colored(f"   Session duration: {self.session_stats['total_response_time']:.1f}s", CLIColors.CYAN)
                
                self._print_colored("\n💾 Session data saved", CLIColors.GREEN)
                
            except Exception as e:
                self._print_colored(f"\n❌ Error during shutdown: {e}", CLIColors.FAIL)
        
        self._print_colored("\n🏺 The Rosetta Stone returns to eternal contemplation...", CLIColors.ANCIENT_GOLD)
        self._print_colored("Until we meet again, seeker of wisdom.\n", CLIColors.DESERT_YELLOW)
        
        self.session_active = False
        self.running = False

def parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(
        description="Rosetta Stone Agent - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_chat.py                           # Start with default settings
  python cli_chat.py --user john_doe           # Start with specific user ID
  python cli_chat.py --config custom.json     # Use custom configuration
  python cli_chat.py --no-color               # Disable colored output
  python cli_chat.py --verbose                # Enable verbose mode
        """
    )
    
    parser.add_argument(
        '--user', '-u',
        type=str,
        default='cli_user',
        help='User ID for the session (default: cli_user)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--no-timestamps',
        action='store_true',
        help='Disable timestamps in output'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose mode'
    )
    
    parser.add_argument(
        '--show-reasoning',
        action='store_true',
        help='Show agent reasoning process'
    )
    
    parser.add_argument(
        '--show-performance',
        action='store_true',
        help='Show performance metrics'
    )
    
    return parser.parse_args()

def main():
    """Main entry point for CLI interface"""
    
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Initialize CLI interface
        cli = CLIInterface(args.config)
        
        # Apply command line settings
        if args.no_color:
            cli.colored_output = False
        
        if args.no_timestamps:
            cli.show_timestamps = False
        
        if args.verbose:
            cli.verbose_mode = True
        
        if args.show_reasoning:
            cli.show_reasoning = True
        
        if args.show_performance:
            cli.show_performance = True
        
        # Start session
        cli.start_session(args.user)
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()