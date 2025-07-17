import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import RosettaStoneAgent
from core.config import get_config

agent = RosettaStoneAgent(get_config())
agent.start_session("test_user")

print("Testing persona commands:")
print("\n1. Help command:")
resp = agent.process_message_sync("/help")
print(resp.content)

print("\n2. Persona status:")
resp = agent.process_message_sync("/persona")
print(resp.content)

print("\n3. Switch to academic:")
resp = agent.process_message_sync("/persona academic")
print(resp.content)