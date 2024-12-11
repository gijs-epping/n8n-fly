import requests
import sqlite3
import logging
import argparse
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAPI:
    def __init__(self):
        self.base_url = 'https://integrationgateway.onewaybike.nl/V1/012/Sales/CSStock'
        self.token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOiIxNjc3ODUzMzI3IiwiaXNzIjoiaW50ZWdyYXRpb25nYXRld2F5Lm9uZXdheWJpa2UubmwiLCJhdWQiOiJpbnRlZ3JhdGlvbmdhdGV3YXkub25ld2F5YmlrZS5ubCIsImV4cCI6IjQxMDIzNTQ4MDAiLCJqdGkiOiI2NjY4MzVkOC01MmY1LTQwZGQtYjhjZi01ZDc4OGY1MmU3NzAiLCJzdWIiOiJzaG9wd29ya3MifQ.Xyn6NWYFshnHPP3tUk-hjda3bigVPYdzaRVmIeKsW3k'
        self.db_path = '../.n8n/database/onewaybike.db'
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with required schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS currentstock (
                sku TEXT PRIMARY KEY,
                stock_shelf REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_stock(self, initial_skip=0, batch_size=500):
        """
        Fetch stock data from API with pagination and store immediately
        
        Args:
            initial_skip (int): Number of records to skip
            batch_size (int): Number of records to fetch per request
        """
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        total_processed = 0
        skip = initial_skip
        
        while True:
            params = {
                '$top': batch_size,
                '$skip': skip
            }
            
            try:
                logger.info(f"Fetching stock with skip={skip}")
                response = requests.get(self.base_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Get current page results
                results = data.get('d', {}).get('results', [])
                
                # If no results returned, we've reached the end
                if not results:
                    break
                
                # Store the current batch immediately
                self.store_stock(results)
                
                total_processed += len(results)
                logger.info(f"Processed and stored {len(results)} stock records (Total: {total_processed})")
                
                # Sleep for 2 seconds before next request to prevent server overload
                time.sleep(2)
                
                # Increment skip for next page
                skip += batch_size
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch stock at skip={skip}: {str(e)}")
                logger.info(f"To resume from this point, use --skip {skip}")
                raise

        return total_processed

    def store_stock(self, stock_data):
        """Store stock data in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Prepare data for insertion
            data = [(item['sku'], item['stock_shelf']) for item in stock_data]
            
            # Insert data with REPLACE to handle duplicates
            cursor.executemany(
                """
                INSERT OR REPLACE INTO currentstock 
                (sku, stock_shelf)
                VALUES (?, ?)
                """, 
                data
            )
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error storing stock data: {str(e)}")
            raise
        finally:
            conn.close()

    def sync_stock(self, skip=0, top=20):  # Changed default top to 20 as per API example
        """
        Fetch and store stock data
        
        Args:
            skip (int): Number of records to skip
            top (int): Number of records to fetch per request
        """
        try:
            total_processed = self.get_stock(initial_skip=skip, batch_size=top)
            logger.info(f"Successfully synchronized {total_processed} stock records")
        except Exception as e:
            logger.error(f"Failed to sync stock: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Sync stock data with optional skip and top parameters')
    parser.add_argument('--skip', type=int, default=0, help='Skip first N records (useful for resuming failed imports)')
    parser.add_argument('--top', type=int, default=500, help='Number of records to fetch per request (default: 500)')
    args = parser.parse_args()

    api = StockAPI()
    api.sync_stock(skip=args.skip, top=args.top)

if __name__ == "__main__":
    main()
