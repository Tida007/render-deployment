"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# If running locally, use the default local database
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:@localhost:3306/bincom_polling"
    load_dotenv()  # Load .env file for local development

# Handle special characters in password for Render's database URL
if DATABASE_URL and DATABASE_URL.startswith('mysql'):
    # Parse the URL to handle special characters in password
    parsed_url = urllib.parse.urlparse(DATABASE_URL)
    if parsed_url.password:
        # Rebuild the URL with proper encoding
        safe_password = urllib.parse.quote_plus(parsed_url.password)
        netloc = f"{parsed_url.username}:{safe_password}@{parsed_url.hostname}"
        if parsed_url.port:
            netloc += f":{parsed_url.port}"
        DATABASE_URL = urllib.parse.urlunparse(parsed_url._replace(netloc=netloc))

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

