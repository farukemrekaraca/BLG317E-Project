import apiClient from './client'
import type { UserResponse } from '@/types/user'
import type { MyTicket } from '@/types/ticket'
import type { PaginationParams } from '@/types/api'

export const usersApi = {
  getCurrentUser: () =>
    apiClient.get<UserResponse>('/users/me'),

  getMyTickets: () =>
    apiClient.get<MyTicket[]>('/users/me/tickets'),

  getAllUsers: (params?: PaginationParams) =>
    apiClient.get<UserResponse[]>('/users', { params }),

  getUserById: (id: number) =>
    apiClient.get<UserResponse>(`/users/${id}`),

  deleteUser: (id: number) =>
    apiClient.delete(`/users/${id}`),
}
