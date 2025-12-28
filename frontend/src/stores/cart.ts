import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { transactionsApi } from '@/api/transactions'
import type { CartItem } from '@/types/ticket'
import type { TransactionCreate } from '@/types/transaction'

export const useCartStore = defineStore('cart', () => {
  // State
  const items = ref<CartItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const itemCount = computed(() => items.value.length)

  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => sum + item.ticketType.price, 0)
  })

  const itemsByEvent = computed(() => {
    const grouped = new Map<number, CartItem[]>()
    items.value.forEach(item => {
      const eventItems = grouped.get(item.eventId) || []
      eventItems.push(item)
      grouped.set(item.eventId, eventItems)
    })
    return grouped
  })

  // Actions
  function addToCart(item: CartItem) {
    // Check if ticket already in cart
    const existingIndex = items.value.findIndex(
      i => i.ticket.ticket_id === item.ticket.ticket_id
    )

    if (existingIndex !== -1) {
      error.value = 'This ticket is already in your cart'
      return false
    }

    items.value.push(item)
    error.value = null
    return true
  }

  function removeFromCart(ticketId: number) {
    items.value = items.value.filter(item => item.ticket.ticket_id !== ticketId)
  }

  function clearCart() {
    items.value = []
    error.value = null
  }

  async function checkout(paymentData: { payment_method: string; installment_period?: number }) {
    if (items.value.length === 0) {
      error.value = 'Cart is empty'
      return null
    }

    loading.value = true
    error.value = null

    try {
      const ticketIds = items.value.map(item => item.ticket.ticket_id)
      const totalAmount = totalPrice.value

      const transactionData: TransactionCreate = {
        ticket_ids: ticketIds,
        price: totalAmount,
        payment_method: paymentData.payment_method,
        installment_period: paymentData.installment_period,
      }

      const response = await transactionsApi.createTransaction(transactionData)

      // Clear cart on success
      clearCart()

      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Checkout failed'
      console.error('Checkout error:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    items,
    loading,
    error,
    // Getters
    itemCount,
    totalPrice,
    itemsByEvent,
    // Actions
    addToCart,
    removeFromCart,
    clearCart,
    checkout,
  }
})
