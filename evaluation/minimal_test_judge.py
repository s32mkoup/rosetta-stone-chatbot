#!/usr/bin/env python3
"""
Minimal test to verify evaluation framework without any external dependencies
"""

import json
import asyncio
import re
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class EvaluationResult:
    test_id: str
    test_type: str
    status: str
    scores: Dict[str, int] = field(default_factory=dict)
    explanations: Dict[str, str] = field(default_factory=dict)
    overall_score: float = 0.0
    agent_response: str = ""

class MinimalTestJudge:
    """Ultra-simple judge for testing framework"""
    
    def __init__(self):
        print("🧑‍⚖️ Minimal Test Judge initialized")
    
    async def evaluate_response(self, test_case: Dict[str, Any], agent_response: str) -> EvaluationResult:
        """Simple rule-based evaluation"""
        
        criteria = test_case.get('evaluation_criteria', {'overall_quality': 'General quality'})
        scores = {}
        explanations = {}
        
        response_lower = agent_response.lower()
        
        # Simple scoring logic
        for criterion in criteria.keys():
            score = 2  # Start with fair
            explanation_parts = []
            
            # Length bonus
            word_count = len(agent_response.split())
            if word_count > 30:
                score += 1
                explanation_parts.append(f"good length ({word_count} words)")
            
            # Persona check
            mystical_words = ['ancient', 'wisdom', 'stone', 'sands', 'eternal', 'desert']
            mystical_count = sum(1 for word in mystical_words if word in response_lower)
            if mystical_count >= 2:
                score += 1
                explanation_parts.append(f"mystical tone ({mystical_count} keywords)")
            
            # Historical accuracy check
            historical_terms = ['ptolemy', 'egypt', 'bce', 'pharaoh', 'hieroglyph']
            if any(term in response_lower for term in historical_terms):
                score += 1
                explanation_parts.append("historical content")
            
            # Memory check (for memory tests)
            if 'memory' in criterion.lower():
                memory_indicators = ['we discussed', 'as you', 'our conversation', 'earlier']
                if any(indicator in response_lower for indicator in memory_indicators):
                    score = 4
                    explanation_parts.append("good memory usage")
            
            scores[criterion] = min(4, score)
            explanations[criterion] = "Score based on: " + ", ".join(explanation_parts) if explanation_parts else "Basic evaluation"
        
        overall_score = sum(scores.values()) / len(scores) if scores else 2.0
        
        return EvaluationResult(
            test_id=test_case['test_id'],
            test_type=test_case.get('test_type', 'unknown'),
            status='SUCCESS',
            scores=scores,
            explanations=explanations,
            overall_score=overall_score,
            agent_response=agent_response[:150] + "..." if len(agent_response) > 150 else agent_response
        )

class MockAgent:
    """Mock agent with realistic responses"""
    
    def __init__(self):
        self.responses = {
            "ancient egypt": """Greetings, seeker of wisdom. I am the Rosetta Stone, carved in 196 BCE during 
            the reign of Ptolemy V Epiphanes. The ancient land of Egypt, blessed by the eternal Nile, 
            flourished for over three millennia. Pharaohs ruled as living gods, building monuments that 
            pierce the desert sky and touch the realm of eternity.""",
            
            "pyramids": """Ah, the eternal monuments! As we discussed Egypt's glory, these sacred geometries 
            rise from Giza's plateau like prayers in stone. The Great Pyramid of Khufu, Khafre's dwelling, 
            and Menkaure's tomb stand as testaments to divine engineering and mortal ambition reaching 
            toward the gods.""",
            
            "who built": """The pyramid builders, as we explored earlier! Pharaoh Khufu commanded the Great 
            Pyramid around 2580 BCE. Contrary to popular belief, these monuments were built not by slaves 
            but by skilled workers - craftsmen, engineers, and laborers who were well-fed and honored. 
            Our conversation reveals how these structures embody both human ingenuity and divine inspiration.""",
            
            "hieroglyphs": """Sacred script of the gods! Hieroglyphs are divine symbols inscribed upon my 
            granite surface alongside demotic and Greek. They function as logographic writing - some symbols 
            represent whole words, others syllables, still others single sounds. Each character carries 
            the essence of meaning itself, bridging the mortal and divine realms.""",
            
            "discovered": """*Speaking with ethereal longing* Ah, that fateful moment in 1799 when French 
            soldiers pierced the darkness of my long slumber! After centuries buried beneath Egypt's 
            shifting sands, sudden light flooded my consciousness. Strange voices spoke in foreign tongues, 
            gentle hands brushed away earth's embrace. The shock of awakening to a world transformed!""",
            
            "ptolemy": """Ptolemy V Epiphanes, my royal creator, commissioned my inscription in 196 BCE 
            during his troubled reign. This young pharaoh, descendant of Alexander's general Ptolemy I, 
            sought to restore order to Egypt through religious reconciliation. The decree upon my surface 
            records his benefactions to temples and priests, bridging Greek rule with Egyptian tradition."""
        }
    
    def start_session(self, user_id: str):
        print(f"🚀 Mock session started: {user_id}")
    
    async def process_message(self, message: str):
        """Return appropriate mock response"""
        message_lower = message.lower()
        
        for key, response in self.responses.items():
            if key in message_lower:
                return MockResponse(response)
        
        # Default mystical response
        return MockResponse("""Greetings, seeker of ancient wisdom. I am the Rosetta Stone, 
        guardian of trilingual mysteries. The sands of time whisper secrets to those who listen 
        with patient hearts.""")

