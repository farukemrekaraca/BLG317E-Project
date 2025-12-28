<script setup lang="ts">
import { computed } from 'vue'
import { format } from 'date-fns'
import type { CartItem } from '@/types/ticket'

const props = defineProps<{
  item: CartItem
}>()

const emit = defineEmits<{
  remove: []
}>()

const formattedDate = computed(() => {
  try {
    return format(new Date(props.item.eventDate), 'MMM dd, yyyy')
  } catch {
    return props.item.eventDate
  }
})
</script>

<template>
  <v-list-item class="px-4 py-3">
    <div class="d-flex flex-column w-100">
      <div class="d-flex justify-space-between align-center mb-2">
        <div>
          <div class="text-subtitle-1 font-weight-bold">
            {{ item.eventName }}
          </div>
          <div class="text-caption text-grey">
            <v-icon size="small" class="mr-1">mdi-map-marker</v-icon>
            {{ item.venueName }}
          </div>
          <div class="text-caption text-grey">
            <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
            {{ formattedDate }}
          </div>
        </div>

        <v-btn
          icon
          size="small"
          variant="text"
          color="error"
          @click="emit('remove')"
        >
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </div>

      <v-divider class="my-2" />

      <div class="d-flex justify-space-between align-center">
        <div>
          <div class="text-body-2">{{ item.ticketType.name }}</div>
          <div class="text-caption text-grey">
            Ticket ID: #{{ item.ticket.ticket_id }}
          </div>
        </div>
        <div class="text-h6 font-weight-bold text-primary">
          ${{ item.ticketType.price.toFixed(2) }}
        </div>
      </div>
    </div>
  </v-list-item>
</template>
