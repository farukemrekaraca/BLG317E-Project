import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ticketsApi } from '@/api/tickets'
import { usersApi } from '@/api/users'
import type { TicketResponse, TicketType, MyTicket } from '@/types/ticket'

export const useTicketsStore = defineStore('tickets', () => {
  // State
  const tickets = ref<TicketResponse[]>([])
  const ticketTypes = ref<TicketType[]>([])
  const myTickets = ref<MyTicket[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchTickets(params?: { event_id?: number; status_filter?: string; skip?: number; limit?: number }) {
    loading.value = true
    error.value = null
    try {
      const response = await ticketsApi.getAllTickets(params)
      tickets.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch tickets'
      console.error('Failed to fetch tickets:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchTicketTypes(eventId?: number) {
    loading.value = true
    error.value = null
    try {
      const params = eventId ? { event_id: eventId } : undefined
      const response = await ticketsApi.getAllTicketTypes(params)
      ticketTypes.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch ticket types'
      console.error('Failed to fetch ticket types:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  async function fetchMyTickets() {
    loading.value = true
    error.value = null
    try {
      const response = await usersApi.getMyTickets()
      myTickets.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch my tickets'
      console.error('Failed to fetch my tickets:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    tickets,
    ticketTypes,
    myTickets,
    loading,
    error,
    // Actions
    fetchTickets,
    fetchTicketTypes,
    fetchMyTickets,
  }
})
