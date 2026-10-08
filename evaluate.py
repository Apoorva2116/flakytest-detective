"""Compare every method against ground truth. Flaky = fails some but not all of the 50 runs."""
import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "baselines"))
from baselines import load, rerun_once_rule, failed_in_history_rule

gt = load("results/ground_truth.json"); hist = load("results/history.json")
truth = {t for t, d in gt.items() if 0 < d["results"].count(0) < len(d["results"])}
always_fail = {t for t, d in gt.items() if d["results"].count(0) == len(d["results"])}

methods = {"rerun_once_rule": rerun_once_rule(hist), "failed_in_history_rule": failed_in_history_rule(hist)}
for f in sorted(glob.glob("results/llm_*.json")):      # written by rag/run_judge.py
    methods[os.path.basename(f)[4:-5]] = {t for t, v in json.load(open(f)).items() if v["flaky"]}

def prf(pred):
    tp = len(pred & truth); fp = len(pred - truth); fn = len(truth - pred)
    p = tp / (tp + fp) if tp + fp else 0.0; r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0), tp, fp, fn

print(f"tests={len(gt)}  truly flaky={len(truth)}  always-failing(real bugs)={sorted(always_fail)}\n")
print(f"{'method':32}{'prec':>6}{'rec':>6}{'F1':>6}{'TP':>4}{'FP':>4}{'FN':>4}")
rows = []
for name, pred in methods.items():
    p, r, f, tp, fp, fn = prf(pred); rows.append((name, p, r, f, tp, fp, fn))
    print(f"{name:32}{p:6.2f}{r:6.2f}{f:6.2f}{tp:4}{fp:4}{fn:4}")
print("\nFAILURE CASES")
for name, pred in methods.items():
    print(f"- {name}: false positives={sorted(pred - truth)} | missed={sorted(truth - pred)}")
json.dump({"truth": sorted(truth), "rows": rows}, open("results/metrics.json", "w"), indent=1)
