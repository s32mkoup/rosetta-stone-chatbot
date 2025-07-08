from core.agent import RosettaStoneAgent
from core.config import get_config

agent = RosettaStoneAgent(get_config())

# Start fresh session to ensure clean user profile
agent.start_session("test_user_academic")

# Test queries that should trigger different personas
test_scenarios = [
    {
        "setup": "Set academic user profile",
        "query": "What are hieroglyphs?",
        "expected_persona": "WISE_SCHOLAR"
    },
    {
        "setup": "Continue as academic user", 
        "query": "Can you explain the translation process?",
        "expected_persona": "WISE_SCHOLAR"
    }
]

print("=== TESTING PERSONA VARIANTS ===\n")

for i, scenario in enumerate(test_scenarios):
    print(f"TEST {i+1}: {scenario['setup']}")
    print(f"Query: {scenario['query']}")
    print(f"Expected: {scenario['expected_persona']}")
    
    response = agent.process_message_sync(scenario['query'])
    
    print(f"Response (first 200 chars):")
    print(f"{response.content[:200]}...")
    print(f"Full length: {len(response.content)} characters")
    print("-" * 60)