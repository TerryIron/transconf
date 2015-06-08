__author__ = 'chijun'


from sqlalchemy import create_engine

class Database(object):
    def __init__(self, engine_url):
        self.engine = create_engine(engine_url)
