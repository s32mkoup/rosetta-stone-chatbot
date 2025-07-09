#!/usr/bin/env python3
"""
Comprehensive evaluation for Rosetta Stone Agent using an LLM as a judge.

This implementation is based on the Hugging Face Cookbook guide for LLM-as-a-judge:
https://huggingface.co/learn/cookbook/en/llm_judge

Key Improvements:
- Structured JSON Output: The judge is required to output JSON, making parsing 100% reliable.
- Robust Prompting: Prompts are engineered for clarity and include detailed scoring rubrics.
- Better Error Handling: API failures are caught gracefully and do not pollute results with default scores.
"""

import json
import asyncio
import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()

from huggingface_hub import AsyncInferenceClient

# --- Data Structures for Evaluation Results ---

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

# --- The LLM Judge ---

class LLMJudge:
    """
    An LLM-based judge that evaluates an agent's response against a set of criteria,
    outputting a structured JSON object with scores and explanations.
    """
    
    def __init__(self, judge_model: str = "meta-llama/Llama-3.1-8B-Instruct", provider: str = "hf-inference"):
        """
        Initializes the LLM Judge.

        Args:
            judge_model: The Hugging Face model to use for judging.
            provider: The specific Hugging Face provider to use. 'hf-inference' is the default free tier.
        """
        self.judge_model = judge_model
        self.provider = provider
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not found in environment variables. Please set it in a .env file.")
        
        # Use the asynchronous client, explicitly setting the provider
        self.llm_client = AsyncInferenceClient(
            model=judge_model, 
            token=hf_token, 
            timeout=120
        )
        
        print(f"🧑‍⚖️ LLM Judge initialized with model: {self.judge_model} via {self.provider}")

    def _create_evaluation_prompt(self, test_case: Dict[str, Any], agent_response: str) -> List[Dict[str, str]]:
        """
        Creates a structured prompt for the LLM judge, instructing it to return JSON.
        """
        query = test_case.get('query', 'See conversation history for context.')
        criteria = test_case.get('evaluation_criteria', {'overall_quality': 'Assess the overall quality of the response.'})
        
        criteria_description = "\n".join(
            f"- {name.upper()}: {desc}" for name, desc in criteria.items()
        )

        system_prompt = f"""
You are a fair and impartial AI quality evaluator. Your task is to evaluate an AI agent's response based on a given user query and a set of evaluation criteria.
The agent you are evaluating is designed to embody the persona of the ancient Rosetta Stone.
SCORING INSTRUCTIONS: Rate each criterion on a scale of 1 to 4 (1: Poor, 2: Fair, 3: Good, 4: Excellent).
OUTPUT FORMAT: You MUST provide your response as a single, valid JSON object with "scores" and "explanations" keys.
"""

        user_prompt = f"""
EVALUATION CRITERIA:
{criteria_description}

USER QUERY: "{query}"
AGENT RESPONSE: "{agent_response}"

Provide your evaluation in the required JSON format.
"""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    async def evaluate_response(self, test_case: Dict[str, Any], agent_response: str) -> EvaluationResult:
        """
        Evaluates a single agent response using the LLM judge.
        """
        messages = self._create_evaluation_prompt(test_case, agent_response)
        criteria_keys = list(test_case.get('evaluation_criteria', {'overall_quality': ''}).keys())
        
        try:
            response = await self.llm_client.chat_completion(
                messages=messages,
                max_tokens=1024,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            
            json_string = response.choices[0].message.content
            parsed_json = json.loads(json_string)
            
            scores = parsed_json.get('scores', {})
            explanations = parsed_json.get('explanations', {})
            
            valid_scores = {k: max(1, min(4, int(v))) for k, v in scores.items() if k in criteria_keys and isinstance(v, (int, float))}
            
            if not valid_scores:
                raise ValueError("Judge response contained no valid scores.")

            overall_score = sum(valid_scores.values()) / len(valid_scores)
            
            return EvaluationResult(
                test_id=test_case['test_id'],
                test_type=test_case.get('test_type', 'unknown'),
                status='SUCCESS',
                scores=valid_scores,
                explanations=explanations,
                overall_score=overall_score,
                agent_response=agent_response,
            )
        except Exception as e:
            print(f"❌ LLM Judge evaluation failed for test '{test_case['test_id']}': {e}")
            return EvaluationResult(
                test_id=test_case['test_id'],
                test_type=test_case.get('test_type', 'unknown'),
                status='FAILED',
                agent_response=agent_response,
                error_message=str(e)
            )

# --- The Main Evaluator Class ---

class AgentEvaluator:
    """Orchestrates the evaluation suite, runs tests, and generates reports."""
    
    def __init__(self, agent, judge: LLMJudge):
        self.agent = agent
        self.judge = judge
        self.results: List[EvaluationResult] = []

    async def run_evaluation_suite(self, test_cases_file: str):
        """Runs the comprehensive evaluation suite against all test cases."""
        try:
            with open(test_cases_file, 'r') as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error loading test cases file: {e}")
            return

        print("🏺 Starting Rosetta Stone Agent Comprehensive Evaluation...")
        
        all_tests = [
            {**test_case, 'category': category}
            for category, tests in test_data.items()
            for test_case in tests
        ]

        tasks = [self._evaluate_test(test_case) for test_case in all_tests]
        self.results = await asyncio.gather(*tasks)
        
        self._generate_comprehensive_report()

    async def _evaluate_test(self, test_case: Dict) -> EvaluationResult:
        """Centralized method to evaluate a single test case."""
        category = test_case['category']
        print(f"Evaluating [{category}]: {test_case['test_id']}...")
        
        self.agent.start_session(f"eval_{test_case['test_id']}")
        agent_response_content = ""
        
        try:
            if category == "memory_tests":
                responses = [await self.agent.process_message(turn['user']) for turn in test_case['conversation']]
                agent_response_content = responses[-1].content if responses else ""
            else:
                if category == "persona_tests":
                    personas = test_case.get('personas', ['mystical'])
                    responses = []
                    for persona in personas:
                        if persona != 'mystical':
                            await self.agent.process_message(f"/persona {persona}")
                        response = await self.agent.process_message(test_case['query'])
                        responses.append(f"[{persona.upper()}]: {response.content}")
                    agent_response_content = "\n\n".join(responses)
                else:
                    response = await self.agent.process_message(test_case['query'])
                    agent_response_content = response.content
                    if hasattr(response, 'tools_used') and response.tools_used:
                        agent_response_content += f"\n\n[TOOLS USED: {', '.join(response.tools_used)}]"
        except Exception as e:
            print(f"❌ Agent failed to process test '{test_case['test_id']}': {e}")
            return EvaluationResult(
                test_id=test_case['test_id'],
                test_type=category.replace('_tests', ''),
                status='FAILED',
                error_message=f"Agent processing error: {e}"
            )

        test_case['test_type'] = category.replace('_tests', '')
        result = await self.judge.evaluate_response(test_case, agent_response_content)
        
        if result.status == 'SUCCESS':
            print(f"   ✅ Score: {result.overall_score:.1f}/4.0")
        else:
            print(f"   ❌ Judge Failed. Reason: {result.error_message}")
        
        return result

    def _generate_comprehensive_report(self):
        """Generates and prints a detailed evaluation report."""
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE ROSETTA STONE AGENT EVALUATION REPORT")
        print("="*80)

        successful_results = [r for r in self.results if r.status == 'SUCCESS']
        failed_results = [r for r in self.results if r.status == 'FAILED']

        if not self.results:
            print("No evaluation results were generated.")
            return

        print(f"\n📊 OVERALL PERFORMANCE:")
        print(f"   • Total Tests Attempted: {len(self.results)}")
        print(f"   • Successful Evaluations: {len(successful_results)}")
        print(f"   • Failed Evaluations: {len(failed_results)}")

        if not successful_results:
            print("\nNo tests were successfully evaluated.")
            if failed_results:
                print("\nFailed Tests:")
                for r in failed_results:
                    print(f"  - {r.test_id}: {r.error_message}")
            return

        overall_scores = [r.overall_score for r in successful_results]
        avg_score = sum(overall_scores) / len(overall_scores) if successful_results else 0
        
        print(f"   • Average Score (successful tests): {avg_score:.2f}/4.0 ({avg_score/4*100:.1f}%)")
        if successful_results:
            print(f"   • Best Score: {max(overall_scores):.2f}/4.0")
            print(f"   • Worst Score: {min(overall_scores):.2f}/4.0")

        by_category = {}
        for result in successful_results:
            category = result.test_type
            by_category.setdefault(category, []).append(result.overall_score)
        
        print("\n📈 PERFORMANCE BY CATEGORY:")
        for category, scores in sorted(by_category.items()):
            avg_cat_score = sum(scores) / len(scores)
            print(f"   • {category.replace('_', ' ').title():<20}: {avg_cat_score:.2f}/4.0 ({len(scores)} tests)")

        worst_results = sorted(successful_results, key=lambda x: x.overall_score)[:5]
        print("\n⚠️ AREAS FOR IMPROVEMENT (Lowest Scoring Tests):")
        for result in worst_results:
            print(f"   • {result.test_id} ({result.test_type}): {result.overall_score:.2f}/4.0")
            if result.scores:
                worst_criterion = min(result.scores.items(), key=lambda item: item[1])
                print(f"     - Lowest Criterion: '{worst_criterion[0]}' ({worst_criterion[1]}/4)")

        self._save_results_to_file()
        print(f"\n💾 Detailed results saved to: evaluation_results.json")
        print("="*80)

    def _save_results_to_file(self):
        """Saves the detailed evaluation results to a JSON file."""
        successful_results = [r for r in self.results if r.status == 'SUCCESS']
        avg_score = (sum(r.overall_score for r in successful_results) / len(successful_results)) if successful_results else 0
        
        results_data = {
            'evaluation_summary': {
                'timestamp': datetime.now().isoformat(),
                'judge_model': self.judge.judge_model,
                'total_tests': len(self.results),
                'successful_tests': len(successful_results),
                'failed_tests': len([r for r in self.results if r.status == 'FAILED']),
                'average_score': avg_score,
            },
            'results': [res.__dict__ for res in self.results]
        }
        with open('evaluation_results.json', 'w') as f:
            json.dump(results_data, f, indent=2)

# --- Main Execution Block ---

async def main():
    """Main function to run the evaluation."""
    from core.agent import RosettaStoneAgent
    from core.config import get_config

    try:
        # --- Configuration Override for Free Evaluation ---
        config = get_config()
        
        free_model_id = "meta-llama/Llama-3.1-8B-Instruct"
        free_provider = "hf-inference" # Use the default, free Hugging Face provider
        
        print("🔧 Overriding agent and judge configuration for free evaluation...")
        print(f"🔧 Using model: {free_model_id} via provider: {free_provider}")
        
        # Override the agent's LLM config by modifying the attributes directly
        config.llm.model_id = free_model_id
        config.llm.provider = free_provider

        # Initialize the agent with the new, free configuration
        agent = RosettaStoneAgent(config)
        
        # Initialize the judge with the same free model and provider
        judge = LLMJudge(judge_model=free_model_id, provider=free_provider)
        
        evaluator = AgentEvaluator(agent, judge)
        await evaluator.run_evaluation_suite("evaluation/test_cases.json")

    except Exception as e:
        print(f"❌ A critical error occurred during the evaluation setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
