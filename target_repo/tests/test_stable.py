from shop import *

def test_add(): assert add(2, 3) == 5
def test_add_negative(): assert add(-1, 1) == 0
def test_total(): assert total([1, 2, 3]) == 6
def test_total_empty(): assert total([]) == 0
def test_discount(): assert discount(100, 10) == 90.0
def test_discount_zero(): assert discount(50, 0) == 50.0
def test_is_adult_true(): assert is_adult(18)
def test_is_adult_false(): assert not is_adult(17)
def test_slugify(): assert slugify(" Hello World ") == "hello-world"
def test_first(): assert first([4, 5]) == 4
def test_first_empty(): assert first([]) is None
def test_cap(): assert cap("abc") == "Abc"
def test_clamp_low(): assert clamp(-5, 0, 10) == 0
def test_clamp_high(): assert clamp(50, 0, 10) == 10
def test_mean(): assert mean([2, 4]) == 3
def test_unique_sorted(): assert unique_sorted([3, 1, 3, 2]) == [1, 2, 3]
def test_apply_tax(): assert apply_tax(100) == 118.0
def test_total_floats(): assert round(total([0.5, 0.25]), 2) == 0.75
def test_slugify_spaces(): assert slugify("a b c") == "a-b-c"

def test_known_bug_mean_empty():
    # A REAL, consistent failure (not flaky): mean([]) divides by zero.
    assert mean([]) == 0
