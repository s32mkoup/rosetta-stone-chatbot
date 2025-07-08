from core.config import get_config, PersonaDepth
from core.agent import RosettaStoneAgent

# Test different persona depths
configs = []

# BASIC persona
config_basic = get_config()
config_basic.persona.persona_depth = PersonaDepth.BASIC
config_basic.persona.poetic_language = False
config_basic.persona.ancient_wisdom_style = False

# RICH persona  
config_rich = get_config()
config_rich.persona.persona_depth = PersonaDepth.RICH
config_rich.persona.sensory_descriptions = True
config_rich.persona.metaphor_frequency = "high"

agents = {
    "BASIC": RosettaStoneAgent(config_basic),
    "STANDARD": RosettaStoneAgent(get_config()),
    "RICH": RosettaStoneAgent(config_rich)
}

query = "What are hieroglyphs?"

for persona_type, agent in agents.items():
    print(f"\n=== {persona_type} PERSONA ===")
    response = agent.process_message_sync(query)
    print(f"Length: {len(response.content)} chars")
    print(f"Response: {response.content[:200]}...")