import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserRole } from '@/types/user'

export function authGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  const authStore = useAuthStore()

  if (!authStore.isAuthenticated) {
    // Store intended destination
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
  } else {
    next()
  }
}

export function roleGuard(requiredRole: UserRole) {
  return (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
  ) => {
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }

    const userRole = authStore.userRole

    // Admin can access everything
    if (userRole === UserRole.ADMIN) {
      next()
      return
    }

    // Check specific role requirements
    if (requiredRole === UserRole.ADMIN && !authStore.isAdmin) {
      next({ path: '/', replace: true })
      return
    }

    if (requiredRole === UserRole.ORGANIZER && !authStore.canManageEvents) {
      next({ path: '/', replace: true })
      return
    }

    if (requiredRole === UserRole.VENUE_OWNER && !authStore.canManageVenues) {
      next({ path: '/', replace: true })
      return
    }

    next()
  }
}

export function guestGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  const authStore = useAuthStore()

  if (authStore.isAuthenticated) {
    // Redirect to role-appropriate dashboard
    if (authStore.isAdmin) {
      next('/admin/dashboard')
    } else if (authStore.isOrganizer) {
      next('/organizer/dashboard')
    } else if (authStore.isVenueOwner) {
      next('/venue-owner/dashboard')
    } else {
      next('/attendee/my-tickets')
    }
  } else {
    next()
  }
}
