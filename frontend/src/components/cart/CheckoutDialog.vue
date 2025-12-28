<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cart'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const cartStore = useCartStore()

const paymentMethod = ref('credit_card')
const installmentPeriod = ref<number | undefined>(undefined)
const loading = ref(false)
const error = ref<string | null>(null)

const paymentMethods = [
  { value: 'credit_card', title: 'Credit Card' },
  { value: 'debit_card', title: 'Debit Card' },
  { value: 'cash', title: 'Cash' },
]

const installmentOptions = [
  { value: undefined, title: 'No Installment' },
  { value: 3, title: '3 Months' },
  { value: 6, title: '6 Months' },
  { value: 9, title: '9 Months' },
  { value: 12, title: '12 Months' },
]

const showInstallments = computed(() => paymentMethod.value === 'credit_card')

const handleCheckout = async () => {
  loading.value = true
  error.value = null

  try {
    const paymentData = {
      payment_method: paymentMethod.value,
      installment_period: showInstallments.value ? installmentPeriod.value : undefined,
    }

    await cartStore.checkout(paymentData)
    emit('success')
    emit('update:modelValue', false)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Checkout failed. Please try again.'
  } finally {
    loading.value = false
  }
}

const closeDialog = () => {
  emit('update:modelValue', false)
  error.value = null
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    max-width="500"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5 pa-4">
        Checkout
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4">
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
          closable
          @click:close="error = null"
        >
          {{ error }}
        </v-alert>

        <!-- Order Summary -->
        <div class="mb-6">
          <div class="text-subtitle-1 font-weight-bold mb-2">Order Summary</div>
          <div class="d-flex justify-space-between mb-2">
            <span class="text-body-2">Total Items:</span>
            <span class="text-body-2 font-weight-bold">{{ cartStore.itemCount }}</span>
          </div>
          <div class="d-flex justify-space-between">
            <span class="text-h6">Total Amount:</span>
            <span class="text-h6 font-weight-bold text-primary">
              ${{ cartStore.totalPrice.toFixed(2) }}
            </span>
          </div>
        </div>

        <v-divider class="mb-4" />

        <!-- Payment Method Selection -->
        <div class="mb-4">
          <div class="text-subtitle-1 font-weight-bold mb-2">Payment Method</div>
          <v-radio-group v-model="paymentMethod" hide-details>
            <v-radio
              v-for="method in paymentMethods"
              :key="method.value"
              :label="method.title"
              :value="method.value"
              color="primary"
            />
          </v-radio-group>
        </div>

        <!-- Installment Options (only for credit card) -->
        <div v-if="showInstallments" class="mb-4">
          <div class="text-subtitle-1 font-weight-bold mb-2">Installment Period</div>
          <v-select
            v-model="installmentPeriod"
            :items="installmentOptions"
            item-title="title"
            item-value="value"
            variant="outlined"
            density="comfortable"
            hide-details
          />
        </div>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-btn
          variant="text"
          @click="closeDialog"
          :disabled="loading"
        >
          Cancel
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          variant="flat"
          size="large"
          @click="handleCheckout"
          :loading="loading"
          :disabled="loading"
        >
          Complete Purchase
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
