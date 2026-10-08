"""REAL bugs: deterministic failures (not flaky)."""
import buggy

def test_bug_fib_ten(): assert buggy.fib(10) == 55
def test_bug_palindrome_sentence(): assert buggy.is_palindrome("A man a plan a canal Panama")
def test_bug_reverse_words(): assert buggy.reverse_words("a b c") == "c b a"
def test_bug_percent_zero_total(): assert buggy.percent(5, 0) == 0.0
def test_bug_last_two_items(): assert buggy.last_n([1, 2, 3], 2) == [2, 3]
def test_bug_leap_year_1900(): assert not buggy.is_leap(1900)
def test_bug_gcd_twelve_eight(): assert buggy.gcd(12, 8) == 4
def test_bug_median_even_length(): assert buggy.median([1, 3, 2, 4]) == 2.5
def test_bug_word_count_double_space(): assert buggy.word_count("a  b") == 2
def test_bug_parse_thousands(): assert buggy.parse_int("1,000") == 1000
def test_bug_max_subarray_negatives(): assert buggy.max_subarray([-3, -1, -2]) == -1
def test_bug_binary_search_last(): assert buggy.binary_search([1, 3, 5, 7], 7) == 3
def test_bug_celsius_boiling(): assert buggy.celsius_to_f(100) == 212
