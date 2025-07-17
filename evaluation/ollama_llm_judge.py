#!/usr/bin/env python3
"""
Multi‑framework Ollama LLM Judge
================================
Compare Rosetta‑Stone agent quality across langgraph, llamaindex,
and smolagents adapters.

Usage
-----
    python3 evaluation/ollama_llm_judge.py        # quick debug
    python3 evaluation/ollama_llm_judge.py full   # full test suite
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List

# ------------------------------------------------------------------ #
# 0.  Ensure repo root on PYTHONPATH                                  #
# ------------------------------------------------------------------ #
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_ROOT)

# ------------------------------------------------------------------ #
# 1.  Third‑party dependency check                                    #
# ------------------------------------------------------------------ #
try:
    import ollama
    print("✅  Ollama imported successfully")
except ImportError:
    print("❌  Install the Ollama Python client with `pip install ollama`")
    sys.exit(1)

# ------------------------------------------------------------------ #
# 2.  Internal imports (core.*)                                       #
# ------------------------------------------------------------------ #
try:
    from core.agent import RosettaStoneAgent
    from core.config import get_config
except ModuleNotFoundError as e:
    print("❌  Could not import core modules – is the repo intact?")
    print(e)
    sys.exit(1)

# ------------------------------------------------------------------ #
# 3.  Globals                                                         #
# ------------------------------------------------------------------ #
FRAMEWORKS         = ["langgraph", "llamaindex", "smolagents"]
OLLAMA_MODEL       = "llama3.1"
MAX_TOTAL_CASES    = 5     # caps in debug mode
MAX_PER_CATEGORY   = 2

# ------------------------------------------------------------------ #
# 4.  Helper: clone/patch Config safely                               #
# ------------------------------------------------------------------ #
def _with_framework(cfg, fw: str):
    """
    Return a *new* Config with .framework set to `fw`, handling
    pydantic or dataclass objects transparently.
    """
    # pydantic BaseModel
    if hasattr(cfg, "copy"):
        try:
            return cfg.copy(update={"framework": fw})
        except Exception:
            pass

    # dataclass (maybe frozen)
    try:
        from dataclasses import replace, is_dataclass
        if is_dataclass(cfg):
            return replace(cfg, framework=fw)
    except Exception:
        pass

    # attribute assignment (mutable object)
    if hasattr(cfg, "framework"):
        try:
            setattr(cfg, "framework", fw)
            return cfg
        except Exception:
            pass

    # dictionary‑like fallback
    if isinstance(cfg, dict):
        new_cfg = cfg.copy()
        new_cfg["framework"] = fw
        return new_cfg

    raise TypeError("Unable to set framework on Config object")

# ------------------------------------------------------------------ #
# 5.  Ollama‑based judge (unchanged logic)                            #
# ------------------------------------------------------------------ #
class DebugOllamaJudge:
    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model
        print(f"🤖  Judge initialised with model: {model}")

    def evaluate(self, test_case: dict, agent_response: str) -> dict:
        # (same body as before – omitted for brevity)
        # ------------------------------------------------------------
        print(f"\n🔍  EVALUATING: {test_case['test_id']}")
        if "conversation" in test_case:
            q_text   = f"Conversation: {len(test_case['conversation'])} turns"
            conv_txt = " → ".join(t['user'] for t in test_case['conversation'])
            q_ctx    = f"Multi‑turn conversation: {conv_txt}"
        else:
            q_text = test_case['query'][:50] + "..."
            q_ctx  = f"Single query: {test_case['query']}"
        print(f"📝  Query: {q_text}")
        print(f"📝  Response length: {len(agent_response)} chars")

        criteria  = test_case.get('evaluation_criteria', {'quality': 'Rate quality'})
        crit_keys = list(criteria.keys())
        print(f"📊  Criteria: {crit_keys}")

        prompt = self._build_prompt(criteria, q_ctx, agent_response)
        print("🚀  Sending to Ollama …")

        try:
            resp = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                options={"temperature": 0.1, "num_predict": 300},
            )
            raw = resp["message"]["content"].strip()
            print(f"✅  Ollama responded (first 100 chars): {raw[:100]}")
            data = self._extract_json(raw)
            if data:
                scores = {k: max(1, min(4, int(data["scores"].get(k, 3))))
                          for k in crit_keys}
                avg = sum(scores.values()) / len(scores)
                print(f"📊  Scores: {scores} | Avg: {avg:.1f}/4")
                return {"test_id": test_case["test_id"],
                        "scores": scores,
                        "overall": avg,
                        "status": "SUCCESS"}
        except Exception as e:
            print(f"❌  Ollama interaction failed: {e}")

        fallback = {k: 2 for k in crit_keys}
        return {"test_id": test_case["test_id"],
                "scores": fallback,
                "overall": 2.0,
                "status": "FAILED"}

    @staticmethod
    def _build_prompt(criteria, context, agent_resp):
        crit_block = "\n".join(f"- {k}: {v}" for k, v in criteria.items())
        crit_stub  = ", ".join(f'"{k}": 3' for k in criteria)
        exp_stub   = ", ".join(f'"{k}": "reason"' for k in criteria)
        return f"""You are evaluating an AI that embodies the ancient Rosetta Stone.
