<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { analyticsApi } from '@/api/analytics'

const appName = import.meta.env.VITE_APP_NAME
const authStore = useAuthStore()

const loading = ref(false)
const error = ref<string | null>(null)

const venuePerformance = ref<any[]>([])
const upcomingEvents = ref<any[]>([])
const userSpending = ref<any>(null)

const loadAnalytics = async () => {
  loading.value = true
  error.value = null

  try {
    const [venueRes, upcomingRes, spendingRes] = await Promise.all([
      analyticsApi.getVenuePerformance(),
      analyticsApi.getUpcomingEventsWithAvailability(20),
      analyticsApi.getUserSpendingAnalytics(),
    ])

    venuePerformance.value = venueRes.data
    upcomingEvents.value = upcomingRes.data
    userSpending.value = spendingRes.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to load analytics'
    console.error('Failed to load analytics:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnalytics()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }} - Analytics</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/organizer/dashboard">Dashboard</v-btn>
        <v-btn to="/organizer/my-events">My Events</v-btn>
        <v-btn @click="authStore.logout">Logout</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <h1 class="text-h3 mb-6">Analytics Dashboard</h1>

        <v-progress-linear
          v-if="loading"
          indeterminate
          color="primary"
          class="mb-4"
        />

        <v-alert v-if="error" type="error" class="mb-4">
          {{ error }}
        </v-alert>

        <template v-else>
          <!-- User Spending Card -->
          <v-row class="mb-6" v-if="userSpending">
            <v-col cols="12">
              <v-card>
                <v-card-title class="bg-primary text-white">
                  <v-icon start>mdi-cash-multiple</v-icon>
                  Your Spending Summary
                </v-card-title>
                <v-card-text class="pa-6">
                  <v-row>
                    <v-col cols="6" md="3">
                      <div class="text-center">
                        <div class="text-h4 font-weight-bold text-primary">
                          {{ userSpending.total_transactions || 0 }}
                        </div>
                        <div class="text-caption text-grey">Transactions</div>
                      </div>
                    </v-col>
                    <v-col cols="6" md="3">
                      <div class="text-center">
                        <div class="text-h4 font-weight-bold text-success">
                          {{ userSpending.total_tickets_purchased || 0 }}
                        </div>
                        <div class="text-caption text-grey">Tickets Purchased</div>
                      </div>
                    </v-col>
                    <v-col cols="6" md="3">
                      <div class="text-center">
                        <div class="text-h4 font-weight-bold text-info">
                          ${{ userSpending.total_spent || 0 }}
                        </div>
                        <div class="text-caption text-grey">Total Spent</div>
                      </div>
                    </v-col>
                    <v-col cols="6" md="3">
                      <div class="text-center">
                        <div class="text-h6 font-weight-bold">
                          {{ userSpending.favorite_event_type || 'N/A' }}
                        </div>
                        <div class="text-caption text-grey">Favorite Type</div>
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Upcoming Events Table -->
          <v-row class="mb-6">
            <v-col cols="12">
              <v-card>
                <v-card-title class="bg-success text-white">
                  <v-icon start>mdi-calendar-clock</v-icon>
                  Upcoming Events with Availability
                </v-card-title>
                <v-table v-if="upcomingEvents.length > 0">
                  <thead>
                    <tr>
                      <th>Event</th>
                      <th>Date</th>
                      <th>Venue</th>
                      <th>City</th>
                      <th>Available</th>
                      <th>Total</th>
                      <th>Price Range</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="event in upcomingEvents" :key="event.event_id">
                      <td class="font-weight-bold">{{ event.event_name }}</td>
                      <td>{{ new Date(event.date).toLocaleDateString() }}</td>
                      <td>{{ event.venue_name }}</td>
                      <td>{{ event.city }}</td>
                      <td>
                        <v-chip
                          :color="event.available_tickets > 0 ? 'success' : 'error'"
                          size="small"
                        >
                          {{ event.available_tickets }}
                        </v-chip>
                      </td>
                      <td>{{ event.total_tickets }}</td>
                      <td>
                        ${{ event.min_price }} - ${{ event.max_price }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
                <v-card-text v-else class="text-center py-6 text-grey">
                  No upcoming events
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Venue Performance Table -->
          <v-row>
            <v-col cols="12">
              <v-card>
                <v-card-title class="bg-info text-white">
                  <v-icon start>mdi-office-building</v-icon>
                  Venue Performance
                </v-card-title>
                <v-table v-if="venuePerformance.length > 0">
                  <thead>
                    <tr>
                      <th>Venue</th>
                      <th>City</th>
                      <th>Events</th>
                      <th>Tickets Available</th>
                      <th>Tickets Sold</th>
                      <th>Occupancy Rate</th>
                      <th>Revenue</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="venue in venuePerformance" :key="venue.venue_id">
                      <td class="font-weight-bold">{{ venue.venue_name }}</td>
                      <td>{{ venue.city }}</td>
                      <td>{{ venue.total_events }}</td>
                      <td>{{ venue.total_tickets_available }}</td>
                      <td>{{ venue.tickets_sold }}</td>
                      <td>
                        <v-chip
                          :color="venue.occupancy_rate > 80 ? 'success' : venue.occupancy_rate > 50 ? 'warning' : 'error'"
                          size="small"
                        >
                          {{ venue.occupancy_rate }}%
                        </v-chip>
                      </td>
                      <td class="font-weight-bold text-success">
                        ${{ venue.total_revenue }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
                <v-card-text v-else class="text-center py-6 text-grey">
                  No venue data available
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </v-container>
    </v-main>
  </v-app>
</template>
