from fastapi import HTTPException
from .db import get_db_connection

def handle_get_delivery_time_order(params):
    order_id = params[0].get("orderid")
    if not order_id:
        raise HTTPException(status_code=400, detail="orderid parameter is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            WITH 
            order_lines AS (
                SELECT 
                    o.OrderNumber,
                    o.ItemCode,
                    o.NumberOrdered - COALESCE(o.NumberDelivered, 0) as open_amount,
                    cs.EANCode as EAN
                FROM open_orders o
                JOIN currentstock cs ON cs.Artikelcode = o.ItemCode
                WHERE o.OrderNumber = ?
            ),
            backorder_availability AS (
                SELECT 
                    b.productStandardIdentification as EAN,
                    b.calculatedDeliveryWeek,
                    SUM(b.amountBackorder) as amount,
                    MIN(b.orderDate) as orderDate
                FROM backorders b
                JOIN order_lines ol ON ol.EAN = b.productStandardIdentification
                GROUP BY b.productStandardIdentification, b.calculatedDeliveryWeek
            ),
            current_stock AS (
                SELECT 
                    cs.EANCode as EAN,
                    cs.Artikelcode as SKU,
                    cs.Voorraad as amount
                FROM currentstock cs
                JOIN order_lines ol ON ol.ItemCode = cs.Artikelcode
            ),
            total_open_orders AS (
                SELECT 
                    cs.EANCode as EAN,
                    SUM(o.NumberOrdered - COALESCE(o.NumberDelivered, 0)) as open_order_amount
                FROM open_orders o
                JOIN currentstock cs ON cs.Artikelcode = o.ItemCode
                JOIN order_lines ol ON ol.ItemCode = o.ItemCode
                GROUP BY cs.EANCode
            ),
            running_availability AS (
                SELECT 
                    ba.EAN,
                    ba.calculatedDeliveryWeek,
                    ba.amount as backorder_amount,
                    cs.amount as current_stock,
                    COALESCE(too.open_order_amount, 0) as total_open_orders,
                    ol.OrderNumber,
                    ol.ItemCode,
                    ol.open_amount as order_line_amount,
                    SUM(ba.amount) OVER (
                        PARTITION BY ba.EAN 
                        ORDER BY ba.calculatedDeliveryWeek
                    ) + COALESCE(cs.amount, 0) - COALESCE(too.open_order_amount, 0) as cumulative_availability
                FROM backorder_availability ba
                LEFT JOIN current_stock cs ON ba.EAN = cs.EAN
                LEFT JOIN total_open_orders too ON ba.EAN = too.EAN
                JOIN order_lines ol ON ol.EAN = ba.EAN
            )
            SELECT 
                OrderNumber,
                ItemCode,
                EAN,
                order_line_amount as ordered_amount,
                current_stock,
                total_open_orders as all_open_orders,
                backorder_amount as incoming_amount,
                calculatedDeliveryWeek as estimated_delivery_week,
                cumulative_availability,
                CASE 
                    WHEN current_stock >= order_line_amount THEN 'Available from stock'
                    WHEN cumulative_availability >= 0 THEN 'Available in week ' || calculatedDeliveryWeek
                    ELSE 'Not enough stock/backorders'
                END as availability_status
            FROM running_availability
            WHERE cumulative_availability >= order_line_amount
               OR calculatedDeliveryWeek = (
                   SELECT MAX(calculatedDeliveryWeek) 
                   FROM running_availability r2 
                   WHERE r2.EAN = running_availability.EAN
               )
            ORDER BY OrderNumber ASC, ItemCode ASC, calculatedDeliveryWeek ASC
        """, (order_id,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No delivery time information found for order {order_id}")
        
        return {
            "status": "success",
            "data": results
        }
    finally:
        conn.close()
