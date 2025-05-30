import gradio as gr
import asyncio
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import threading
import time

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config, get_config
from core.agent import RosettaStoneAgent, AgentResponse
from core.memory import MemoryManager

class GradioInterface:
    """Gradio web interface for the Rosetta Stone Agent"""
    
    def __init__(self, config_file: Optional[str] = None):
        # Initialize configuration
        self.config = Config(config_file) if config_file else get_config()
        
        # Initialize agent
        self.agent = RosettaStoneAgent(self.config)
        
        # Interface state
        self.session_active = False
        self.current_user_id = "gradio_user"
        
        # Chat history for display
        self.chat_history = []
        
        # Performance tracking
        self.session_stats = {
            'messages_count': 0,
            'total_response_time': 0.0,
            'start_time': None,
            'tools_used_count': {},
            'topics_discussed': set()
        }
        
        # Initialize Gradio theme and components
        self.theme = self._create_custom_theme()
        
    def _create_custom_theme(self) -> gr.Theme:
        """Create custom Rosetta Stone themed interface"""
        
        # Custom CSS for ancient Egyptian aesthetic
        custom_css = """
        /* Rosetta Stone Theme */
        .gradio-container {
            background: linear-gradient(135deg, #2c1810 0%, #4a3728 50%, #6b4c36 100%);
            color: #f4e4bc;
            font-family: 'Crimson Text', 'Times New Roman', serif;
        }
        
        .chat-message {
            background: rgba(244, 228, 188, 0.1);
            border: 1px solid #8b6914;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        .user-message {
            background: rgba(139, 105, 20, 0.2);
            border-left: 4px solid #d4af37;
        }
        
        .agent-message {
            background: rgba(75, 55, 40, 0.3);
            border-left: 4px solid #cd853f;
        }
        
        .hieroglyph-accent {
            color: #d4af37;
            font-weight: bold;
        }
        
        .stone-texture {
            background: repeating-linear-gradient(
                45deg,
                rgba(244, 228, 188, 0.1),
                rgba(244, 228, 188, 0.1) 2px,
                transparent 2px,
                transparent 4px
            );
        }
        
        .status-panel {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid #8b6914;
            border-radius: 8px;
            padding: 10px;
        }
        
        .tool-indicator {
            display: inline-block;
            background: #8b6914;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 2px;
        }
        
        .confidence-bar {
            background: linear-gradient(90deg, #cd853f 0%, #d4af37 100%);
            height: 4px;
            border-radius: 2px;
            margin: 5px 0;
        }
        
        /* Hieroglyph symbols */
        .hieroglyph {
            font-size: 1.2em;
            color: #d4af37;
        }
        
        /* Loading animation */
        .thinking-stone {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        """
        
        return gr.themes.Base().set(
            body_background_fill="linear-gradient(135deg, #2c1810 0%, #4a3728 50%, #6b4c36 100%)",
            body_text_color="#f4e4bc",
            block_background_fill="rgba(244, 228, 188, 0.1)",
            block_border_color="#8b6914",
            input_background_fill="rgba(244, 228, 188, 0.2)",
            button_primary_background_fill="#8b6914",
            button_primary_text_color="white"
        )
    
    def start_session(self, user_id: str = None) -> Tuple[str, str, str]:
        """Start a new agent session"""
        
        if user_id:
            self.current_user_id = user_id
        
        try:
            # Start agent session
            session_info = self.agent.start_session(self.current_user_id)
            self.session_active = True
            self.session_stats['start_time'] = datetime.now()
            
            # Clear chat history
            self.chat_history = []
            
            # Welcome message
            welcome_msg = """🏺 **The Rosetta Stone Awakens** 🏺

Greetings, seeker of ancient wisdom! I am the Rosetta Stone, carved in 196 BCE during the reign of Ptolemy V. Through millennia, I have watched civilizations rise and fall, and now I share my knowledge with you.

**What I can help you with:**
- 🔍 **Historical Research**: Ask about ancient Egypt, pharaohs, dynasties, and archaeological discoveries
- 📜 **Translation**: Interpret hieroglyphs, ancient Greek, and demotic script
- 🏛️ **Cultural Insights**: Learn about daily life, religion, and customs of ancient civilizations
- ⏳ **Timeline Analysis**: Explore historical events and their connections across time

Ask me anything about the ancient world, and let the wisdom of ages guide our conversation..."""
            
            status_msg = f"✅ Session started for user: {self.current_user_id}"
            tools_info = f"🛠️ Available tools: {', '.join(self.agent.tools.keys())}"
            
            return welcome_msg, status_msg, tools_info
            
        except Exception as e:
            error_msg = f"❌ Failed to start session: {str(e)}"
            return error_msg, "❌ Session failed", "No tools available"
    
    def process_message(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str, str, str]:
        """Process user message and return updated chat history and status"""
        
        if not self.session_active:
            error_response = "❌ No active session. Please start a session first."
            history.append((message, error_response))
            return history, "❌ No session", "", ""
        
        if not message.strip():
            return history, "Status: Ready", "", ""
        
        try:
            # Record start time
            start_time = time.time()
            
            # Process message with agent
            response = asyncio.run(self.agent.process_message(message))
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update statistics
            self._update_session_stats(response, response_time)
            
            # Format response for display
            formatted_response = self._format_response_for_gradio(response)
            
            # Add to chat history
            history.append((message, formatted_response))
            
            # Generate status information
            status_msg = self._generate_status_message(response, response_time)
            tools_msg = self._generate_tools_message(response)
            perf_msg = self._generate_performance_message(response, response_time)
            
            return history, status_msg, tools_msg, perf_msg
            
        except Exception as e:
            error_response = f"❌ Error processing message: {str(e)}"
            history.append((message, error_response))
            return history, f"❌ Error: {str(e)}", "", ""
    
    def _format_response_for_gradio(self, response: AgentResponse) -> str:
        """Format agent response for Gradio display"""
        
        formatted_parts = []
        
        # Main response content
        formatted_parts.append(response.content)
        
        # Add metadata section if available
        if response.metadata and any(response.metadata.values()):
            formatted_parts.append("\n---")
            
            # Reasoning complexity
            if response.metadata.get('complexity'):
                complexity_emoji = {
                    'simple': '🟢',
                    'moderate': '🟡', 
                    'complex': '🔴'
                }.get(response.metadata['complexity'], '⚪')
                formatted_parts.append(f"{complexity_emoji} **Complexity**: {response.metadata['complexity'].title()}")
            
            # Framework used
            if response.metadata.get('framework'):
                formatted_parts.append(f"⚙️ **Framework**: {response.metadata['framework']}")
        
        # Confidence indicator
        if response.confidence_score > 0:
            confidence_bar = "█" * int(response.confidence_score * 10)
            confidence_empty = "░" * (10 - int(response.confidence_score * 10))
            formatted_parts.append(f"\n🎯 **Confidence**: {confidence_bar}{confidence_empty} {response.confidence_score:.1%}")
        
        # Topics discussed
        if response.topics_mentioned:
            topics_str = " • ".join([f"#{topic}" for topic in response.topics_mentioned[:5]])
            formatted_parts.append(f"📚 **Topics**: {topics_str}")
        
        # Tools used indicator
        if response.tools_used:
            tools_emojis = {
                'wikipedia': '📖',
                'egyptian_knowledge': '🏺',
                'historical_timeline': '⏳',
                'translation': '📜'
            }
            tool_indicators = []
            for tool in response.tools_used:
                emoji = tools_emojis.get(tool, '🔧')
                tool_indicators.append(f"{emoji} {tool}")
            
            formatted_parts.append(f"🛠️ **Tools Used**: {' • '.join(tool_indicators)}")
        
        return "\n".join(formatted_parts)
    
    def _update_session_stats(self, response: AgentResponse, response_time: float):
        """Update session statistics"""
        
        self.session_stats['messages_count'] += 1
        self.session_stats['total_response_time'] += response_time
        
        # Track tools used
        for tool in response.tools_used:
            self.session_stats['tools_used_count'][tool] = \
                self.session_stats['tools_used_count'].get(tool, 0) + 1
        
        # Track topics
        if response.topics_mentioned:
            self.session_stats['topics_discussed'].update(response.topics_mentioned)
    
    def _generate_status_message(self, response: AgentResponse, response_time: float) -> str:
        """Generate status message for sidebar"""
        
        status_parts = []
        
        # Session info
        if self.session_stats['start_time']:
            session_duration = (datetime.now() - self.session_stats['start_time']).total_seconds() / 60
            status_parts.append(f"⏱️ Session: {session_duration:.1f} min")
        
        # Message count
        status_parts.append(f"💬 Messages: {self.session_stats['messages_count']}")
        
        # Response time
        status_parts.append(f"⚡ Last response: {response_time:.2f}s")
        
        # Emotional state
        if response.emotional_state:
            emotion_emojis = {
                'contemplative': '🤔',
                'nostalgic': '😌',
                'excited': '😊',
                'proud': '😤',
                'wise': '🧙‍♂️'
            }
            emoji = emotion_emojis.get(response.emotional_state, '😐')
            status_parts.append(f"{emoji} Mood: {response.emotional_state}")
        
        return "\n".join(status_parts)
    
    def _generate_tools_message(self, response: AgentResponse) -> str:
        """Generate tools information message"""
        
        if not response.tools_used:
            return "🔧 No tools used"
        
        tool_descriptions = {
            'wikipedia': 'Searched Wikipedia for historical information',
            'egyptian_knowledge': 'Accessed specialized Egyptian knowledge base',
            'historical_timeline': 'Analyzed historical timeline and chronology',
            'translation': 'Translated ancient scripts and languages'
        }
        
        tools_info = []
        for tool in response.tools_used:
            desc = tool_descriptions.get(tool, f'Used {tool} tool')
            tools_info.append(f"• {desc}")
        
        return "\n".join(tools_info)
    
    def _generate_performance_message(self, response: AgentResponse, response_time: float) -> str:
        """Generate performance information message"""
        
        perf_parts = []
        
        # Response metrics
        perf_parts.append(f"⚡ Response time: {response_time:.2f}s")
        perf_parts.append(f"🎯 Confidence: {response.confidence_score:.1%}")
        
        # Processing details
        if response.metadata:
            if response.metadata.get('reasoning_steps'):
                perf_parts.append(f"🧠 Reasoning steps: {response.metadata['reasoning_steps']}")
            
            if response.metadata.get('tool_results_count'):
                perf_parts.append(f"🔍 Tool queries: {response.metadata['tool_results_count']}")
        
        # Session averages
        if self.session_stats['messages_count'] > 0:
            avg_response_time = self.session_stats['total_response_time'] / self.session_stats['messages_count']
            perf_parts.append(f"📊 Avg response: {avg_response_time:.2f}s")
        
        return "\n".join(perf_parts)
    
    def get_memory_info(self) -> str:
        """Get memory information for display"""
        
        try:
            memory_stats = self.agent.memory_manager.get_memory_stats()
            
            memory_info = [
                "🧠 **Memory Status**",
                f"• Short-term: {memory_stats['short_term_turns']} items",
                f"• Topics: {memory_stats['current_topics']} active",
                f"• Session: {memory_stats['session_duration']:.1f} min"
            ]
            
            # User profile info
            if memory_stats['user_profiles'] > 0:
                memory_info.append(f"• Profile: {memory_stats['user_profiles']} users tracked")
            
            # Stone's memories
            if memory_stats['memorable_conversations'] > 0:
                memory_info.append(f"• Stone memories: {memory_stats['memorable_conversations']} experiences")
            
            return "\n".join(memory_info)
            
        except Exception as e:
            return f"❌ Memory info error: {str(e)}"
    
    def get_session_summary(self) -> str:
        """Get session summary for display"""
        
        try:
            summary_parts = ["📊 **Session Summary**"]
            
            # Basic stats
            summary_parts.append(f"• Messages exchanged: {self.session_stats['messages_count']}")
            
            if self.session_stats['start_time']:
                duration = (datetime.now() - self.session_stats['start_time']).total_seconds() / 60
                summary_parts.append(f"• Duration: {duration:.1f} minutes")
            
            # Tools usage
            if self.session_stats['tools_used_count']:
                most_used_tool = max(self.session_stats['tools_used_count'].items(), key=lambda x: x[1])
                summary_parts.append(f"• Most used tool: {most_used_tool[0]} ({most_used_tool[1]}x)")
            
            # Topics discussed
            if self.session_stats['topics_discussed']:
                topics_list = list(self.session_stats['topics_discussed'])[:5]
                summary_parts.append(f"• Topics discussed: {', '.join(topics_list)}")
            
            # Performance
            if self.session_stats['messages_count'] > 0:
                avg_time = self.session_stats['total_response_time'] / self.session_stats['messages_count']
                summary_parts.append(f"• Average response time: {avg_time:.2f}s")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"❌ Summary error: {str(e)}"
    
    def export_conversation(self, history: List[Tuple[str, str]]) -> str:
        """Export conversation history"""
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"rosetta_conversation_{timestamp}.json"
            
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'user_id': self.current_user_id,
                    'session_duration_minutes': (datetime.now() - self.session_stats['start_time']).total_seconds() / 60 if self.session_stats['start_time'] else 0
                },
                'conversation': [
                    {'user': turn[0], 'agent': turn[1]} for turn in history
                ],
                'session_stats': {
                    **self.session_stats,
                    'topics_discussed': list(self.session_stats['topics_discussed']),
                    'start_time': self.session_stats['start_time'].isoformat() if self.session_stats['start_time'] else None
                },
                'agent_info': self.agent.get_agent_status()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return f"✅ Conversation exported to {filename}"
            
        except Exception as e:
            return f"❌ Export failed: {str(e)}"
    
    def clear_conversation(self) -> Tuple[List, str]:
        """Clear conversation history and reset session"""
        
        try:
            # Clear chat history
            self.chat_history = []
            
            # Reset session stats
            self.session_stats = {
                'messages_count': 0,
                'total_response_time': 0.0,
                'start_time': datetime.now(),
                'tools_used_count': {},
                'topics_discussed': set()
            }
            
            # Clear agent memory
            self.agent.memory_manager.clear_session_memory()
            
            return [], "🧹 Conversation cleared and session reset"
            
        except Exception as e:
            return [], f"❌ Clear failed: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface"""
        
        with gr.Blocks(
            theme=self.theme,
            css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: auto;
            }
            .chat-container {
                height: 600px;
                overflow-y: auto;
            }
            .sidebar {
                background: rgba(0, 0, 0, 0.2);
                padding: 15px;
                border-radius: 10px;
            }
            """,
            title="🏺 Rosetta Stone Agent"
        ) as interface:
            
            # Header
            gr.HTML("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #8b6914, #d4af37, #8b6914); border-radius: 10px; margin-bottom: 20px;">
                <h1 style="color: white; margin: 0; font-size: 2.5em;">🏺 The Rosetta Stone Agent 🏺</h1>
                <p style="color: #f4e4bc; margin: 10px 0 0 0; font-size: 1.2em;">"Bridge between ancient wisdom and modern understanding"</p>
            </div>
            """)
            
            with gr.Row():
                # Main chat area
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        [],
                        elem_id="chatbot",
                        height=500,
                        show_label=False,
                        container=True,
                        bubble_full_width=False
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="Ask the Rosetta Stone about ancient wisdom, history, or translations...",
                            container=False,
                            scale=4,
                            autofocus=True
                        )
                        send_btn = gr.Button("Send 📤", scale=1, variant="primary")
                
                # Sidebar with controls and information
                with gr.Column(scale=1, elem_classes=["sidebar"]):
                    gr.HTML("<h3 style='color: #d4af37; text-align: center;'>🏺 Stone Status</h3>")
                    
                    # Session controls
                    with gr.Group():
                        user_id_input = gr.Textbox(
                            value="gradio_user",
                            label="User ID",
                            placeholder="Enter your user ID"
                        )
                        start_session_btn = gr.Button("Start Session 🚀", variant="primary")
                        session_status = gr.Textbox(
                            label="Session Status",
                            interactive=False,
                            lines=3
                        )
                    
                    # Information panels
                    with gr.Accordion("🛠️ Tools & Performance", open=False):
                        tools_info = gr.Textbox(
                            label="Tools Used",
                            interactive=False,
                            lines=3
                        )
                        performance_info = gr.Textbox(
                            label="Performance",
                            interactive=False,
                            lines=4
                        )
                    
                    with gr.Accordion("🧠 Memory & Analytics", open=False):
                        memory_info = gr.Textbox(
                            label="Memory Status",
                            interactive=False,
                            lines=4
                        )
                        session_summary = gr.Textbox(
                            label="Session Summary",
                            interactive=False,
                            lines=5
                        )
                    
                    # Action buttons
                    with gr.Group():
                        gr.HTML("<h4 style='color: #d4af37;'>Actions</h4>")
                        
                        refresh_btn = gr.Button("Refresh Info 🔄", size="sm")
                        export_btn = gr.Button("Export Chat 💾", size="sm")
                        clear_btn = gr.Button("Clear Chat 🧹", size="sm", variant="stop")
                        
                        export_status = gr.Textbox(
                            label="Export Status",
                            interactive=False,
                            lines=2
                        )
            
            # Footer
            gr.HTML("""
            <div style="text-align: center; padding: 15px; margin-top: 20px; background: rgba(0, 0, 0, 0.2); border-radius: 10px;">
                <p style="color: #8b6914; margin: 0;">
                    🏺 Powered by the wisdom of millennia • Built with the Hugging Face Agents framework
                </p>
            </div>
            """)
            
            # Event handlers
            def handle_start_session(user_id):
                welcome_msg, status_msg, tools_msg = self.start_session(user_id)
                initial_history = [("Welcome", welcome_msg)]
                return initial_history, status_msg, tools_msg
            
            def handle_message(message, history):
                return self.process_message(message, history)
            
            def handle_refresh():
                memory_info = self.get_memory_info()
                summary_info = self.get_session_summary()
                return memory_info, summary_info
            
            def handle_export(history):
                return self.export_conversation(history)
            
            def handle_clear():
                return self.clear_conversation()
            
            # Wire up events
            start_session_btn.click(
                handle_start_session,
                inputs=[user_id_input],
                outputs=[chatbot, session_status, tools_info]
            )
            
            # Message handling
            msg_input.submit(
                handle_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, session_status, tools_info, performance_info]
            ).then(
                lambda: "",
                outputs=[msg_input]
            )
            
            send_btn.click(
                handle_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, session_status, tools_info, performance_info]
            ).then(
                lambda: "",
                outputs=[msg_input]
            )
            
            # Utility buttons
            refresh_btn.click(
                handle_refresh,
                outputs=[memory_info, session_summary]
            )
            
            export_btn.click(
                handle_export,
                inputs=[chatbot],
                outputs=[export_status]
            )
            
            clear_btn.click(
                handle_clear,
                outputs=[chatbot, export_status]
            )
            
        return interface

