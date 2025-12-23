export interface EventType {
  event_type_id: number
  name: string
}

export interface EventTypeCreate {
  name: string
}

export interface EventBase {
  name: string
  date: string
  venue_id: number
  event_type_id: number
}

export interface EventCreate extends EventBase {}

export interface EventUpdate {
  name?: string
  date?: string
  venue_id?: number
  event_type_id?: number
}

export interface EventResponse extends EventBase {
  event_id: number
  organizer_id: number
}

export interface EventWithDetails extends EventResponse {
  venue_name?: string
  venue_city?: string
  event_type_name?: string
  organizer_name?: string
  available_tickets?: number
  total_tickets?: number
  min_price?: number
  max_price?: number
}
