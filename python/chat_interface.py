from openai import OpenAI
import sqlite3
from typing import List, Dict
import json
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ChatInterface:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "OneWayBike Chat Interface"
            }
        )
        self.model = "google/gemini-exp-1114"
        self.db_path = "database/backorders.db"
        logger.info("ChatInterface initialized")

    def extract_order_id(self, text: str) -> str:
        """Extract order ID from text."""
        # Look for 7-8 digit numbers
        match = re.search(r'\b\d{7,8}\b', text)
        if match:
            return match.group(0)
        return None

    def get_order_info(self, order_id: str) -> Dict:
        """Retrieve order information from the database."""
        logger.info(f"Fetching order info for order_id: {order_id}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            externalOrderId,
            productDescription,
            amountBackorder,
            orderTypeDescription,
            orderDate,
            calculatedDeliveryWeek,
            requestedDeliveryDate
        FROM backorders 
        WHERE externalOrderId = ?
        """
        
        cursor.execute(query, (order_id,))
        results = cursor.fetchall()
        conn.close()
        
        if results:
            logger.info(f"Found {len(results)} products for order {order_id}")
            order_info = []
            for result in results:
                order_info.append({
                    "externalOrderId": result[0],
                    "productDescription": result[1],
                    "amountBackorder": result[2],
                    "orderTypeDescription": result[3],
                    "orderDate": result[4],
                    "calculatedDeliveryWeek": result[5],
                    "requestedDeliveryDate": result[6]
                })
            return order_info
        logger.warning(f"No order found with ID: {order_id}")
        return None

    def get_recent_orders(self, limit: int = 5) -> List[str]:
        """Get a list of recent order IDs."""
        logger.info(f"Fetching {limit} recent orders")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT externalOrderId 
        FROM backorders 
        ORDER BY orderDate DESC 
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        orders = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"Found {len(orders)} recent orders")
        return orders

    def format_order_details(self, order_info: List[Dict]) -> str:
        """Format order details for display."""
        if not order_info:
            return "No order information available."
        
        details = f"""Order Details:
Order ID: {order_info[0]['externalOrderId']}
Order Date: {order_info[0]['orderDate']}
Order Type: {order_info[0]['orderTypeDescription']}
Delivery Week: {order_info[0]['calculatedDeliveryWeek']}
Requested Delivery: {order_info[0]['requestedDeliveryDate']}

Products in this order:"""
        
        for item in order_info:
            details += f"\n- {item['productDescription']} (Quantity: {item['amountBackorder']})"
        
        return details

    def generate_response(self, user_input: str) -> str:
        """Generate a response based on user input."""
        try:
            # Extract order ID directly from input
            order_id = self.extract_order_id(user_input)
            
            if order_id:
                logger.info(f"Found order ID in input: {order_id}")
                order_info = self.get_order_info(order_id)
                
                if order_info:
                    # Format and return order details directly
                    return self.format_order_details(order_info)
                else:
                    recent_orders = self.get_recent_orders()
                    return f"I couldn't find any order with ID {order_id}. Here are some recent orders you can ask about:\n" + "\n".join(
                        f"- {order}" for order in recent_orders
                    )
            else:
                # Check if the input contains keywords related to orders
                if any(word in user_input.lower() for word in ['order', 'orders', 'products']):
                    recent_orders = self.get_recent_orders()
                    return f"Please provide an order ID. Here are some recent orders you can ask about:\n" + "\n".join(
                        f"- {order}" for order in recent_orders
                    )
                else:
                    return "You can ask about orders by including the order ID in your question. For example:\n" + \
                           "- What products are in order 27213709?\n" + \
                           "- Show me the details for order 27213749\n" + \
                           "- What's the status of my order 27213710?"

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            recent_orders = self.get_recent_orders()
            return f"I encountered an error. You can ask about these recent orders:\n" + "\n".join(
                f"- {order}" for order in recent_orders
            )

    def run_chat_interface(self):
        """Run the chat interface in a loop."""
        logger.info("Starting chat interface")
        print("Welcome to OneWayBike Chat Interface!")
        print("Type 'exit' to quit.")
        print("\nYou can ask questions like:")
        print("- What products are in order 27213709?")
        print("- Show me the details for order 27213749")
        print("- What's the status of my order 27213710?")
        
        # Show some recent orders at startup
        recent_orders = self.get_recent_orders()
        if recent_orders:
            print("\nRecent orders you can ask about:")
            for order_id in recent_orders:
                print(order_id)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'exit':
                    logger.info("Chat interface terminated by user")
                    print("Goodbye!")
                    break
                
                logger.info(f"User input: {user_input}")
                response = self.generate_response(user_input)
                print(f"\nAssistant: {response}")
                
            except KeyboardInterrupt:
                logger.info("Chat interface interrupted by user")
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in chat interface: {str(e)}", exc_info=True)
                print("\nAn error occurred. Please try again.")

if __name__ == "__main__":
    chat_interface = ChatInterface()
    chat_interface.run_chat_interface()
