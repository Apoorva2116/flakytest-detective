"""Resumable LLM judge for flaky-test detection with RAG and guardrails."""

import argparse
import ast
import json
import os
import re
import time

import requests

from pipeline.guardrails import (
    validate_input,
    validate_output,
    fallback_classification,
)


ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".."
)

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

OLLAMA = f"{OLLAMA_HOST}/api/generate"

# ---------------------------------------------------------
# KNOWLEDGE BASE
# ---------------------------------------------------------

KB = [
    (
        "Randomness: tests using random numbers, random choice, "
        "or UUID without a fixed seed can pass or fail on different runs."
    ),
    (
        "Timing: tests using fixed sleeps, timing thresholds, "
        "or background threads without proper synchronization can be flaky."
    ),
    (
        "Hash ordering: set iteration order can change because "
        "of Python hash randomization."
    ),
    (
        "Wall clock: tests depending on current time, microseconds, "
        "or timestamps can fail at different times."
    ),
    (
        "Network/service: intermittent services, timeouts, "
        "and connection errors can cause flaky tests."
    ),
    (
        "Order dependence/shared state: tests depending on state "
        "left by other tests can fail depending on execution order."
    ),
    (
        "Real failure: a deterministic failure that happens every run "
        "usually indicates a real bug, not flakiness."
    ),
]


# ---------------------------------------------------------
# DISCOVER TEST SOURCE CODE
# ---------------------------------------------------------

def test_sources():
    """Extract pytest test functions from target_repo/tests."""

    out = {}

    test_dir = os.path.join(
        ROOT,
        "target_repo",
        "tests"
    )

    for filename in os.listdir(test_dir):

        if (
            filename.startswith("test_")
            and filename.endswith(".py")
        ):

            path = os.path.join(
                test_dir,
                filename
            )

            with open(
                path,
                encoding="utf-8"
            ) as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):

                if (
                    isinstance(node, ast.FunctionDef)
                    and node.name.startswith("test_")
                ):

                    out[node.name] = (
                        ast.get_source_segment(
                            source,
                            node
                        )
                    )

    return out


# ---------------------------------------------------------
# BUILD RAG INDEX
# ---------------------------------------------------------

def build_index(history):
    """Build a ChromaDB collection from knowledge and test history."""

    import chromadb

    collection = chromadb.Client().create_collection(
        "flaky_ctx"
    )

    documents = list(KB)

    ids = [
        f"kb{i}"
        for i in range(len(KB))
    ]

    for test_name, data in history["tests"].items():

        if data["msgs"]:

            documents.append(
                f"Past failure of {test_name}: "
                f"{data['msgs'][0]} "
                f"(failed "
                f"{data['results'].count(0)} "
                f"of "
                f"{len(data['results'])} "
                f"recent runs)"
            )

            ids.append(
                f"history_{test_name}"
            )

    collection.add(
        documents=documents,
        ids=ids
    )

    return collection


# ---------------------------------------------------------
# CALL OLLAMA
# ---------------------------------------------------------

def ask(
    model,
    prompt,
    retries=3
):
    """Send prompt to Ollama with retry support."""

    for attempt in range(
        1,
        retries + 1
    ):

        try:

            start = time.time()

            response = requests.post(
                OLLAMA,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0
                    }
                },
                timeout=300
            )

            response.raise_for_status()

            data = response.json()

            return (
                data.get(
                    "response",
                    ""
                ),
                time.time() - start
            )

        except Exception as e:

            print(
                f"\nOllama request failed "
                f"(attempt {attempt}/{retries})"
            )

            print(
                type(e).__name__,
                e
            )

            if attempt < retries:

                wait = 5 * attempt

                print(
                    f"Retrying in {wait} seconds..."
                )

                time.sleep(wait)

            else:

                raise


# ---------------------------------------------------------
# PARSE LEGACY / INVALID MODEL OUTPUT
# ---------------------------------------------------------

def parse(text):
    """
    Parse model output.

    Supports the original format:

        {"flaky": true, "reason": "..."}

    and the new format:

        {
            "classification": "FLAKY",
            "confidence": 0.85,
            "reason": "...",
            "evidence": [...]
        }
    """

    try:

        data = json.loads(text)

    except Exception:

        match = re.search(
            r"\{.*\}",
            text,
            re.S
        )

        if match:

            try:
                data = json.loads(
                    match.group(0)
                )

            except Exception:
                data = {}

        else:

            data = {}

    # New structured format
    classification = data.get(
        "classification"
    )

    if classification:

        classification = str(
            classification
        ).strip().upper()

        if classification not in {
            "FLAKY",
            "REAL_BUG",
            "STABLE"
        }:

            classification = None

    # Legacy format
    if classification is None:

        flaky = data.get(
            "flaky",
            False
        )

        if isinstance(
            flaky,
            str
        ):

            flaky = (
                flaky.strip().lower()
                in ("true", "yes")
            )

        classification = (
            "FLAKY"
            if bool(flaky)
            else "STABLE"
        )

    # Confidence
    confidence = data.get(
        "confidence",
        0.0
    )

    try:

        confidence = float(
            confidence
        )

    except (
        TypeError,
        ValueError
    ):

        confidence = 0.0

    # Keep confidence within valid range
    confidence = max(
        0.0,
        min(
            1.0,
            confidence
        )
    )

    # Reason
    reason = str(
        data.get(
            "reason",
            ""
        )
    )[:500]

    # Evidence
    evidence = data.get(
        "evidence",
        []
    )

    if not isinstance(
        evidence,
        list
    ):

        evidence = []

    evidence = [
        str(item)[:300]
        for item in evidence[:5]
    ]

    return {
        "classification": classification,
        "confidence": confidence,
        "reason": reason,
        "evidence": evidence
    }


