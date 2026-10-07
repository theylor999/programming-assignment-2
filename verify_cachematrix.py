"""Python mirror of cachematrix.R, used to check the caching logic.

R is not installed on the machine where this was written, so the same logic
(closure + cached inverse + invalidation on set) is reproduced here with numpy.
Each function maps one-to-one to the R code:
    make_cache_matrix  <->  makeCacheMatrix
    cache_solve        <->  cacheSolve
"""
import time
import numpy as np


def make_cache_matrix(x):
    inv = None

    def set_(y):
        nonlocal x, inv
        x = y
        inv = None

    def get():
        return x

    def set_inverse(i):
        nonlocal inv
        inv = i

    def get_inverse():
        return inv

    return {"set": set_, "get": get, "setinverse": set_inverse, "getinverse": get_inverse}


def cache_solve(m):
    inv = m["getinverse"]()
    if inv is not None:
        print("getting cached data")
        return inv
    data = m["get"]()
    inv = np.linalg.inv(data)
    m["setinverse"](inv)
    return inv


if __name__ == "__main__":
    rng = np.random.default_rng(2026)
    n = 1000
    # Diagonally dominant matrix => always invertible
    a = rng.standard_normal((n, n)) + n * np.eye(n)
    m = make_cache_matrix(a)

    t0 = time.perf_counter()
    i1 = cache_solve(m)
    t1 = time.perf_counter()
    i2 = cache_solve(m)  # must print "getting cached data"
    t2 = time.perf_counter()

    print(f"matrix size                : {n}x{n}")
    print(f"first call (computes)      : {t1 - t0:.4f} s")
    print(f"second call (from cache)   : {t2 - t1:.6f} s")
    print(f"same object returned       : {i1 is i2}")
    print(f"max |A %*% inv(A) - I|     : {np.abs(a @ i1 - np.eye(n)).max():.3e}")
    print(f"inverse[1,1], inverse[2,3] : {i1[0, 0]:.10f}, {i1[1, 2]:.10f}")

    # Changing the matrix with set() must invalidate the cache
    b = rng.standard_normal((n, n)) + n * np.eye(n)
    m["set"](b)
    print(f"cache after set()          : {m['getinverse']() is None}")
    i3 = cache_solve(m)
    print(f"new inverse correct        : {np.allclose(b @ i3, np.eye(n))}")
    print(f"new inverse != old inverse : {not np.allclose(i3, i1)}")
    cache_solve(m)  # cached again
