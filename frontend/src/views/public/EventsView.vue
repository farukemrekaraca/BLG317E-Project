<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useEventsStore } from '@/stores/events'
import { useVenuesStore } from '@/stores/venues'
import { useCartStore } from '@/stores/cart'
import EventList from '@/components/events/EventList.vue'
import CartDrawer from '@/components/cart/CartDrawer.vue'

const appName = import.meta.env.VITE_APP_NAME
const eventsStore = useEventsStore()
const venuesStore = useVenuesStore()
const cartStore = useCartStore()
const showCartDrawer = ref(false)

onMounted(() => {
  eventsStore.fetchEvents()
  eventsStore.fetchEventTypes()
  venuesStore.fetchVenues()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title to="/">{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn
          icon
          @click="showCartDrawer = true"
          class="mr-2"
        >
          <v-badge
            :content="cartStore.itemCount"
            :model-value="cartStore.itemCount > 0"
            color="error"
          >
            <v-icon>mdi-cart</v-icon>
          </v-badge>
        </v-btn>
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

    <!-- Cart Drawer -->
    <CartDrawer v-model="showCartDrawer" />
  </v-app>
</template>
