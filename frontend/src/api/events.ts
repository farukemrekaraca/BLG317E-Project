import apiClient from './client'
import type { EventResponse, EventCreate, EventUpdate, EventType, EventTypeCreate } from '@/types/event'
import type { PaginationParams } from '@/types/api'

export const eventsApi = {
  // Event Types
  getAllEventTypes: () =>
    apiClient.get<EventType[]>('/events/types'),

  getEventTypeById: (id: number) =>
    apiClient.get<EventType>(`/events/types/${id}`),

  createEventType: (data: EventTypeCreate) =>
    apiClient.post<EventType>('/events/types', data),

  // Events
  getAllEvents: (params?: PaginationParams) =>
    apiClient.get<EventResponse[]>('/events', { params }),

  getEventById: (id: number) =>
    apiClient.get<EventResponse>(`/events/${id}`),

  createEvent: (data: EventCreate) =>
    apiClient.post<EventResponse>('/events', data),

  updateEvent: (id: number, data: EventUpdate) =>
    apiClient.put<EventResponse>(`/events/${id}`, data),

  deleteEvent: (id: number) =>
    apiClient.delete(`/events/${id}`),
}
