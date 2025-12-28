<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'

const appName = import.meta.env.VITE_APP_NAME
const authStore = useAuthStore()

const userRoleName = computed(() => {
  if (!authStore.user) return 'Unknown'
  switch (authStore.user.type_id) {
    case 1: return 'Administrator'
    case 2: return 'Organizer'
    case 3: return 'Venue Owner'
    case 4: return 'Attendee'
    default: return 'Unknown'
  }
})

const userRoleColor = computed(() => {
  if (!authStore.user) return 'grey'
  switch (authStore.user.type_id) {
    case 1: return 'error'
    case 2: return 'primary'
    case 3: return 'info'
    case 4: return 'success'
    default: return 'grey'
  }
})

const formattedJoinDate = computed(() => {
  if (!authStore.user) return ''
  try {
    return format(new Date(authStore.user.created_at), 'MMMM dd, yyyy')
  } catch {
    return authStore.user.created_at
  }
})
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-title>{{ appName }}</v-app-bar-title>
      <template v-slot:append>
        <v-btn to="/events">Browse Events</v-btn>
        <v-btn to="/attendee/my-tickets">My Tickets</v-btn>
        <v-btn to="/attendee/transactions">Transactions</v-btn>
        <v-btn @click="authStore.logout">Logout</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container>
        <div class="d-flex justify-space-between align-center mb-6">
          <h1 class="text-h3">My Profile</h1>
        </div>

        <v-row>
          <v-col cols="12" md="8">
            <v-card>
              <v-card-title class="bg-primary text-white d-flex align-center">
                <v-icon size="large" class="mr-3">mdi-account-circle</v-icon>
                User Information
              </v-card-title>

              <v-card-text class="pa-6">
                <v-list lines="two">
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="primary">mdi-account</v-icon>
                    </template>
                    <v-list-item-title class="text-grey">Name</v-list-item-title>
                    <v-list-item-subtitle class="text-h6 mt-1">
                      {{ authStore.user?.name || 'N/A' }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-divider class="my-2" />

                  <v-list-item>
                    <template #prepend>
                      <v-icon color="primary">mdi-email</v-icon>
                    </template>
                    <v-list-item-title class="text-grey">Email Address</v-list-item-title>
                    <v-list-item-subtitle class="text-h6 mt-1">
                      {{ authStore.user?.mail_address || 'N/A' }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-divider class="my-2" />

                  <v-list-item>
                    <template #prepend>
                      <v-icon color="primary">mdi-phone</v-icon>
                    </template>
                    <v-list-item-title class="text-grey">Phone Number</v-list-item-title>
                    <v-list-item-subtitle class="text-h6 mt-1">
                      {{ authStore.user?.phone_number || 'Not provided' }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-divider class="my-2" />

                  <v-list-item>
                    <template #prepend>
                      <v-icon color="primary">mdi-shield-account</v-icon>
                    </template>
                    <v-list-item-title class="text-grey">Account Type</v-list-item-title>
                    <v-list-item-subtitle class="mt-1">
                      <v-chip :color="userRoleColor" size="small">
                        {{ userRoleName }}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-divider class="my-2" />

                  <v-list-item>
                    <template #prepend>
                      <v-icon color="primary">mdi-calendar-clock</v-icon>
                    </template>
                    <v-list-item-title class="text-grey">Member Since</v-list-item-title>
                    <v-list-item-subtitle class="text-h6 mt-1">
                      {{ formattedJoinDate }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-divider class="my-2" />

                  <v-list-item>
                    <template #prepend>
                      <v-icon color="primary">mdi-identifier</v-icon>
                    </template>
                    <v-list-item-title class="text-grey">User ID</v-list-item-title>
                    <v-list-item-subtitle class="text-h6 mt-1">
                      #{{ authStore.user?.user_id }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card class="mb-4">
              <v-card-title class="bg-success text-white">
                Quick Actions
              </v-card-title>
              <v-card-text class="pa-4">
                <v-btn
                  color="primary"
                  variant="flat"
                  block
                  size="large"
                  class="mb-3"
                  to="/events"
                >
                  <v-icon start>mdi-ticket-outline</v-icon>
                  Browse Events
                </v-btn>
                <v-btn
                  color="info"
                  variant="flat"
                  block
                  size="large"
                  class="mb-3"
                  to="/attendee/my-tickets"
                >
                  <v-icon start>mdi-ticket-confirmation</v-icon>
                  My Tickets
                </v-btn>
                <v-btn
                  color="secondary"
                  variant="flat"
                  block
                  size="large"
                  to="/attendee/transactions"
                >
                  <v-icon start>mdi-receipt</v-icon>
                  Transaction History
                </v-btn>
              </v-card-text>
            </v-card>

            <v-card>
              <v-card-title class="bg-grey-darken-3 text-white">
                Account Settings
              </v-card-title>
              <v-card-text class="pa-4">
                <v-alert type="info" variant="tonal">
                  To update your account information, please contact support.
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
