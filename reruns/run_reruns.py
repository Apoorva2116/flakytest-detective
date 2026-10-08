"""Run the target repo's tests N times; save per-run pass/fail and failure messages.
Usage:
  python reruns/run_reruns.py --n 50 --out results/ground_truth.json   # ground truth (never shown to the AI)
  python reruns/run_reruns.py --n 5  --out results/history.json        # 'past CI history' (AI/baselines may use it)
"""
import argparse, json, os, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "target_repo")

def run_once():
    fd, xml = tempfile.mkstemp(suffix=".xml"); os.close(fd)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONHASHSEED"}
    subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider",
                    "--junitxml", xml], cwd=TARGET, env=env, capture_output=True)
    out = {}
    for tc in ET.parse(xml).getroot().iter("testcase"):
        name = tc.get("name")
        bad = tc.find("failure")
        if bad is None: bad = tc.find("error")
        out[name] = (0, (bad.get("message") or "")[:200]) if bad is not None else (1, "")
    os.remove(xml)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = {}
    for i in range(a.n):
        for name, (ok, msg) in run_once().items():
            d = data.setdefault(name, {"results": [], "msgs": []})
            d["results"].append(ok)
            if msg: d["msgs"].append(msg)
        print(f"run {i+1}/{a.n}", end="\r")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump({"n": a.n, "tests": data}, open(a.out, "w"), indent=1)
    print(f"\nsaved {a.out}")
