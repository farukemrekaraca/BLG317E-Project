import { defineStore } from 'pinia'
import { ref } from 'vue'
import { eventsApi } from '@/api/events'
import type { EventResponse, EventType } from '@/types/event'

export const useEventsStore = defineStore('events', () => {
  // State
  const events = ref<EventResponse[]>([])
  const eventTypes = ref<EventType[]>([])
  const currentEvent = ref<EventResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchEvents(params?: { skip?: number; limit?: number }) {
    loading.value = true
    error.value = null
    try {
      const response = await eventsApi.getAllEvents(params)
      events.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch events'
      console.error('Failed to fetch events:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchEventById(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await eventsApi.getEventById(id)
      currentEvent.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch event'
      console.error('Failed to fetch event:', e)
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchEventTypes() {
    try {
      const response = await eventsApi.getAllEventTypes()
      eventTypes.value = response.data
    } catch (e: any) {
      console.error('Failed to fetch event types:', e)
    }
  }

  async function createEvent(data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await eventsApi.createEvent(data)
      events.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to create event'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateEvent(id: number, data: any) {
    loading.value = true
    error.value = null
    try {
      const response = await eventsApi.updateEvent(id, data)
      const index = events.value.findIndex(e => e.event_id === id)
      if (index !== -1) {
        events.value[index] = response.data
      }
      if (currentEvent.value?.event_id === id) {
        currentEvent.value = response.data
      }
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to update event'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteEvent(id: number) {
    loading.value = true
    error.value = null
    try {
      await eventsApi.deleteEvent(id)
      events.value = events.value.filter(e => e.event_id !== id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete event'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    events,
    eventTypes,
    currentEvent,
    loading,
    error,
    // Actions
    fetchEvents,
    fetchEventById,
    fetchEventTypes,
    createEvent,
    updateEvent,
    deleteEvent,
  }
})
