<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventsStore } from '@/stores/events'
import { useVenuesStore } from '@/stores/venues'
import { useTicketsStore } from '@/stores/tickets'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'
import type { TicketType } from '@/types/ticket'
import CartDrawer from '@/components/cart/CartDrawer.vue'

const route = useRoute()
const router = useRouter()
const appName = import.meta.env.VITE_APP_NAME

const eventsStore = useEventsStore()
const venuesStore = useVenuesStore()
const ticketsStore = useTicketsStore()
const cartStore = useCartStore()
const authStore = useAuthStore()

const eventId = Number(route.params.id)
const selectedTicketTypeId = ref<number | null>(null)
const showCartDrawer = ref(false)

const formattedDate = computed(() => {
  if (!eventsStore.currentEvent) return ''
  try {
    return format(new Date(eventsStore.currentEvent.date), 'MMMM dd, yyyy')
  } catch {
    return eventsStore.currentEvent.date
  }
})

const availableTicketsCount = computed(() => {
  return ticketsStore.tickets.filter(t => t.status === 'available').length
})

const availableTicketsByType = computed(() => {
  const ticketMap = new Map<number, typeof ticketsStore.tickets>()
  ticketsStore.tickets
    .filter(t => t.status === 'available')
    .forEach(ticket => {
      const existing = ticketMap.get(ticket.ticket_type_id) || []
      existing.push(ticket)
      ticketMap.set(ticket.ticket_type_id, existing)
    })
  return ticketMap
})

const selectedTicketType = computed(() => {
  if (!selectedTicketTypeId.value) return null
  return ticketsStore.ticketTypes.find(tt => tt.ticket_type_id === selectedTicketTypeId.value)
})

const canAddToCart = computed(() => {
  if (!selectedTicketTypeId.value) return false
  const tickets = availableTicketsByType.value.get(selectedTicketTypeId.value)
  return tickets !== undefined && tickets.length > 0
})

const handleAddToCart = () => {
  if (!authStore.isAuthenticated) {
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }

  if (!canAddToCart.value || !selectedTicketType.value || !eventsStore.currentEvent || !venuesStore.currentVenue) {
    return
  }

  const availableTickets = availableTicketsByType.value.get(selectedTicketTypeId.value!)
  if (!availableTickets || availableTickets.length === 0) {
    cartStore.error = 'No tickets available for this type'
    return
  }

  const ticket = availableTickets[0]
  if (!ticket) {
    cartStore.error = 'Failed to select ticket'
    return
  }

  const added = cartStore.addToCart({
    ticket,
    ticketType: selectedTicketType.value,
    eventId: eventsStore.currentEvent.event_id,
    eventName: eventsStore.currentEvent.name,
    eventDate: eventsStore.currentEvent.date,
    venueName: venuesStore.currentVenue.name,
  })

  if (added) {
    showCartDrawer.value = true
    selectedTicketTypeId.value = null
  }
}

onMounted(async () => {
  // Fetch event details
  const event = await eventsStore.fetchEventById(eventId)

  if (event) {
    // Fetch venue details
    await venuesStore.fetchVenueById(event.venue_id)

    // Fetch ticket types and tickets for this event
    await ticketsStore.fetchTicketTypes(eventId)
    await ticketsStore.fetchTickets({ event_id: eventId })
  }
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
        <v-btn to="/events">Back to Events</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-progress-linear
          v-if="eventsStore.loading"
          indeterminate
          color="primary"
          class="mb-4"
        />

        <div v-else-if="eventsStore.currentEvent">
          <!-- Event Header -->
          <v-card class="mb-6">
            <v-card-title class="text-h3">
              {{ eventsStore.currentEvent.name }}
            </v-card-title>
            <v-card-subtitle class="text-h6 mt-2">
              <v-icon class="mr-2">mdi-calendar</v-icon>
              {{ formattedDate }}
            </v-card-subtitle>
          </v-card>

          <v-row>
            <!-- Venue Information -->
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>Venue Information</v-card-title>
                <v-card-text v-if="venuesStore.currentVenue">
                  <div class="mb-2">
                    <v-icon class="mr-2">mdi-map-marker</v-icon>
                    <strong>{{ venuesStore.currentVenue.name }}</strong>
                  </div>
                  <div class="mb-2">
                    {{ venuesStore.currentVenue.address }}
                  </div>
                  <div class="mb-2">
                    {{ venuesStore.currentVenue.city }}, {{ venuesStore.currentVenue.country }}
                  </div>
                  <div class="mb-2">
                    <v-icon class="mr-2">mdi-seat</v-icon>
                    Capacity: {{ venuesStore.currentVenue.seat_count }} seats
                  </div>
                </v-card-text>
                <v-card-text v-else>
                  <v-progress-circular indeterminate />
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Ticket Availability -->
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>Ticket Availability</v-card-title>
                <v-card-text>
                  <div class="text-h4 mb-4" :class="availableTicketsCount > 0 ? 'text-success' : 'text-error'">
                    {{ availableTicketsCount }} Available
                  </div>

                  <v-alert
                    v-if="cartStore.error"
                    type="error"
                    variant="tonal"
                    class="mb-4"
                    closable
                    @click:close="cartStore.error = null"
                  >
                    {{ cartStore.error }}
                  </v-alert>

                  <!-- Ticket Type Selection -->
                  <div v-if="availableTicketsCount > 0" class="mb-4">
                    <div class="text-subtitle-1 font-weight-bold mb-2">Select Ticket Type</div>
                    <v-list lines="two" density="compact">
                      <v-list-item
                        v-for="ticketType in ticketsStore.ticketTypes"
                        :key="ticketType.ticket_type_id"
                        :class="{ 'bg-grey-lighten-4': selectedTicketTypeId === ticketType.ticket_type_id }"
                        @click="selectedTicketTypeId = ticketType.ticket_type_id"
                      >
                        <template #prepend>
                          <v-radio
                            :model-value="selectedTicketTypeId"
                            :value="ticketType.ticket_type_id"
                            color="primary"
                          />
                        </template>
                        <v-list-item-title>{{ ticketType.name }}</v-list-item-title>
                        <v-list-item-subtitle>
                          <span class="font-weight-bold text-primary">
                            ${{ ticketType.price.toFixed(2) }}
                          </span>
                          <span class="text-grey ml-2">
                            ({{ availableTicketsByType.get(ticketType.ticket_type_id)?.length || 0 }} available)
                          </span>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </div>

                  <v-btn
                    v-if="availableTicketsCount > 0"
                    color="primary"
                    size="large"
                    block
                    :disabled="!canAddToCart"
                    @click="handleAddToCart"
                  >
                    <v-icon start>mdi-cart-plus</v-icon>
                    Add to Cart
                  </v-btn>

                  <v-alert v-else type="warning" class="mt-4">
                    Sold Out
                  </v-alert>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <v-alert v-else-if="eventsStore.error" type="error" class="mt-4">
          {{ eventsStore.error }}
        </v-alert>
      </v-container>
    </v-main>

    <!-- Cart Drawer -->
    <CartDrawer v-model="showCartDrawer" />
  </v-app>
</template>
