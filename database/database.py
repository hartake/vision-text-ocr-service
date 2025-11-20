from dotenv import load_dotenv
import asyncpg
import os


TABLE_NAME = "vision_text_ocr_results"


load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST", "localhost")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

cached_db_pool = None

async def connect_to_db():
    global cached_db_pool
    print("Connecting to database...")
    try:
        cached_db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("Database connection pool created.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        raise

async def close_db_connection():
    global cached_db_pool
    if cached_db_pool:
        print("Closing database connection pool...")
        await cached_db_pool.close()
        print("Database connection pool closed.")

async def create_db_table():
    print(f"Ensuring tables exist...")
    async with cached_db_pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    extracted_text TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS vision_text_feedback (
                    id SERIAL PRIMARY KEY,
                    comment TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
    print(f"Tables verified/created.")
