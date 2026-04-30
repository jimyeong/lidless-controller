import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class BaseDB:
    def __init__(self, host, port, database, user, password):
        self.con_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }
        self.db_conn = None

    def connect(self):
        self.db_conn = psycopg2.connect(**self.con_params)
        return self

    def close(self):
        if self.db_conn and not self.db_conn.closed:
            self.db_conn.close()
    @contextmanager
    def cursor(self, dict_cursor=False):
        cursor_factory = RealDictCursor if dict_cursor else None
        cur = self.db_conn.cursor(cursor_factory=cursor_factory)
        try: 
            yield cur
        finally: 
            cur.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



class WriteDB(BaseDB):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def execute(self, query, params=None):
        if not self.db_conn or self.db_conn.closed:
            self.connect()
        with self.cursor() as cur:
            cur.execute(query, params)
            self.db_conn.commit()
            return cur.rowcount
    def execute_many(self, query, params=None):
        if not self.db_conn or self.db_conn.closed:
            self.connect()
        with self.cursor() as cur:
            cur.executemany(query, params)
            self.db_conn.commit()
            return cur.rowcount


class ReadDB(BaseDB):
    def fetch_one(self, query, params=None, dict_cursor=True):
        if not self.db_conn or self.db_conn.closed:
            self.connect()
        with self.cursor(dict_cursor=dict_cursor) as cur:
            cur.execute(query, params)
            return cur.fetchone()



