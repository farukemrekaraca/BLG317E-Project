<script setup lang="ts">
import EventCard from './EventCard.vue'
import type { EventResponse } from '@/types/event'

defineProps<{
  events: EventResponse[]
  loading?: boolean
}>()
</script>

<template>
  <div>
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <v-row v-if="!loading && events.length > 0">
      <v-col
        v-for="event in events"
        :key="event.event_id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <EventCard :event="event" />
      </v-col>
    </v-row>

    <v-alert
      v-else-if="!loading && events.length === 0"
      type="info"
      variant="tonal"
      class="mt-4"
    >
      <template #title>No Events Found</template>
      No events are currently available. Check back later!
    </v-alert>
  </div>
</template>
