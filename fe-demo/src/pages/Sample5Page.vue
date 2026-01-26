<template>
  <div class="q-ma-sm">
    <div class="q-mb-sm">
      <q-btn
        @click="q(1)"
        outline
        :color="teamId === 1 ? 'primary' : 'grey'"
        class="q-mr-sm"
        >Team 1</q-btn
      >
      <q-btn @click="q(2)" outline :color="teamId === 2 ? 'primary' : 'grey'"
        >Team 2</q-btn
      >
    </div>

    <div class="text-h6 q-mb-sm">Page Info (context)</div>

    <q-card v-if="page" flat bordered class="q-mb-xs">
      <q-card-section class="q-pa-sm">
        <div class="text-caption q-mb-xs">Summary</div>
        <div class="text-body2">{{ page.summary }}</div>
      </q-card-section>

      <q-card-section v-if="page.team" class="q-pa-sm q-pt-none">
        <div class="text-caption q-mb-xs">Team</div>
        <q-card flat bordered class="bg-grey-1">
          <q-card-section class="q-pa-xs">
            <div class="text-subtitle2">{{ page.team.name }}</div>
          </q-card-section>

          <q-card-section
            v-if="page.team.sprints && page.team.sprints.length > 0"
            class="q-pa-xs q-pt-none"
          >
            <div class="text-caption q-mb-xs">
              Sprints ({{ page.team.sprints.length }})
            </div>
            <q-card
              v-for="sprint in page.team.sprints"
              :key="sprint.id"
              flat
              bordered
              class="q-mb-xs q-ml-sm bg-grey-2"
            >
              <q-card-section class="q-pa-xs">
                <div class="row items-center no-wrap">
                  <div class="text-caption">{{ sprint.name }}</div>
                  <q-space />
                  <div class="text-caption text-grey">ID: {{ sprint.id }}</div>
                </div>
              </q-card-section>
            </q-card>
          </q-card-section>
        </q-card>
      </q-card-section>
    </q-card>
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

<style scoped></style>
