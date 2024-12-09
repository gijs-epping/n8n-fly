from fastapi import HTTPException
from .db import get_db_connection

def handle_get_debtor_orders(params):
    debtor_id = params[0].get("debtorid")
    if not debtor_id:
        raise HTTPException(status_code=400, detail="debtorid parameter is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                o.*,
                c.Omschrijving as ProductDescription,
                c.Voorraad as CurrentStock
            FROM open_orders o
            LEFT JOIN currentstock c ON o.ItemCode = c.EANCode
            WHERE o.Debtor = ?
            ORDER BY o.sysmodified DESC
        """, (debtor_id,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "data": results
        }
    finally:
        conn.close()
