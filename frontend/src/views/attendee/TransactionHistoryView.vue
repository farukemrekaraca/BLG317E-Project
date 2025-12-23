<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
const appName = import.meta.env.VITE_APP_NAME
</script>
<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn @click="authStore.logout" to="/">Logout</v-btn>
      </template>
    </v-app-bar>
    <v-main>
      <v-container>
        <v-alert type="info">Coming soon!</v-alert>
      </v-container>
    </v-main>
  </v-app>
</template>
