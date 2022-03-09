import numpy as np
import ast
message = np.load('msg.npy', allow_pickle=True)[()]
print(type(message))
message = str(message)
# print(type(message))
# print(message)
data3 = ast.literal_eval(message)
#print(data3)
print(type(data3))