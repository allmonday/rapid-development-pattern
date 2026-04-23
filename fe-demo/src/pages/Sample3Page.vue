<template>
  <div class="q-pa-md">
    <div class="text-subtitle1 q-mb-md">Teams (with ancestor field: full_name)</div>

    <div class="root-card" v-for="team in teams" :key="team.id">
      <div class="card-header">
        <div class="text-subtitle2">{{ team.name }}</div>
      </div>

      <div v-if="team.sprints?.length" class="child-nest">
        <div class="nest-label">Sprints ({{ team.sprints.length }})</div>
        <div class="child-card" v-for="sprint in team.sprints" :key="sprint.id">
          <div class="card-header row items-center no-wrap">
            <div class="text-body2">{{ sprint.name }}</div>
            <q-space />
            <div class="text-caption text-grey">{{ sprint.status }}</div>
          </div>
        </div>
      </div>
    </div>
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