Rate 1‑4 (4=Excellent).

CRITERIA:
{crit_block}

CONTEXT: {context}

AI RESPONSE (first 300 chars):
{agent_resp[:300]}…

Respond ONLY with JSON:
{{"scores": {{{crit_stub}}}, "explanations": {{{exp_stub}}}}}"""

    @staticmethod
    def _extract_json(text: str):
        start, end = text.find("{"), text.rfind("}") + 1
        if start == -1 or end <= start:
            return None
        blob = text[start:end].replace("\n", " ").replace("...", "")
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            return None

# ------------------------------------------------------------------ #
# 6.  Utility functions                                               #
# ------------------------------------------------------------------ #
def load_test_suite() -> dict:
    path = os.path.join(REPO_ROOT, "evaluation", "test_cases.json")
    try:
        with open(path, "r", encoding="utf‑8") as f:
            data = json.load(f)
        print(f"📋  Loaded {sum(len(v) for v in data.values())} test cases.")
        return data
    except FileNotFoundError:
        print("⚠️  test_cases.json not found – using fallback test.")
        return {
            "simple_tests": [
                {
                    "test_id": "simple_1",
                    "query": "What are hieroglyphs?",
                    "evaluation_criteria": {
                        "accuracy": "Factual correctness",
                        "persona":  "Maintains Rosetta Stone persona",
                    },
                }
            ]
        }

def run_conversation(agent: RosettaStoneAgent, convo: List[dict]) -> str:
    reply = ""
    for turn in convo:
        reply = agent.process_message_sync(turn["user"]).content
    return reply

def print_summary(res: Dict[str, List[dict]]) -> None:
    print("\n🏁  COMPARISON SUMMARY")
    print("Framework         Avg   Success/Total")
    print("--------------------------------------")
    for fw, lst in res.items():
        ok = [r for r in lst if r["status"] == "SUCCESS"]
        avg = sum(r["overall"] for r in ok) / len(ok) if ok else 0
        print(f"{fw:<16} {avg:>4.2f}   {len(ok)}/{len(lst)}")

def save_results(blob: dict) -> None:
    path = os.path.join(REPO_ROOT, "multi_framework_results.json")
    with open(path, "w", encoding="utf‑8") as f:
        json.dump(blob, f, indent=2)
    print(f"\n💾  Results saved → {path}")

# ------------------------------------------------------------------ #
# 7.  Evaluation driver                                              #
# ------------------------------------------------------------------ #
def run_evaluation(full: bool = False) -> None:
    suite   = load_test_suite()
    judge   = DebugOllamaJudge()
    results = {fw: [] for fw in FRAMEWORKS}

    for fw in FRAMEWORKS:
        print(f"\n🛠️  ===== Framework: {fw} =====")
        base_cfg = get_config()
        cfg      = _with_framework(base_cfg, fw)
        agent    = RosettaStoneAgent(cfg)

        executed     = 0
        limit_total  = float("inf") if full else MAX_TOTAL_CASES

        for cat, tests in suite.items():
            subset = tests if full else tests[:MAX_PER_CATEGORY]
            for tc in subset:
                if executed >= limit_total:
                    break
                executed += 1

                print(f"\n[{executed}] {tc['test_id']}")
                agent.start_session(f"{fw}_{tc['test_id']}")

                reply = (agent.process_message_sync(tc["query"]).content
                         if "query" in tc else
                         run_conversation(agent, tc["conversation"]))
                scored = judge.evaluate(tc, reply)
                results[fw].append(scored)

            if executed >= limit_total:
                break

    print_summary(results)
    save_results({"timestamp": datetime.now().isoformat(),
                  "frameworks": FRAMEWORKS,
                  "judge_model": OLLAMA_MODEL,
                  "results": results})

# ------------------------------------------------------------------ #
# 8.  CLI entry‑point                                                #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    full_mode = len(sys.argv) > 1 and sys.argv[1].lower() == "full"
    try:
        run_evaluation(full_mode)
    except Exception as exc:
        print("💥  Fatal error during evaluation:", exc)
        traceback.print_exc()
