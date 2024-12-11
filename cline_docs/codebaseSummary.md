## Key Components

### Data Synchronization
- open_orders.py: Manages order synchronization with OneWayBike API
  - Implements pagination for large datasets
  - Provides immediate database storage
  - Includes error recovery through skip parameter
  - Uses MD5 hashing for unique record identification
  - Handles timestamp normalization for consistent API queries
  - Supports filtering by modification time

### Data Verification
- verify_data.py: Database schema inspection tool
  - Displays all tables and their structures
  - Helps verify database integrity
  - Essential for schema validation

- verify_orders.py: Order data verification tool
  - Shows total order count
  - Provides sample record inspection
  - Helps validate data synchronization

### Database Operations
- SQLite database for data persistence
- Optimized for immediate storage of batched data
- Uses UPSERT operations to handle duplicates
- Stores normalized timestamps for consistency

## Data Flow
1. API Request Flow:
   - Client initiates sync through CLI
   - System fetches orders in 500-record batches
   - Timestamps are normalized for API queries
   - Each batch is immediately stored in database
   - Process continues until all records are synced

2. Error Recovery Flow:
   - If sync fails, system logs skip position
   - Operator can resume using --skip parameter
   - Ensures data consistency during recovery

3. Verification Flow:
   - Schema verification through verify_data.py
   - Data validation through verify_orders.py
   - Regular checks ensure data integrity

## External Dependencies
- OneWayBike API for order data
- SQLite for data storage

## Recent Significant Changes
- [2024-01-18] Added timestamp normalization functionality
- [2024-01-18] Implemented modified_after filtering for orders
- [2024-01-17] Added comprehensive verification tool documentation
- [2024-01-17] Implemented immediate database storage in open_orders.py
- [2024-01-17] Added skip parameter for error recovery
- [2024-01-17] Enhanced logging for better operational control

## Architecture Decisions
1. Timestamp Normalization:
   - Decision: Implement consistent timestamp handling
   - Rationale: Ensures reliable API queries and data consistency
   - Impact: Improved data accuracy and query reliability

2. Immediate Storage Pattern:
   - Decision: Store data immediately after each API batch
   - Rationale: Reduces memory usage, improves reliability
   - Impact: Better handling of large datasets

3. CLI Parameter Addition:
   - Decision: Added --skip and --modified-after parameters
   - Rationale: Enables granular control and filtered synchronization
   - Impact: Improved operational flexibility and efficiency

4. Verification Tools:
   - Decision: Separate tools for schema and data verification
   - Rationale: Enables focused, specific validation tasks
   - Impact: Improved monitoring and troubleshooting capabilities

## Performance Considerations
- Batch size of 500 records balances API load and efficiency
- Immediate storage prevents memory overflow
- Database operations optimized for frequent inserts
- Regular verification ensures data quality
- Timestamp normalization optimized for minimal overhead
