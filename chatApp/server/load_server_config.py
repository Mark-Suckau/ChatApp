import json
from chatapp import path_util

def load_config():
  with open(path_util.get_file_path('server', 'server_config.json'), 'r') as server_config_json:
    server_config = json.load(server_config_json)
  
  return server_config
