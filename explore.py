import pandas as pd
p0 = pd.read_pickle('matrix_0.pkl')
long_cols = []
for c in p0.columns:
	if len(c.split(' '))>1: long_cols.append(c)
for c in long_cols: print(c)