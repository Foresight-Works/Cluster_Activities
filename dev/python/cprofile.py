import cProfile
import numpy as np
def mul(x):
    return x*2

def plus(x):
    return x+2


pr = cProfile.Profile()
pr.enable()
a = np.arange(1,100)
for n in a:
    b = mul(a)
for n in a:
    c = plus(a)


pr.disable()
pr.print_stats(sort='time')