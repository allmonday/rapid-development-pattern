<template>
  <div class="q-ma-sm">
    <div class="text-h6 q-mb-sm">Teams (with ancestor field: full_name)</div>
    <q-card v-for="team in teams" :key="team.id" flat bordered class="q-mb-xs">
      <q-card-section class="q-pa-sm">
        <div class="text-subtitle2">{{ team.name }}</div>
      </q-card-section>

      <q-card-section
        v-if="team.sprints && team.sprints.length > 0"
        class="q-pa-sm q-pt-none"
      >
        <div class="text-caption q-mb-xs">
          Sprints ({{ team.sprints.length }})
        </div>
        <q-card
          v-for="sprint in team.sprints"
          :key="sprint.id"
          flat
          bordered
          class="q-mb-xs q-ml-sm bg-grey-1"
        >
          <q-card-section class="q-pa-xs">
            <div class="row items-center no-wrap">
              <div class="text-caption">{{ sprint.name }}</div>
              <q-space />
              <div class="text-caption text-grey">{{ sprint.status }}</div>
            </div>
          </q-card-section>
        </q-card>
      </q-card-section>
    </q-card>
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
