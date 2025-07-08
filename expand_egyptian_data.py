# Let's see what specific data you have and expand it
from tools.egyptian_tool import EgyptianKnowledgeTool
from core.config import get_config

tool = EgyptianKnowledgeTool(get_config())

print("=== CURRENT PHARAOHS ===")
for pharaoh in tool.knowledge_base.get('pharaohs', []):
    print(f"- {pharaoh.get('title', 'Unknown')}: {pharaoh.get('description', '')[:100]}...")

print("\n=== CURRENT DYNASTIES ===")
for dynasty in tool.knowledge_base.get('dynasties', []):
    print(f"- {dynasty.get('title', 'Unknown')}: {dynasty.get('description', '')[:100]}...")

print("\n=== CURRENT HIEROGLYPHS ===")
from tools.translation_tool import TranslationTool
trans_tool = TranslationTool(get_config())

for symbol, info in list(trans_tool.hieroglyph_dictionary.items())[:5]:
    print(f"- {symbol}: {info.get('transliteration', '?')} = {info.get('meaning', '?')}")

print("\n=== TIMELINE COVERAGE ===")
from tools.historical_tool import HistoricalTimelineTool
hist_tool = HistoricalTimelineTool(get_config())

print("Historical events by era:")
bce_events = [e for e in hist_tool.historical_events if e.era == 'BCE']
ce_events = [e for e in hist_tool.historical_events if e.era == 'CE']
print(f"BCE events: {len(bce_events)}")
print(f"CE events: {len(ce_events)}")

# Show timeline gaps
years = [e.year for e in bce_events]
if years:
    print(f"BCE timeline: {min(years)} to {max(years)} BCE")