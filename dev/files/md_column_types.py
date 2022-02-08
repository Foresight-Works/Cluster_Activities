import pandas as pd
import re
df = pd.read_csv('../../data/raw_data/CCGT_CSV/CCGT D1.csv')
print(df.dtypes)
# cols = df.columns
# cid = [c for c in cols if re.findall('ID', c)]
# cols_types = {}
# df = df.drop(cid, axis=1)
# cols = df.columns
# float_cols = [c for c in cols if df[c].dtypes == float]
# print(df[float_cols].head())
#
# for c in cols:
#     if c in float_cols:
#         cols_types[c] = float
#     # elif any(y in c for y in['Start', 'Finish']):
#     #     cols_types[c] = datetime64[ns]
#
#     elif c in cid:
#         if any(y in c for y in['ID', 'Resource IDs']):
#             cols_types[c] = str
#         else:
#             cols_types[c] = int
#
# cols = [c for c in cols if c not in cols_types.keys()]
# df = df[cols]
# print(df.dtypes)
# dt_cols = [c for c in cols if any(y in c for y in['Start', 'Finish'])]
# print(df[dt_cols])
# df = df[dt_cols]
# for c in dt_cols:
#     df[c]= pd.to_datetime(df[c])
#
# print(df)
# print(df.dtypes)