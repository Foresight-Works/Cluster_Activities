import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
from config import *

def build_create_table_statement(table_name, cols, cols_types):
    '''
    Build Create table statement with the cluster_key and types for each column
    :param table_name(str): The name of the table to create
    :param cols(list): Table column cluster_key
    :param cols_types: Column response types (postgres)
    '''
    statement_cols_types = ''
    for index, col in enumerate(cols):
        col = col.lower().replace(' ', '_').replace('%', 'perc')
        type = cols_types[index]
        col_type_str = '{c} {t},'.format(c=col, t=type)
        statement_cols_types += col_type_str
    statement_cols_types = statement_cols_types.rstrip(',')
    return "CREATE TABLE IF NOT EXISTS {tn} ({ct});".format(tn=table_name, ct=statement_cols_types)

def insert_into_table_statement(table_name, cols, cols_vals):
    '''
    Update table
    :param db_name(str): The name of the database to connect using the engine
    :param table_name(str): The name of the table to create
    :param cols(list): Table column cluster_key
    :param cols_vals(list): Column values
    '''
    cols_str, vals_str = "(", "("
    for index, col in enumerate(cols):
        val = cols_vals[index]
        #cols_str += "'{c}',".format(c=col)
        vals_str += "'{v}',".format(v=val)
        cols_str += "{c},".format(c=col)
        #vals_str += "{v},".format(v=val)
    cols_str = cols_str.rstrip(",")+")"
    vals_str = vals_str.rstrip(",")+")"
    return "INSERT INTO {tn} {cv} VALUES {vs}".format(tn=table_name, cv=cols_str, vs=vals_str)

