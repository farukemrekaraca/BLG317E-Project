<script setup lang="ts">
const appName = import.meta.env.VITE_APP_NAME
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title to="/">{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/">Home</v-btn>
        <v-btn to="/events">Events</v-btn>
        <v-btn to="/login">Login</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <h1 class="text-h3 mb-6">Venues</h1>
        <v-alert type="info">
          Venues page - Coming soon! This will show a list of all venues.
        </v-alert>
      </v-container>
    </v-main>
  </v-app>
</template>
