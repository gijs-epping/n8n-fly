import requests
import sqlite3
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CubeAPI:
    def __init__(self):
        self.auth_url = 'https://auth-core-cloud.cube.eu/connect/token'
        self.backorders_url = 'https://connect-api.cube.eu/api/v1/backorders'
        self.api_key = '65ab9df921b846eb942d30603897abe9'
        self.client_id = '01592be3-6f63-4150-8cda-493b0e77cd42'
        self.client_secret = 'J0ICQGCa7J7aoCAEc85I6OLLr5woSi3eWcbA7zey9pJzGNvpAu0-LBaQlRDNsJG5'
        self.token = None
        self.db_path = '../.n8n/database/onewaybike.db'
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with required schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backorders (
                externalOrderId TEXT,
                cubeOrderId INTEGER,
                cubeLineId INTEGER,
                productStandardIdentification TEXT,
                productDescription TEXT,
                amountBackorder REAL,
                orderTypeId INTEGER,
                orderTypeDescription TEXT,
                orderDate TEXT,
                calculatedDeliveryWeek INTEGER,
                requestedDeliveryDate TEXT,
                PRIMARY KEY (cubeOrderId, cubeLineId)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_token(self):
        """Get authentication token from Cube API"""
        data = {    
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'profile',
            'acr_values': 'tenant:c4c124a7-3f84-4f9d-bcd4-67316c7bba01',
            'resource': 'connectapi'
        }
        
        try:
            response = requests.post(self.auth_url, data=data)
            response.raise_for_status()
            self.token = response.json()['access_token']
            logger.info("Successfully obtained authentication token")
            return self.token
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get authentication token: {str(e)}")
            raise

    def get_backorders(self):
        """Fetch backorders from Cube API"""
        if not self.token:
            self.get_token()

        headers = {
            'CubeAPI-Key': self.api_key,
            'Authorization': f'Bearer {self.token}'
        }

        try:
            response = requests.get(self.backorders_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch backorders: {str(e)}")
            raise

    def store_backorders(self, backorders_data):
        """Store backorders data in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for line in backorders_data.get('backOrderLines', []):
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO backorders 
                    (externalOrderId, cubeOrderId, cubeLineId, productStandardIdentification,
                    productDescription, amountBackorder, orderTypeId, orderTypeDescription,
                    orderDate, calculatedDeliveryWeek, requestedDeliveryDate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    line['externalOrderId'],
                    line['cubeOrderId'],
                    line['cubeLineId'],
                    line['product']['productStandardIdentification'],
                    line['product']['productDescription'],
                    line['amountBackorder'],
                    line['orderType']['orderTypeId'],
                    line['orderType']['orderTypeDescription'],
                    line['orderDate'],
                    line['calculatedDeliveryWeek'],
                    line['requestedDeliveryDate']
                ))
            except Exception as e:
                logger.error(f"Error storing backorder line {line.get('cubeLineId')}: {str(e)}")
                continue

        conn.commit()
        conn.close()
        logger.info("Successfully stored backorders in database")

    def sync_backorders(self):
        """Fetch and store backorders data"""
        try:
            backorders = self.get_backorders()
            self.store_backorders(backorders)
            logger.info("Successfully synchronized backorders")
        except Exception as e:
            logger.error(f"Failed to sync backorders: {str(e)}")
            raise

def main():
    api = CubeAPI()
    api.sync_backorders()

if __name__ == "__main__":
    main()
