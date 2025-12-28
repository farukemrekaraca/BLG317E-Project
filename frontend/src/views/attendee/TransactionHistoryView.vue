<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTransactionsStore } from '@/stores/transactions'
import { useTicketsStore } from '@/stores/tickets'
import { format } from 'date-fns'

const appName = import.meta.env.VITE_APP_NAME
const authStore = useAuthStore()
const transactionsStore = useTransactionsStore()
const ticketsStore = useTicketsStore()

const selectedTransactionId = ref<number | null>(null)
const showDetailsDialog = ref(false)

// Create a map of ticket ID to ticket details
const ticketDetailsMap = computed(() => {
  const map = new Map()
  ticketsStore.myTickets.forEach(ticket => {
    map.set(ticket.ticket_id, ticket)
  })
  return map
})

const enrichedTransactionItems = computed(() => {
  return transactionsStore.currentTransactionItems.map(item => {
    const ticketDetails = ticketDetailsMap.value.get(item.ticket_id)
    return {
      ...item,
      event_name: ticketDetails?.event_name || 'Unknown Event',
      ticket_type_name: ticketDetails?.ticket_type_name || 'Unknown Type',
      seat_id: ticketDetails?.seat_id
    }
  })
})

const formatDate = (dateStr: string) => {
  try {
    return format(new Date(dateStr), 'MMMM dd, yyyy HH:mm')
  } catch {
    return dateStr
  }
}

const formatPaymentMethod = (method: string) => {
  return method.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const getPaymentMethodColor = (method: string) => {
  switch (method) {
    case 'credit_card': return 'primary'
    case 'debit_card': return 'info'
    case 'cash': return 'success'
    default: return 'grey'
  }
}

const totalSpent = computed(() => {
  return transactionsStore.transactions.reduce((sum, t) => sum + t.price, 0)
})

const handleViewDetails = async (transactionId: number) => {
  selectedTransactionId.value = transactionId
  await transactionsStore.fetchTransactionById(transactionId)
  await transactionsStore.fetchTransactionItems(transactionId)
  showDetailsDialog.value = true
}

onMounted(async () => {
  await transactionsStore.fetchMyTransactions()
  // Also fetch my tickets to get event and ticket type information
  await ticketsStore.fetchMyTickets()
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/events">Browse Events</v-btn>
        <v-btn to="/attendee/my-tickets">My Tickets</v-btn>
        <v-btn to="/attendee/profile">Profile</v-btn>
        <v-btn @click="authStore.logout">Logout</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <div class="d-flex justify-space-between align-center mb-6">
          <h1 class="text-h3">Transaction History</h1>
          <v-chip color="primary" size="large">
            Total Spent: ${{ totalSpent.toFixed(2) }}
          </v-chip>
        </div>

        <v-progress-linear
          v-if="transactionsStore.loading"
          indeterminate
          color="primary"
          class="mb-4"
        />

        <v-alert
          v-else-if="transactionsStore.error"
          type="error"
          class="mb-4"
        >
          {{ transactionsStore.error }}
        </v-alert>

        <div v-else-if="transactionsStore.transactions.length === 0" class="text-center py-12">
          <v-icon size="80" color="grey-lighten-1">mdi-receipt-text-outline</v-icon>
          <p class="text-h5 mt-4 text-grey">No transactions yet</p>
          <p class="text-body-1 text-grey mb-6">Your purchase history will appear here</p>
          <v-btn color="primary" size="large" to="/events">
            <v-icon start>mdi-ticket-outline</v-icon>
            Browse Events
          </v-btn>
        </div>

        <v-card v-else>
          <v-table>
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Date</th>
                <th>Payment Method</th>
                <th>Installments</th>
                <th>Amount</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="transaction in transactionsStore.transactions"
                :key="transaction.transaction_id"
              >
                <td>
                  <v-chip size="small" variant="outlined">
                    #{{ transaction.transaction_id }}
                  </v-chip>
                </td>
                <td>{{ formatDate(transaction.date) }}</td>
                <td>
                  <v-chip
                    :color="getPaymentMethodColor(transaction.payment_method)"
                    size="small"
                  >
                    {{ formatPaymentMethod(transaction.payment_method) }}
                  </v-chip>
                </td>
                <td>
                  <span v-if="transaction.installment_period">
                    {{ transaction.installment_period }} months
                  </span>
                  <span v-else class="text-grey">-</span>
                </td>
                <td class="font-weight-bold text-success">
                  ${{ transaction.price.toFixed(2) }}
                </td>
                <td>
                  <v-btn
                    size="small"
                    color="primary"
                    variant="tonal"
                    @click="handleViewDetails(transaction.transaction_id)"
                  >
                    <v-icon start>mdi-eye</v-icon>
                    View Details
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>

        <!-- Transaction Details Dialog -->
        <v-dialog v-model="showDetailsDialog" max-width="600">
          <v-card v-if="transactionsStore.currentTransaction">
            <v-card-title class="bg-primary text-white">
              <div class="d-flex justify-space-between align-center w-100">
                <span>Transaction #{{ transactionsStore.currentTransaction.transaction_id }}</span>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="showDetailsDialog = false"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </div>
            </v-card-title>

            <v-card-text class="pa-4">
              <div class="mb-4">
                <div class="text-subtitle-2 text-grey mb-1">Date & Time</div>
                <div class="text-body-1">
                  {{ formatDate(transactionsStore.currentTransaction.date) }}
                </div>
              </div>

              <v-divider class="my-3" />

              <div class="mb-4">
                <div class="text-subtitle-2 text-grey mb-1">Receipt ID</div>
                <div class="text-body-1 font-weight-bold">
                  {{ transactionsStore.currentTransaction.receipt_id }}
                </div>
              </div>

              <v-divider class="my-3" />

              <div class="mb-4">
                <div class="text-subtitle-2 text-grey mb-1">Payment Method</div>
                <v-chip
                  :color="getPaymentMethodColor(transactionsStore.currentTransaction.payment_method)"
                  size="small"
                >
                  {{ formatPaymentMethod(transactionsStore.currentTransaction.payment_method) }}
                </v-chip>
                <span v-if="transactionsStore.currentTransaction.installment_period" class="ml-2">
                  ({{ transactionsStore.currentTransaction.installment_period }} months)
                </span>
              </div>

              <v-divider class="my-3" />

              <div class="mb-4">
                <div class="text-subtitle-2 text-grey mb-2">Tickets Purchased</div>
                <v-list density="compact">
                  <v-list-item
                    v-for="item in enrichedTransactionItems"
                    :key="item.ticket_id"
                    class="px-0"
                  >
                    <template #prepend>
                      <v-icon color="primary">mdi-ticket</v-icon>
                    </template>
                    <v-list-item-title>
                      {{ item.event_name }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      Ticket #{{ item.ticket_id }} - {{ item.ticket_type_name }}
                      <span v-if="item.seat_id"> - Seat {{ item.seat_id }}</span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
                <div class="text-caption text-grey mt-2">
                  Total: {{ enrichedTransactionItems.length }} ticket(s)
                </div>
              </div>

              <v-divider class="my-3" />

              <div class="d-flex justify-space-between align-center">
                <div class="text-h6">Total Amount</div>
                <div class="text-h5 font-weight-bold text-success">
                  ${{ transactionsStore.currentTransaction.price.toFixed(2) }}
                </div>
              </div>
            </v-card-text>

            <v-card-actions>
              <v-spacer />
              <v-btn
                color="primary"
                variant="text"
                @click="showDetailsDialog = false"
              >
                Close
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-container>
    </v-main>
  </v-app>
</template>
