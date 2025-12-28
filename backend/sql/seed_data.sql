-- Insert User Types
-- Authorization hierarchy: Admin (3) > Venue Owner (2) > Organizer (1) > Attendee (0)
INSERT INTO user_type (type_name, authorization_level) VALUES
('Admin', 3),
('Organizer', 1),
('Venue Owner', 2),
('Attendee', 0);

-- Insert Users (password: 'password123' hashed with bcrypt)
-- Note: In production, these will be created through the registration endpoint
INSERT INTO users (type_id, name, mail_address, phone_number, password_hash) VALUES
(2, 'Ahmet Organizer', 'ahmet@biletix.com', '555-0001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYkIc7Oc3aW'),
(3, 'Ayse Venue Owner', 'ayse@gmail.com', '555-0002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYkIc7Oc3aW'),
(1, 'Can Admin', 'admin@system.com', '555-0003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYkIc7Oc3aW'),
(4, 'Mehmet Attendee', 'mehmet@gmail.com', '555-0004', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYkIc7Oc3aW');

-- Insert Event Types
INSERT INTO event_type (name) VALUES
('Concert'),
('Theatre'),
('Sports'),
('Conference'),
('Festival');

-- Insert Venues
INSERT INTO venues (owner_id, name, country, city, address, website_url, seat_count, section_count) VALUES
(2, 'Harbiye Cemil Topuzlu', 'Turkey', 'Istanbul', 'Sisli', 'http://harbiye.com', 5000, 2),
(2, 'Zorlu PSM', 'Turkey', 'Istanbul', 'Besiktas', 'http://zorlu.com', 3000, 3),
(2, 'Vodafone Park', 'Turkey', 'Istanbul', 'Besiktas', 'http://vodafonepark.com', 42000, 4);

-- Insert Sections
INSERT INTO sections (venue_id, name) VALUES
(1, 'Section A'),
(1, 'Section B'),
(2, 'VIP'),
(2, 'General'),
(2, 'Balcony'),
(3, 'Tribune 1'),
(3, 'Tribune 2'),
(3, 'Tribune 3'),
(3, 'VIP Section');

-- Insert Seats (sample seats for each section)
INSERT INTO seats (section_id, name) VALUES
-- Section A (section_id: 1)
(1, 'A1'), (1, 'A2'), (1, 'A3'), (1, 'A4'), (1, 'A5'),
-- Section B (section_id: 2)
(2, 'B1'), (2, 'B2'), (2, 'B3'), (2, 'B4'), (2, 'B5'),
-- VIP (section_id: 3)
(3, 'VIP1'), (3, 'VIP2'), (3, 'VIP3'),
-- General (section_id: 4)
(4, 'G1'), (4, 'G2'), (4, 'G3'), (4, 'G4'), (4, 'G5'),
-- Balcony (section_id: 5)
(5, 'BAL1'), (5, 'BAL2'), (5, 'BAL3'),
-- Tribune 1 (section_id: 6)
(6, 'T1-1'), (6, 'T1-2'), (6, 'T1-3');

-- Insert Events
INSERT INTO events (organizer_id, venue_id, event_type_id, name, date) VALUES
(1, 1, 1, 'Tarkan Yaz Konseri', '2024-07-20'),
(1, 2, 2, 'Hamlet Theatre', '2024-08-15'),
(1, 3, 3, 'Besiktas vs Galatasaray', '2024-09-10'),
(1, 2, 1, 'Sezen Aksu Concert', '2024-10-05');

-- Insert Ticket Types
INSERT INTO ticket_type (event_id, name, price) VALUES
(1, 'Standard', 500.0),
(1, 'VIP', 1000.0),
(2, 'Standard', 300.0),
(2, 'Premium', 600.0),
(3, 'Tribune', 200.0),
(3, 'VIP', 800.0);

-- Insert Section Ticket Type Mapping
INSERT INTO section_ticket_type_mapping (section_id, ticket_type_id) VALUES
(1, 1), -- Section A -> Standard tickets for event 1
(2, 2), -- Section B -> VIP tickets for event 1
(3, 3), -- VIP section -> Standard tickets for event 2
(4, 4), -- General -> Premium tickets for event 2
(6, 5), -- Tribune 1 -> Tribune tickets for event 3
(9, 6); -- VIP Section -> VIP tickets for event 3

-- Insert Tickets
INSERT INTO tickets (seat_id, owner_id, ticket_type_id, status) VALUES
(1, NULL, 1, 'available'),
(2, 4, 1, 'sold'),
(3, NULL, 1, 'available'),
(6, NULL, 2, 'available'),
(7, NULL, 2, 'available'),
(11, NULL, 3, 'available'),
(14, NULL, 4, 'available'),
(21, NULL, 5, 'available');

-- Insert Transactions
INSERT INTO transactions (user_id, date, price, payment_method, receipt_id, installment_period) VALUES
(4, '2024-05-10 15:00:00', 500.0, 'Credit Card', 'TFR1273961239GOV', 1);

-- Insert Transaction Items
INSERT INTO transaction_items (ticket_id, transaction_id) VALUES
(2, 1); -- Ticket 2 was sold in transaction 1
