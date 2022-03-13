import pandas as pd
import numpy as np

# Create a DataFrame
df1 = {
	'Name': ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi'],
	'Math_score': [52, 87, 49, 74, 28, 59, 48]}

df1 = pd.DataFrame(df1, columns=['Name', 'Math_score'])

# Computing Cumulative Percentage
df1['cumsum'] = df1.Math_score.cumsum()
df1['cum_percent'] = 100 * (df1.Math_score.cumsum() / df1.Math_score.sum())
print(df1)
#####
duration_ratios = [1, 2, 3, 4]
out_sum = np.cumsum(duration_ratios)
print(out_sum)
sum_ratios = sum(duration_ratios)
print(sum_ratios)
ratios_cumsum = np.cumsum(duration_ratios)
ratios_cum_perc = 100 * (ratios_cumsum / sum_ratios)
print(ratios_cum_perc)