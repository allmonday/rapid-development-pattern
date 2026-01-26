<template>
  <div class="q-ma-sm">
    <div class="text-h6 q-mb-sm">Teams (with member filters)</div>
    <q-card v-for="team in teams" :key="team.id" flat bordered class="q-mb-xs">
      <q-card-section class="q-pa-sm">
        <div class="text-subtitle2">{{ team.name }}</div>
      </q-card-section>

      <q-card-section
        v-if="team.senior_members && team.senior_members.length > 0"
        class="q-pa-sm q-pt-none"
      >
        <div class="text-caption q-mb-xs">
          Senior Members ({{ team.senior_members.length }})
        </div>
        <div class="row q-gutter-xs">
          <q-chip
            v-for="member in team.senior_members"
            :key="member.id"
            size="sm"
            dense
          >
            {{ member.name }}
          </q-chip>
        </div>
      </q-card-section>

      <q-card-section
        v-if="team.junior_members && team.junior_members.length > 0"
        class="q-pa-sm q-pt-none"
      >
        <div class="text-caption q-mb-xs">
          Junior Members ({{ team.junior_members.length }})
        </div>
        <div class="row q-gutter-xs">
          <q-chip
            v-for="member in team.junior_members"
            :key="member.id"
            size="sm"
            dense
          >
            {{ member.name }}
          </q-chip>
        </div>
      </q-card-section>

      <q-card-section
        v-if="team.senior_junior && team.senior_junior.length > 0"
        class="q-pa-sm q-pt-none"
      >
        <div class="text-caption q-mb-xs">
          Senior + Junior ({{ team.senior_junior.length }})
        </div>
        <div class="row q-gutter-xs">
          <q-chip
            v-for="member in team.senior_junior"
            :key="member.id"
            size="sm"
            dense
          >
            {{ member.name }}
          </q-chip>
        </div>
      </q-card-section>
    </q-card>
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
