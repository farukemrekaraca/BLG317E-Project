import apiClient from './client'
import type { TransactionResponse, TransactionCreate, TransactionItem } from '@/types/transaction'
import type { PaginationParams } from '@/types/api'

export const transactionsApi = {
  // User's transactions
  getMyTransactions: (params?: PaginationParams) =>
    apiClient.get<TransactionResponse[]>('/transactions', { params }),

  // Admin: all transactions
  getAllTransactions: (params?: PaginationParams) =>
    apiClient.get<TransactionResponse[]>('/transactions/all', { params }),

  // Get specific transaction
  getTransactionById: (id: number) =>
    apiClient.get<TransactionResponse>(`/transactions/${id}`),

  // Get transaction items (tickets in transaction)
  getTransactionItems: (id: number) =>
    apiClient.get<TransactionItem[]>(`/transactions/${id}/items`),

  // Create transaction (purchase tickets)
  createTransaction: (data: TransactionCreate) =>
    apiClient.post<TransactionResponse>('/transactions', data),
}
