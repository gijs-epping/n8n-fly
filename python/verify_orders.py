import sqlite3
import json

def verify_orders():
    conn = sqlite3.connect('../.n8n/database/onewaybike.db')
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM open_orders')
    count = cursor.fetchone()[0]
    print(f'Total open orders: {count}')
    
    # Get sample record
    cursor.execute('SELECT * FROM open_orders LIMIT 1')
    columns = [description[0] for description in cursor.description]
    row = cursor.fetchone()
    
    if row:
        print('\nSample record:')
        record = {columns[i]: row[i] for i in range(len(columns))}
        print(json.dumps(record, indent=2))
    
    conn.close()

if __name__ == '__main__':
    verify_orders()
