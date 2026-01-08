<template>
  <div class="q-ma-sm">
    teams (read fields of ancestor): full_name
    <pre>{{ teams }} </pre>
  </div>
</template>

<script setup lang="ts">
import { Sample3, Sample3TeamDetail } from 'src/sdk';
import { onMounted, ref } from 'vue';

const teams = ref<Sample3TeamDetail[]>([]);

onMounted(async () => {
  teams.value = (await Sample3.getTeamsWithDetail()).data!;
});
</script>

<style scoped></style>
