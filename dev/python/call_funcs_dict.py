def funca(*args):
    x, y = args
    return(x+y)

def funcb(*args):
    x, y = args
    return(x*y)

param_func = {'a':funca(0,0), 'b':funcb(0,0)}
param = 'a'
if param == 'a': print(param_func[param](2, 3))

# -> TypeError: 'int' object is not callable
# search: place function in dictionary python (found some solutions)