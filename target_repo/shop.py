"""Tiny shop module: the code under test."""

def add(a, b): return a + b
def total(prices): return sum(prices)
def discount(price, pct): return round(price * (1 - pct / 100), 2)
def is_adult(age): return age >= 18
def slugify(s): return s.strip().lower().replace(" ", "-")
def first(items): return items[0] if items else None
def cap(s): return s[:1].upper() + s[1:]
def clamp(x, lo, hi): return max(lo, min(hi, x))
def mean(xs): return sum(xs) / len(xs)
def unique_sorted(xs): return sorted(set(xs))
def apply_tax(price, rate=0.18): return round(price * (1 + rate), 2)
