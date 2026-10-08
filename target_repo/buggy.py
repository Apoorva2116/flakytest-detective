"""Functions with REAL, deterministic bugs. Their tests fail on every run."""
def fib(n):                       # wrong start values
    a, b = 1, 2
    for _ in range(n - 1): a, b = b, a + b
    return a
def is_palindrome(s): return s == s[::-1]                 # ignores case/spaces
def reverse_words(s): return " ".join(s.split())          # forgot to reverse
def percent(part, total): return part / total * 100       # no zero check
def last_n(items, n): return items[-(n - 1):]             # off by one
def is_leap(y): return y % 4 == 0                         # ignores century rule
def gcd(a, b): return min(a, b)                           # wrong algorithm
def median(xs):
    s = sorted(xs)
    return s[len(s) // 2]                                 # wrong for even length
def word_count(s): return len(s.split(" "))               # breaks on double spaces
def parse_int(s): return int(s)                           # fails on "1,000"
def max_subarray(xs):
    best = cur = 0                                        # wrong when all negative
    for x in xs:
        cur = max(0, cur + x); best = max(best, cur)
    return best
def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo < hi:                                        # should be <=
        mid = (lo + hi) // 2
        if a[mid] == target: return mid
        if a[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
def celsius_to_f(c): return c * 1.7 + 32                  # wrong factor
