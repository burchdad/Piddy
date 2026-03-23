---
name: vue
description: Vue 3 with Composition API, Pinia state management, Nuxt, and the Vue ecosystem
---

# Vue.js Development

## Vue 3 Core
- Single File Components: <script setup>, <template>, <style scoped>
- Composition API: ref(), reactive(), computed(), watch(), watchEffect()
- ref vs reactive: ref for primitives (access via .value), reactive for objects
- Template syntax: {{ interpolation }}, v-bind (:attr), v-on (@event), v-model
- Directives: v-if/v-else/v-show, v-for (always use :key), v-slot
- Components: props (defineProps), emits (defineEmits), slots (named, scoped)
- Lifecycle: onMounted, onUpdated, onUnmounted, onBeforeMount
- Provide/Inject: dependency injection across component tree
- Composables: reusable logic functions (use* naming), replacing mixins
- defineModel (Vue 3.4+): simplified two-way binding for components
- Teleport: render content in different DOM location
- Suspense: async component loading with fallback

## State Management (Pinia)
- defineStore: setup syntax (recommended) or options syntax
- State: ref() in setup stores, reactive properties
- Getters: computed() in setup stores
- Actions: regular functions, can be async
- Store composition: use one store inside another
- Plugins: persistence, devtools integration
- $reset, $patch for state manipulation

## Routing (Vue Router)
- createRouter: routes array, history mode (createWebHistory)
- Route params: /user/:id, useRoute().params
- Navigation guards: beforeEach, beforeRouteEnter, meta fields
- Lazy loading: () => import('./views/Page.vue')
- Nested routes: children array, <RouterView> in parent

## Nuxt 3
- File-based routing: pages/ directory
- Auto-imports: composables, components, utils
- Server routes: server/api/ directory, defineEventHandler
- useFetch, useAsyncData for data fetching
- Middleware: route middleware in middleware/ directory
- Layouts: layouts/ directory, NuxtLayout component
- SEO: useHead, useSeoMeta composables
- Nitro server engine: API routes, server middleware

## Testing
- Vitest: test runner, compatible with Jest API
- Vue Test Utils: mount, shallowMount, wrapper.find, trigger
- Component testing: render → interact → assert
- Pinia testing: createTestingPinia, mock stores
- Cypress/Playwright for E2E testing

## Best Practices
- Use <script setup> always — cleaner, better TypeScript support
- Prefer Composition API over Options API for new code
- Use TypeScript with Vue for type safety
- Keep components small and focused
- Use composables to extract reusable logic
- v-for always needs :key with unique stable identifier
- Use Pinia over Vuex (official recommendation)
