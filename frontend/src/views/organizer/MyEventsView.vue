<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import { useVenuesStore } from '@/stores/venues'
import { format } from 'date-fns'

const appName = import.meta.env.VITE_APP_NAME
const router = useRouter()
const authStore = useAuthStore()
const eventsStore = useEventsStore()
const venuesStore = useVenuesStore()

const deleteDialog = ref(false)
const eventToDelete = ref<number | null>(null)

const myEvents = computed(() => {
  return eventsStore.events.filter(event => event.organizer_id === authStore.user?.user_id)
})

const formatDate = (dateStr: string) => {
  try {
    return format(new Date(dateStr), 'MMM dd, yyyy')
  } catch {
    return dateStr
  }
}

const getVenueName = (venueId: number) => {
  const venue = venuesStore.venues.find(v => v.venue_id === venueId)
  return venue?.name || `Venue #${venueId}`
}

const getEventTypeName = (typeId: number) => {
  const eventType = eventsStore.eventTypes.find(t => t.event_type_id === typeId)
  return eventType?.name || `Type #${typeId}`
}

const getEventStatus = (dateStr: string) => {
  const eventDate = new Date(dateStr)
  const now = new Date()
  return eventDate >= now ? 'Upcoming' : 'Past'
}

const getStatusColor = (dateStr: string) => {
  return getEventStatus(dateStr) === 'Upcoming' ? 'success' : 'grey'
}

const handleDelete = async () => {
  if (!eventToDelete.value) return

  try {
    await eventsStore.deleteEvent(eventToDelete.value)
    deleteDialog.value = false
    eventToDelete.value = null
  } catch (error) {
    console.error('Failed to delete event:', error)
  }
}

const confirmDelete = (eventId: number) => {
  eventToDelete.value = eventId
  deleteDialog.value = true
}

onMounted(async () => {
  await eventsStore.fetchEvents()
  await eventsStore.fetchEventTypes()
  await venuesStore.fetchVenues()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }} - My Events</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/organizer/dashboard">Dashboard</v-btn>
        <v-btn to="/organizer/create-event">Create Event</v-btn>
        <v-btn @click="authStore.logout">Logout</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <div class="d-flex justify-space-between align-center mb-6">
          <h1 class="text-h3">My Events</h1>
          <v-btn color="primary" size="large" to="/organizer/create-event">
            <v-icon start>mdi-plus-circle</v-icon>
            Create New Event
          </v-btn>
        </div>

        <v-progress-linear
          v-if="eventsStore.loading"
          indeterminate
          color="primary"
          class="mb-4"
        />

        <v-alert
          v-else-if="eventsStore.error"
          type="error"
          class="mb-4"
        >
          {{ eventsStore.error }}
        </v-alert>

        <div v-else-if="myEvents.length === 0" class="text-center py-12">
          <v-icon size="80" color="grey-lighten-1">mdi-calendar-plus</v-icon>
          <p class="text-h5 mt-4 text-grey">No events yet</p>
          <p class="text-body-1 text-grey mb-6">Create your first event to get started!</p>
          <v-btn color="primary" size="large" to="/organizer/create-event">
            <v-icon start>mdi-plus-circle</v-icon>
            Create Your First Event
          </v-btn>
        </div>

        <v-card v-else>
          <v-table>
            <thead>
              <tr>
                <th>Event Name</th>
                <th>Date</th>
                <th>Venue</th>
                <th>Type</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="event in myEvents" :key="event.event_id">
                <td class="font-weight-bold">{{ event.name }}</td>
                <td>{{ formatDate(event.date) }}</td>
                <td>{{ getVenueName(event.venue_id) }}</td>
                <td>{{ getEventTypeName(event.event_type_id) }}</td>
                <td>
                  <v-chip
                    :color="getStatusColor(event.date)"
                    size="small"
                  >
                    {{ getEventStatus(event.date) }}
                  </v-chip>
                </td>
                <td>
                  <v-btn
                    icon
                    size="small"
                    color="primary"
                    variant="text"
                    :to="`/events/${event.event_id}`"
                  >
                    <v-icon>mdi-eye</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    size="small"
                    color="info"
                    variant="text"
                    :to="`/organizer/events/${event.event_id}/edit`"
                  >
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    size="small"
                    color="error"
                    variant="text"
                    @click="confirmDelete(event.event_id)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>

        <!-- Delete Confirmation Dialog -->
        <v-dialog v-model="deleteDialog" max-width="500">
          <v-card>
            <v-card-title class="bg-error text-white">
              Confirm Delete
            </v-card-title>
            <v-card-text class="pa-4">
              <p class="text-body-1">Are you sure you want to delete this event?</p>
              <p class="text-body-2 text-grey mt-2">This action cannot be undone.</p>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn
                variant="text"
                @click="deleteDialog = false"
              >
                Cancel
              </v-btn>
              <v-btn
                color="error"
                variant="flat"
                @click="handleDelete"
                :loading="eventsStore.loading"
              >
                Delete
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-container>
    </v-main>
  </v-app>
</template>
