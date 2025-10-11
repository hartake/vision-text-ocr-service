from dotenv import load_dotenv
import asyncpg
import os


# New constant for the table name, adhering to DRY principle
TABLE_NAME = "vision_text_ocr_results"


load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}"

# Global variable to hold the database connection pool
# It's good practice to use a connection pool in async applications
# to manage connections efficiently.
cached_db_pool = None

async def connect_to_db():
    """
    Establishes a connection pool to the PostgreSQL database.
    This function should be called once on application startup.
    """
    global cached_db_pool
    print("Connecting to database...")
    try:
        cached_db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("Database connection pool created.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        # In a real application, you might want to exit or retry.
        raise

async def close_db_connection():
    """
    Closes the PostgreSQL database connection pool.
    This function should be called once on application shutdown.
    """
    global cached_db_pool
    if cached_db_pool:
        print("Closing database connection pool...")
        await cached_db_pool.close()
        print("Database connection pool closed.")

async def create_db_table():
    """
    Creates the '{TABLE_NAME}' table in the database if it doesn't already exist.
    This ensures our schema is ready when the application starts.
    """
    print(f"Ensuring '{TABLE_NAME}' table exists...")
    async with cached_db_pool.acquire() as connection:
        # Ensure table creation is done within a transaction
        async with connection.transaction():
            await connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    extracted_text TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
    print(f"'{TABLE_NAME}' table verified/created.")
