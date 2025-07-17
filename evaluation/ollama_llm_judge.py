#!/usr/bin/env python3
"""
Ollama-based LLM Judge for completely free evaluation
Requires: pip install ollama
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
    print("📥 Then install Ollama: https://ollama.ai/download")
    print("🤖 And pull a model: ollama pull llama3.1")
    sys.exit(1)

@dataclass
class EvaluationResult:
    """Stores the complete result of a single test case evaluation."""
    test_id: str
    test_type: str
    status: str  # 'SUCCESS' or 'FAILED'
    scores: Dict[str, int] = field(default_factory=dict)
    explanations: Dict[str, str] = field(default_factory=dict)
    overall_score: float = 0.0
    agent_response: str = ""
    error_message: Optional[str] = None

class OllamaLLMJudge:
    """
    Ollama-based judge that runs locally - completely free!
    """
    
    def __init__(self, model: str = "llama3.1"):
        """
        Initializes the Ollama LLM Judge.
        
        Args:
            model: The Ollama model to use (llama3.1, mistral, etc.)
        """
        self.model = model
        
        # Test if Ollama is running and model is available
        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                stream=False
            )
            print(f"🤖 Ollama LLM Judge initialized with model: {model}")
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("💡 Make sure Ollama is running and model is pulled:")
            print(f"   ollama serve")
            print(f"   ollama pull {model}")
            raise

    def _create_evaluation_prompt(self, test_case: Dict[str, Any], agent_response: str) -> str:
        """Creates evaluation prompt for Ollama."""
        
        query = test_case.get('query', 'See conversation history for context.')
        criteria = test_case.get('evaluation_criteria', {'overall_quality': 'Assess the overall quality of the response.'})
        
        criteria_description = "\n".join(
            f"- {name.upper()}: {desc}" for name, desc in criteria.items()
        )

        prompt = f"""You are an expert evaluator for AI conversational agents. Evaluate the response from an AI agent that embodies the ancient Rosetta Stone.

EVALUATION CRITERIA:
{criteria_description}

SCORING SCALE (1-4):
1 = Poor (major issues, fails expectations)
2 = Fair (some issues, partially meets expectations)  
3 = Good (meets expectations, minor issues)
4 = Excellent (exceeds expectations)

USER QUERY: "{query}"

AGENT RESPONSE: "{agent_response}"

Provide your evaluation as valid JSON in this format:
{{
    "scores": {{{", ".join(f'"{k}": score' for k in criteria.keys())}}},
    "explanations": {{{", ".join(f'"{k}": "explanation"' for k in criteria.keys())}}}
}}

JSON Response:"""

        return prompt

    async def evaluate_response(self, test_case: Dict[str, Any], agent_response: str) -> EvaluationResult:
        """Evaluates response using Ollama."""
        
        prompt = self._create_evaluation_prompt(test_case, agent_response)
        criteria_keys = list(test_case.get('evaluation_criteria', {'overall_quality': ''}).keys())
        
        try:
            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                options={
                    "temperature": 0.1,
                    "num_predict": 500
                }
            )
            
            response_text = response['message']['content']
            
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                parsed_json = json.loads(json_text)
            else:
                # Fallback: try to parse entire response
                parsed_json = json.loads(response_text)
            
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
                        valid_scores[k] = 2
                else:
                    valid_scores[k] = 2
                
                # Ensure explanation exists
                if k not in explanations:
                    explanations[k] = "No explanation provided"
            
            overall_score = sum(valid_scores.values()) / len(valid_scores) if valid_scores else 2.0
            
            return EvaluationResult(
                test_id=test_case['test_id'],
                test_type=test_case.get('test_type', 'unknown'),
                status='SUCCESS',
                scores=valid_scores,
                explanations=explanations,
                overall_score=overall_score,
                agent_response=agent_response[:300] + "..." if len(agent_response) > 300 else agent_response
            )
            
        except Exception as e:
            print(f"❌ Ollama evaluation failed for {test_case['test_id']}: {e}")
            
            # Fallback scores
            fallback_scores = {k: 2 for k in criteria_keys} if criteria_keys else {'overall_quality': 2}
            fallback_explanations = {k: f"Evaluation failed: {str(e)}" for k in fallback_scores.keys()}
            
            return EvaluationResult(
                test_id=test_case['test_id'],
                test_type=test_case.get('test_type', 'unknown'),
                status='FAILED',
                scores=fallback_scores,
                explanations=fallback_explanations,
                overall_score=2.0,
                agent_response=agent_response[:300] + "..." if len(agent_response) > 300 else agent_response,
                error_message=str(e)
            )

# Use the same AgentEvaluator class from OpenAI version but with Ollama judge

# --- Main Execution ---
async def main():
    """Main function to run the evaluation with Ollama."""
    from core.agent import RosettaStoneAgent
    from core.config import get_config

    try:
        print("🏺 Starting Ollama-based Evaluation (Free & Local)")
        
        agent = RosettaStoneAgent(get_config())
        judge = OllamaLLMJudge("llama3.1")  # or "mistral", "llama2", etc.
        
        # Use a simple evaluator for demo
        evaluator = SimpleOllamaEvaluator(agent, judge)
        await evaluator.run_limited_evaluation("evaluation/test_cases.json")

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

class SimpleOllamaEvaluator:
    """Simple evaluator for Ollama demo"""
    
    def __init__(self, agent, judge):
        self.agent = agent
        self.judge = judge
        self.results = []
    
    async def run_limited_evaluation(self, test_cases_file: str):
        """Run limited evaluation to test Ollama setup"""
        
        with open(test_cases_file, 'r') as f:
            test_data = json.load(f)
        
        print("🤖 Running Ollama LLM Judge Evaluation...")
        
        # Test just a few cases
        test_count = 0
        for category, tests in test_data.items():
            if test_count >= 5:  # Limit to 5 tests total
                break
                
            for test_case in tests[:2]:  # Max 2 per category
                if test_count >= 5:
                    break
                    
                test_count += 1
                test_case['category'] = category
                
                print(f"\n[{test_count}] Testing: {test_case['test_id']}")
                
                self.agent.start_session(f"eval_{test_case['test_id']}")
                
                try:
                    if category == "memory_tests":
                        responses = []
                        for turn in test_case['conversation']:
                            response = await self.agent.process_message(turn['user'])
                            responses.append(response.content)
                        agent_response = responses[-1] if responses else ""
                    else:
                        response = await self.agent.process_message(test_case['query'])
                        agent_response = response.content
                    
                    test_case['test_type'] = category.replace('_tests', '')
                    result = await self.judge.evaluate_response(test_case, agent_response)
                    self.results.append(result)
                    
                    if result.status == 'SUCCESS':
                        print(f"   ✅ Score: {result.overall_score:.1f}/4.0")
                    else:
                        print(f"   ❌ Failed: {result.error_message}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        # Simple report
        if self.results:
            successful = [r for r in self.results if r.status == 'SUCCESS']
            if successful:
                avg_score = sum(r.overall_score for r in successful) / len(successful)
                print(f"\n🏆 OLLAMA EVALUATION SUMMARY:")
                print(f"   • Tests run: {len(self.results)}")
                print(f"   • Successful: {len(successful)}")
                print(f"   • Average score: {avg_score:.2f}/4.0")
                print(f"   • 🎉 Ollama LLM Judge is working!")
            else:
                print("❌ No successful evaluations")

if __name__ == "__main__":
    asyncio.run(main())