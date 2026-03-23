# Vue.js Quick Reference

## Language: Vue 3.4+ (Composition API)
**Paradigm:** Progressive UI framework  
**Typing:** JavaScript/TypeScript + SFC (.vue)  
**Rendering:** Reactive system, virtual DOM  

## Single File Component

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ title: string }>()
const emit = defineEmits<{ update: [value: string] }>()

const message = ref('Hello Piddy')
const reversed = computed(() => message.value.split('').reverse().join(''))
</script>

<template>
  <div>
    <h1>{{ title }}</h1>
    <input v-model="message">
    <p>{{ reversed }}</p>
    <ul><li v-for="item in items" :key="item.id">{{ item.name }}</li></ul>
  </div>
</template>

<style scoped>
div { padding: 1rem; }
</style>
```

## Reactivity

```typescript
const count = ref(0)         // .value in script
const state = reactive({ user: null, loading: false })
const full = computed(() => `${first.value} ${last.value}`)

watch(count, (newVal, oldVal) => console.log(newVal))
watchEffect(() => console.log(count.value))
```

## Composables

```typescript
export function useFetch<T>(url: MaybeRef<string>) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  async function execute() {
    loading.value = true
    try { data.value = await (await fetch(toValue(url))).json() }
    finally { loading.value = false }
  }
  watchEffect(() => execute())
  return { data, loading, execute }
}
```

## Tooling

```bash
npm create vue@latest
npm run dev
npm run build
```
