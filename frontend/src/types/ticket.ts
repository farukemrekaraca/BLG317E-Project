export interface TicketType {
  ticket_type_id: number
  event_id: number
  name: string
  price: number
}

export interface TicketTypeCreate {
  event_id: number
  name: string
  price: number
}

export interface TicketBase {
  seat_id: number
  ticket_type_id: number
  status: TicketStatus
}

export interface TicketCreate extends TicketBase {}

export interface TicketUpdate {
  owner_id?: number
  status?: TicketStatus
}

export interface TicketResponse extends TicketBase {
  ticket_id: number
  owner_id?: number
}

export enum TicketStatus {
  AVAILABLE = 'available',
  RESERVED = 'reserved',
  SOLD = 'sold'
}

export interface MyTicket {
  ticket_id: number
  seat_id: number
  ticket_type_id: number
  status: string
  ticket_type_name: string
  price: number
  event_id: number
  event_name: string
  event_date: string
  venue_name: string
  venue_city: string
}

export interface CartItem {
  ticket: TicketResponse
  ticketType: TicketType
  eventId: number
  eventName: string
  eventDate: string
  venueName: string
}
