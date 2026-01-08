<template>
    <div class="q-ma-sm">
        <div class="text-h6 q-mb-sm">Page Info (pick fields and hide fields)</div>

        <q-card v-if="page" flat bordered class="q-mb-xs">
            <q-card-section class="q-pa-sm">
                <div class="text-caption q-mb-xs">Summary</div>
                <div class="text-body2">{{ page.summary }}</div>
            </q-card-section>

            <q-card-section v-if="page.teams && page.teams.length > 0" class="q-pa-sm q-pt-none">
                <div class="text-caption q-mb-xs">Teams ({{ page.teams.length }})</div>
                <q-card v-for="team in page.teams" :key="team.id" flat bordered class="q-mb-xs q-ml-sm bg-grey-1">
                    <q-card-section class="q-pa-xs">
                        <div class="text-subtitle2">{{ team.name }}</div>
                    </q-card-section>

                    <q-card-section v-if="team.sprints && team.sprints.length > 0" class="q-pa-xs q-pt-none">
                        <div class="text-caption q-mb-xs">Sprints ({{ team.sprints.length }})</div>
                        <q-card v-for="sprint in team.sprints" :key="sprint.name" flat bordered class="q-mb-xs q-ml-xs bg-grey-2">
                            <q-card-section class="q-pa-xs">
                                <div class="text-caption">{{ sprint.name }}</div>
                            </q-card-section>

                            <q-card-section v-if="sprint.stories && sprint.stories.length > 0" class="q-pa-none q-pt-none">
                                <q-list dense bordered separator>
                                    <q-item v-for="story in sprint.stories" :key="story.name" dense>
                                        <q-item-section>
                                            <q-item-label class="text-caption">{{ story.name }}</q-item-label>
                                        </q-item-section>
                                    </q-item>
                                </q-list>
                            </q-card-section>
                        </q-card>
                    </q-card-section>
                </q-card>
            </q-card-section>
        </q-card>
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

<style scoped></style>
