from fastapi import HTTPException
from .db import get_db_connection

def handle_get_recent_orders(params):
    limit = int(params[0].get("limit", 10))
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                OrderNumber,
                YourReference,
                PackingSlipNumber,
                Debtor,
                ItemCode,
                NumberOrdered,
                NumberDelivered,
                OrderStatus,
                ShipmentStatus,
                sysmodified
            FROM open_orders 
            ORDER BY sysmodified DESC 
            LIMIT ?
        """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "data": results
        }
    finally:
        conn.close()
