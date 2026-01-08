<template>
  <div class="q-ma-sm">
    teams (add filter for dataloader):
    <pre>{{ teams }} </pre>
  </div>
</template>

<script setup lang="ts">
import { Sample2, Sample2TeamDetailMultipleLevel } from 'src/sdk';
import { onMounted, ref } from 'vue';

const teams = ref<Sample2TeamDetailMultipleLevel[]>([]);

onMounted(async () => {
  teams.value = (await Sample2.getTeamsWithDetailOfMultipleLevel()).data!;
});
</script>

<style scoped></style>
