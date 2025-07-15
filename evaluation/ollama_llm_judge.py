#!/usr/bin/env python3
"""Debug Ollama LLM Judge with extensive logging"""

import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import ollama
    print("✅ Ollama imported successfully")
except ImportError:
    print("❌ Ollama import failed")
    sys.exit(1)

class DebugOllamaJudge:
    def __init__(self, model="llama3.1"):
        self.model = model
        print(f"🤖 Judge initialized with model: {model}")

    def evaluate(self, test_case, agent_response):
        print(f"\n🔍 EVALUATING: {test_case['test_id']}")
        
        # Handle conversation vs single query
        if 'conversation' in test_case:
            query_text = f"Conversation: {len(test_case['conversation'])} turns"
            conversation_text = " → ".join([turn['user'] for turn in test_case['conversation']])
            query_context = f"Multi-turn conversation: {conversation_text}"
        else:
            query_text = test_case['query'][:50] + "..."
            query_context = f"Single query: {test_case['query']}"
        
        print(f"📝 Query: {query_text}")
        print(f"📝 Response length: {len(agent_response)} chars")
        
        criteria = test_case.get('evaluation_criteria', {'quality': 'Rate quality'})
        print(f"📊 Criteria: {list(criteria.keys())}")
        
        prompt = f"""You are evaluating an AI that embodies the ancient Rosetta Stone. Rate 1-4 (4=Excellent, 3=Good, 2=Fair, 1=Poor).

The AI should be mystical, wise, knowledgeable about ancient Egypt, and maintain personality as the actual Rosetta Stone artifact.

CRITERIA:
{chr(10).join(f"- {k}: {v}" for k, v in criteria.items())}

CONTEXT: {query_context}

AI RESPONSE: {agent_response[:300]}...

Consider: The response shows mystical personality, ancient wisdom, historical accuracy, and maintains character as the Rosetta Stone.

Respond ONLY with JSON:
{{"scores": {{{", ".join(f'"{k}": 3' for k in criteria.keys())}}}, "explanations": {{{", ".join(f'"{k}": "brief reason"' for k in criteria.keys())}}}}}"""

        print(f"🚀 Sending to Ollama...")
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                options={"temperature": 0.1, "num_predict": 300}
            )
            print(f"✅ Ollama responded")
            
            text = response['message']['content'].strip()
            print(f"📤 Raw response: {text[:100]}...")
            
            # Extract JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_text = text[start:end]
                print(f"🔍 JSON extracted: {json_text[:80]}...")
                
                # Clean JSON
                json_text = json_text.replace('\n', ' ').replace('  ', ' ')
                if json_text.count('"') % 2 != 0:  # Fix unclosed quotes
                    json_text += '"'
                
                try:
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON parse error, trying to fix: {e}")
                    # Try to fix common issues
                    json_text = json_text.replace('...', '')  # Remove truncation
                    data = json.loads(json_text)
                scores = data.get('scores', {})
                
                # Validate
                valid_scores = {}
                for k in criteria.keys():
                    score = int(scores.get(k, 3))
                    valid_scores[k] = max(1, min(4, score))
                
                avg = sum(valid_scores.values()) / len(valid_scores)
                print(f"📊 Scores: {valid_scores}")
                print(f"📈 Average: {avg:.1f}/4.0")
                
                return {
                    'test_id': test_case['test_id'],
                    'scores': valid_scores,
                    'overall': avg,
                    'status': 'SUCCESS'
                }
            else:
                print("❌ No JSON found in response")
                
        except Exception as e:
            print(f"❌ Ollama error: {e}")
        
        # Fallback
        fallback = {k: 2 for k in criteria.keys()}
        return {
            'test_id': test_case['test_id'],
            'scores': fallback,
            'overall': 2.0,
            'status': 'FAILED'
        }

