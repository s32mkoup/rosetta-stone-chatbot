from core.agent import RosettaStoneAgent
from core.config import get_config

agent = RosettaStoneAgent(get_config())

# Test emotional triggers
test_queries = [
    "I'm so excited about ancient Egypt!",    # Should trigger EXCITED
    "That's so sad about lost civilizations", # Should trigger MELANCHOLIC  
    "You're amazing at translation",          # Should trigger PROUD
    "Tell me about your ancient memories"     # Should trigger NOSTALGIC
]

for i, query in enumerate(test_queries):
    print(f"\n=== TEST {i+1}: {query} ===")
    response = agent.process_message_sync(query)
    print(f"Response tone: {response.emotional_state}")
    print(f"First 150 chars: {response.content[:150]}...")