from numba import jit, cuda
import numpy as np
# to measure exec time
from timeit import default_timer as timer

#import code
#code.interact(local=locals)

# normal function to run on cpu
def func(a,n):
    for i in range(n):
        a[i] += 1

# function optimized to run on gpu
#@jit(target="cuda")
@jit
def func2(a, n):
    for i in range(n):
        a[i] += 1

n = 10000000
a = np.ones(n, dtype=np.float64)
b = np.ones(n, dtype=np.float32)

start = timer()
func(a, n)
print("numpy:", timer() - start)

start = timer()
func2(a, n)
print("jit compiler:", timer() - start)

a_gpu = cuda.to_device(a)
n_gpu = cuda.to_device(n)
start = timer()
func2(a_gpu, n_gpu)
print("GPU:", timer() - start)