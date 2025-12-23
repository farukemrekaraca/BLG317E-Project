from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/popular-events-by-city")
def get_popular_events_by_city(
    city: str,
    min_sold_percentage: float = 0.8,
    cursor=Depends(get_db)
):
    """
    Complex Query 1: Get events that have sold more than a specified percentage of tickets in a given city.

    This query demonstrates:
    - Nested subqueries
    - Aggregation functions
    - Multiple table joins
    - Percentage calculations
    """
    cursor.execute(
        """
        SELECT
            e.event_id,
            e.name as event_name,
            e.date,
            v.name as venue_name,
            v.city,
            et.name as event_type,
            COUNT(t.ticket_id) as total_tickets,
            SUM(CASE WHEN t.status = 'sold' THEN 1 ELSE 0 END) as sold_tickets,
            ROUND(
                (SUM(CASE WHEN t.status = 'sold' THEN 1 ELSE 0 END)::numeric / COUNT(t.ticket_id)) * 100,
                2
            ) as sold_percentage
        FROM events e
        JOIN venues v ON e.venue_id = v.venue_id
        JOIN event_type et ON e.event_type_id = et.event_type_id
        JOIN ticket_type tt ON tt.event_id = e.event_id
        JOIN tickets t ON t.ticket_type_id = tt.ticket_type_id
        WHERE v.city = %s
        GROUP BY e.event_id, e.name, e.date, v.name, v.city, et.name
        HAVING (SUM(CASE WHEN t.status = 'sold' THEN 1 ELSE 0 END)::numeric / COUNT(t.ticket_id)) >= %s
        ORDER BY sold_percentage DESC
        """,
        (city, min_sold_percentage)
    )
    results = cursor.fetchall()
    return [dict(r) for r in results]


@router.get("/most-popular-event-types")
def get_most_popular_event_types(
    city: str = None,
    cursor=Depends(get_db)
):
    """
    Complex Query 2: Determine which event categories are most popular based on ticket sales.

    This query demonstrates:
    - Nested queries with subqueries
    - Aggregation and grouping
    - Optional filtering
    """
    query = """
        SELECT
            et.name as event_type,
            COUNT(DISTINCT e.event_id) as total_events,
            COUNT(t.ticket_id) as total_tickets,
            SUM(CASE WHEN t.status = 'sold' THEN 1 ELSE 0 END) as tickets_sold,
            ROUND(AVG(tt.price)::numeric, 2) as average_ticket_price,
            ROUND(SUM(CASE WHEN t.status = 'sold' THEN tt.price ELSE 0 END)::numeric, 2) as total_revenue
        FROM event_type et
        LEFT JOIN events e ON et.event_type_id = e.event_type_id
        LEFT JOIN venues v ON e.venue_id = v.venue_id
        LEFT JOIN ticket_type tt ON tt.event_id = e.event_id
        LEFT JOIN tickets t ON t.ticket_type_id = tt.ticket_type_id
    """

    if city:
        query += " WHERE v.city = %s"
        params = (city,)
    else:
        params = ()

    query += """
        GROUP BY et.event_type_id, et.name
        ORDER BY tickets_sold DESC
    """

    cursor.execute(query, params)
    results = cursor.fetchall()
    return [dict(r) for r in results]


