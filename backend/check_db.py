
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL not found in .env")
    exit(1)

engine = create_engine(database_url)
inspector = inspect(engine)

if "bot_sessions" in inspector.get_table_names():
    print("Table 'bot_sessions' exists.")
    columns = inspector.get_columns("bot_sessions")
    for column in columns:
        print(f"Column: {column['name']}, Type: {column['type']}")
else:
    print("Table 'bot_sessions' does not exist.")
