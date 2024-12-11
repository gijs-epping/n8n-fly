import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_timestamp(timestamp_str):
    """
    Test implementation of timestamp normalization function.
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

def test_timestamp_normalization():
    # Test cases
    test_cases = [
        {
            'input': '2024-09-11T11:14:44.587',
            'expected': '2024-09-11T11:14:44'
        },
        {
            'input': '2024-10-17T07:01:55 1',
            'expected': '2024-10-17T07:01:55'
        }
    ]
    
    # Run tests
    for test in test_cases:
        try:
            result = normalize_timestamp(test['input'])
            assert result == test['expected'], f"Expected {test['expected']}, got {result}"
            logger.info(f"✓ Successfully normalized '{test['input']}' to '{result}'")
            
            # Demonstrate API query usage
            query = f"sysmodified gt '{result}'"
            logger.info(f"✓ API query parameter: {query}")
            
        except Exception as e:
            logger.error(f"✗ Test failed for '{test['input']}': {str(e)}")

if __name__ == "__main__":
    test_timestamp_normalization()
