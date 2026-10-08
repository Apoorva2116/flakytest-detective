# Test suite catalog (118 tests)

| Category | Count | Where |
|---|---|---|
| Flaky (injected) | 39 | test_flaky.py (10 original) + test_flaky_*.py + 3 readers in test_shared_state.py |
| Stable | 65 | test_stable.py (19) + test_stable_extra.py (25) + test_stable_lookalikes.py (18) + 3 "writer" tests in test_shared_state.py |
| Real bugs (fail every run) | 14 | test_bugs.py (13) + test_known_bug_mean_empty in test_stable.py |

## Flakiness types
random values, timing/deadlines, ordering assumptions (set/dict order, thread completion order),
wall-clock timestamps, random IDs/tokens, intermittent service failures, shared-state pollution,
concurrency races, resource availability (simulated).

## Built-in hard cases
- 7 flaky tests hide their nondeterminism inside services.py, so the test body looks innocent.
- 18 "lookalike" stable tests use random/threads/sleep/uuid/time safely (seeded RNG, join, locks, fixed dates).
  A judge that only keyword-matches will raise false alarms on these.
- 3 shared-state "writer" tests always pass but cause the following "reader" test to fail sometimes.
- Rarest flaky tests fail ~4-7% of runs (test_uuid_first_char, test_token_has_no_repeated_ff, test_gaussian_within_two_sigma).

## Limitations to state in the report
- Flakiness is injected, and several sources are simulated (service, pool, file handles).
- Ground truth = 200 reruns; a flaky test with a failure rate below ~1.5% could be labelled stable.
- Labels come from reruns on one machine (a VM); rates may differ elsewhere.
