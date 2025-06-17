def fib_it_py(n):
    x, y = 0, 1
    for _ in range(1, n + 1):
        x, y = y, x + y
    return x