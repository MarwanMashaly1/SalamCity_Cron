from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

class ConnectionPool:
    def __init__(self, db_config, time_to_sleep=30, test_run=False):
        self.username = db_config.get('user')
        self.password = db_config.get('password')
        self.host = db_config.get('host')
        self.port = int(db_config.get('port'))
        self.max_pool_size = 20
        self.test_run = test_run
        self.time_to_sleep = time_to_sleep
        self._initialize_pool()

    def get_initialized_connection_pool(self):
        return self.Session

    def _initialize_pool(self):
        self.engine = create_engine(f'mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/your_database',
                                    poolclass=QueuePool,
                                    pool_size=self.max_pool_size,
                                    max_overflow=0)
        self.Session = scoped_session(sessionmaker(bind=self.engine))