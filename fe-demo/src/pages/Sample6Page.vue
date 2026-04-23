<template>
  <div class="q-pa-md">
    <div class="text-subtitle1 q-mb-md">Page Info (pick fields and hide fields)</div>

    <div v-if="page" class="root-card">
      <div class="card-header">
        <div class="nest-label">Summary</div>
        <div class="text-body2">{{ page.summary }}</div>
      </div>

      <div v-if="page.teams?.length" class="child-nest">
        <div class="nest-label">Teams ({{ page.teams.length }})</div>
        <div class="child-card" v-for="team in page.teams" :key="team.id">
          <div class="card-header">
            <div class="text-body2">{{ team.name }}</div>
          </div>

          <div v-if="team.sprints?.length" class="child-nest">
            <div class="nest-label">Sprints ({{ team.sprints.length }})</div>
            <div class="child-card" v-for="sprint in team.sprints" :key="sprint.name">
              <div class="card-header">
                <div class="text-body2">{{ sprint.name }}</div>
              </div>

              <div v-if="sprint.stories?.length" class="child-nest">
                <div class="nest-label">Stories</div>
                <div class="child-card" v-for="story in sprint.stories" :key="story.name">
                  <div class="card-header">
                    <div class="text-body2">{{ story.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sample6, Sample6Root } from 'src/sdk';
import { onMounted, ref } from 'vue';

const page = ref<Sample6Root>();

onMounted(async () => {
  page.value = (await Sample6.getPageInfo6()).data!;
});
</script>
