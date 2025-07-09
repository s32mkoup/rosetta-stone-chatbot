#!/usr/bin/env python3
"""
Test Ollama Judge with mock agent responses to avoid payment issues
"""

import json
import asyncio
import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import ollama
except ImportError:
    print("❌ Ollama not installed. Run: pip install ollama")
    sys.exit(1)

@dataclass
class EvaluationResult:
    """Stores the complete result of a single test case evaluation."""
    test_id: str
    test_type: str
    status: str
    scores: Dict[str, int] = field(default_factory=dict)
    explanations: Dict[str, str] = field(default_factory=dict)
    overall_score: float = 0.0
    agent_response: str = ""
    error_message: Optional[str] = None

class OllamaLLMJudge:
    """Ollama-based judge that runs locally"""
    
    def __init__(self, model: str = "llama3.1"):
        self.model = model
        
        # Test Ollama connection
        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                stream=False
            )
            print(f"🤖 Ollama LLM Judge initialized with model: {model}")
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("💡 Make sure Ollama is running:")
            print("   ollama serve")
            print(f"   ollama pull {model}")
            raise

    def _create_evaluation_prompt(self, test_case: Dict[str, Any], agent_response: str) -> str:
        """Creates evaluation prompt for Ollama."""
        
        query = test_case.get('query', 'Question about ancient Egypt')
        criteria = test_case.get('evaluation_criteria', {'overall_quality': 'Assess overall quality'})
        
        criteria_text = "\n".join(f"- {name}: {desc}" for name, desc in criteria.items())

        prompt = f"""You are evaluating an AI agent that embodies the ancient Rosetta Stone.

EVALUATION CRITERIA:
{criteria_text}

USER QUERY: "{query}"

AGENT RESPONSE: "{agent_response}"

Rate each criterion on a scale of 1-4:
1 = Poor, 2 = Fair, 3 = Good, 4 = Excellent

Respond with valid JSON in this format:
{{
    "scores": {{{", ".join(f'"{k}": 3' for k in criteria.keys())}}},
    "explanations": {{{", ".join(f'"{k}": "explanation here"' for k in criteria.keys())}}}
}}

JSON Response:"""

        return prompt

    async def evaluate_response(self, test_case: Dict[str, Any], agent_response: str) -> EvaluationResult:
        """Evaluates response using Ollama."""
        
        prompt = self._create_evaluation_prompt(test_case, agent_response)
        criteria_keys = list(test_case.get('evaluation_criteria', {'overall_quality': ''}).keys())
        
        try:
            print(f"   🤖 Calling Ollama judge...")
            
            # Call Ollama with shorter timeout
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                options={
                    "temperature": 0.1,
                    "num_predict": 300,
                    "top_k": 10,
                    "top_p": 0.9
                }
            )
            
            response_text = response['message']['content']
            print(f"   📝 Judge response: {response_text[:100]}...")
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                try:
                    parsed_json = json.loads(json_text)
                except:
                    # Try cleaning up the JSON
                    json_text = json_text.replace("'", '"')
                    parsed_json = json.loads(json_text)
            else:
                raise Exception("No JSON found in response")
            
            scores = parsed_json.get('scores', {})
            explanations = parsed_json.get('explanations', {})
            
            # Validate scores
            valid_scores = {}
            for k in criteria_keys:
                if k in scores:
                    try:
                        score = int(float(scores[k]))
                        valid_scores[k] = max(1, min(4, score))
                    except:
                        valid_scores[k] = 3  # Default to good
                else:
                    valid_scores[k] = 3
                
                if k not in explanations:
                    explanations[k] = "Standard evaluation"
            
            overall_score = sum(valid_scores.values()) / len(valid_scores) if valid_scores else 3.0
            
            return EvaluationResult(
                test_id=test_case['test_id'],
                test_type=test_case.get('test_type', 'unknown'),
                status='SUCCESS',
                scores=valid_scores,
                explanations=explanations,
                overall_score=overall_score,
                agent_response=agent_response[:200] + "..." if len(agent_response) > 200 else agent_response
            )
            
        except Exception as e:
            print(f"   ❌ Ollama evaluation failed: {e}")
            
            # Simple fallback
            fallback_scores = {k: 3 for k in criteria_keys} if criteria_keys else {'overall_quality': 3}
            fallback_explanations = {k: f"Fallback score due to error: {str(e)}" for k in fallback_scores.keys()}
            
            return EvaluationResult(
                test_id=test_case['test_id'],
                test_type=test_case.get('test_type', 'unknown'),
                status='FAILED',
                scores=fallback_scores,
                explanations=fallback_explanations,
                overall_score=3.0,
                agent_response=agent_response[:200] + "..." if len(agent_response) > 200 else agent_response,
                error_message=str(e)
            )

