from sqlmodel import SQLModel, create_engine, Session
from backend.config import settings
from sqlalchemy import event
import time

# Create engine with a longer timeout for local concurrency
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False, "timeout": 30}
)

# Enable WAL mode for better concurrency in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency to get a database session with basic retry logic for locks.
    """
    retries = 3
    while retries > 0:
        try:
            with Session(engine) as session:
                yield session
                break
        except Exception as e:
            if "database is locked" in str(e).lower() and retries > 1:
                retries -= 1
                time.sleep(0.5)
                continue
            raise e