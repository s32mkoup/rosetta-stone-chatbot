from core.config import get_config
from core.agent import RosettaStoneAgent

# Test 1: Current settings
config1 = get_config()
agent1 = RosettaStoneAgent(config1)

# Test 2: Modified settings
config2 = get_config()
config2.persona.poetic_language = False
config2.persona.sensory_descriptions = True
config2.persona.metaphor_frequency = "high"
agent2 = RosettaStoneAgent(config2)

print("=== AGENT 1 (Current) ===")
response1 = agent1.process_message_sync("Tell me about yourself")
print(response1.content[:200] + "...")

print("\n=== AGENT 2 (Modified) ===") 
response2 = agent2.process_message_sync("Tell me about yourself")
print(response2.content[:200] + "...")