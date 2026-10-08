import mathutil, textutil
from inventory import Inventory

def test_square_of_four(): assert mathutil.square(4) == 16
def test_is_even_true(): assert mathutil.is_even(10)
def test_is_even_false(): assert not mathutil.is_even(7)
def test_factorial_five(): assert mathutil.factorial(5) == 120
def test_factorial_zero(): assert mathutil.factorial(0) == 1
def test_sign_negative(): assert mathutil.sign(-9) == -1
def test_gcd_twelve_eight(): assert mathutil.gcd(12, 8) == 4
def test_lcm_four_six(): assert mathutil.lcm(4, 6) == 12
def test_prime_seven(): assert mathutil.is_prime(7)
def test_fib_ten(): assert mathutil.fib(10) == 55

def test_reverse_abc(): assert textutil.reverse("abc") == "cba"
def test_palindrome_racecar(): assert textutil.is_palindrome("Racecar")
def test_palindrome_hello_false(): assert not textutil.is_palindrome("hello")
def test_vowels_in_education(): assert textutil.count_vowels("education") == 5
def test_title_case_words(): assert textutil.title_case("hello world") == "Hello World"
def test_truncate_three(): assert textutil.truncate("abcdef", 3) == "abc"
def test_word_count_double_space(): assert textutil.word_count("a  b") == 2
def test_strip_punctuation(): assert textutil.strip_punct("hi, there!") == "hi there"

def test_inventory_add():
    inv = Inventory(); inv.add("pen", 3)
    assert inv.items["pen"] == 3
def test_inventory_remove_ok():
    inv = Inventory(); inv.add("pen", 3)
    assert inv.remove("pen", 2) and inv.items["pen"] == 1
def test_inventory_remove_too_many():
    inv = Inventory(); inv.add("pen", 1)
    assert inv.remove("pen", 5) is False
def test_inventory_total():
    inv = Inventory(); inv.add("a", 2); inv.add("b", 3)
    assert inv.total() == 5
def test_inventory_empty_total(): assert Inventory().total() == 0
def test_inventory_add_twice():
    inv = Inventory(); inv.add("pen"); inv.add("pen")
    assert inv.items["pen"] == 2
def test_inventory_snapshot_is_copy():
    inv = Inventory(); inv.add("pen")
    snap = inv.snapshot(); snap["pen"] = 99
    assert inv.items["pen"] == 1
