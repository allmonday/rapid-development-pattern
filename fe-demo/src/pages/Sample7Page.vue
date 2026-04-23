<template>
  <div class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-subtitle1">User Stats (loader instance)</div>
      <q-space />
      <div class="row items-center q-gutter-sm">
        <div class="text-caption">User ID:</div>
        <q-select
          outlined
          dense
          style="min-width: 120px"
          :options="[1, 2, 3, 4, 5, 6, 7]"
          v-model="userId"
          @update:model-value="(val) => pick(val)"
        />
      </div>
    </div>

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
            <div class="text-caption text-grey">{{ sprint.stories?.length || 0 }} stories</div>
          </div>

          <div v-if="sprint.stories?.length" class="child-nest">
            <div class="nest-label">Stories</div>
            <div class="child-card" v-for="story in sprint.stories" :key="story.id">
              <div class="card-header row items-center no-wrap">
                <div class="text-body2">{{ story.name }}</div>
                <q-space />
                <div class="text-caption text-grey">Owner: {{ story.owner_id }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sample7, Sample7TeamDetail } from 'src/sdk';
import { onMounted, ref } from 'vue';

const teams = ref<Sample7TeamDetail[]>([]);
const userId = ref(1);

onMounted(async () => {
  teams.value = (
    await Sample7.getUserStat({ path: { id: userId.value } })
  ).data!;
});

const pick = async (id: number) => {
  teams.value = (await Sample7.getUserStat({ path: { id } })).data!;
};
</script>
