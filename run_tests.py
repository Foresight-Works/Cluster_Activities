import os
import sys
import ast
import inspect

import pandas as pd
modules_dir = './modules'
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

def get_functions_modules(modules_dir):
    # Extract and write modules paths: modules_paths.xlsx
    function_modules = {}
    for path, subdirs, file_names in os.walk(modules_dir):
        for file_name in file_names:
            if (('cpython' not in file_name) & ('libraries' not in file_name)):
                name = file_name.replace('.py', '')
                #print(name, path, modules_dir)
                if path == modules_dir:
                    module_dir_name = name
                else:
                    subdir = path.split('modules')[1][1:]
                    module_dir_name = '{s}.{n}'.format(s=subdir, n=name)
    
                file_path = os.path.join(path, file_name)
                source = open(file_path, encoding='utf8').read()
                functions = [f.name for f in ast.parse(source).body
                             if isinstance(f, ast.FunctionDef)]
                if functions:
                    for function in functions:
                        function_modules[function] = module_dir_name
    return function_modules
function_modules = get_functions_modules(modules_dir)
function_names = list(function_modules.keys())
modules_dirs = list(function_modules.values())
for module_action in modules_dirs:
    exec('from {m} import *'.format(m=module_action))
print('test function_names:', function_names)
tests_data_path = '/home/rony/Projects_Code/Cluster_Activities/data/tests'
tests_results_path = '/home/rony/Projects_Code/Cluster_Activities/data/tests/results'
for function_name in function_names:
    function = locals()[function_name]
    func_args = list(inspect.signature(function).parameters.keys())
    print(90 * '=')
    print(print('name: {n}\narguments: {a}'.format(n=function_name, a=func_args)))
    if 'test' in func_args:
        test_file = inspect.signature(function).parameters['test'].default
        test_file_type = test_file.split('.')[1]
        print('test_file:', test_file, test_file_type)
        if test_file_type == 'txt':
            data = open(os.path.join(tests_data_path, test_file)).read().split('\n')
            data = [i for i in data if i]
            result = function(data, unique=True, exclude_stopwords=True)
            if type(result[0]) == list:
                print('result composed of lists')
                result = [', '.join(i) for i in result]
            result = '\n'.join(result)
            results_file = '{n}.{t}'.format(n=function_name, t=test_file_type)
            with open(os.path.join(tests_results_path, results_file), 'w') as f: f.write(result)