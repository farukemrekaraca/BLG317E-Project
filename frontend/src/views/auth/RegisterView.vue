<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserRoleLabels, UserRole } from '@/types/user'

const router = useRouter()
const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const userType = ref(UserRole.ATTENDEE)
const showPassword = ref(false)

const userTypes = [
  { value: UserRole.ATTENDEE, title: UserRoleLabels[UserRole.ATTENDEE] },
  { value: UserRole.ORGANIZER, title: UserRoleLabels[UserRole.ORGANIZER] },
  { value: UserRole.VENUE_OWNER, title: UserRoleLabels[UserRole.VENUE_OWNER] },
]

const nameRules = [
  (v: string) => !!v || 'Name is required',
]

const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid',
]

const passwordRules = [
  (v: string) => !!v || 'Password is required',
  (v: string) => v.length >= 6 || 'Password must be at least 6 characters',
]

const confirmPasswordRules = [
  (v: string) => !!v || 'Please confirm password',
  (v: string) => v === password.value || 'Passwords do not match',
]

const handleRegister = async () => {
  const success = await authStore.register({
    name: name.value,
    mail_address: email.value,
    phone_number: phone.value || undefined,
    password: password.value,
    type_id: userType.value,
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
      <v-col cols="12" sm="8" md="5">
        <v-card>
          <v-card-title class="text-h5 text-center pa-6">
            {{ appName }}
          </v-card-title>
          <v-card-subtitle class="text-center">
            Create a new account
          </v-card-subtitle>

          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="name"
                :rules="nameRules"
                label="Full Name"
                prepend-inner-icon="mdi-account"
                required
              />

              <v-text-field
                v-model="email"
                :rules="emailRules"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
                required
              />

              <v-text-field
                v-model="phone"
                label="Phone Number (Optional)"
                prepend-inner-icon="mdi-phone"
              />

              <v-select
                v-model="userType"
                :items="userTypes"
                label="Account Type"
                prepend-inner-icon="mdi-account-group"
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

              <v-text-field
                v-model="confirmPassword"
                :rules="confirmPasswordRules"
                :type="showPassword ? 'text' : 'password'"
                label="Confirm Password"
                prepend-inner-icon="mdi-lock-check"
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
                Register
              </v-btn>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center pb-6">
            <v-btn
              variant="text"
              to="/login"
            >
              Already have an account? Login
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
