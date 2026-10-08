# FlakyTest Detective
Research question: can an LLM with retrieval over test code and past CI failures identify flaky tests
more accurately than simple rerun rules, at lower CI cost?

## Run (Ubuntu VM)
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python reruns/run_reruns.py --n 50 --out results/ground_truth.json   # ground truth, never shown to the AI
    python reruns/run_reruns.py --n 5  --out results/history.json        # short "past CI history"
    python rag/run_judge.py --model codellama --mode norag
    python rag/run_judge.py --model codellama --mode rag
    python evaluate.py

## Method notes (for the report)
- Flaky = fails some but not all of 50 runs. Always-failing tests are real bugs, not flaky.
- 10 of 30 tests have INJECTED flakiness (test_flaky.py); 1 test is a deliberate real bug.
- Baselines and the LLM use only history.json. Ground truth is used only by evaluate.py.
- Limitations: injected flakiness is the easy case; small test set; history is only 5 runs.
