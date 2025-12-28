<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import { useVenuesStore } from '@/stores/venues'

const appName = import.meta.env.VITE_APP_NAME
const router = useRouter()
const authStore = useAuthStore()
const eventsStore = useEventsStore()
const venuesStore = useVenuesStore()

const form = ref({
  name: '',
  date: '',
  venue_id: null as number | null,
  event_type_id: null as number | null,
})

const valid = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

const rules = {
  required: (v: any) => !!v || 'This field is required',
}

const handleSubmit = async () => {
  if (!valid.value || !form.value.venue_id || !form.value.event_type_id) {
    error.value = 'Please fill in all required fields'
    return
  }

  loading.value = true
  error.value = null

  try {
    // Convert datetime-local format to ISO 8601 format with seconds
    const dateTime = new Date(form.value.date)
    const isoDate = dateTime.toISOString()

    await eventsStore.createEvent({
      name: form.value.name,
      date: isoDate,
      venue_id: form.value.venue_id,
      event_type_id: form.value.event_type_id,
    })

    router.push('/organizer/my-events')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to create event'
    console.error('Failed to create event:', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await venuesStore.fetchVenues()
  await eventsStore.fetchEventTypes()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }} - Create Event</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/organizer/dashboard">Dashboard</v-btn>
        <v-btn to="/organizer/my-events">My Events</v-btn>
        <v-btn @click="authStore.logout">Logout</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="8" lg="6">
            <v-card>
              <v-card-title class="bg-primary text-white">
                <v-icon start>mdi-calendar-plus</v-icon>
                Create New Event
              </v-card-title>

              <v-card-text class="pa-6">
                <v-alert
                  v-if="error"
                  type="error"
                  variant="tonal"
                  class="mb-4"
                  closable
                  @click:close="error = null"
                >
                  {{ error }}
                </v-alert>

                <v-form v-model="valid" @submit.prevent="handleSubmit">
                  <v-text-field
                    v-model="form.name"
                    label="Event Name"
                    variant="outlined"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-text"
                    class="mb-3"
                    required
                  />

                  <v-text-field
                    v-model="form.date"
                    label="Event Date & Time"
                    type="datetime-local"
                    variant="outlined"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-calendar-clock"
                    class="mb-3"
                    hint="Select the date and time for your event"
                    required
                  />

                  <v-select
                    v-model="form.venue_id"
                    :items="venuesStore.venues"
                    item-title="name"
                    item-value="venue_id"
                    label="Venue"
                    variant="outlined"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-map-marker"
                    class="mb-3"
                    required
                  >
                    <template #item="{ props, item }">
                      <v-list-item v-bind="props">
                        <v-list-item-subtitle>
                          {{ item.raw.city }}, {{ item.raw.country }}
                        </v-list-item-subtitle>
                      </v-list-item>
                    </template>
                  </v-select>

                  <v-select
                    v-model="form.event_type_id"
                    :items="eventsStore.eventTypes"
                    item-title="name"
                    item-value="event_type_id"
                    label="Event Type"
                    variant="outlined"
                    :rules="[rules.required]"
                    prepend-inner-icon="mdi-tag"
                    class="mb-3"
                    required
                  />

                  <v-divider class="my-4" />

                  <div class="d-flex gap-3">
                    <v-btn
                      color="grey"
                      variant="outlined"
                      @click="router.push('/organizer/my-events')"
                      :disabled="loading"
                    >
                      Cancel
                    </v-btn>
                    <v-spacer />
                    <v-btn
                      color="primary"
                      type="submit"
                      :loading="loading"
                      :disabled="!valid || loading"
                      size="large"
                    >
                      <v-icon start>mdi-check</v-icon>
                      Create Event
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
