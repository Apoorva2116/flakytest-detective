def reverse(s): return s[::-1]
def is_palindrome(s):
    t = "".join(c.lower() for c in s if c.isalnum())
    return t == t[::-1]
def count_vowels(s): return sum(c in "aeiouAEIOU" for c in s)
def title_case(s): return s.title()
def truncate(s, n): return s[:n]
def word_count(s): return len(s.split())
def strip_punct(s): return "".join(c for c in s if c.isalnum() or c.isspace())
