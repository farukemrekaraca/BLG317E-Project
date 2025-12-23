<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useEventsStore } from '@/stores/events'
import { useVenuesStore } from '@/stores/venues'
import { useTicketsStore } from '@/stores/tickets'
import { format } from 'date-fns'

const route = useRoute()
const appName = import.meta.env.VITE_APP_NAME

const eventsStore = useEventsStore()
const venuesStore = useVenuesStore()
const ticketsStore = useTicketsStore()

const eventId = Number(route.params.id)

const formattedDate = computed(() => {
  if (!eventsStore.currentEvent) return ''
  try {
    return format(new Date(eventsStore.currentEvent.date), 'MMMM dd, yyyy')
  } catch {
    return eventsStore.currentEvent.date
  }
})

const availableTicketsCount = computed(() => {
  return ticketsStore.tickets.filter(t => t.status === 'available').length
})

onMounted(async () => {
  // Fetch event details
  const event = await eventsStore.fetchEventById(eventId)

  if (event) {
    // Fetch venue details
    await venuesStore.fetchVenueById(event.venue_id)

    // Fetch ticket types and tickets for this event
    await ticketsStore.fetchTicketTypes(eventId)
    await ticketsStore.fetchTickets({ event_id: eventId })
  }
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title to="/">{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/events">Back to Events</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-progress-linear
          v-if="eventsStore.loading"
          indeterminate
          color="primary"
          class="mb-4"
        />

        <div v-else-if="eventsStore.currentEvent">
          <!-- Event Header -->
          <v-card class="mb-6">
            <v-card-title class="text-h3">
              {{ eventsStore.currentEvent.name }}
            </v-card-title>
            <v-card-subtitle class="text-h6 mt-2">
              <v-icon class="mr-2">mdi-calendar</v-icon>
              {{ formattedDate }}
            </v-card-subtitle>
          </v-card>

          <v-row>
            <!-- Venue Information -->
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>Venue Information</v-card-title>
                <v-card-text v-if="venuesStore.currentVenue">
                  <div class="mb-2">
                    <v-icon class="mr-2">mdi-map-marker</v-icon>
                    <strong>{{ venuesStore.currentVenue.name }}</strong>
                  </div>
                  <div class="mb-2">
                    {{ venuesStore.currentVenue.address }}
                  </div>
                  <div class="mb-2">
                    {{ venuesStore.currentVenue.city }}, {{ venuesStore.currentVenue.country }}
                  </div>
                  <div class="mb-2">
                    <v-icon class="mr-2">mdi-seat</v-icon>
                    Capacity: {{ venuesStore.currentVenue.seat_count }} seats
                  </div>
                </v-card-text>
                <v-card-text v-else>
                  <v-progress-circular indeterminate />
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Ticket Availability -->
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>Ticket Availability</v-card-title>
                <v-card-text>
                  <div class="text-h4 mb-4" :class="availableTicketsCount > 0 ? 'text-success' : 'text-error'">
                    {{ availableTicketsCount }} Available
                  </div>

                  <v-list v-if="ticketsStore.ticketTypes.length > 0">
                    <v-list-item
                      v-for="ticketType in ticketsStore.ticketTypes"
                      :key="ticketType.ticket_type_id"
                    >
                      <v-list-item-title>{{ ticketType.name }}</v-list-item-title>
                      <v-list-item-subtitle>
                        ${{ ticketType.price.toFixed(2) }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>

                  <v-btn
                    v-if="availableTicketsCount > 0"
                    color="primary"
                    size="large"
                    block
                    class="mt-4"
                  >
                    <v-icon start>mdi-ticket</v-icon>
                    Buy Tickets
                  </v-btn>

                  <v-alert v-else type="warning" class="mt-4">
                    Sold Out
                  </v-alert>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <v-alert v-else-if="eventsStore.error" type="error" class="mt-4">
          {{ eventsStore.error }}
        </v-alert>
      </v-container>
    </v-main>
  </v-app>
</template>
