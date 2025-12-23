import apiClient from './client'
import type { TicketResponse, TicketCreate, TicketUpdate, TicketType, TicketTypeCreate } from '@/types/ticket'
import type { PaginationParams } from '@/types/api'

export const ticketsApi = {
  // Ticket Types
  getAllTicketTypes: (params?: { event_id?: number }) =>
    apiClient.get<TicketType[]>('/tickets/types', { params }),

  createTicketType: (data: TicketTypeCreate) =>
    apiClient.post<TicketType>('/tickets/types', data),

  // Tickets
  getAllTickets: (params?: PaginationParams & { event_id?: number; status_filter?: string }) =>
    apiClient.get<TicketResponse[]>('/tickets', { params }),

  getTicketById: (id: number) =>
    apiClient.get<TicketResponse>(`/tickets/${id}`),

  createTicket: (data: TicketCreate) =>
    apiClient.post<TicketResponse>('/tickets', data),

  updateTicket: (id: number, data: TicketUpdate) =>
    apiClient.put<TicketResponse>(`/tickets/${id}`, data),

  deleteTicket: (id: number) =>
    apiClient.delete(`/tickets/${id}`),
}
