from fastapi import HTTPException
from .db import get_db_connection

def handle_get_delivery_time_product(params):
    product_number = params[0].get("product_number")
    if not product_number:
        raise HTTPException(status_code=400, detail="productnumber parameter is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            WITH 
                -- Get all backorders for the SKU, ordered by delivery week
                backorder_availability AS (
                    SELECT 
                        productStandardIdentification as EAN,
                        calculatedDeliveryWeek,
                        SUM(amountBackorder) as amount,
                        MIN(orderDate) as orderDate
                    FROM backorders 
                    WHERE productStandardIdentification = (
                        SELECT EANCode 
                        FROM currentstock 
                        WHERE Artikelcode = ?
                    )
                    GROUP BY productStandardIdentification, calculatedDeliveryWeek
                ),
                -- Calculate current stock
                current_stock AS (
                    SELECT 
                        EANCode as EAN,
                        Artikelcode as SKU,
                        Voorraad as amount
                    FROM currentstock
                    WHERE Artikelcode = ?
                ),
                -- Calculate total open orders
                total_open_orders AS (
                    SELECT 
                        cs.EAN,
                        SUM(o.NumberOrdered - COALESCE(o.NumberDelivered, 0)) as open_order_amount
                    FROM open_orders o
                    JOIN current_stock cs ON cs.SKU = o.ItemCode
                    WHERE o.ItemCode = ?
                    GROUP BY cs.EAN
                ),
                -- Running total of availability by delivery week
                running_availability AS (
                    SELECT 
                        ba.EAN,
                        ba.calculatedDeliveryWeek,
                        ba.amount as backorder_amount,
                        cs.amount as current_stock,
                        COALESCE(too.open_order_amount, 0) as open_orders,
                        SUM(ba.amount) OVER (
                            PARTITION BY ba.EAN 
                            ORDER BY ba.calculatedDeliveryWeek
                        ) + COALESCE(cs.amount, 0) - COALESCE(too.open_order_amount, 0) as cumulative_availability
                    FROM backorder_availability ba
                    LEFT JOIN current_stock cs ON ba.EAN = cs.EAN
                    LEFT JOIN total_open_orders too ON ba.EAN = too.EAN
                )
                SELECT 
                    EAN,
                    calculatedDeliveryWeek as estimated_delivery_week,
                    backorder_amount,
                    current_stock,
                    open_orders,
                    cumulative_availability,
                    CASE 
                        WHEN current_stock > open_orders THEN 'Available from stock'
                        WHEN cumulative_availability > 0 THEN 'Available in week ' || calculatedDeliveryWeek
                        ELSE 'Not enough stock/backorders'
                    END as availability_status
                FROM running_availability
                ORDER BY calculatedDeliveryWeek;
        """, (product_number,product_number,product_number,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No delivery time information found for product {product_number}")
        
        return {
            "status": "success",
            "data": results
        }
    finally:
        conn.close()
