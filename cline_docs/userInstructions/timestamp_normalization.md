# Timestamp Normalization Guide

## Overview
This guide explains how to use the timestamp normalization functionality in the OpenOrdersAPI class, which handles two different timestamp formats from our system.

## Supported Timestamp Formats
1. ISO format with milliseconds: `2024-09-11T11:14:44.587`
2. ISO format with trailing '1': `2024-10-17T07:01:55 1`

## Usage Examples

### Command Line Interface
Filter orders modified after a specific timestamp:
```bash
python open_orders.py --modified-after "2024-09-11T11:14:44.587"
# or
python open_orders.py --modified-after "2024-10-17T07:01:55 1"
```

### Python API Usage
```python
from open_orders import OpenOrdersAPI

api = OpenOrdersAPI()

# Example 1: Sync orders modified after a specific time
api.sync_open_orders(modified_after="2024-09-11T11:14:44.587")

# Example 2: Direct timestamp normalization
normalized = api.normalize_timestamp("2024-10-17T07:01:55 1")
print(normalized)  # Output: 2024-10-17T07:01:55
```

## Error Handling
The timestamp normalization includes robust error handling:
- Invalid formats will raise ValueError with descriptive messages
- Errors are logged for debugging purposes
- Original timestamps are preserved in case of normalization failures

## Best Practices
1. Always use ISO format timestamps (YYYY-MM-DDThh:mm:ss)
2. When querying recent changes, use the most recent sysmodified timestamp
3. Handle potential errors when working with timestamps from external sources

## Testing
You can run the timestamp normalization tests:
```bash
python test_timestamps.py
```

This will verify:
- Handling of both timestamp formats
- Proper API query parameter formatting
- Error handling capabilities
