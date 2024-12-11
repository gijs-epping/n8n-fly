import logging
from pathlib import Path
from cube_api import CubeAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_database_directory():
    """Ensure database directory exists."""
    Path('database').mkdir(exist_ok=True)
    logger.info("Database directory verified")

def main():
    # Ensure database directory exists
    ensure_database_directory()
    
    try:
        # Initialize CubeAPI and sync backorders
        api = CubeAPI()
        api.sync_backorders()
        logger.info("Successfully completed backorder synchronization")
    except Exception as e:
        logger.error(f"Failed to sync backorders: {str(e)}")
        raise

if __name__ == "__main__":
    main()
