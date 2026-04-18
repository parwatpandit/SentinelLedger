from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Your database credentials
DB_USER = "root"
DB_PASSWORD = "Maninblack90"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "sentinelledger"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()