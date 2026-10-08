"""Two simple rules that use ONLY the short history (never the 50-run ground truth).
Return the set of test names each rule flags as flaky."""
import json

def load(path): return json.load(open(path))["tests"]

def rerun_once_rule(history):
    """Run 1 failed, rerun (run 2) passed -> flaky. What most CI tools do."""
    return {t for t, d in history.items() if d["results"][0] == 0 and d["results"][1] == 1}

def failed_in_history_rule(history):
    """Any failure in past runs -> flaky."""
    return {t for t, d in history.items() if 0 in d["results"]}