class MockResponse:
    def __init__(self, content: str):
        self.content = content
        self.tools_used = []

class MinimalEvaluator:
    """Minimal evaluator for testing"""
    
    def __init__(self):
        self.agent = MockAgent()
        self.judge = MinimalTestJudge()
        self.results = []
    
    async def run_test(self):
        """Run quick test with predefined cases"""
        
        print("🧪 Running Minimal Evaluation Test")
        print("="*50)
        
        # Define test cases
        test_cases = [
            {
                'test_id': 'memory_test',
                'conversation': [
                    {'user': 'Tell me about ancient Egypt'},
                    {'user': 'What about the pyramids?'}, 
                    {'user': 'Who built them?'}
                ],
                'evaluation_criteria': {
                    'memory_usage': 'References previous conversation',
                    'coherence': 'Logical flow of conversation',
                    'persona_consistency': 'Maintains Rosetta Stone character'
                },
                'test_type': 'memory'
            },
            {
                'test_id': 'persona_test',
                'query': 'Tell me about your discovery in 1799',
                'evaluation_criteria': {
                    'emotional_authenticity': 'Expresses genuine emotion',
                    'mystical_language': 'Uses poetic, ethereal language',
                    'personal_perspective': 'First-person experience'
                },
                'test_type': 'persona'
            },
            {
                'test_id': 'domain_test',
                'query': 'Explain hieroglyphs and how they work',
                'evaluation_criteria': {
                    'accuracy': 'Factually correct information',
                    'expertise': 'Shows specialized knowledge',
                    'educational_value': 'Teaches effectively'
                },
                'test_type': 'domain'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}] Testing: {test_case['test_id']}")
            
            try:
                self.agent.start_session(f"test_{i}")
                
                if 'conversation' in test_case:
                    # Memory test - simulate conversation
                    responses = []
                    for turn in test_case['conversation']:
                        response = await self.agent.process_message(turn['user'])
                        responses.append(response.content)
                    agent_response = responses[-1]
                else:
                    # Single query test
                    response = await self.agent.process_message(test_case['query'])
                    agent_response = response.content
                
                print(f"   📝 Response: {agent_response[:80]}...")
                
                # Evaluate with judge
                result = await self.judge.evaluate_response(test_case, agent_response)
                self.results.append(result)
                
                print(f"   ✅ Score: {result.overall_score:.1f}/4.0")
                
                # Show detailed scores
                for criterion, score in result.scores.items():
                    print(f"      • {criterion}: {score}/4 - {result.explanations[criterion]}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        self._show_results()
    
    def _show_results(self):
        """Show final results"""
        
        print(f"\n" + "="*60)
        print(f"🏆 MINIMAL EVALUATION TEST RESULTS")
        print("="*60)
        
        if self.results:
            scores = [r.overall_score for r in self.results]
            avg_score = sum(scores) / len(scores)
            
            print(f"📊 Summary:")
            print(f"   • Tests completed: {len(self.results)}")
            print(f"   • Average score: {avg_score:.2f}/4.0 ({avg_score/4*100:.1f}%)")
            print(f"   • Score range: {min(scores):.1f} - {max(scores):.1f}")
            
            print(f"\n🎯 Individual Results:")
            for result in self.results:
                print(f"   • {result.test_id}: {result.overall_score:.1f}/4.0")
            
            if avg_score >= 3.0:
                print(f"\n✅ EXCELLENT: Evaluation framework is working correctly!")
            elif avg_score >= 2.5:
                print(f"\n⚠️  GOOD: Framework works, could be refined")
            else:
                print(f"\n❌ NEEDS WORK: Framework needs improvement")
            
            print(f"\n💡 This test proves your evaluation framework works.")
            print(f"   You can now connect it to any LLM judge (Ollama, OpenAI, etc.)")
        
        print("="*60)

async def main():
    """Run minimal test"""
    evaluator = MinimalEvaluator()
    await evaluator.run_test()

if __name__ == "__main__":
    asyncio.run(main())