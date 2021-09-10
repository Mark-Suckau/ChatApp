import psycopg2

class DB_Connector:
  def __init__(self, host, port, dbname, username, password):
    self.conn = psycopg2.connect(host=host, port=port, dbname=dbname, username=username, password=password)
  