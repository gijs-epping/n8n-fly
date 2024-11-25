WITH 
        -- Get all inkooporders for the SKU, ordered by delivery week
        backorder_availability AS (
            SELECT 
                productStandardIdentification as EAN,
                calculatedDeliveryWeek,
                SUM(amountBackorder) as amount,
                MIN(orderDate) as orderDate
            FROM inkooporders 
            WHERE productStandardIdentification = (
                SELECT EANCode 
                FROM currentstock 
                WHERE Artikelcode = "1-AT-MTAIR-V104" 
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
            WHERE Artikelcode = "1-AT-MTAIR-V104" 
        ),
        -- Calculate total open orders
        total_open_orders AS (
            SELECT 
                cs.EAN,
                SUM(o.NumberOrdered - ALESCE(o.NumberDelivered, 0)) as open_order_amount
            FROM open_orders o
            JOIN current_stock cs ON cs.SKU = o.ItemCode
            WHERE o.ItemCode = "1-AT-MTAIR-V104" 
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
                ) + COALESCE(cs.amount, 0) - OALESCE(too.open_order_amount, 0) as cumulative_availability
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
                ELSE 'Not enough stock/inkooporders'
            END as availability_status
        FROM running_availability
        ORDER BY calculatedDeliveryWeek;