<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const eventId = route.params.id
const appName = import.meta.env.VITE_APP_NAME
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
        <h1 class="text-h3 mb-6">Event Detail #{{ eventId }}</h1>
        <v-alert type="info">
          Event detail page - Coming soon!
        </v-alert>
      </v-container>
    </v-main>
  </v-app>
</template>
