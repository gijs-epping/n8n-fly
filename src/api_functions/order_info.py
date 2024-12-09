from fastapi import HTTPException
from .db import get_db_connection

def handle_get_order_info(params):
    order_id = params[0].get("orderid")
    if not order_id:
        raise HTTPException(status_code=400, detail="orderid parameter is required")
    
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
            WHERE o.OrderNumber = ?
        """, (order_id,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        
        return {
            "status": "success",
            "data": results
        }
    finally:
        conn.close()