# ---------------------------------------------------------
# BUILD AI PROMPT
# ---------------------------------------------------------

def build_prompt(
    code,
    test_history,
    context
):
    """Create the structured prompt for the LLM."""

    return (
        "You are an expert software testing assistant "
        "for CI/CD failure triage.\n\n"

        "Your task is to classify a Python test into "
        "exactly ONE of these categories:\n\n"

        "FLAKY\n"
        "REAL_BUG\n"
        "STABLE\n\n"

        "Definitions:\n\n"

        "FLAKY:\n"
        "The test is nondeterministic and can pass or fail "
        "without a relevant code change. Possible causes "
        "include timing, randomness, concurrency, ordering, "
        "shared state, environment conditions, network "
        "instability, or resource availability.\n\n"

        "REAL_BUG:\n"
        "The test fails consistently because the software "
        "implementation or expected behaviour is incorrect.\n\n"

        "STABLE:\n"
        "The test behaves consistently and there is no "
        "evidence of nondeterministic behaviour.\n\n"

        "IMPORTANT:\n"
        "A test that fails repeatedly is NOT automatically flaky. "
        "Persistent deterministic failure can indicate a real bug.\n\n"

        "Use only the supplied evidence. "
        "Do not invent facts.\n\n"

        f"{context}\n"

        f"Test code:\n{code}\n\n"

        "Execution history:\n"
        f"{json.dumps(test_history, indent=2)}\n\n"

        "Return ONLY valid JSON using exactly this structure:\n\n"

        "{\n"
        '  "classification": "FLAKY",\n'
        '  "confidence": 0.85,\n'
        '  "reason": "short explanation",\n'
        '  "evidence": [\n'
        '    "evidence item 1",\n'
        '    "evidence item 2"\n'
        "  ]\n"
        "}\n\n"

        "The classification MUST be exactly "
        "FLAKY, REAL_BUG, or STABLE.\n"

        "Confidence MUST be a number between 0 and 1."
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True
    )

    parser.add_argument(
        "--mode",
        choices=[
            "rag",
            "norag"
        ],
        required=True
    )

    parser.add_argument(
        "--top_k",
        type=int,
        default=3
    )

    args = parser.parse_args()

    # -----------------------------------------------------
    # RESULTS DIRECTORY
    # -----------------------------------------------------

    results_dir = os.path.join(
        ROOT,
        "results"
    )

    os.makedirs(
        results_dir,
        exist_ok=True
    )

    # -----------------------------------------------------
    # LOAD HISTORY
    # -----------------------------------------------------

    history_path = os.path.join(
        results_dir,
        "history.json"
    )

    with open(
        history_path,
        encoding="utf-8"
    ) as f:

        history = json.load(f)

    # -----------------------------------------------------
    # LOAD TEST SOURCES
    # -----------------------------------------------------

    sources = test_sources()

    # -----------------------------------------------------
    # BUILD RAG COLLECTION
    # -----------------------------------------------------

    collection = (
        build_index(history)
        if args.mode == "rag"
        else None
    )

    # -----------------------------------------------------
    # OUTPUT FILE
    # -----------------------------------------------------

    output_path = os.path.join(
        results_dir,
        f"llm_{args.model}_{args.mode}.json"
    )

    # -----------------------------------------------------
    # RESUME INTERRUPTED RUN
    # -----------------------------------------------------

    if os.path.exists(
        output_path
    ):

        try:

            with open(
                output_path,
                encoding="utf-8"
            ) as f:

                results = json.load(f)

            print(
                f"Resuming existing run: "
                f"{len(results)} tests already completed."
            )

        except Exception:

            print(
                "Existing result file is invalid. "
                "Starting a new run."
            )

            results = {}

    else:

        results = {}

    # -----------------------------------------------------
    # RUN INFORMATION
    # -----------------------------------------------------

    total = len(
        sources
    )

    print(
        f"Total tests: {total}"
    )

    print(
        f"Already completed: "
        f"{len(results)}"
    )

    print(
        f"Remaining: "
        f"{total - len(results)}"
    )

    print()

    # -----------------------------------------------------
    # PROCESS EACH TEST
    # -----------------------------------------------------

    for index, (
        name,
        code
    ) in enumerate(
        sources.items(),
        start=1
    ):

        # -------------------------------------------------
        # SKIP COMPLETED TESTS
        # -------------------------------------------------

        if name in results:

            print(
                f"[{index}/{total}] "
                f"{name:40} "
                f"SKIPPED"
            )

            continue

        # -------------------------------------------------
        # TEST HISTORY
        # -------------------------------------------------

        test_history = history[
            "tests"
        ].get(
            name,
            {
                "results": [],
                "msgs": []
            }
        )

        # -------------------------------------------------
        # INPUT GUARDRAIL
        # -------------------------------------------------

        input_check = validate_input(
            test_name=name,
            test_code=code,
            history=test_history
        )

        if not input_check["valid"]:

            print(
                f"[{index}/{total}] "
                f"{name:40} "
                f"NEEDS_REVIEW "
                f"(input guardrail)"
            )

            results[name] = {
                "flaky": False,
                "classification": "NEEDS_REVIEW",
                "confidence": 0.0,
                "reason": (
                    "Input validation failed: "
                    + "; ".join(
                        input_check["errors"]
                    )
                ),
                "evidence": [],
                "seconds": 0
            }

            # Save checkpoint
            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    results,
                    f,
                    indent=1
                )

            continue

        # -------------------------------------------------
        # RAG RETRIEVAL
        # -------------------------------------------------

        context = ""

        if collection:

            query = (
                code
                + " "
                + " ".join(
                    test_history[
                        "msgs"
                    ][:1]
                )
            )

            hits = collection.query(
                query_texts=[
                    query
                ],
                n_results=args.top_k
            )[
                "documents"
            ][0]

            context = (
                "Retrieved context:\n- "
                + "\n- ".join(
                    hits
                )
                + "\n"
            )

        # -------------------------------------------------
        # BUILD PROMPT
        # -------------------------------------------------

        prompt = build_prompt(
            code=code,
            test_history=test_history,
            context=context
        )

        # -------------------------------------------------
        # CALL LLM
        # -------------------------------------------------

        try:

            text,
            seconds = ask(
                args.model,
                prompt
            )

            # ---------------------------------------------
            # PARSE MODEL RESPONSE
            # ---------------------------------------------

            parsed = parse(
                text
            )

            # ---------------------------------------------
            # OUTPUT GUARDRAIL
            # ---------------------------------------------

            output_check = validate_output(
                parsed
            )

            if output_check["valid"]:

                validated = (
                    output_check["result"]
                )

                classification = (
                    validated[
                        "classification"
                    ]
                )

                confidence = (
                    validated[
                        "confidence"
                    ]
                )

                reason = validated[
                    "reason"
                ]

                evidence = validated[
                    "evidence"
                ]

                print(
                    f"[{index}/{total}] "
                    f"{name:40} "
                    f"{classification} "
                    f"confidence={confidence:.2f} "
                    f"{seconds:.1f}s"
                )

                results[name] = {
                    "flaky": (
                        classification
                        == "FLAKY"
                    ),
                    "classification": (
                        classification
                    ),
                    "confidence": (
                        confidence
                    ),
                    "reason": reason,
                    "evidence": evidence,
                    "seconds": round(
                        seconds,
                        2
                    )
                }

            else:

                # -----------------------------------------
                # FALLBACK
                # -----------------------------------------

                fallback = (
                    fallback_classification(
                        test_history
                    )
                )

                print(
                    f"[{index}/{total}] "
                    f"{name:40} "
                    f"NEEDS_REVIEW "
                    f"(output guardrail)"
                )

                results[name] = {
                    "flaky": False,
                    "classification": (
                        fallback[
                            "classification"
                        ]
                    ),
                    "confidence": (
                        fallback[
                            "confidence"
                        ]
                    ),
                    "reason": (
                        fallback[
                            "reason"
                        ]
                    ),
                    "evidence": (
                        fallback[
                            "evidence"
                        ]
                    ),
                    "seconds": round(
                        seconds,
                        2
                    )
                }

            # ---------------------------------------------
            # CHECKPOINT SAVE
            # ---------------------------------------------

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    results,
                    f,
                    indent=1
                )

            print(
                f"  checkpoint saved "
                f"({len(results)}/{total})"
            )

        except Exception as e:

            print()

            print(
                f"Could not process {name}"
            )

            print(
                type(e).__name__,
                e
            )

            print(
                f"Checkpoint preserved: "
                f"{len(results)}/{total}"
            )

            print(
                "You can restart the same command "
                "after Ollama is available."
            )

            raise

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        f"COMPLETE: "
        f"{len(results)}/{total} tests"
    )

    print(
        "=" * 60
    )

    print(
        "Saved:",
        output_path
    )
