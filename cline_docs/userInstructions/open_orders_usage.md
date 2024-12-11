# Open Orders Synchronization Tool Usage Guide

## Basic Usage
To run a full synchronization of open orders:
```bash
python open_orders.py
```

## Error Recovery
If the synchronization process fails, the script will output a message like:
```
ERROR: Failed to fetch open orders at skip=1000: ...
INFO: To resume from this point, use --skip 1000
```

To resume from the failure point:
```bash
python open_orders.py --skip 1000
```

## Progress Monitoring
The script provides detailed progress information:
1. Each batch fetch: "Fetching orders with skip=X"
2. Batch processing: "Processed and stored X orders (Total: Y)"
3. Completion: "Successfully synchronized X open orders"

## Error Messages
- API Fetch Errors: Include the skip value for easy recovery
- Database Errors: Include the specific order number that failed
- All errors are logged with timestamp and context

## Best Practices
1. Monitor the progress output to ensure successful synchronization
2. If a failure occurs, note the skip value from the error message
3. Use the --skip parameter to resume from the exact failure point
4. Verify the final success message shows the expected total count

## Troubleshooting
1. If the script fails repeatedly at the same point:
   - Verify API connectivity
   - Check database permissions
   - Ensure sufficient disk space
   - Contact support if issues persist

2. If database errors occur:
   - Note the specific order numbers from error messages
   - Check for data consistency issues
   - Report persistent errors to the development team