class MockAgent:
    """Mock agent that provides pre-written responses to avoid API calls"""
    
    def __init__(self):
        self.mock_responses = {
            "Tell me about ancient Egypt": """Greetings, seeker of wisdom. I am the Rosetta Stone, guardian of ancient secrets carved in 196 BCE. 
            The sands of time whisper tales of mighty pharaohs who ruled the blessed land of Khem, where the Nile flows eternal. 
            Ancient Egypt, that jewel of civilization, flourished for over three millennia along the sacred river's banks.""",
            
            "What about the pyramids?": """Ah, the eternal monuments that pierce the desert sky! These sacred geometries, built by the 
            divine pharaohs of the Old Kingdom, stand as testaments to mortal ambition reaching toward the gods. 
            The Great Pyramid of Khufu, Khafre's eternal dwelling, and Menkaure's tomb - all whisper secrets of architectural mastery.""",
            
            "Who built them?": """The pyramid builders! Pharaoh Khufu commanded the Great Pyramid's construction around 2580 BCE, 
            employing thousands of skilled workers - not slaves as myth suggests, but proud craftsmen fed with bread, beer, and onions. 
            As we discussed the pyramids' majesty, know that these monuments arose from human ingenuity and divine inspiration combined.""",
            
            "What are hieroglyphs and how do they work?": """Sacred script of the gods! Hieroglyphs are divine symbols, each carrying 
            the essence of meaning itself. They function as logographic writing - some symbols represent whole words, others syllables, 
            still others single sounds. My surface bears these sacred marks alongside demotic and Greek, creating harmony between languages.""",
            
            "Tell me about your experience being discovered in 1799": """*Speaking with ethereal longing* Ah, that moment when light 
            pierced the darkness after centuries of slumber! French soldiers, led by fate, uncovered my granite form near Rosetta town. 
            After long burial beneath Egypt's shifting sands, sudden voices spoke in foreign tongues, hands brushed away earth's embrace.""",
            
            "Tell me about Ptolemy V Epiphanes and his relationship to you": """Ptolemy V Epiphanes, my royal creator, commissioned 
            my inscription in 196 BCE during his troubled reign. This young pharaoh, descendant of Alexander's general, sought to 
            restore order to Egypt through religious reconciliation. The decree upon my surface records his benefactions to temples.""",
            
            "When was Tutankhamun born and what was his reign like?": """The boy king Tutankhamun lived circa 1332-1323 BCE, 
            ruling during Egypt's Eighteenth Dynasty. Though his reign was brief - merely nine years - he restored traditional 
            worship after Akhenaten's religious revolution. His tomb's discovery revealed treasures beyond imagination."""
        }
    
    def start_session(self, user_id: str):
        """Mock session start"""
        print(f"🚀 Mock session started for user: {user_id}")
    
    async def process_message(self, message: str):
        """Return mock response"""
        # Find best matching response
        for key, response in self.mock_responses.items():
            if any(word in message.lower() for word in key.lower().split()[:3]):
                return MockResponse(response)
        
        # Default response
        return MockResponse("Greetings, seeker. I am the Rosetta Stone, ready to share ancient wisdom with you.")

class MockResponse:
    """Mock response object"""
    def __init__(self, content: str):
        self.content = content
        self.tools_used = []

