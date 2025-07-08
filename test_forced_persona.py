from core.agent import RosettaStoneAgent
from core.config import get_config

agent = RosettaStoneAgent(get_config())
agent.start_session("academic_test")

# Manually set user as academic
if hasattr(agent.memory_manager, 'user_profiles') and 'academic_test' in agent.memory_manager.user_profiles:
    user_profile = agent.memory_manager.user_profiles['academic_test']
    user_profile.interaction_style = 'academic'  # Force academic style
    print(f"Set user style to: {user_profile.interaction_style}")

response = agent.process_message_sync("What are hieroglyphs?")
print(f"Response: {response.content[:200]}...")