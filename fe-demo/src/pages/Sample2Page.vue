<template>
  <div class="q-pa-md">
    <div class="text-subtitle1 q-mb-md">Teams (with member filters)</div>

    <div class="root-card" v-for="team in teams" :key="team.id">
      <div class="card-header">
        <div class="text-subtitle2">{{ team.name }}</div>
      </div>

      <div v-if="team.senior_members?.length" class="card-body">
        <div class="nest-label">Senior Members ({{ team.senior_members.length }})</div>
        <div class="row q-gutter-xs">
          <q-chip v-for="member in team.senior_members" :key="member.id" size="sm" dense color="blue-1" text-color="blue-8">{{ member.name }}</q-chip>
        </div>
      </div>

      <div v-if="team.junior_members?.length" class="card-body q-pt-none">
        <div class="nest-label">Junior Members ({{ team.junior_members.length }})</div>
        <div class="row q-gutter-xs">
          <q-chip v-for="member in team.junior_members" :key="member.id" size="sm" dense color="green-1" text-color="green-8">{{ member.name }}</q-chip>
        </div>
      </div>

      <div v-if="team.senior_junior?.length" class="card-body q-pt-none">
        <div class="nest-label">Senior + Junior ({{ team.senior_junior.length }})</div>
        <div class="row q-gutter-xs">
          <q-chip v-for="member in team.senior_junior" :key="member.id" size="sm" dense>{{ member.name }}</q-chip>
        </div>
      </div>
    </div>
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
