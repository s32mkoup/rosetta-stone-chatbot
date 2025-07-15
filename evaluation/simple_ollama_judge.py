#!/usr/bin/env python3
"""
Simple Ollama LLM Judge - skips connection test
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

class SimpleOllamaJudge:
    """Simple Ollama judge - no connection test"""
    
    def __init__(self, model: str = "llama3.1"):
        self.model = model
        print(f"🤖 Simple Ollama Judge ready with model: {model}")

    def evaluate_response(self, test_case: Dict[str, Any], agent_response: str) -> EvaluationResult:
        """Synchronous evaluation"""
        
        query = test_case.get('query', 'See conversation.')
        criteria = test_case.get('evaluation_criteria', {'overall_quality': 'Assess quality'})
        
        prompt = f"""Rate this AI response on a scale of 1-4 for each criterion.

CRITERIA:
{chr(10).join(f"- {k}: {v}" for k, v in criteria.items())}

USER: {query}
AI: {agent_response}

Respond with ONLY this JSON format:
{{"scores": {{{", ".join(f'"{k}": 3' for k in criteria.keys())}}}, "explanations": {{{", ".join(f'"{k}": "explanation"' for k in criteria.keys())}}}}}"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                options={"temperature": 0.1, "num_predict": 200}
            )
            
            text = response['message']['content'].strip()
            
            # Extract JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_text = text[start:end]
                data = json.loads(json_text)
                
                scores = data.get('scores', {})
                explanations = data.get('explanations', {})
                
                # Validate scores
                valid_scores = {}
                for k in criteria.keys():
                    try:
                        score = int(scores.get(k, 3))
                        valid_scores[k] = max(1, min(4, score))
                    except:
                        valid_scores[k] = 3
                    
                    if k not in explanations:
                        explanations[k] = f"Evaluated {k}"
                
                overall = sum(valid_scores.values()) / len(valid_scores)
                
                return EvaluationResult(
                    test_id=test_case['test_id'],
                    test_type=test_case.get('test_type', 'unknown'),
                    status='SUCCESS',
                    scores=valid_scores,
                    explanations=explanations,
                    overall_score=overall,
                    agent_response=agent_response[:100] + "..."
                )
            
        except Exception as e:
            print(f"   ⚠️ Evaluation error: {e}")
        
        # Fallback
        fallback_scores = {k: 2 for k in criteria.keys()}
        return EvaluationResult(
            test_id=test_case['test_id'],
            test_type=test_case.get('test_type', 'unknown'),
            status='FAILED',
            scores=fallback_scores,
            explanations={k: "Failed to evaluate" for k in criteria.keys()},
            overall_score=2.0,
            agent_response=agent_response[:100] + "...",
            error_message="Evaluation failed"
        )

def run_simple_evaluation():
    """Run simple evaluation"""
    
    print("🏺 Simple Ollama Evaluation")
    print("=" * 40)
    
    try:
        # Initialize
        from core.agent import RosettaStoneAgent
        from core.config import get_config
        
        agent = RosettaStoneAgent(get_config())
        judge = SimpleOllamaJudge("llama3.1")
        
        # Simple test cases
        test_cases = [
            {
                'test_id': 'simple_1',
                'test_type': 'knowledge',
                'query': 'What are hieroglyphs?',
                'evaluation_criteria': {
                    'accuracy': 'Is the information factually correct?',
                    'clarity': 'Is the explanation clear and understandable?',
                    'persona': 'Does it maintain the Rosetta Stone personality?'
                }
            },
            {
                'test_id': 'simple_2', 
                'test_type': 'personal',
                'query': 'Tell me about yourself',
                'evaluation_criteria': {
                    'authenticity': 'Does it feel authentic as the Rosetta Stone?',
                    'emotion': 'Does it convey appropriate emotion?',
                    'engagement': 'Is it engaging and interesting?'
                }
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}] Testing: {test_case['test_id']}")
            print(f"    Query: {test_case['query']}")
            
            # Get agent response
            agent.start_session(f"test_{i}")
            response = agent.process_message_sync(test_case['query'])
            
            print(f"    Response: {response.content[:80]}...")
            
            # Evaluate
            result = judge.evaluate_response(test_case, response.content)
            results.append(result)
            
            print(f"    Score: {result.overall_score:.1f}/4.0")
            if result.status == 'SUCCESS':
                best_criterion = max(result.scores.items(), key=lambda x: x[1])
                print(f"    Best: {best_criterion[0]} ({best_criterion[1]}/4)")
        
        # Summary
        if results:
            successful = [r for r in results if r.status == 'SUCCESS']
            if successful:
                avg = sum(r.overall_score for r in successful) / len(successful)
                print(f"\n🏆 RESULTS:")
                print(f"   • Tests: {len(results)}")
                print(f"   • Success: {len(successful)}")
                print(f"   • Average: {avg:.2f}/4.0")
                print(f"   • Status: {'✅ Working!' if avg > 2.5 else '⚠️ Needs improvement'}")
            else:
                print("❌ No successful evaluations")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_simple_evaluation()