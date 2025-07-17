from core.agent import RosettaStoneAgent
from core.config import get_config
from core.memory import UserProfile
from datetime import datetime

agent = RosettaStoneAgent(get_config())

# Create a proper academic user profile
academic_profile = UserProfile(
    user_id="academic_user",
    first_interaction=datetime.now(),
    last_interaction=datetime.now(),
    total_conversations=1,
    favorite_topics=["history", "linguistics"],
    interaction_style="academic",  # THIS IS KEY
    preferred_response_length="detailed",
    historical_interests={"ancient_egypt": 5}
)

# Manually inject the profile
agent.memory_manager.user_profiles["academic_user"] = academic_profile
agent.start_session("academic_user")

print("=== ACADEMIC USER TEST ===")
print(f"User profile style: {agent.memory_manager.user_profiles['academic_user'].interaction_style}")

response = agent.process_message_sync("What are hieroglyphs?")
print(f"Response: {response.content[:300]}...")

# Test casual user
casual_profile = UserProfile(
    user_id="casual_user",
    first_interaction=datetime.now(),
    last_interaction=datetime.now(),
    total_conversations=1,
    favorite_topics=["stories"],
    interaction_style="casual",  # THIS IS KEY
    preferred_response_length="brief",
    historical_interests={}
)

agent.memory_manager.user_profiles["casual_user"] = casual_profile
agent.start_session("casual_user")

print("\n=== CASUAL USER TEST ===")
print(f"User profile style: {agent.memory_manager.user_profiles['casual_user'].interaction_style}")

response = agent.process_message_sync("What are hieroglyphs?")
print(f"Response: {response.content[:300]}...")