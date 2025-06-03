#!/usr/bin/env python3
"""
API Bridge for Rosetta Stone Agent UI
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.agent import RosettaStoneAgent
from core.config import get_config

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize the agent
config = get_config()
agent = RosettaStoneAgent(config)
session_started = False

@app.route('/')
def serve_ui():
    """Serve the main UI file"""
    return send_from_directory('interfaces/rosetta_ui', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory('interfaces/rosetta_ui', filename)

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Start a new agent session"""
    global session_started
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'web_user')
        
        session_info = agent.start_session(user_id)
        session_started = True
        
        return jsonify({
            'success': True,
            'session_info': session_info,
            'message': 'Session started successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """Send message to the agent"""
    global session_started
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        message = data['message']
        framework = data.get('framework', 'smolagents')
        
        # Start session if not started
        if not session_started:
            agent.start_session('web_user')
            session_started = True
        
        # Update framework if changed
        if hasattr(agent.config.agent, 'framework'):
            from core.config import Framework 
            framework_map = {
        'smolagents': Framework.SMOLAGENTS,
        'llamaindex': Framework.LLAMAINDEX, 
        'langgraph': Framework.LANGGRAPH
    }
            if framework in framework_map:
                agent.config.agent.framework = framework_map[framework]
            print(f"✅ Framework switched to: {framework}")
        else:
            print(f"⚠️ Unknown framework: {framework}, keeping current")
        
        # Process message with the real agent
        response = asyncio.run(agent.process_message(message))
        
        # Format response for UI
        formatted_response = {
            'success': True,
            'content': response.content,
            'confidence': response.confidence_score,
            'tools_used': response.tools_used,
            'processing_time': response.processing_time,
            'emotional_state': response.emotional_state,
            'topics_mentioned': response.topics_mentioned,
            'framework': framework,
            'metadata': response.metadata or {}
        }
        
        return jsonify(formatted_response)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'content': f"The ancient mechanisms encounter difficulty: {str(e)}"
        }), 500

@app.route('/api/agent_status', methods=['GET'])
def get_agent_status():
    """Get current agent status"""
    try:
        status = agent.get_agent_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/switch_framework', methods=['POST'])
def switch_framework():
    """Switch AI framework"""
    try:
        data = request.get_json()
        framework = data.get('framework', 'smolagents')
        
        # Update framework in config (convert string to proper enum)
        if hasattr(agent.config.agent, 'framework'):
            from core.config import Framework
            
            framework_map = {
                'smolagents': Framework.SMOLAGENTS,
                'llamaindex': Framework.LLAMAINDEX,
                'langgraph': Framework.LANGGRAPH
            }
            
            if framework in framework_map:
                agent.config.agent.framework = framework_map[framework]
                print(f"✅ Framework switched to: {framework}")
            else:
                print(f"⚠️ Unknown framework: {framework}, keeping current")
        
        return jsonify({
            'success': True,
            'framework': framework,
            'message': f'Framework switched to {framework}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
if __name__ == '__main__':
    print("🏺 Starting Rosetta Stone Agent API Bridge...")
    print("🌐 UI will be available at: http://localhost:8080")  # Change this
    print("🔗 API endpoints available at: http://localhost:8080/api/") 
    
    app.run(host='0.0.0.0', port=8080, debug=True)

