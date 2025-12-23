export interface VenueBase {
  name: string
  country: string
  city: string
  address: string
  media_url?: string
  website_url?: string
  seat_count: number
  section_count: number
}

export interface VenueCreate extends VenueBase {}

export interface VenueUpdate {
  name?: string
  country?: string
  city?: string
  address?: string
  media_url?: string
  website_url?: string
  seat_count?: number
  section_count?: number
}

export interface VenueResponse extends VenueBase {
  venue_id: number
  owner_id: number
}
