"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

# Detect production environment (Render, Heroku, etc.)
IS_PRODUCTION = (
    os.getenv("RENDER") is not None or
    os.getenv("RENDER_EXTERNAL_HOSTNAME") is not None or
    os.getenv("DYNO") is not None or  # Heroku
    os.getenv("RAILWAY_ENVIRONMENT") is not None  # Railway
)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL in production
if IS_PRODUCTION:
    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is required in production. "
            "Please set it in your Render service environment variables."
        )
    # Prevent localhost connections in production
    if DATABASE_URL and "localhost" in DATABASE_URL.lower():
        raise ValueError(
            "Cannot use localhost database in production. "
            "Please configure an external database and set DATABASE_URL correctly."
        )
elif not DATABASE_URL:
    # Only use localhost fallback in local development
    DATABASE_URL = "mysql+pymysql://root:@localhost:3306/bincom_polling"
    load_dotenv()  # Load .env file for local development

# Handle special characters in password for database URL
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
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False  # Set to True for SQL query logging
    )
except Exception as e:
    raise ValueError(
        f"Failed to create database engine. Please check your DATABASE_URL. "
        f"Error: {str(e)}"
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
        # Extract connection details for error message (without password)
        if DATABASE_URL:
            try:
                parsed = urllib.parse.urlparse(DATABASE_URL)
                host_info = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
                db_name = parsed.path.lstrip('/') if parsed.path else "unknown"
                error_msg = (
                    f"Database connection error to {host_info}/{db_name}. "
                    f"Error: {str(e)}. "
                    f"Please verify DATABASE_URL is correct and database is accessible."
                )
            except:
                error_msg = f"Database connection error: {str(e)}"
        else:
            error_msg = f"Database connection error: {str(e)}. DATABASE_URL is not set."
        
        raise Exception(error_msg) from e
    finally:
        db.close()

