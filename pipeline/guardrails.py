from typing import Any, Dict


ALLOWED_CLASSIFICATIONS = {
    "FLAKY",
    "REAL_BUG",
    "STABLE",
}


def validate_input(test_name: str, test_code: str, history: Any) -> Dict[str, Any]:
    """
    Basic input guardrails before sending information to the LLM.
    """

    errors = []

    if not test_name or not isinstance(test_name, str):
        errors.append("Invalid test name.")

    if not test_code or not isinstance(test_code, str):
        errors.append("Test source code is missing.")

    if history is None:
        errors.append("Execution history is missing.")

    if len(test_code) > 30000:
        errors.append("Test/source input is too large.")

    if errors:
        return {
            "valid": False,
            "errors": errors
        }

    return {
        "valid": True,
        "errors": []
    }


def validate_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalise the LLM response.
    """

    if not isinstance(result, dict):
        return {
            "valid": False,
            "errors": ["LLM response is not a JSON object."]
        }

    errors = []

    classification = result.get("classification")
    confidence = result.get("confidence")
    reason = result.get("reason")

    if classification not in ALLOWED_CLASSIFICATIONS:
        errors.append(
            f"Invalid classification: {classification}"
        )

    try:
        confidence = float(confidence)

        if not 0 <= confidence <= 1:
            errors.append("Confidence must be between 0 and 1.")

    except (TypeError, ValueError):
        errors.append("Confidence must be numeric.")

    if not isinstance(reason, str) or not reason.strip():
        errors.append("Reason is missing.")

    if errors:
        return {
            "valid": False,
            "errors": errors
        }

    return {
        "valid": True,
        "errors": [],
        "result": {
            "classification": classification,
            "confidence": confidence,
            "reason": reason.strip(),
            "evidence": result.get("evidence", [])
        }
    }


def fallback_classification(history: Any) -> Dict[str, Any]:
    """
    Safe fallback when the LLM output cannot be trusted.

    We do NOT automatically claim that a failure is flaky.
    Instead, we return NEEDS_REVIEW.
    """

    return {
        "classification": "NEEDS_REVIEW",
        "confidence": 0.0,
        "reason": (
            "The AI response failed validation. "
            "Manual review is required."
        ),
        "evidence": []
    }
