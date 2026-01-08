<template>
  <div class="q-ma-sm">
    teams, with task count(post hook):
    <pre>{{ teams }} </pre>
  </div>
</template>

<script setup lang="ts">
import { Sample4, Sample4TeamDetail } from 'src/sdk';
import { onMounted, ref } from 'vue';

const teams = ref<Sample4TeamDetail[]>([]);

onMounted(async () => {
  teams.value = (await Sample4.getTeamsWithDetail()).data!;
});
</script>

<style scoped></style>