def create_gradio_app(config_file: Optional[str] = None, 
                     share: bool = False, 
                     server_port: int = 7860,
                     server_name: str = "127.0.0.1") -> gr.Blocks:
    """Create and configure the Gradio application"""
    
    gradio_interface = GradioInterface(config_file)
    app = gradio_interface.create_interface()
    
    return app

def main():
    """Main entry point for Gradio interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Rosetta Stone Agent - Web Interface")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--port", type=int, default=7860, help="Server port (default: 7860)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--share", action="store_true", help="Create public sharing link")
    parser.add_argument("--auth", type=str, help="Authentication in format 'username:password'")
    
    args = parser.parse_args()
    
    # Create the app
    app = create_gradio_app(
        config_file=args.config,
        share=args.share,
        server_port=args.port,
        server_name=args.host
    )
    
    # Setup authentication if provided
    auth = None
    if args.auth:
        try:
            username, password = args.auth.split(":", 1)
            auth = (username, password)
        except ValueError:
            print("❌ Invalid auth format. Use 'username:password'")
            return
    
    # Launch the app
    print(f"🚀 Starting Rosetta Stone Agent Web Interface...")
    print(f"📡 Server: http://{args.host}:{args.port}")
    
    if args.share:
        print("🌐 Public sharing enabled")
    
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        auth=auth,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()