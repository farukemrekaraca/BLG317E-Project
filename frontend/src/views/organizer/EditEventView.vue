<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import { useVenuesStore } from '@/stores/venues'

const appName = import.meta.env.VITE_APP_NAME
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const eventsStore = useEventsStore()
const venuesStore = useVenuesStore()

const eventId = Number(route.params.id)

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

const loadEvent = async () => {
  const event = await eventsStore.fetchEventById(eventId)
  if (event) {
    form.value.name = event.name
    // Convert datetime to datetime-local format (YYYY-MM-DDTHH:mm)
    const date = new Date(event.date)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    form.value.date = `${year}-${month}-${day}T${hours}:${minutes}`
    form.value.venue_id = event.venue_id
    form.value.event_type_id = event.event_type_id
  }
}

const handleSubmit = async () => {
  if (!valid.value || !form.value.venue_id || !form.value.event_type_id) {
    error.value = 'Please fill in all required fields'
    return
  }

  loading.value = true
  error.value = null

  try {
    const dateTime = new Date(form.value.date)
    const isoDate = dateTime.toISOString()

    await eventsStore.updateEvent(eventId, {
      name: form.value.name,
      date: isoDate,
      venue_id: form.value.venue_id,
      event_type_id: form.value.event_type_id,
    })

    router.push('/organizer/my-events')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to update event'
    console.error('Failed to update event:', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await venuesStore.fetchVenues()
  await eventsStore.fetchEventTypes()
  await loadEvent()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }} - Edit Event</v-app-bar-title>
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
                <v-icon start>mdi-pencil</v-icon>
                Edit Event
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

                <v-progress-linear
                  v-if="eventsStore.loading && !form.name"
                  indeterminate
                  color="primary"
                  class="mb-4"
                />

                <v-form v-else v-model="valid" @submit.prevent="handleSubmit">
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
                      Save Changes
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
