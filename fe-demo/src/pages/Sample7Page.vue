<template>
    <div class="q-ma-sm">
        <div class="row items-center q-mb-sm">
            <div class="text-h6">User Stats (loader instance)</div>
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
                ></q-select>
            </div>
        </div>

        <q-card v-for="team in teams" :key="team.id" flat bordered class="q-mb-xs">
            <q-card-section class="q-pa-sm">
                <div class="text-subtitle2">{{ team.name }}</div>
            </q-card-section>

            <q-card-section v-if="team.sprints && team.sprints.length > 0" class="q-pa-sm q-pt-none">
                <div class="text-caption q-mb-xs">Sprints ({{ team.sprints.length }})</div>
                <q-card v-for="sprint in team.sprints" :key="sprint.id" flat bordered class="q-mb-xs q-ml-sm bg-grey-1">
                    <q-card-section class="q-pa-xs">
                        <div class="row items-center no-wrap">
                            <div class="text-caption">{{ sprint.name }}</div>
                            <q-space />
                            <div class="text-caption text-grey">{{ sprint.stories?.length || 0 }} stories</div>
                        </div>
                    </q-card-section>

                    <q-card-section v-if="sprint.stories && sprint.stories.length > 0" class="q-pa-xs q-pt-none">
                        <q-list dense bordered separator>
                            <q-item v-for="story in sprint.stories" :key="story.id" dense>
                                <q-item-section>
                                    <q-item-label class="text-caption">{{ story.name }}</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-item-label caption>Owner: {{ story.owner_id }}</q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </q-card-section>
        </q-card>
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

<style scoped></style>
