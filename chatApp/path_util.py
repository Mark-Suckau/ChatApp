import os

base_path = os.path.abspath(os.path.dirname(__file__))

# adds project dir to relative path
def get_dir_path(relative_dir_path):
    folder_dir = os.path.join(base_path, relative_dir_path + os.sep)
    return folder_dir

# adds project dir to relative path
def get_file_path(relative_dir_path, file_name):
    file_dir = os.path.join(get_dir_path(relative_dir_path), file_name)
    return file_dir