def run_full_evaluation():
    print("🏺 FULL OLLAMA EVALUATION")
    print("=" * 50)
    
    try:
        from core.agent import RosettaStoneAgent
        from core.config import get_config
        
        agent = RosettaStoneAgent(get_config())
        judge = DebugOllamaJudge()
        
        # Load test cases
        try:
            with open('evaluation/test_cases.json', 'r') as f:
                test_data = json.load(f)
            print(f"📋 Loaded test cases: {len(test_data)} categories")
        except FileNotFoundError:
            print("❌ test_cases.json not found, using simple tests")
            test_data = {
                "simple_tests": [
                    {
                        "test_id": "simple_1",
                        "query": "What are hieroglyphs?",
                        "evaluation_criteria": {
                            "accuracy": "Factual correctness about hieroglyphs",
                            "persona": "Maintains Rosetta Stone personality"
                        }
                    }
                ]
            }
        
        results = []
        test_count = 0
        
        for category, tests in test_data.items():
            if test_count >= 5:  # Limit tests
                break
                
            print(f"\n📂 CATEGORY: {category}")
            
            for test_case in tests[:2]:  # Max 2 per category
                if test_count >= 5:
                    break
                    
                test_count += 1
                test_case['test_type'] = category.replace('_tests', '')
                
                print(f"\n[{test_count}] {test_case['test_id']}")
                
                agent.start_session(f"eval_{test_count}")
                
                # Handle conversation vs single query
                if 'conversation' in test_case:
                    print("🗣️ Multi-turn conversation")
                    responses = []
                    for turn in test_case['conversation']:
                        resp = agent.process_message_sync(turn['user'])
                        responses.append(resp.content)
                    agent_response = responses[-1]  # Use last response
                else:
                    print("💬 Single query")
                    resp = agent.process_message_sync(test_case['query'])
                    agent_response = resp.content
                
                result = judge.evaluate(test_case, agent_response)
                results.append(result)
        
        # Summary
        print(f"\n🏆 EVALUATION SUMMARY")
        print("=" * 30)
        
        successful = [r for r in results if r['status'] == 'SUCCESS']
        print(f"✅ Successful: {len(successful)}/{len(results)}")
        
        if successful:
            avg_score = sum(r['overall'] for r in successful) / len(successful)
            print(f"📊 Average Score: {avg_score:.2f}/4.0 ({avg_score/4*100:.1f}%)")
            
            best = max(successful, key=lambda x: x['overall'])
            worst = min(successful, key=lambda x: x['overall'])
            print(f"🥇 Best: {best['test_id']} ({best['overall']:.1f})")
            print(f"📉 Lowest: {worst['test_id']} ({worst['overall']:.1f})")
        
        # Save results
        with open('ollama_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total': len(results),
                    'successful': len(successful),
                    'average_score': avg_score if successful else 0
                }
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: ollama_results.json")
        
    except Exception as e:
        print(f"💥 ERROR: {e}")
        import traceback
        traceback.print_exc()

def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        run_full_evaluation()
    else:
        # Single test for debugging
        print("🏺 DEBUG OLLAMA JUDGE")
        print("=" * 40)
        
        try:
            from core.agent import RosettaStoneAgent
            from core.config import get_config
            print("✅ Imports successful")
            
            agent = RosettaStoneAgent(get_config())
            judge = DebugOllamaJudge()
            print("✅ Components initialized")
            
            # Single test
            test_case = {
                'test_id': 'debug_test',
                'query': 'What are hieroglyphs?',
                'evaluation_criteria': {
                    'accuracy': 'Factual correctness about hieroglyphs',
                    'persona': 'Maintains mystical Rosetta Stone personality',
                    'engagement': 'Response is engaging and interesting'
                }
            }
            
            print(f"\n🎯 RUNNING TEST")
            agent.start_session("debug_session")
            print("✅ Session started")
            
            response = agent.process_message_sync(test_case['query'])
            print(f"✅ Agent responded: {len(response.content)} chars")
            print(f"📝 Preview: {response.content[:100]}...")
            
            result = judge.evaluate(test_case, response.content)
            
            print(f"\n🏆 FINAL RESULT:")
            print(f"   Status: {result['status']}")
            print(f"   Overall: {result['overall']}/4.0")
            print(f"   Scores: {result['scores']}")
            
            print(f"\n💡 To run full evaluation: python3 {sys.argv[0]} full")
            
        except Exception as e:
            print(f"💥 ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()