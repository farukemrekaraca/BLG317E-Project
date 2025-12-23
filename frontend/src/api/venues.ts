import apiClient from './client'
import type { VenueResponse, VenueCreate, VenueUpdate } from '@/types/venue'
import type { PaginationParams } from '@/types/api'

export const venuesApi = {
  getAllVenues: (params?: PaginationParams & { city?: string }) =>
    apiClient.get<VenueResponse[]>('/venues', { params }),

  getVenueById: (id: number) =>
    apiClient.get<VenueResponse>(`/venues/${id}`),

  createVenue: (data: VenueCreate) =>
    apiClient.post<VenueResponse>('/venues', data),

  updateVenue: (id: number, data: VenueUpdate) =>
    apiClient.put<VenueResponse>(`/venues/${id}`, data),

  deleteVenue: (id: number) =>
    apiClient.delete(`/venues/${id}`),
}
