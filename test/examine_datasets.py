from tools.egyptian_tool import EgyptianKnowledgeTool
from tools.historical_tool import HistoricalTimelineTool
from tools.translation_tool import TranslationTool
from core.config import get_config

config = get_config()

# Initialize tools to examine their datasets
egyptian_tool = EgyptianKnowledgeTool(config)
historical_tool = HistoricalTimelineTool(config)
translation_tool = TranslationTool(config)

print("🏺 EGYPTIAN KNOWLEDGE DATASET:")
print(f"Pharaohs: {len(egyptian_tool.knowledge_base.get('pharaohs', []))} entries")
print(f"Dynasties: {len(egyptian_tool.knowledge_base.get('dynasties', []))} entries")
print(f"Culture: {len(egyptian_tool.knowledge_base.get('culture', []))} entries")
print(f"Personal memories: {len(egyptian_tool.personal_memories)} categories")

print(f"\n🕐 HISTORICAL TIMELINE DATASET:")
print(f"Historical events: {len(historical_tool.historical_events)} events")
print(f"Historical periods: {len(historical_tool.historical_periods)} periods")
print(f"Civilizations tracked: {len(historical_tool.civilizations_timeline)}")

print(f"\n📜 TRANSLATION DATASETS:")
print(f"Hieroglyph dictionary: {len(translation_tool.hieroglyph_dictionary)} symbols")
print(f"Greek vocabulary: {len(translation_tool.greek_vocabulary)} words")
print(f"Rosetta Stone texts: {len(translation_tool.rosetta_stone_text)} fragments")

# Show sample data
print(f"\n📋 SAMPLE DATA:")
if egyptian_tool.knowledge_base.get('pharaohs'):
    pharaoh = egyptian_tool.knowledge_base['pharaohs'][0]
    print(f"Sample pharaoh: {pharaoh.get('title', 'Unknown')}")

if historical_tool.historical_events:
    event = historical_tool.historical_events[0]
    print(f"Sample event: {event.year} {event.era} - {event.title}")

print(f"\nSample hieroglyph: {list(translation_tool.hieroglyph_dictionary.keys())[0] if translation_tool.hieroglyph_dictionary else 'None'}")