import requests
import sqlite3
import hashlib
import logging
import argparse
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenOrdersAPI:
    def __init__(self):
        self.base_url = 'https://integrationgateway.onewaybike.nl/V1/012/Sales/CSOrder'
        self.token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOiIxNjc3ODUzMzI3IiwiaXNzIjoiaW50ZWdyYXRpb25nYXRld2F5Lm9uZXdheWJpa2UubmwiLCJhdWQiOiJpbnRlZ3JhdGlvbmdhdGV3YXkub25ld2F5YmlrZS5ubCIsImV4cCI6IjQxMDIzNTQ4MDAiLCJqdGkiOiI2NjY4MzVkOC01MmY1LTQwZGQtYjhjZi01ZDc4OGY1MmU3NzAiLCJzdWIiOiJzaG9wd29ya3MifQ.Xyn6NWYFshnHPP3tUk-hjda3bigVPYdzaRVmIeKsW3k'
        self.db_path = '../.n8n/database/onewaybike.db'
        self._init_db()

    def normalize_timestamp(self, timestamp_str):
        """
        Normalize timestamps from different formats to a consistent ISO format.
        
        Args:
            timestamp_str (str): Timestamp string in either format:
                               - '2024-09-11T11:14:44.587'
                               - '2024-10-17T07:01:55 1'
        
        Returns:
            str: Normalized ISO format timestamp suitable for API queries
        
        Raises:
            ValueError: If the timestamp format is invalid or cannot be parsed
        """
        try:
            # Remove trailing '1' if present
            timestamp_str = timestamp_str.split(' ')[0]
            
            # Try parsing with milliseconds
            try:
                dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                # Try parsing without milliseconds
                dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
            
            # Return consistent ISO format
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
            
        except Exception as e:
            logger.error(f"Failed to normalize timestamp '{timestamp_str}': {str(e)}")
            raise ValueError(f"Invalid timestamp format: {timestamp_str}")

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
                EANCode TEXT,
                syscreator INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_open_orders(self, initial_skip=0, modified_after=None):
        """
        Fetch open orders from API with pagination and store immediately
        
        Args:
            initial_skip (int): Number of records to skip
            modified_after (str, optional): Fetch orders modified after this timestamp
        """
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        filter_conditions = ["OrderStatus eq 'V' and ShipmentStatus ne 'DONE'"]
        
        # Add timestamp filter if provided
        if modified_after:
            try:
                normalized_timestamp = self.normalize_timestamp(modified_after)
                filter_conditions.append(f"sysmodified gt '{normalized_timestamp}'")
            except ValueError as e:
                logger.error(f"Invalid modified_after timestamp: {str(e)}")
                raise

        base_params = {
            '$filter': " and ".join(filter_conditions),
            '$top': 500
        }

        total_processed = 0
        skip = initial_skip
        
        while True:
            params = {**base_params, '$skip': skip}
            try:
                logger.info(f"Fetching orders with skip={skip}")
                response = requests.get(self.base_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('d', {}).get('results', [])
                
                if not results:
                    break
                
                self.store_open_orders({'d': {'results': results}})
                
                total_processed += len(results)
                logger.info(f"Processed and stored {len(results)} orders (Total: {total_processed})")
                
                skip += 500
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch open orders at skip={skip}: {str(e)}")
                logger.info(f"To resume from this point, use --skip {skip}")
                raise

        return total_processed

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
                unique_id = self.generate_unique_id(order['OrderNumber'], order['ItemCode'])
                
                # Normalize the sysmodified timestamp before storing
                try:
                    normalized_sysmodified = self.normalize_timestamp(order['sysmodified'])
                except ValueError:
                    logger.error(f"Invalid sysmodified timestamp for order {order['OrderNumber']}")
                    normalized_sysmodified = order['sysmodified']  # Store original if normalization fails
                
                cursor.execute('''
                    INSERT OR REPLACE INTO open_orders 
                    (id, OrderNumber, YourReference, PackingSlipNumber, Debtor,
                    ItemCode, NumberOrdered, NumberDelivered, OrderStatus,
                    ShipmentReference, TrackTraceCode, TrackTraceUrl,
                    ShipmentStatus, sysmodified, syscreator, EANCode)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    normalized_sysmodified,
                    order['syscreator'],
                    order['EANCode']
                ))
            except Exception as e:
                logger.error(f"Error storing order {order.get('OrderNumber')}: {str(e)}")
                continue

        conn.commit()
        conn.close()

    def sync_open_orders(self, skip=0, modified_after=None):
        """
        Fetch and store open orders data
        
        Args:
            skip (int): Number of records to skip
            modified_after (str, optional): Fetch orders modified after this timestamp
        """
        try:
            total_processed = self.get_open_orders(initial_skip=skip, modified_after=modified_after)
            logger.info(f"Successfully synchronized {total_processed} open orders")
        except Exception as e:
            logger.error(f"Failed to sync open orders: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Sync open orders with optional skip parameter')
    parser.add_argument('--skip', type=int, default=0, help='Skip first N records (useful for resuming failed imports)')
    parser.add_argument('--modified-after', type=str, help='Fetch orders modified after this timestamp')
    args = parser.parse_args()

    api = OpenOrdersAPI()
    api.sync_open_orders(skip=args.skip, modified_after=args.modified_after)

if __name__ == "__main__":
    main()
