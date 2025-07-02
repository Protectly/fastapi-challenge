from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Bug: Wrong database URL format will cause immediate connection error
engine = create_engine("postgresql://wrong:connection@localhost/nonexistent")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Bug: Missing database initialization function
def create_tables():
    Base.metadata.create_all(bind=engine)
