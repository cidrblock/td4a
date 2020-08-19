""" filter loader helper
"""
import os
import sys
import importlib
import ansible.plugins.filter as apf

def load_dir(directory):
    """ Load jinja filters in ansible format
    """
    filter_list = []
    sys.path.append(directory)
    for entry in os.listdir(directory):
        if entry != '__init__.py' and entry.split('.')[-1] == 'py':
            filters = importlib.import_module(entry[:-3]).FilterModule().filters()
            for key, value in filters.items():
                filter_list.append((key, value))
    return filter_list

def filters_load(custom_filters):
    """ load the filters
    """
    filters = []
    filters.extend(load_dir(os.path.dirname(apf.__file__)))
    if custom_filters:
        filters.extend(load_dir(custom_filters))
    return filters
