import numpy as np
from scipy import stats
b = [[2,2,2], [4,4,4],[6,6,6]]
stacked = np.stack(b)
print('stacked:\n', stacked)
print(stacked.shape, type(stacked))
print('z-scored:\n', stats.zscore(stacked, axis=0))

