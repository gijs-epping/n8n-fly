import sqlite3

def print_schema():
    try:
        conn = sqlite3.connect('database/backorders.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Database Tables:")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            # Get schema for each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print_schema()
