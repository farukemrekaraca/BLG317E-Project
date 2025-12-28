<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import { useTicketsStore } from '@/stores/tickets'

const appName = import.meta.env.VITE_APP_NAME
const authStore = useAuthStore()
const eventsStore = useEventsStore()
const ticketsStore = useTicketsStore()

const myEvents = computed(() => {
  return eventsStore.events.filter(event => event.organizer_id === authStore.user?.user_id)
})

const upcomingEvents = computed(() => {
  const now = new Date()
  return myEvents.value.filter(event => new Date(event.date) >= now)
})

const pastEvents = computed(() => {
  const now = new Date()
  return myEvents.value.filter(event => new Date(event.date) < now)
})

const stats = computed(() => {
  return {
    totalEvents: myEvents.value.length,
    upcomingEvents: upcomingEvents.value.length,
    pastEvents: pastEvents.value.length,
    totalTickets: ticketsStore.tickets.length,
  }
})

onMounted(async () => {
  await eventsStore.fetchEvents()
  await eventsStore.fetchEventTypes()
  await ticketsStore.fetchTickets()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }} - Organizer</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/organizer/my-events">My Events</v-btn>
        <v-btn to="/organizer/create-event">Create Event</v-btn>
        <v-btn @click="authStore.logout">Logout</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <div class="mb-6">
          <h1 class="text-h3 mb-2">
            Welcome back, {{ authStore.user?.name }}!
          </h1>
          <p class="text-subtitle-1 text-grey">Here's an overview of your events</p>
        </div>

        <!-- Statistics Cards -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6" md="3">
            <v-card color="primary" dark>
              <v-card-text>
                <div class="d-flex justify-space-between align-center">
                  <div>
                    <div class="text-h4 font-weight-bold">{{ stats.totalEvents }}</div>
                    <div class="text-subtitle-2">Total Events</div>
                  </div>
                  <v-icon size="48">mdi-calendar-multiple</v-icon>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card color="success" dark>
              <v-card-text>
                <div class="d-flex justify-space-between align-center">
                  <div>
                    <div class="text-h4 font-weight-bold">{{ stats.upcomingEvents }}</div>
                    <div class="text-subtitle-2">Upcoming Events</div>
                  </div>
                  <v-icon size="48">mdi-calendar-clock</v-icon>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card color="info" dark>
              <v-card-text>
                <div class="d-flex justify-space-between align-center">
                  <div>
                    <div class="text-h4 font-weight-bold">{{ stats.pastEvents }}</div>
                    <div class="text-subtitle-2">Past Events</div>
                  </div>
                  <v-icon size="48">mdi-calendar-check</v-icon>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card color="secondary" dark>
              <v-card-text>
                <div class="d-flex justify-space-between align-center">
                  <div>
                    <div class="text-h4 font-weight-bold">{{ stats.totalTickets }}</div>
                    <div class="text-subtitle-2">Total Tickets</div>
                  </div>
                  <v-icon size="48">mdi-ticket-confirmation</v-icon>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Quick Actions -->
        <v-row class="mb-6">
          <v-col cols="12">
            <v-card>
              <v-card-title class="bg-grey-darken-3 text-white">
                Quick Actions
              </v-card-title>
              <v-card-text class="pa-4">
                <v-row>
                  <v-col cols="12" sm="6" md="3">
                    <v-btn
                      color="primary"
                      size="large"
                      block
                      to="/organizer/create-event"
                    >
                      <v-icon start>mdi-plus-circle</v-icon>
                      Create Event
                    </v-btn>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-btn
                      color="info"
                      size="large"
                      block
                      to="/organizer/my-events"
                    >
                      <v-icon start>mdi-calendar-multiple</v-icon>
                      Manage Events
                    </v-btn>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-btn
                      color="success"
                      size="large"
                      block
                      to="/organizer/analytics"
                    >
                      <v-icon start>mdi-chart-line</v-icon>
                      View Analytics
                    </v-btn>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-btn
                      color="secondary"
                      size="large"
                      block
                      to="/events"
                    >
                      <v-icon start>mdi-eye</v-icon>
                      Browse All Events
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Upcoming Events List -->
        <v-row v-if="upcomingEvents.length > 0">
          <v-col cols="12">
            <v-card>
              <v-card-title class="bg-primary text-white">
                Upcoming Events
              </v-card-title>
              <v-list>
                <v-list-item
                  v-for="event in upcomingEvents.slice(0, 5)"
                  :key="event.event_id"
                  :to="`/organizer/events/${event.event_id}`"
                >
                  <template #prepend>
                    <v-icon color="primary">mdi-calendar</v-icon>
                  </template>
                  <v-list-item-title>{{ event.name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ new Date(event.date).toLocaleDateString() }}
                  </v-list-item-subtitle>
                  <template #append>
                    <v-chip size="small" color="success">
                      Upcoming
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <v-card-actions v-if="upcomingEvents.length > 5">
                <v-spacer />
                <v-btn color="primary" variant="text" to="/organizer/my-events">
                  View All Events
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- Empty State -->
        <v-row v-if="myEvents.length === 0 && !eventsStore.loading">
          <v-col cols="12">
            <v-card class="text-center py-12">
              <v-icon size="80" color="grey-lighten-1">mdi-calendar-plus</v-icon>
              <p class="text-h5 mt-4 text-grey">No events yet</p>
              <p class="text-body-1 text-grey mb-6">Create your first event to get started!</p>
              <v-btn color="primary" size="large" to="/organizer/create-event">
                <v-icon start>mdi-plus-circle</v-icon>
                Create Your First Event
              </v-btn>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
