<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTicketsStore } from '@/stores/tickets'
import { format } from 'date-fns'

const appName = import.meta.env.VITE_APP_NAME
const authStore = useAuthStore()
const ticketsStore = useTicketsStore()

const groupedTickets = computed(() => {
  const groups = new Map<string, typeof ticketsStore.myTickets>()

  ticketsStore.myTickets.forEach(ticket => {
    const key = `${ticket.event_id}-${ticket.event_name}`
    const existing = groups.get(key) || []
    existing.push(ticket)
    groups.set(key, existing)
  })

  return Array.from(groups.entries())
    .map(([, tickets]) => {
      const firstTicket = tickets[0]
      if (!firstTicket) return null

      return {
        eventId: firstTicket.event_id,
        eventName: firstTicket.event_name,
        eventDate: firstTicket.event_date,
        venueName: firstTicket.venue_name,
        tickets: tickets
      }
    })
    .filter((group): group is NonNullable<typeof group> => group !== null)
})

const formatDate = (dateStr: string) => {
  try {
    return format(new Date(dateStr), 'MMMM dd, yyyy')
  } catch {
    return dateStr
  }
}

onMounted(() => {
  ticketsStore.fetchMyTickets()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/events">Browse Events</v-btn>
        <v-btn to="/attendee/transactions">Transaction History</v-btn>
        <v-btn to="/attendee/profile">Profile</v-btn>
        <v-btn @click="authStore.logout">Logout</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <div class="d-flex justify-space-between align-center mb-6">
          <h1 class="text-h3">My Tickets</h1>
        </div>

        <v-progress-linear
          v-if="ticketsStore.loading"
          indeterminate
          color="primary"
          class="mb-4"
        />

        <v-alert
          v-else-if="ticketsStore.error"
          type="error"
          class="mb-4"
        >
          {{ ticketsStore.error }}
        </v-alert>

        <div v-else-if="ticketsStore.myTickets.length === 0" class="text-center py-12">
          <v-icon size="80" color="grey-lighten-1">mdi-ticket-outline</v-icon>
          <p class="text-h5 mt-4 text-grey">No tickets yet</p>
          <p class="text-body-1 text-grey mb-6">Browse events and purchase tickets to see them here</p>
          <v-btn color="primary" size="large" to="/events">
            <v-icon start>mdi-magnify</v-icon>
            Browse Events
          </v-btn>
        </div>

        <div v-else>
          <v-card
            v-for="group in groupedTickets"
            :key="group.eventId"
            class="mb-6"
          >
            <v-card-title class="bg-primary text-white">
              <div class="d-flex justify-space-between align-center w-100">
                <div>
                  <div class="text-h5">{{ group.eventName }}</div>
                  <div class="text-body-2 mt-1">
                    <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
                    {{ formatDate(group.eventDate) }}
                  </div>
                  <div class="text-body-2">
                    <v-icon size="small" class="mr-1">mdi-map-marker</v-icon>
                    {{ group.venueName }}
                  </div>
                </div>
                <v-chip color="white" variant="flat">
                  {{ group.tickets.length }} {{ group.tickets.length === 1 ? 'Ticket' : 'Tickets' }}
                </v-chip>
              </div>
            </v-card-title>

            <v-list>
              <v-list-item
                v-for="ticket in group.tickets"
                :key="ticket.ticket_id"
                class="px-6"
              >
                <template #prepend>
                  <v-icon color="primary">mdi-ticket-confirmation</v-icon>
                </template>

                <v-list-item-title>
                  Ticket #{{ ticket.ticket_id }}
                </v-list-item-title>

                <v-list-item-subtitle>
                  {{ ticket.ticket_type_name }} - Seat {{ ticket.seat_id }}
                </v-list-item-subtitle>

                <template #append>
                  <v-chip
                    :color="ticket.status === 'sold' ? 'success' : 'grey'"
                    size="small"
                  >
                    {{ ticket.status }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>
