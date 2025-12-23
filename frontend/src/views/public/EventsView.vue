<script setup lang="ts">
import { onMounted } from 'vue'
import { useEventsStore } from '@/stores/events'
import EventList from '@/components/events/EventList.vue'

const appName = import.meta.env.VITE_APP_NAME
const eventsStore = useEventsStore()

onMounted(() => {
  eventsStore.fetchEvents()
  eventsStore.fetchEventTypes()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title to="/">{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/">Home</v-btn>
        <v-btn to="/venues">Venues</v-btn>
        <v-btn to="/login">Login</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <h1 class="text-h3 mb-6">All Events</h1>

        <EventList
          :events="eventsStore.events"
          :loading="eventsStore.loading"
        />
      </v-container>
    </v-main>
  </v-app>
</template>
