<template>
  <div class="q-pa-md">
    <div class="q-mb-md">
      <q-btn @click="q(1)" outline :color="teamId === 1 ? 'primary' : 'grey'" class="q-mr-sm">Team 1</q-btn>
      <q-btn @click="q(2)" outline :color="teamId === 2 ? 'primary' : 'grey'">Team 2</q-btn>
    </div>

    <div class="text-subtitle1 q-mb-md">Page Info (context)</div>

    <div v-if="page" class="root-card">
      <div class="card-header">
        <div class="nest-label">Summary</div>
        <div class="text-body2">{{ page.summary }}</div>
      </div>

      <div v-if="page.team" class="child-nest">
        <div class="nest-label">Team</div>
        <div class="child-card">
          <div class="card-header">
            <div class="text-body2">{{ page.team.name }}</div>
          </div>

          <div v-if="page.team.sprints?.length" class="child-nest">
            <div class="nest-label">Sprints ({{ page.team.sprints.length }})</div>
            <div class="child-card" v-for="sprint in page.team.sprints" :key="sprint.id">
              <div class="card-header row items-center no-wrap">
                <div class="text-body2">{{ sprint.name }}</div>
                <q-space />
                <div class="text-caption text-grey">ID: {{ sprint.id }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sample5, Sample5Root } from 'src/sdk';
import { onMounted, ref } from 'vue';

const page = ref<Sample5Root>();
const teamId = ref<number>(1);

onMounted(async () => {
  page.value = (await Sample5.getPageInfo({ path: { team_id: 1 } })).data!;
});

const q = async (id: number) => {
  teamId.value = id;
  page.value = (await Sample5.getPageInfo({ path: { team_id: id } })).data!;
};
</script>
