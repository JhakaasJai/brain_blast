import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("C:/coding/brain_blast/.env")
db_url = os.environ.get("DATABASE_URL")

try:
    with open("C:/coding/brain_blast/init.sql", "r") as f:
        sql = f.read()

    print("Connecting to Supabase...")
    if "?" not in db_url:
        db_url += "?sslmode=require"
    elif "sslmode" not in db_url:
        db_url += "&sslmode=require"
        
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Executing schema migration...")
    cursor.execute(sql)
    print("  PASS  Schema initialized.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
    raise
