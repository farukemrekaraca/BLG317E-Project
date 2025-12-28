<script setup lang="ts">
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useRouter } from 'vue-router'
import CartItem from './CartItem.vue'
import CheckoutDialog from './CheckoutDialog.vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const cartStore = useCartStore()
const router = useRouter()

const showCheckoutDialog = ref(false)

const closeDrawer = () => {
  emit('update:modelValue', false)
}

const handleCheckoutSuccess = () => {
  showCheckoutDialog.value = false
  closeDrawer()
  router.push('/attendee/my-tickets')
}
</script>

<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    location="right"
    temporary
    width="400"
  >
    <v-toolbar color="primary">
      <v-toolbar-title>Shopping Cart</v-toolbar-title>
      <v-btn icon @click="closeDrawer">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-toolbar>

    <v-container v-if="cartStore.itemCount === 0" class="text-center pa-8">
      <v-icon size="64" color="grey">mdi-cart-outline</v-icon>
      <p class="text-h6 mt-4">Your cart is empty</p>
      <p class="text-body-2 text-grey">Add tickets to get started!</p>
    </v-container>

    <v-list v-else>
      <CartItem
        v-for="item in cartStore.items"
        :key="item.ticket.ticket_id"
        :item="item"
        @remove="cartStore.removeFromCart(item.ticket.ticket_id)"
      />
    </v-list>

    <template #append>
      <div v-if="cartStore.itemCount > 0" class="pa-4">
        <v-divider class="mb-4" />

        <div class="d-flex justify-space-between align-center mb-4">
          <span class="text-h6">Total:</span>
          <span class="text-h5 font-weight-bold">${{ cartStore.totalPrice.toFixed(2) }}</span>
        </div>

        <v-btn
          color="primary"
          size="large"
          block
          @click="showCheckoutDialog = true"
        >
          Proceed to Checkout
        </v-btn>

        <v-btn
          variant="text"
          block
          class="mt-2"
          @click="cartStore.clearCart()"
        >
          Clear Cart
        </v-btn>
      </div>
    </template>

    <CheckoutDialog
      v-model="showCheckoutDialog"
      @success="handleCheckoutSuccess"
    />
  </v-navigation-drawer>
</template>
