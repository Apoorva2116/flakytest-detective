def square(x): return x * x
def is_even(n): return n % 2 == 0
def sign(x): return (x > 0) - (x < 0)
def factorial(n):
    r = 1
    for i in range(2, n + 1): r *= i
    return r
def gcd(a, b):
    while b: a, b = b, a % b
    return a
def lcm(a, b): return a * b // gcd(a, b)
def is_prime(n):
    if n < 2: return False
    return all(n % i for i in range(2, int(n ** 0.5) + 1))
def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
