import csv
import yaml
import openai # The library is used to interface with Ollama's OpenAI-compatible API
import pandas as pd
import os
import json
from time import sleep
import pathlib
import sys
import asyncio # Import asyncio to run the agent's async methods

# --- PATHING SETUP ---
script_dir = pathlib.Path(__file__).parent.resolve()
root_dir = script_dir.parent
sys.path.insert(0, str(root_dir))
rubric_path = root_dir / 'persona_rubric.yaml'
benchmark_path = root_dir / 'prompt_benchmark.csv'
metaprompt_path = root_dir / 'judge_metaprompt.txt'
results_path = script_dir / 'pas_results.csv'

# --- CONFIGURATION for OLLAMA ---
print("--- Initializing for Local Evaluation (Ollama) ---")
# This client points to your local Ollama server. No API key needed.
try:
    local_client = openai.OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama',
    )
    # Test connection to Ollama server
    local_client.models.list()
    print("✅ Successfully connected to Ollama server.")
except Exception as e:
    print(f"❌ ERROR: Could not connect to Ollama server at http://localhost:11434.")
    print("Please ensure Ollama is running before starting the script.")
    sys.exit(f"Details: {e}")


# --- AGENT INITIALIZATION ---
from core.agent import RosettaStoneAgent
from core.config import get_config
print("--- Initializing Rosetta Stone Agent ---")
agent_config = get_config()
rosetta_agent = RosettaStoneAgent(agent_config)
print("✅ Rosetta Stone Agent initialized successfully.")

# --- HELPER FUNCTIONS ---
def get_rosetta_stone_response(prompt: str) -> str:
    print(f"Getting response for prompt: '{prompt[:30]}...'")
    try:
        response_obj = asyncio.run(rosetta_agent.process_message(prompt))
        content = response_obj.content
        print(f"  -> Agent responded: '{content[:50]}...'")
        return content
    except Exception as e:
        print(f"  -> ERROR calling agent directly: {e}")
        return f"Error: {e}"

def load_yaml(file_path: pathlib.Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_csv(file_path: pathlib.Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_text(file_path: pathlib.Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_judge_evaluation(persona_definition: str, user_prompt: str, agent_response: str, meta_prompt_template: str):
    print("  -> Asking LOCAL LLM Judge (Ollama) for evaluation...")
    filled_prompt = meta_prompt_template.format(
        persona_definition=str(persona_definition),
        user_prompt=user_prompt,
        agent_response=agent_response
    )
    try:
        response = local_client.chat.completions.create(
            model="llama3", # Using the local llama3 model
            messages=[{"role": "system", "content": "You are a helpful assistant designed to output JSON. Do not include any text outside of the JSON object."},
                      {"role": "user", "content": filled_prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        print(f"  -> Judge scored: {result.get('score')}/5")
        return result
    except Exception as e:
        print(f"  -> ERROR getting evaluation from judge: {e}")
        return {"score": -1, "justification": f"API Error: {e}"}

# --- MAIN EXECUTION ---
def main():
    print("\n--- Starting Phase 1: Loading Assets ---")
    persona_rubric = load_yaml(rubric_path)
    prompt_benchmark = load_csv(benchmark_path)
    judge_metaprompt = load_text(metaprompt_path)
    print("Assets loaded successfully.")

    results = []

    print("\n--- Starting Phase 2: Executing Evaluation Loop ---")
    for i, item in enumerate(prompt_benchmark):
        print(f"\n--- Processing Prompt {i+1}/{len(prompt_benchmark)} ---")
        prompt_id = item['prompt_id']
        prompt_text = item['prompt_text']
        target_persona = item['target_persona']

        agent_response = get_rosetta_stone_response(prompt_text)
        
        if agent_response.startswith("Error:"):
            evaluation = {"score": 0, "justification": "Agent returned an error, not evaluated."}
        else:
            persona_definition = persona_rubric.get(target_persona, {})
            evaluation = get_judge_evaluation(
                persona_definition=persona_definition,
                user_prompt=prompt_text,
                agent_response=agent_response,
                meta_prompt_template=judge_metaprompt
            )
        
        sleep(1)

        result_entry = {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "target_persona": target_persona,
            "agent_response": agent_response,
            "score": evaluation.get('score'),
            "justification": evaluation.get('justification')
        }
        results.append(result_entry)

    print("\n--- Starting Phase 3: Saving Results ---")
    results_df = pd.DataFrame(results)
    results_df.to_csv(results_path, index=False, encoding='utf-8')
    print(f"Evaluation complete. Results saved to '{results_path}'.")

if __name__ == "__main__":
    main()