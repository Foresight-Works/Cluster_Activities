import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor

def mul_div(num, action):
  result = 0
  if action == 'div':
      #print(num, action, num / 2)
      result = num/2
  elif action == 'mul':
      result = num*2
  return result

def apply(L, f, action):
    """
    Applies function given by f to each element in L
    Parameters
    ----------
    L : list containing the operands
    f : A function to apply
    Returns
    -------
    result: resulting list
    """

    result = []
    for i in range(len(L)):
        result.append(f(L[i], action))

    return result

L = list(np.arange(1, 1e6))
#print(apply(L, mul_div, 'div'))

def run(action, data, num_executors):
    executor = ProcessPoolExecutor(num_executors)
    results = []
    action_list = len(data) * [action]
    print('action_list:', action_list[:10])
    print(len(data), len(action_list))
    start = time.time()
    if num_executors > 1:
        for result in executor.map(mul_div, data, action_list):
            results.append(result)
        executor.shutdown()
    else:
        for result in map(mul_div, data, action_list):
            results.append(result)
    print('results:', results[1:200])
    print('processes = {s} seconds'.format(s=time.time()-start))
#result=list(map(Multiply,lst1,lst2,lst3))
num_executors = 4
action = 'div'
run(action, L, num_executors)