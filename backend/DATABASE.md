# Database Management

## Quick Reference

### Reset Database (Interactive)
```bash
python reset_db.py
```
- Prompts for confirmation before resetting
- Drops all tables and recreates with seed data
- **All data will be lost!**

### Reset Database (Force)
```bash
python reset_db.py --force
```
- Resets without confirmation
- Useful for automation/scripts

### Initial Setup
```bash
python setup_db.py
```
- Sets up database for the first time
- Also works for resetting (schema.sql has DROP TABLE statements)

## When to Reset the Database

### After Schema Changes
If you modified `sql/schema.sql`, reset the database:
```bash
python reset_db.py --force
```

### After Authorization Level Changes
We recently updated authorization levels. Reset to apply:
```bash
python reset_db.py --force
```

**New levels:**
- Admin: 3
- Venue Owner: 2
- Organizer: 1
- Attendee: 0

### Before Running Tests
Tests automatically reset the database using the `reset_test_database` fixture in `tests/conftest.py`.

You can also manually reset before testing:
```bash
python reset_db.py --force && pytest
```

## Database Files

- **`sql/schema.sql`**: Table definitions and structure
- **`sql/seed_data.sql`**: Initial data for development/testing
- **`setup_db.py`**: Initial database setup script
- **`reset_db.py`**: Database reset script (recommended)

## Authorization Levels

After resetting, the following user types are available:

| User Type    | Type ID | Auth Level | Permissions                           |
|--------------|---------|------------|---------------------------------------|
| Admin        | 1       | 3          | Full access to everything             |
| Organizer    | 2       | 1          | Create events, manage tickets         |
| Venue Owner  | 3       | 2          | Create/manage venues and sections     |
| Attendee     | 4       | 0          | View events, purchase tickets         |

## Test Users (from seed_data.sql)

After reset, these users are available:
- **Admin**: admin@system.com (password: password123)
- **Organizer**: ahmet@gmail.com (password: password123)
- **Venue Owner**: ayse@gmail.com (password: password123)
- **Attendee**: mehmet@gmail.com (password: password123)

## Troubleshooting

### SQL file not found?
→ Make sure you're running scripts from the `backend/` directory

### Connection errors?
→ Check your `.env` file has correct `DATABASE_URL`