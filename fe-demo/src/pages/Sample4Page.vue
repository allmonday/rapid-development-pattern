<template>
  <div class="q-pa-md">
    <div class="text-subtitle1 q-mb-md">Teams (with task count from post hook)</div>

    <div class="root-card" v-for="team in teams" :key="team.id">
      <div class="card-header row items-center no-wrap">
        <div class="text-subtitle2">{{ team.name }}</div>
        <q-space />
        <div class="text-caption text-grey">Task Count: {{ team.task_count }}</div>
        <q-separator vertical class="q-mx-sm" />
        <div class="text-caption text-primary">Total: {{ team.total_task_count }}</div>
      </div>

      <div v-if="team.sprints?.length" class="child-nest">
        <div class="nest-label">Sprints ({{ team.sprints.length }})</div>
        <div class="child-card" v-for="sprint in team.sprints" :key="sprint.id">
          <div class="card-header row items-center no-wrap">
            <div class="text-body2">{{ sprint.name }}</div>
            <q-space />
            <div class="text-caption text-grey">Tasks: {{ sprint.task_count }}</div>
          </div>
        </div>
      </div>
    </div>
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
