export interface PopularEventByCity {
  event_id: number
  event_name: string
  date: string
  venue_name: string
  city: string
  event_type: string
  total_tickets: number
  sold_tickets: number
  sold_percentage: number
}

export interface EventTypePopularity {
  event_type: string
  total_events: number
  total_tickets: number
  tickets_sold: number
  average_ticket_price: number
  total_revenue: number
}

export interface UserSpendingAnalytics {
  user_id: number
  name: string
  total_transactions: number
  total_tickets_purchased: number
  total_spent: number
  average_transaction_value: number
  favorite_event_type?: string
}

export interface VenuePerformance {
  venue_id: number
  venue_name: string
  city: string
  total_events: number
  total_tickets_available: number
  tickets_sold: number
  occupancy_rate: number
  total_revenue: number
}

export interface UpcomingEvent {
  event_id: number
  event_name: string
  date: string
  venue_name: string
  city: string
  event_type: string
  organizer_name: string
  available_tickets: number
  total_tickets: number
  min_price: number
  max_price: number
}

export interface TopSpendingUser {
  user_id: number
  name: string
  mail_address: string
  total_transactions: number
  total_tickets: number
  total_spent: number
  avg_transaction_value: number
}
