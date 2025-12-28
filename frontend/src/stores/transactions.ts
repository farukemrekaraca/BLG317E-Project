import { defineStore } from 'pinia'
import { ref } from 'vue'
import { transactionsApi } from '@/api/transactions'
import type { TransactionResponse, TransactionItem } from '@/types/transaction'

export const useTransactionsStore = defineStore('transactions', () => {
  // State
  const transactions = ref<TransactionResponse[]>([])
  const currentTransaction = ref<TransactionResponse | null>(null)
  const currentTransactionItems = ref<TransactionItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchMyTransactions() {
    loading.value = true
    error.value = null
    try {
      const response = await transactionsApi.getMyTransactions()
      transactions.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch transactions'
      console.error('Failed to fetch transactions:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchTransactionById(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionsApi.getTransactionById(id)
      currentTransaction.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch transaction'
      console.error('Failed to fetch transaction:', e)
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchTransactionItems(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await transactionsApi.getTransactionItems(id)
      currentTransactionItems.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch transaction items'
      console.error('Failed to fetch transaction items:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  async function fetchAllTransactions() {
    loading.value = true
    error.value = null
    try {
      const response = await transactionsApi.getAllTransactions()
      transactions.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch all transactions'
      console.error('Failed to fetch all transactions:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    transactions,
    currentTransaction,
    currentTransactionItems,
    loading,
    error,
    // Actions
    fetchMyTransactions,
    fetchTransactionById,
    fetchTransactionItems,
    fetchAllTransactions,
  }
})
