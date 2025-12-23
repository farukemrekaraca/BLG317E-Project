<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const appName = import.meta.env.VITE_APP_NAME
</script>

<template>
  <v-app>
    <v-app-bar color="primary" prominent>
      <v-app-bar-title>{{ appName }}</v-app-bar-title>

      <template v-slot:append>
        <v-btn to="/events">Events</v-btn>
        <v-btn to="/venues">Venues</v-btn>
        <v-btn to="/login" variant="outlined">Login</v-btn>
        <v-btn to="/register" variant="tonal">Register</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12" class="text-center py-16">
            <h1 class="text-h2 mb-4">Welcome to Event Ticketing Platform</h1>
            <p class="text-h5 mb-8">Discover and book tickets for amazing events</p>
            <v-btn
              to="/events"
              color="primary"
              size="x-large"
            >
              Browse Events
            </v-btn>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="4">
            <v-card>
              <v-card-title>Easy Booking</v-card-title>
              <v-card-text>Find and book tickets for your favorite events in just a few clicks</v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card>
              <v-card-title>Secure Payments</v-card-title>
              <v-card-text>Your payments are safe with our secure checkout system</v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card>
              <v-card-title>24/7 Support</v-card-title>
              <v-card-text>Get help whenever you need it from our support team</v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
