import apiClient from './client'
import type { UserCreate, UserLogin, UserResponse, Token } from '@/types/user'

export const authApi = {
  register: (data: UserCreate) =>
    apiClient.post<UserResponse>('/auth/register', data),

  login: (credentials: UserLogin) =>
    apiClient.post<Token>('/auth/login', credentials),
}
