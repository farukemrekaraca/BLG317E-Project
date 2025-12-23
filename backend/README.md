# Event Management and Ticketing API

RESTful API for Event Management and Ticketing Platform - BLG317E Database Systems Project

## Team Members
- Yavuz Burak Yalçın (150220752)
- Alper Düzgün (150220312)
- Faruk Emre Karaca (150240723)

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Documentation**: Swagger/OpenAPI (auto-generated)
- **Database Driver**: psycopg3 (raw SQL - no ORM)

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── events.py        # Event CRUD
│   │       ├── venues.py        # Venue CRUD
│   │       ├── tickets.py       # Ticket CRUD
│   │       ├── transactions.py  # Transaction CRUD
│   │       ├── users.py         # User management
│   │       └── analytics.py     # Complex queries
│   ├── core/
│   │   ├── config.py           # App configuration
│   │   ├── security.py         # JWT & password hashing
│   │   └── dependencies.py     # Auth dependencies
│   ├── db/
│   │   └── database.py         # Database connection
│   ├── schemas/
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── venue.py
│   │   ├── ticket.py
│   │   └── transaction.py
│   └── main.py                 # FastAPI app
├── sql/
│   ├── schema.sql              # Database schema (12 tables)
│   └── seed_data.sql           # Dummy data
├── requirements.txt
├── setup_db.py                 # Database setup script
└── .env                        # Environment variables
```

## Database Schema

The database consists of 12 tables:
1. **user_type** - User role definitions
2. **users** - User accounts
3. **event_type** - Event categories
4. **events** - Event information
5. **venues** - Venue details
6. **sections** - Venue sections
7. **seats** - Individual seats
8. **ticket_type** - Ticket pricing tiers
9. **tickets** - Ticket inventory
10. **transactions** - Purchase records
11. **transaction_items** - Transaction details
12. **section_ticket_type_mapping** - Section-ticket type relationships

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pgAdmin4

### 2. Create Database
Using pgAdmin4 or psql:
```sql
CREATE DATABASE event_ticketing;
```

### 3. Configure Environment
Edit the `.env` file with your database credentials:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/event_ticketing
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Set Up Database
```bash
python setup_db.py
```

This will:
- Create all 12 tables with proper relationships
- Insert seed data (users, events, venues, tickets)
- Set up indexes for performance

### 6. Run the Server
```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### 7. Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Users
- `GET /api/users/me` - Get current user info
- `GET /api/users` - List all users (Admin only)
- `GET /api/users/{user_id}` - Get user by ID (Admin only)
- `DELETE /api/users/{user_id}` - Delete user (Admin only)
- `GET /api/users/me/tickets` - Get my tickets

### Events
- `POST /api/events` - Create event (Organizer+)
- `GET /api/events` - List events
- `GET /api/events/{event_id}` - Get event details
- `PUT /api/events/{event_id}` - Update event
- `DELETE /api/events/{event_id}` - Delete event (Admin)
- `POST /api/events/types` - Create event type
- `GET /api/events/types` - List event types

### Venues
- `POST /api/venues` - Create venue (Venue Owner+)
- `GET /api/venues` - List venues
- `GET /api/venues/{venue_id}` - Get venue details
- `PUT /api/venues/{venue_id}` - Update venue
- `DELETE /api/venues/{venue_id}` - Delete venue (Admin)

### Tickets
- `POST /api/tickets` - Create ticket (Organizer+)
- `GET /api/tickets` - List tickets
- `GET /api/tickets/{ticket_id}` - Get ticket details
- `PUT /api/tickets/{ticket_id}` - Update ticket
- `DELETE /api/tickets/{ticket_id}` - Delete ticket (Admin)
- `POST /api/tickets/types` - Create ticket type
- `GET /api/tickets/types` - List ticket types

### Transactions
- `POST /api/transactions` - Purchase tickets
- `GET /api/transactions` - Get my transactions
- `GET /api/transactions/all` - Get all transactions (Admin)
- `GET /api/transactions/{transaction_id}` - Get transaction details
- `GET /api/transactions/{transaction_id}/items` - Get transaction items

### Analytics (Complex Queries)
- `GET /api/analytics/popular-events-by-city` - Events >80% sold in a city
- `GET /api/analytics/most-popular-event-types` - Popular event categories
- `GET /api/analytics/user-spending-analytics` - User spending analysis
- `GET /api/analytics/venue-performance` - Venue performance metrics
- `GET /api/analytics/upcoming-events-with-availability` - Upcoming events
- `GET /api/analytics/top-spending-users` - Top spenders (Admin)

## User Roles

1. **Admin** (authorization_level: 3)
   - Full system access
   - Can delete any resource
   - View all transactions

2. **Organizer** (authorization_level: 2)
   - Create and manage events
   - Create ticket types

3. **Venue Owner** (authorization_level: 2)
   - Create and manage venues

4. **Attendee** (authorization_level: 1)
   - Purchase tickets
   - View events and venues

## Testing

### Default Test Accounts (password: 'password123')
- Admin: admin@system.com
- Organizer: ahmet@biletix.com
- Venue Owner: ayse@gmail.com
- Attendee: mehmet@gmail.com

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Login using `/api/auth/login`
4. Copy the access token
5. Paste in the authorization dialog
6. Test any endpoint

## Complex Queries Demonstration

The `/api/analytics` endpoints demonstrate:
- Nested subqueries
- Window functions
- Aggregation functions
- Multiple table joins
- Conditional aggregations
- Date-based filtering

Example:
```
GET /api/analytics/popular-events-by-city?city=Istanbul&min_sold_percentage=0.8
```

## Notes

- All passwords are hashed using bcrypt
- All database operations use raw SQL (no ORM)
- API follows RESTful best practices
- Authentication required for protected endpoints
- Comprehensive error handling
- Comprehensive unit tests with pytest
- Automatic API documentation via Swagger