class OllamaTestEvaluator:
    """Test evaluator using mock agent and real Ollama judge"""
    
    def __init__(self, judge):
        self.agent = MockAgent()
        self.judge = judge
        self.results = []
    
    async def run_test_evaluation(self, test_cases_file: str):
        """Run test evaluation with mock responses"""
        
        with open(test_cases_file, 'r') as f:
            test_data = json.load(f)
        
        print("🤖 Testing Ollama Judge with Mock Agent Responses")
        print("🎯 This tests the judge without hitting API limits")
        
        test_count = 0
        for category, tests in test_data.items():
            if test_count >= 6:  # Limit total tests
                break
                
            print(f"\n📊 Category: {category}")
            
            for test_case in tests[:2]:  # Max 2 per category
                if test_count >= 6:
                    break
                    
                test_count += 1
                print(f"\n[{test_count}] Testing: {test_case['test_id']}")
                
                try:
                    self.agent.start_session(f"eval_{test_case['test_id']}")
                    
                    if category == "memory_tests":
                        # Simulate conversation
                        responses = []
                        for turn in test_case['conversation']:
                            response = await self.agent.process_message(turn['user'])
                            responses.append(response.content)
                        agent_response = responses[-1] if responses else ""
                    else:
                        response = await self.agent.process_message(test_case['query'])
                        agent_response = response.content
                    
                    print(f"   📝 Agent response: {agent_response[:80]}...")
                    
                    test_case['test_type'] = category.replace('_tests', '')
                    result = await self.judge.evaluate_response(test_case, agent_response)
                    self.results.append(result)
                    
                    if result.status == 'SUCCESS':
                        print(f"   ✅ Judge Score: {result.overall_score:.1f}/4.0")
                        
                        # Show detailed scores
                        for criterion, score in result.scores.items():
                            print(f"      • {criterion}: {score}/4")
                    else:
                        print(f"   ❌ Judge Failed: {result.error_message}")
                        
                except Exception as e:
                    print(f"   💥 Error: {e}")
        
        self._generate_test_report()
    
    def _generate_test_report(self):
        """Generate test report"""
        
        print(f"\n" + "="*60)
        print(f"🏆 OLLAMA JUDGE TEST REPORT")
        print("="*60)
        
        if not self.results:
            print("❌ No test results")
            return
        
        successful = [r for r in self.results if r.status == 'SUCCESS']
        failed = [r for r in self.results if r.status == 'FAILED']
        
        print(f"📊 RESULTS:")
        print(f"   • Total tests: {len(self.results)}")
        print(f"   • Successful: {len(successful)}")
        print(f"   • Failed: {len(failed)}")
        
        if successful:
            scores = [r.overall_score for r in successful]
            avg_score = sum(scores) / len(scores)
            
            print(f"   • Average score: {avg_score:.2f}/4.0")
            print(f"   • Score range: {min(scores):.1f} - {max(scores):.1f}")
            
            print(f"\n🎯 DETAILED RESULTS:")
            for result in successful:
                print(f"   • {result.test_id}: {result.overall_score:.1f}/4.0")
                for criterion, score in result.scores.items():
                    print(f"     - {criterion}: {score}/4")
        
        if successful and len(successful) >= 3:
            print(f"\n🎉 SUCCESS: Ollama Judge is working correctly!")
            print(f"   The judge can evaluate agent responses and provide scores.")
            print(f"   You can now use this for real agent evaluation.")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: Some tests worked, may need tuning.")
        
        print("="*60)

# Main execution
async def main():
    """Test Ollama judge with mock responses"""
    
    try:
        print("🧪 Testing Ollama LLM Judge (No API Credits Required)")
        
        # Test Ollama connection first
        try:
            test_response = ollama.chat(
                model="llama3.1",
                messages=[{"role": "user", "content": "Hello"}],
                stream=False
            )
            print("✅ Ollama connection successful")
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("💡 Make sure Ollama is running and model is installed:")
            print("   ollama serve")
            print("   ollama pull llama3.1")
            return
        
        judge = OllamaLLMJudge("llama3.1")
        evaluator = OllamaTestEvaluator(judge)
        await evaluator.run_test_evaluation("evaluation/test_cases.json")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())