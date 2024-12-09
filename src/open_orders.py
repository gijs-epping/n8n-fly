import requests
import sqlite3
import hashlib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenOrdersAPI:
    def __init__(self):
        self.base_url = 'https://integrationgateway.onewaybike.nl/V1/012/Sales/CSOrder'
        self.token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOiIxNjc3ODUzMzI3IiwiaXNzIjoiaW50ZWdyYXRpb25nYXRld2F5Lm9uZXdheWJpa2UubmwiLCJhdWQiOiJpbnRlZ3JhdGlvbmdhdGV3YXkub25ld2F5YmlrZS5ubCIsImV4cCI6IjQxMDIzNTQ4MDAiLCJqdGkiOiI2NjY4MzVkOC01MmY1LTQwZGQtYjhjZi01ZDc4OGY1MmU3NzAiLCJzdWIiOiJzaG9wd29ya3MifQ.Xyn6NWYFshnHPP3tUk-hjda3bigVPYdzaRVmIeKsW3k'
        self.db_path = 'database/backorders.db'
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with required schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS open_orders (
                id TEXT PRIMARY KEY,
                OrderNumber TEXT,
                YourReference TEXT,
                PackingSlipNumber TEXT,
                Debtor TEXT,
                ItemCode TEXT,
                NumberOrdered REAL,
                NumberDelivered REAL,
                OrderStatus TEXT,
                ShipmentReference TEXT,
                TrackTraceCode TEXT,
                TrackTraceUrl TEXT,
                ShipmentStatus TEXT,
                sysmodified TEXT,
                syscreator INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_open_orders(self):
        """Fetch open orders from API"""
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        params = {
            '$filter': "OrderStatus eq 'V' and ShipmentStatus ne 'DONE'"
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch open orders: {str(e)}")
            raise

    def generate_unique_id(self, order_number, item_code):
        """Generate MD5 hash from order number and item code"""
        unique_string = f"{order_number}{item_code}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def store_open_orders(self, orders_data):
        """Store open orders data in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for order in orders_data.get('d', {}).get('results', []):
            try:
                # Generate unique ID using MD5 hash
                unique_id = self.generate_unique_id(order['OrderNumber'], order['ItemCode'])
                
                cursor.execute('''
                    INSERT OR REPLACE INTO open_orders 
                    (id, OrderNumber, YourReference, PackingSlipNumber, Debtor,
                    ItemCode, NumberOrdered, NumberDelivered, OrderStatus,
                    ShipmentReference, TrackTraceCode, TrackTraceUrl,
                    ShipmentStatus, sysmodified, syscreator)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    unique_id,
                    order['OrderNumber'],
                    order['YourReference'],
                    order['PackingSlipNumber'],
                    order['Debtor'],
                    order['ItemCode'],
                    order['NumberOrdered'],
                    order['NumberDelivered'],
                    order['OrderStatus'],
                    order['ShipmentReference'],
                    order['TrackTraceCode'],
                    order['TrackTraceUrl'],
                    order['ShipmentStatus'],
                    order['sysmodified'],
                    order['syscreator']
                ))
            except Exception as e:
                logger.error(f"Error storing order {order.get('OrderNumber')}: {str(e)}")
                continue

        conn.commit()
        conn.close()
        logger.info("Successfully stored open orders in database")

    def sync_open_orders(self):
        """Fetch and store open orders data"""
        try:
            orders = self.get_open_orders()
            self.store_open_orders(orders)
            logger.info("Successfully synchronized open orders")
        except Exception as e:
            logger.error(f"Failed to sync open orders: {str(e)}")
            raise

def main():
    api = OpenOrdersAPI()
    api.sync_open_orders()

if __name__ == "__main__":
    main()
