import { defineStore } from 'pinia'
import { ref } from 'vue'
import { venuesApi } from '@/api/venues'
import type { VenueResponse } from '@/types/venue'

export const useVenuesStore = defineStore('venues', () => {
  // State
  const venues = ref<VenueResponse[]>([])
  const currentVenue = ref<VenueResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchVenues(params?: { city?: string; skip?: number; limit?: number }) {
    loading.value = true
    error.value = null
    try {
      const response = await venuesApi.getAllVenues(params)
      venues.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch venues'
      console.error('Failed to fetch venues:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchVenueById(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await venuesApi.getVenueById(id)
      currentVenue.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch venue'
      console.error('Failed to fetch venue:', e)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    venues,
    currentVenue,
    loading,
    error,
    // Actions
    fetchVenues,
    fetchVenueById,
  }
})
