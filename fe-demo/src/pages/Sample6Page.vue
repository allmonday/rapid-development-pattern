<template>
  <div class="q-ma-sm">
    page info (pick fields and hide fields)
    <pre>{{ page }}</pre>
  </div>
</template>

<script setup lang="ts">
import { Sample6, Sample6Root } from 'src/sdk';
import { onMounted, ref } from 'vue';

const page = ref<Sample6Root>();

onMounted(async () => {
  page.value = (await Sample6.getPageInfo6()).data!;
});
</script>

<style scoped></style>
