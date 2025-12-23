<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)

const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid',
]

const passwordRules = [
  (v: string) => !!v || 'Password is required',
  (v: string) => v.length >= 6 || 'Password must be at least 6 characters',
]

const handleLogin = async () => {
  const success = await authStore.login({
    mail_address: email.value,
    password: password.value,
  })

  if (success) {
    // Redirect based on user role
    if (authStore.isAdmin) {
      router.push('/admin/dashboard')
    } else if (authStore.isOrganizer) {
      router.push('/organizer/dashboard')
    } else if (authStore.isVenueOwner) {
      router.push('/venue-owner/dashboard')
    } else {
      router.push('/events')
    }
  }
}
const appName = import.meta.env.VITE_APP_NAME
</script>

<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="text-h5 text-center pa-6">
            {{ appName }}
          </v-card-title>
          <v-card-subtitle class="text-center">
            Login to your account
          </v-card-subtitle>

          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                :rules="emailRules"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
                required
              />

              <v-text-field
                v-model="password"
                :rules="passwordRules"
                :type="showPassword ? 'text' : 'password'"
                label="Password"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                required
              />

              <v-alert
                v-if="authStore.error"
                type="error"
                class="mb-4"
              >
                {{ authStore.error }}
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="authStore.loading"
                class="mt-4"
              >
                Login
              </v-btn>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center pb-6">
            <v-btn
              variant="text"
              to="/register"
            >
              Don't have an account? Register
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
