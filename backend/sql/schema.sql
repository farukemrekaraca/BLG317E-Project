-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS transaction_items CASCADE;
DROP TABLE IF EXISTS section_ticket_type_mapping CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS seats CASCADE;
DROP TABLE IF EXISTS sections CASCADE;
DROP TABLE IF EXISTS ticket_type CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS venues CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS event_type CASCADE;
DROP TABLE IF EXISTS user_type CASCADE;

-- Create User_Type table
CREATE TABLE user_type (
    user_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL,
    authorization_level INT NOT NULL
);

-- Create Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    type_id INT NOT NULL REFERENCES user_type(user_type_id),
    name VARCHAR(100) NOT NULL,
    mail_address VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Event_Type table
CREATE TABLE event_type (
    event_type_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create Venues table
CREATE TABLE venues (
    venue_id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL REFERENCES users(user_id),
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(100) NOT NULL,
    media_url VARCHAR(255),
    website_url VARCHAR(100),
    seat_count INT NOT NULL,
    section_count INT NOT NULL
);

-- Create Events table
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    organizer_id INT NOT NULL REFERENCES users(user_id),
    venue_id INT NOT NULL REFERENCES venues(venue_id),
    event_type_id INT NOT NULL REFERENCES event_type(event_type_id),
    name VARCHAR(100) NOT NULL,
    date DATE NOT NULL
);

-- Create Sections table
CREATE TABLE sections (
    section_id SERIAL PRIMARY KEY,
    venue_id INT NOT NULL REFERENCES venues(venue_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL
);

-- Create Seats table
CREATE TABLE seats (
    seat_id SERIAL PRIMARY KEY,
    section_id INT NOT NULL REFERENCES sections(section_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL
);

-- Create Ticket_Type table
CREATE TABLE ticket_type (
    ticket_type_id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL
);

-- Create Section_Ticket_Type_Mapping table
CREATE TABLE section_ticket_type_mapping (
    section_id INT NOT NULL REFERENCES sections(section_id) ON DELETE CASCADE,
    ticket_type_id INT NOT NULL REFERENCES ticket_type(ticket_type_id) ON DELETE CASCADE,
    PRIMARY KEY (section_id, ticket_type_id)
);

-- Create Transactions table
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price FLOAT NOT NULL,
    payment_method VARCHAR(100) NOT NULL,
    receipt_id VARCHAR(100) NOT NULL UNIQUE,
    installment_period INT
);

-- Create Tickets table
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    seat_id INT NOT NULL REFERENCES seats(seat_id) ON DELETE CASCADE,
    owner_id INT REFERENCES users(user_id),
    ticket_type_id INT NOT NULL REFERENCES ticket_type(ticket_type_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('available', 'reserved', 'sold'))
);

-- Create Transaction_Items table
CREATE TABLE transaction_items (
    ticket_id INT NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    transaction_id INT NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    PRIMARY KEY (ticket_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_users_mail ON users(mail_address);
CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_events_organizer ON events(organizer_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_venues_city ON venues(city);
