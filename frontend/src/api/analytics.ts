import apiClient from './client'

export const analyticsApi = {
  // Get events with high sold percentage in a city
  getPopularEventsByCity: (city: string, minSoldPercentage: number = 0.8) =>
    apiClient.get('/analytics/popular-events-by-city', {
      params: { city, min_sold_percentage: minSoldPercentage }
    }),

  // Get most popular event types
  getMostPopularEventTypes: (city?: string) =>
    apiClient.get('/analytics/most-popular-event-types', {
      params: city ? { city } : undefined
    }),

  // Get current user's spending analytics
  getUserSpendingAnalytics: () =>
    apiClient.get('/analytics/user-spending-analytics'),

  // Get venue performance metrics
  getVenuePerformance: () =>
    apiClient.get('/analytics/venue-performance'),

  // Get upcoming events with availability
  getUpcomingEventsWithAvailability: (limit: number = 10) =>
    apiClient.get('/analytics/upcoming-events-with-availability', {
      params: { limit }
    }),

  // Get top spending users (admin only)
  getTopSpendingUsers: (limit: number = 10) =>
    apiClient.get('/analytics/top-spending-users', {
      params: { limit }
    }),
}
