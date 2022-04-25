d1={1:2,3:4}
d2={5:6,7:9}
d3={10:8,13:22, 5:7}
d4 = {**d1, **d2, **d3}
print(d4)

from functools import reduce
#collection = [{'hello': 1}, {'world': 2}]
collection = [d1, d2, d3]
answer = reduce(lambda aggr, new: aggr.update(new) or aggr, collection, {})
print(answer)