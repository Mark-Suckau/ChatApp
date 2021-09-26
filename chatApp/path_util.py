import os

base_path = os.path.abspath(os.path.dirname(__file__))

def get_data_path(relative_path):
    data_dir = os.path.join(base_path, relative_path + os.sep)
    return data_dir