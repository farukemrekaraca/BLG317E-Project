import { createRouter, createWebHistory } from 'vue-router'
import { authGuard, guestGuard, roleGuard } from './guards'
import { UserRole } from '@/types/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public routes
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/public/HomeView.vue'),
    },
    {
      path: '/events',
      name: 'events',
      component: () => import('@/views/public/EventsView.vue'),
    },
    {
      path: '/events/:id',
      name: 'event-detail',
      component: () => import('@/views/public/EventDetailView.vue'),
    },
    {
      path: '/venues',
      name: 'venues',
      component: () => import('@/views/public/VenuesView.vue'),
    },

    // Auth routes
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      beforeEnter: guestGuard,
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      beforeEnter: guestGuard,
    },

    // Attendee routes
    {
      path: '/attendee',
      redirect: '/attendee/my-tickets',
      meta: { requiresAuth: true },
      beforeEnter: authGuard,
      children: [
        {
          path: 'my-tickets',
          name: 'my-tickets',
          component: () => import('@/views/attendee/MyTicketsView.vue'),
        },
        {
          path: 'transactions',
          name: 'transaction-history',
          component: () => import('@/views/attendee/TransactionHistoryView.vue'),
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/attendee/ProfileView.vue'),
        },
      ],
    },

    // Organizer routes
    {
      path: '/organizer',
      redirect: '/organizer/dashboard',
      meta: { requiresAuth: true, requiredRole: UserRole.ORGANIZER },
      beforeEnter: roleGuard(UserRole.ORGANIZER),
      children: [
        {
          path: 'dashboard',
          name: 'organizer-dashboard',
          component: () => import('@/views/organizer/DashboardView.vue'),
        },
        {
          path: 'my-events',
          name: 'my-events',
          component: () => import('@/views/organizer/MyEventsView.vue'),
        },
        {
          path: 'create-event',
          name: 'create-event',
          component: () => import('@/views/organizer/CreateEventView.vue'),
        },
        {
          path: 'events/:id/edit',
          name: 'edit-event',
          component: () => import('@/views/organizer/EditEventView.vue'),
        },
        {
          path: 'analytics',
          name: 'event-analytics',
          component: () => import('@/views/organizer/EventAnalyticsView.vue'),
        },
      ],
    },

    // Venue Owner routes
    {
      path: '/venue-owner',
      redirect: '/venue-owner/dashboard',
      meta: { requiresAuth: true, requiredRole: UserRole.VENUE_OWNER },
      beforeEnter: roleGuard(UserRole.VENUE_OWNER),
      children: [
        {
          path: 'dashboard',
          name: 'venue-owner-dashboard',
          component: () => import('@/views/venue-owner/DashboardView.vue'),
        },
        {
          path: 'venues',
          name: 'my-venues',
          component: () => import('@/views/venue-owner/MyVenuesView.vue'),
        },
        {
          path: 'venues/create',
          name: 'create-venue',
          component: () => import('@/views/venue-owner/CreateVenueView.vue'),
        },
        {
          path: 'venues/:id/edit',
          name: 'edit-venue',
          component: () => import('@/views/venue-owner/EditVenueView.vue'),
        },
        {
          path: 'venues/:id/analytics',
          name: 'venue-analytics',
          component: () => import('@/views/venue-owner/VenueAnalyticsView.vue'),
        },
      ],
    },

    // Admin routes
    {
      path: '/admin',
      redirect: '/admin/dashboard',
      meta: { requiresAuth: true, requiredRole: UserRole.ADMIN },
      beforeEnter: roleGuard(UserRole.ADMIN),
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/DashboardView.vue'),
        },
        {
          path: 'users',
          name: 'users-management',
          component: () => import('@/views/admin/UsersManagementView.vue'),
        },
        {
          path: 'events',
          name: 'events-management',
          component: () => import('@/views/admin/EventsManagementView.vue'),
        },
        {
          path: 'venues',
          name: 'venues-management',
          component: () => import('@/views/admin/VenuesManagementView.vue'),
        },
        {
          path: 'transactions',
          name: 'transactions-management',
          component: () => import('@/views/admin/TransactionsView.vue'),
        },
        {
          path: 'analytics',
          name: 'admin-analytics',
          component: () => import('@/views/admin/AnalyticsView.vue'),
        },
      ],
    },

    // 404 Not Found
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

export default router
