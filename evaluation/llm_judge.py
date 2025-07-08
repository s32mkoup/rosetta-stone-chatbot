import json
import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
import sys
import os
import openai

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class EvaluationResult:
    test_id: str
    test_type: str
    scores: Dict[str, int]  # criteria -> score (1-10)
    explanations: Dict[str, str]
    overall_score: float
    agent_response: str
    baseline_response: str = None

class LLMJudge:
    def __init__(self, judge_model="gpt-4"):
        self.judge_model = judge_model
        # Initialize your LLM client here
        
    def create_evaluation_prompt(self, test_case: Dict, agent_response: str, 
                               baseline_response: str = None) -> str:
        """Create prompt for LLM judge"""
        
        prompt = f"""
You are an expert evaluator of AI conversational agents. Evaluate the following response from a specialized Rosetta Stone AI agent.

**TEST CONTEXT:**
- Test ID: {test_case['test_id']}
- Query: {test_case.get('query', 'See conversation below')}

**AGENT RESPONSE:**
{agent_response}

**EVALUATION CRITERIA:**
"""
        
        # Add specific criteria for this test
        criteria = test_case.get('evaluation_criteria', {})
        for criterion, description in criteria.items():
            prompt += f"\n{criterion.upper()}: {description}"
        
        prompt += f"""

**SCORING INSTRUCTIONS:**
Rate each criterion on a scale of 1-10 where:
- 1-2: Poor (major issues)
- 3-4: Below average (some issues)
- 5-6: Average (meets basic expectations)
- 7-8: Good (exceeds expectations)
- 9-10: Excellent (exceptional quality)

**REQUIRED OUTPUT FORMAT:**
{{
    "scores": {{
        "{list(criteria.keys())[0] if criteria else 'overall'}": X,
        "{list(criteria.keys())[1] if len(criteria) > 1 else 'accuracy'}": X
    }},
    "explanations": {{
        "{list(criteria.keys())[0] if criteria else 'overall'}": "explanation here",
        "{list(criteria.keys())[1] if len(criteria) > 1 else 'accuracy'}": "explanation here"
    }},
    "overall_score": X.X
}}

Respond with ONLY the JSON, no additional text.
"""
        return prompt
    
    async def evaluate_response(self, test_case: Dict, agent_response: str) -> EvaluationResult:
        """Evaluate a single agent response"""
        
        prompt = self.create_evaluation_prompt(test_case, agent_response)
        
        # TODO: Replace with your actual LLM call
        # judge_response = await self.call_llm(prompt)
        
        # Mock response for now - replace with actual LLM call
        mock_evaluation = {
            "scores": {"memory_usage": 8, "coherence": 7},
            "explanations": {
                "memory_usage": "Agent effectively references previous conversation",
                "coherence": "Response flows logically but could be more natural"
            },
            "overall_score": 7.5
        }
        
        return EvaluationResult(
            test_id=test_case['test_id'],
            test_type=test_case.get('test_type', 'unknown'),
            scores=mock_evaluation['scores'],
            explanations=mock_evaluation['explanations'],
            overall_score=mock_evaluation['overall_score'],
            agent_response=agent_response
        )

class AgentEvaluator:
    def __init__(self, agent, judge):
        self.agent = agent
        self.judge = judge
        self.results = []
    
    async def run_evaluation_suite(self, test_cases_file: str):
        """Run full evaluation suite"""
        
        with open(test_cases_file, 'r') as f:
            test_data = json.load(f)
        
        print("🏺 Starting Rosetta Stone Agent Evaluation...")
        
        # Evaluate each test category
        for category, tests in test_data.items():
            print(f"\n📊 Evaluating {category}...")
            
            for test_case in tests:
                if category == "memory_tests":
                    result = await self._evaluate_memory_test(test_case)
                elif category == "persona_tests":
                    result = await self._evaluate_persona_test(test_case)
                elif category == "domain_expertise_tests":
                    result = await self._evaluate_domain_test(test_case)
                elif category == "tool_usage_tests":
                    result = await self._evaluate_tool_test(test_case)
                
                self.results.append(result)
                print(f"✅ {test_case['test_id']}: {result.overall_score}/10")
        
        self._generate_report()
    
    async def _evaluate_memory_test(self, test_case: Dict) -> EvaluationResult:
        """Evaluate memory/conversation continuity"""
        
        # Start fresh session
        self.agent.start_session("eval_user")
        
        conversation_responses = []
        for turn in test_case['conversation']:
            response = await self.agent.process_message(turn['user'])

            conversation_responses.append(response.content)
        
        # Evaluate the final response (most complex one)
        final_response = conversation_responses[-1]
        test_case['test_type'] = 'memory'
        
        return await self.judge.evaluate_response(test_case, final_response)
    
    async def _evaluate_persona_test(self, test_case: Dict) -> EvaluationResult:
        """Evaluate persona consistency"""
        
        # Test with academic persona
        self.agent.start_session("eval_academic")
        await self.agent.process_message("/persona academic")
        academic_response = await self.agent.process_message(test_case['query'])
        
        test_case['test_type'] = 'persona'
        return await self.judge.evaluate_response(test_case, academic_response.content)
    
    async def _evaluate_domain_test(self, test_case: Dict) -> EvaluationResult:
        """Evaluate domain expertise"""
        
        self.agent.start_session("eval_domain")
        response = await self.agent.process_message(test_case['query'])
        
        test_case['test_type'] = 'domain'
        return await self.judge.evaluate_response(test_case, response.content)
    
    async def _evaluate_tool_test(self, test_case: Dict) -> EvaluationResult:
        """Evaluate tool usage"""
        
        self.agent.start_session("eval_tools")
        response = await self.agent.process_message(test_case['query'])
        
        test_case['test_type'] = 'tools'
        return await self.judge.evaluate_response(test_case, response.content)
    
    def _generate_report(self):
        """Generate evaluation report"""
        
        print(f"\n🏆 EVALUATION REPORT")
        print("=" * 50)
        
        by_category = {}
        for result in self.results:
            category = result.test_type
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result.overall_score)
        
        for category, scores in by_category.items():
            avg_score = sum(scores) / len(scores)
            print(f"{category.upper()}: {avg_score:.1f}/10 (n={len(scores)})")
        
        overall_avg = sum(r.overall_score for r in self.results) / len(self.results)
        print(f"\nOVERALL SCORE: {overall_avg:.1f}/10")

# Usage
async def main():
    from core.agent import RosettaStoneAgent
    from core.config import get_config
    
    # Initialize agent and judge
    agent = RosettaStoneAgent(get_config())
    judge = LLMJudge("gpt-4")  
    
    # Run evaluation
    evaluator = AgentEvaluator(agent, judge)
    await evaluator.run_evaluation_suite("evaluation/test_cases.json")

if __name__ == "__main__":
    asyncio.run(main())