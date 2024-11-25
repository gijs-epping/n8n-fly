import sqlite3
import pandas as pd
import os

def ensure_table_exists(conn):
    """Create the currentstock table if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currentstock (
            Artikelcode TEXT PRIMARY KEY,
            EANCode TEXT,
            Assortiment TEXT,
            Omschrijving TEXT,
            Voorraad INTEGER
        )
    """)
    conn.commit()

def import_stock():
    """Import stock data from CSV into SQLite database"""
    try:
        # Use the persistent storage path
        db_path = '/home/node/.n8n/database/onewaybike.db'

        # Create database connection
        conn = sqlite3.connect(db_path)
        
        # Ensure table exists
        ensure_table_exists(conn)
        
        # Use persistent storage for data files
        csv_path = '/home/node/.n8n/python/data/plankvoorraad.csv'
        if not os.path.exists(csv_path):
            print(f"Warning: CSV file not found at {csv_path}")
            return
            
        # Read CSV in chunks and insert into database
        chunk_size = 1000  # Process 1000 rows at a time
        for chunk in pd.read_csv(csv_path, 
                               sep=';', 
                               chunksize=chunk_size,
                               encoding='utf-8',
                               dtype={'Voorraad': int}):  # Ensure Voorraad is read as integer
            
            # Convert chunk to list of tuples
            data = [tuple(x) for x in chunk.values]
            
            # Insert data with REPLACE to handle duplicates
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO currentstock 
                (Artikelcode, EANCode, Assortiment, Omschrijving, Voorraad)
                VALUES (?, ?, ?, ?, ?)
                """, 
                data
            )
            conn.commit()
            print(f"Processed {len(data)} records...")
            
        print("Stock import completed successfully")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import_stock()
