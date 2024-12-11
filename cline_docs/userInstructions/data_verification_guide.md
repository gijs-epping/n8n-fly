# Data Verification Tools Guide

This guide covers two verification tools used to inspect and validate the OneWayBike database:
1. verify_data.py - Database schema inspection
2. verify_orders.py - Order data verification

## Database Schema Inspection (verify_data.py)

### Purpose
The `verify_data.py` script allows you to inspect the structure of the OneWayBike database, showing all tables and their column definitions.

### Usage
```bash
python verify_data.py
```

### Output Example
```
Database Tables:

Table: open_orders
  id (TEXT)
  OrderNumber (TEXT)
  YourReference (TEXT)
  PackingSlipNumber (TEXT)
  Debtor (TEXT)
  ItemCode (TEXT)
  NumberOrdered (REAL)
  NumberDelivered (REAL)
  OrderStatus (TEXT)
  ShipmentReference (TEXT)
  TrackTraceCode (TEXT)
  TrackTraceUrl (TEXT)
  ShipmentStatus (TEXT)
  sysmodified (TEXT)
  EANCode (TEXT)
  syscreator (INTEGER)
```

### When to Use
1. After database schema updates
2. When troubleshooting data structure issues
3. During development of new database features
4. To verify database migrations

## Order Data Verification (verify_orders.py)

### Purpose
The `verify_orders.py` script provides a quick overview of the orders in the database, showing:
- Total count of open orders
- Sample record with all fields

### Usage
```bash
python verify_orders.py
```

### Output Example
```
Total open orders: 1234

Sample record:
{
  "id": "abc123...",
  "OrderNumber": "ORD001",
  "YourReference": "REF001",
  "PackingSlipNumber": "PSN001",
  "Debtor": "DEBT001",
  "ItemCode": "ITEM001",
  "NumberOrdered": 5.0,
  "NumberDelivered": 0.0,
  "OrderStatus": "V",
  "ShipmentReference": "",
  "TrackTraceCode": "",
  "TrackTraceUrl": "",
  "ShipmentStatus": "NEW",
  "sysmodified": "2024-01-17T12:00:00",
  "EANCode": "1234567890123",
  "syscreator": 1
}
```

### When to Use
1. After running open_orders.py to verify successful synchronization
2. To check the current state of open orders
3. When troubleshooting order synchronization issues
4. To verify data format and completeness

## Best Practices

### Regular Verification
1. Run verify_orders.py after each synchronization to confirm:
   - Orders were properly imported
   - Total count seems reasonable
   - Data format is correct

2. Run verify_data.py when:
   - Setting up new environments
   - After database schema updates
   - Before major data operations

### Troubleshooting
1. If verify_orders.py shows unexpected counts:
   - Check the last synchronization logs
   - Verify API connectivity
   - Run a new synchronization if needed

2. If verify_data.py shows unexpected schema:
   - Compare with expected schema in documentation
   - Check for pending migrations
   - Consult development team if discrepancies found

### Data Quality Checks
1. Use verify_orders.py sample record to check:
   - All required fields are present
   - Data formats are correct
   - Status fields have expected values

2. Monitor total order counts for:
   - Unexpected changes
   - Missing or duplicate records
   - Synchronization completeness
