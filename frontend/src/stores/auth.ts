import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { usersApi } from '@/api/users'
import type { UserResponse, UserCreate, UserLogin, UserRole } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<UserResponse | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const userRole = computed((): UserRole | null => {
    if (!user.value) return null
    return user.value.type_id as UserRole
  })

  const isAdmin = computed(() => userRole.value === 1)
  const isOrganizer = computed(() => userRole.value === 2)
  const isVenueOwner = computed(() => userRole.value === 3)
  const isAttendee = computed(() => userRole.value === 4)

  const canAccessAdmin = computed(() => isAdmin.value)
  const canManageEvents = computed(() => isOrganizer.value || isAdmin.value)
  const canManageVenues = computed(() => isVenueOwner.value || isAdmin.value || isOrganizer.value)

  // Actions
  async function login(credentials: UserLogin) {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.login(credentials)
      token.value = response.data.access_token
      localStorage.setItem('access_token', response.data.access_token)

      // Fetch user data
      await fetchCurrentUser()

      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(userData: UserCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.register(userData)
      user.value = response.data
      // Auto-login after registration
      await login({ mail_address: userData.mail_address, password: userData.password })
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser() {
    try {
      const response = await usersApi.getCurrentUser()
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (e: any) {
      console.error('Failed to fetch user:', e)
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    error.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  function initializeAuth() {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      try {
        user.value = JSON.parse(storedUser)
        // Fetch fresh user data
        fetchCurrentUser()
      } catch (e) {
        logout()
      }
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    userRole,
    isAdmin,
    isOrganizer,
    isVenueOwner,
    isAttendee,
    canAccessAdmin,
    canManageEvents,
    canManageVenues,
    // Actions
    login,
    register,
    logout,
    fetchCurrentUser,
    initializeAuth,
  }
})
