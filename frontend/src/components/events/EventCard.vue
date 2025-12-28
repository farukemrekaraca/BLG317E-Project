<script setup lang="ts">
import { computed } from 'vue'
import { format } from 'date-fns'
import { useVenuesStore } from '@/stores/venues'
import { useEventsStore } from '@/stores/events'
import type { EventResponse } from '@/types/event'

const props = defineProps<{
  event: EventResponse
}>()

const venuesStore = useVenuesStore()
const eventsStore = useEventsStore()

const formattedDate = computed(() => {
  try {
    return format(new Date(props.event.date), 'MMM dd, yyyy')
  } catch {
    return props.event.date
  }
})

const venueName = computed(() => {
  const venue = venuesStore.venues.find(v => v.venue_id === props.event.venue_id)
  return venue?.name || `Venue #${props.event.venue_id}`
})

const eventTypeName = computed(() => {
  const eventType = eventsStore.eventTypes.find(t => t.event_type_id === props.event.event_type_id)
  return eventType?.name || `Type #${props.event.event_type_id}`
})
</script>

<template>
  <v-card
    :to="`/events/${event.event_id}`"
    hover
    class="event-card"
  >
    <v-card-title class="text-h6">
      {{ event.name }}
    </v-card-title>

    <v-card-subtitle>
      <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
      {{ formattedDate }}
    </v-card-subtitle>

    <v-card-text>
      <div class="d-flex align-center mb-2">
        <v-icon size="small" class="mr-2">mdi-map-marker</v-icon>
        <span class="text-body-2">{{ venueName }}</span>
      </div>
      <div class="d-flex align-center">
        <v-icon size="small" class="mr-2">mdi-tag</v-icon>
        <span class="text-body-2">{{ eventTypeName }}</span>
      </div>
    </v-card-text>

    <v-card-actions>
      <v-btn
        color="primary"
        variant="text"
        :to="`/events/${event.event_id}`"
      >
        View Details
        <v-icon end>mdi-arrow-right</v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.event-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.event-card :deep(.v-card-text) {
  flex-grow: 1;
}
</style>
