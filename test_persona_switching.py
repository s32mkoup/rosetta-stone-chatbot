from core.agent import RosettaStoneAgent
from core.config import get_config

agent = RosettaStoneAgent(get_config())
agent.start_session("switching_test_user")

# Store current user for persona controller
agent.current_user_id = "switching_test_user"

test_sequence = [
    "/help",
    "/persona",
    "What are hieroglyphs?",  # Default mystical
    "/persona academic",
    "What are hieroglyphs?",  # Should be scholarly
    "/persona casual", 
    "What are hieroglyphs?",  # Should be friendly
    "/persona mystical",
    "What are hieroglyphs?"   # Back to mystical
]

for i, command in enumerate(test_sequence):
    print(f"\n=== STEP {i+1}: {command} ===")
    response = agent.process_message_sync(command)
    
    # Show first 200 chars of response
    content_preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
    print(f"Response: {content_preview}")
    
    # Show metadata if it's a command
    if hasattr(response, 'metadata') and response.metadata:
        print(f"Command type: {response.metadata}")
    
    print("-" * 60)