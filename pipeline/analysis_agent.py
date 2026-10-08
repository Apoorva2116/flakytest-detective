import json
import requests

from pipeline.guardrails import (
    validate_input,
    validate_output,
    fallback_classification,
)


OLLAMA_URL = "http://localhost:11434/api/generate"


SYSTEM_INSTRUCTION = """
You are FlakyTest Detective, an AI assistant for CI/CD failure triage.

Your job is to classify a test into exactly one of:

FLAKY
REAL_BUG
STABLE

Definitions:

FLAKY:
The test can pass and fail without a relevant code change because of
timing, randomness, concurrency, ordering, resources, shared state,
environmental conditions, or another nondeterministic cause.

REAL_BUG:
The test fails consistently because the implementation or expected
behaviour is incorrect.

STABLE:
The test is deterministic and does not show evidence of flaky behaviour.

IMPORTANT:
A test failing repeatedly does NOT automatically mean it is flaky.
Persistent failure may indicate a real bug.

Return ONLY valid JSON:

{
  "classification": "FLAKY",
  "confidence": 0.85,
  "reason": "short explanation",
  "evidence": [
    "evidence item 1",
    "evidence item 2"
  ]
}
"""


def analyse_test(
    model: str,
    test_name: str,
    test_code: str,
    history,
    retrieved_context: str = ""
):
    """
    Run the FlakyTest analysis agent with input and output guardrails.
    """

    # -------------------------
    # INPUT GUARDRAIL
    # -------------------------

    validation = validate_input(
        test_name,
        test_code,
        history
    )

    if not validation["valid"]:
        return {
            "classification": "NEEDS_REVIEW",
            "confidence": 0.0,
            "reason": "Input validation failed.",
            "evidence": validation["errors"]
        }

    prompt = f"""
{SYSTEM_INSTRUCTION}

TEST NAME:
{test_name}

TEST SOURCE:
{test_code}

EXECUTION HISTORY:
{json.dumps(history, indent=2)}

RETRIEVED EVIDENCE:
{retrieved_context}

Analyse the evidence carefully.

Do not classify a test as flaky simply because it has failed before.

Return JSON only.
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        raw_response = data.get("response", "")

        parsed = json.loads(raw_response)

    except Exception as exc:

        return {
            "classification": "NEEDS_REVIEW",
            "confidence": 0.0,
            "reason": f"AI analysis failed: {exc}",
            "evidence": []
        }

    # -------------------------
    # OUTPUT GUARDRAIL
    # -------------------------

    output_validation = validate_output(parsed)

    if not output_validation["valid"]:
        return fallback_classification(history)

    return output_validation["result"]
