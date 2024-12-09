import sqlite3
import pandas as pd

def import_stock():
    """Import stock data from CSV into SQLite database"""
    try:
        # Create database connection
        conn = sqlite3.connect('database/backorders.db')
        
        # Read CSV in chunks and insert into database
        chunk_size = 1000  # Process 1000 rows at a time
        for chunk in pd.read_csv('data/plankvoorraad.csv', 
                               sep=';', 
                               chunksize=chunk_size,
                               encoding='utf-8',
                               dtype={'Voorraad': int}):  # Ensure Voorraad is read as integer
            
            # Convert chunk to list of tuples
            data = [tuple(x) for x in chunk.values]
            print(f"Processed {data} records...")
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
