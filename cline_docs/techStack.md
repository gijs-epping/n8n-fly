## Backend
- Language: Python
- Database: SQLite
- API Integration: OneWayBike REST API

## Key Libraries
- requests: HTTP client for API communication
- sqlite3: Database operations
- hashlib: Data integrity (MD5 hashing)
- logging: Application logging
- argparse: CLI argument parsing

## Database Schema
### open_orders Table
- Primary Key: id (MD5 hash of OrderNumber and ItemCode)
- Order Fields:
  - OrderNumber
  - YourReference
  - PackingSlipNumber
  - Debtor
  - ItemCode
  - NumberOrdered
  - NumberDelivered
  - OrderStatus
  - ShipmentReference
  - TrackTraceCode
  - TrackTraceUrl
  - ShipmentStatus
  - sysmodified
  - EANCode
  - syscreator

## API Integration
- Base URL: integrationgateway.onewaybike.nl
- Authentication: Bearer Token
- Pagination: 500 records per request
- Filtering: OrderStatus and ShipmentStatus

## Development Practices
- Immediate data persistence
- Batch processing
- Error recovery mechanisms
- Detailed logging
- CLI-based operation control