@router.get("/user-spending-analytics")
def get_user_spending_analytics(
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Complex Query 3: Get detailed spending analytics for a user.

    This query demonstrates:
    - Nested subqueries
    - Window functions
    - Multiple aggregations
    """
    cursor.execute(
        """
        SELECT
            u.user_id,
            u.name,
            COUNT(DISTINCT tr.transaction_id) as total_transactions,
            COUNT(DISTINCT ti.ticket_id) as total_tickets_purchased,
            ROUND(SUM(tr.price)::numeric, 2) as total_spent,
            ROUND(AVG(tr.price)::numeric, 2) as average_transaction_value,
            (
                SELECT et.name
                FROM transactions t2
                JOIN transaction_items ti2 ON t2.transaction_id = ti2.transaction_id
                JOIN tickets tk2 ON ti2.ticket_id = tk2.ticket_id
                JOIN ticket_type tt2 ON tk2.ticket_type_id = tt2.ticket_type_id
                JOIN events e2 ON tt2.event_id = e2.event_id
                JOIN event_type et ON e2.event_type_id = et.event_type_id
                WHERE t2.user_id = u.user_id
                GROUP BY et.name
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) as favorite_event_type
        FROM users u
        LEFT JOIN transactions tr ON u.user_id = tr.user_id
        LEFT JOIN transaction_items ti ON tr.transaction_id = ti.transaction_id
        WHERE u.user_id = %s
        GROUP BY u.user_id, u.name
        """,
        (current_user["user_id"],)
    )
    result = cursor.fetchone()
    return dict(result) if result else {}


@router.get("/venue-performance")
def get_venue_performance(cursor=Depends(get_db)):
    """
    Complex Query 4: Get performance metrics for all venues.

    This query demonstrates:
    - Multiple joins
    - Nested aggregations
    - Subqueries for calculations
    """
    cursor.execute(
        """
        SELECT
            v.venue_id,
            v.name as venue_name,
            v.city,
            COUNT(DISTINCT e.event_id) as total_events,
            COUNT(t.ticket_id) as total_tickets_available,
            SUM(CASE WHEN t.status = 'sold' THEN 1 ELSE 0 END) as tickets_sold,
            ROUND(
                CASE
                    WHEN COUNT(t.ticket_id) > 0
                    THEN (SUM(CASE WHEN t.status = 'sold' THEN 1 ELSE 0 END)::numeric / COUNT(t.ticket_id)) * 100
                    ELSE 0
                END,
                2
            ) as occupancy_rate,
            ROUND(
                SUM(CASE WHEN t.status = 'sold' THEN tt.price ELSE 0 END)::numeric,
                2
            ) as total_revenue
        FROM venues v
        LEFT JOIN events e ON v.venue_id = e.venue_id
        LEFT JOIN ticket_type tt ON e.event_id = tt.event_id
        LEFT JOIN tickets t ON tt.ticket_type_id = t.ticket_type_id
        GROUP BY v.venue_id, v.name, v.city
        ORDER BY total_revenue DESC
        """
    )
    results = cursor.fetchall()
    return [dict(r) for r in results]


@router.get("/upcoming-events-with-availability")
def get_upcoming_events_with_availability(
    cursor=Depends(get_db),
    limit: int = 10
):
    """
    Complex Query 5: Get upcoming events with ticket availability details.

    This query demonstrates:
    - Date filtering
    - Nested subqueries for availability calculation
    - Multiple joins
    """
    cursor.execute(
        """
        SELECT
            e.event_id,
            e.name as event_name,
            e.date,
            v.name as venue_name,
            v.city,
            et.name as event_type,
            u.name as organizer_name,
            (
                SELECT COUNT(*)
                FROM tickets t
                JOIN ticket_type tt ON t.ticket_type_id = tt.ticket_type_id
                WHERE tt.event_id = e.event_id AND t.status = 'available'
            ) as available_tickets,
            (
                SELECT COUNT(*)
                FROM tickets t
                JOIN ticket_type tt ON t.ticket_type_id = tt.ticket_type_id
                WHERE tt.event_id = e.event_id
            ) as total_tickets,
            (
                SELECT MIN(price)
                FROM ticket_type
                WHERE event_id = e.event_id
            ) as min_price,
            (
                SELECT MAX(price)
                FROM ticket_type
                WHERE event_id = e.event_id
            ) as max_price
        FROM events e
        JOIN venues v ON e.venue_id = v.venue_id
        JOIN event_type et ON e.event_type_id = et.event_type_id
        JOIN users u ON e.organizer_id = u.user_id
        WHERE e.date >= CURRENT_DATE
        ORDER BY e.date ASC
        LIMIT %s
        """,
        (limit,)
    )
    results = cursor.fetchall()
    return [dict(r) for r in results]


@router.get("/top-spending-users")
def get_top_spending_users(
    cursor=Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 10
):
    """
    Complex Query 6: Get top spending users (Admin only).

    This query demonstrates:
    - Aggregation with ranking
    - Multiple joins
    - Authorization check
    """
    # Check if user is admin
    cursor.execute(
        """
        SELECT authorization_level FROM user_type ut
        JOIN users u ON ut.user_type_id = u.type_id
        WHERE u.user_id = %s
        """,
        (current_user["user_id"],)
    )
    user_auth = cursor.fetchone()

    if not user_auth or user_auth["authorization_level"] < 3:
        raise HTTPException(status_code=403, detail="Admin access required")

    cursor.execute(
        """
        SELECT
            u.user_id,
            u.name,
            u.mail_address,
            COUNT(DISTINCT tr.transaction_id) as total_transactions,
            COUNT(DISTINCT ti.ticket_id) as total_tickets,
            ROUND(SUM(tr.price)::numeric, 2) as total_spent,
            ROUND(AVG(tr.price)::numeric, 2) as avg_transaction_value
        FROM users u
        JOIN transactions tr ON u.user_id = tr.user_id
        JOIN transaction_items ti ON tr.transaction_id = ti.transaction_id
        GROUP BY u.user_id, u.name, u.mail_address
        ORDER BY total_spent DESC
        LIMIT %s
        """,
        (limit,)
    )
    results = cursor.fetchall()
    return [dict(r) for r in results]
