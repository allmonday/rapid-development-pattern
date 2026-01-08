<template>
    <div class="q-ma-sm">
        <q-tabs v-model="tab" dense class="text-grey" active-color="primary" indicator-color="primary" align="justify">
            <q-tab name="tasks" label="Tasks" />
            <q-tab name="stories" label="Stories" />
            <q-tab name="sprints" label="Sprints" />
            <q-tab name="teams" label="Teams" />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="tab" animated>
            <!-- Tasks Panel -->
            <q-tab-panel name="tasks" class="q-pa-sm">
                <div class="text-h6 q-mb-sm">Tasks</div>
                <q-card v-for="task in tasks" :key="task.id" flat bordered class="q-mb-xs">
                    <q-card-section class="q-pa-sm">
                        <div class="row items-center no-wrap">
                            <div class="text-subtitle2">{{ task.name }}</div>
                            <q-space />
                            <div class="text-caption text-grey">Story: {{ task.story_id }}</div>
                            <q-separator vertical class="q-mx-xs" />
                            <div class="text-caption text-grey">Estimate: {{ task.estimate }}</div>
                            <q-separator v-if="task.user" vertical class="q-mx-xs" />
                            <div v-if="task.user" class="text-caption text-primary">{{ task.user.name }}</div>
                        </div>
                    </q-card-section>
                </q-card>
            </q-tab-panel>

            <!-- Stories Panel -->
            <q-tab-panel name="stories" class="q-pa-sm">
                <div class="text-h6 q-mb-sm">Stories</div>
                <q-card v-for="story in stories" :key="story.id" flat bordered class="q-mb-xs">
                    <q-card-section class="q-pa-sm">
                        <div class="row items-center no-wrap">
                            <div class="text-subtitle2">{{ story.name }}</div>
                            <q-space />
                            <div class="text-caption text-grey">Sprint: {{ story.sprint_id }}</div>
                            <q-separator v-if="story.owner" vertical class="q-mx-xs" />
                            <div v-if="story.owner" class="text-caption text-primary">Owner: {{ story.owner.name }}</div>
                        </div>
                    </q-card-section>

                    <q-card-section v-if="story.tasks && story.tasks.length > 0" class="q-pa-sm q-pt-none">
                        <div class="text-caption q-mb-xs">Tasks ({{ story.tasks.length }})</div>
                        <div class="row q-col-gutter-xs">
                            <div class="col-12" v-for="task in story.tasks" :key="task.id">
                                <q-card flat bordered class="bg-grey-1">
                                    <q-card-section class="q-pa-xs">
                                        <div class="row items-center no-wrap">
                                            <div class="text-caption">{{ task.name }}</div>
                                            <q-space />
                                            <div class="text-caption text-grey">{{ task.estimate }}</div>
                                            <q-separator v-if="task.user" vertical class="q-mx-xs" />
                                            <div v-if="task.user" class="text-caption text-primary">{{ task.user.name }}</div>
                                        </div>
                                    </q-card-section>
                                </q-card>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </q-tab-panel>

            <!-- Sprints Panel -->
            <q-tab-panel name="sprints" class="q-pa-sm">
                <div class="text-h6 q-mb-sm">Sprints</div>
                <q-card v-for="sprint in sprints" :key="sprint.id" flat bordered class="q-mb-xs">
                    <q-card-section class="q-pa-sm">
                        <div class="row items-center no-wrap">
                            <div class="text-subtitle2">{{ sprint.name }}</div>
                            <q-space />
                            <div class="text-caption text-grey">Team: {{ sprint.team_id }}</div>
                        </div>
                    </q-card-section>

                    <q-card-section v-if="sprint.stories && sprint.stories.length > 0" class="q-pa-sm q-pt-none">
                        <div class="text-caption q-mb-xs">Stories ({{ sprint.stories.length }})</div>
                        <q-card v-for="story in sprint.stories" :key="story.id" flat bordered class="q-mb-xs q-ml-sm bg-grey-1">
                            <q-card-section class="q-pa-xs">
                                <div class="row items-center no-wrap">
                                    <div class="text-caption">{{ story.name }}</div>
                                    <q-space />
                                    <div v-if="story.owner" class="text-caption text-primary">{{ story.owner.name }}</div>
                                    <q-separator v-if="story.tasks && story.tasks.length > 0" vertical class="q-mx-xs" />
                                    <div v-if="story.tasks && story.tasks.length > 0" class="text-caption text-grey">{{ story.tasks.length }} tasks</div>
                                </div>
                            </q-card-section>

                            <q-card-section v-if="story.tasks && story.tasks.length > 0" class="q-pa-xs q-pt-none">
                                <q-list dense bordered separator>
                                    <q-item v-for="task in story.tasks" :key="task.id" dense>
                                        <q-item-section avatar>
                                            <q-item-label class="text-caption">{{ task.name }}</q-item-label>
                                        </q-item-section>
                                        <q-item-section side>
                                            <q-item-label caption>{{ task.estimate }}</q-item-label>
                                        </q-item-section>
                                    </q-item>
                                </q-list>
                            </q-card-section>
                        </q-card>
                    </q-card-section>
                </q-card>
            </q-tab-panel>

            <!-- Teams Panel -->
            <q-tab-panel name="teams" class="q-pa-sm">
                <div class="text-h6 q-mb-sm">Teams</div>
                <q-card v-for="team in teams" :key="team.id" flat bordered class="q-mb-xs">
                    <q-card-section class="q-pa-sm">
                        <div class="row items-center no-wrap">
                            <div class="text-subtitle2">{{ team.name }}</div>
                            <q-space />
                            <div v-if="team.members && team.members.length > 0" class="text-caption text-grey">{{ team.members.length }} members</div>
                            <q-separator v-if="team.sprints && team.sprints.length > 0" vertical class="q-mx-xs" />
                            <div v-if="team.sprints && team.sprints.length > 0" class="text-caption text-grey">{{ team.sprints.length }} sprints</div>
                        </div>
                    </q-card-section>

                    <q-card-section v-if="team.members && team.members.length > 0" class="q-pa-sm q-pt-none">
                        <div class="text-caption q-mb-xs">Members</div>
                        <div class="row q-gutter-xs">
                            <q-chip v-for="member in team.members" :key="member.id" size="sm" dense>
                                {{ member.name }}
                            </q-chip>
                        </div>
                    </q-card-section>

                    <q-card-section v-if="team.sprints && team.sprints.length > 0" class="q-pa-sm q-pt-none">
                        <div class="text-caption q-mb-xs">Sprints ({{ team.sprints.length }})</div>
                        <q-card v-for="sprint in team.sprints" :key="sprint.id" flat bordered class="q-mb-xs q-ml-sm bg-grey-1">
                            <q-card-section class="q-pa-xs">
                                <div class="row items-center no-wrap">
                                    <div class="text-caption">{{ sprint.name }}</div>
                                    <q-space />
                                    <div v-if="sprint.stories" class="text-caption text-grey">{{ sprint.stories.length }} stories</div>
                                </div>
                            </q-card-section>

                            <q-card-section v-if="sprint.stories && sprint.stories.length > 0" class="q-pa-xs q-pt-none">
                                <div class="row q-col-gutter-xs">
                                    <div class="col-12" v-for="story in sprint.stories" :key="story.id">
                                        <q-card flat bordered class="bg-grey-2">
                                            <q-card-section class="q-pa-xs">
                                                <div class="row items-center no-wrap">
                                                    <div class="text-caption">{{ story.name }}</div>
                                                    <q-space />
                                                    <div v-if="story.owner" class="text-caption text-primary">{{ story.owner.name }}</div>
                                                    <q-separator v-if="story.tasks && story.tasks.length > 0" vertical class="q-mx-xs" />
                                                    <div v-if="story.tasks && story.tasks.length > 0" class="text-caption text-grey">{{ story.tasks.length }} tasks</div>
                                                </div>
                                            </q-card-section>

                                            <q-card-section v-if="story.tasks && story.tasks.length > 0" class="q-pa-none">
                                                <q-list dense bordered separator>
                                                    <q-item v-for="task in story.tasks" :key="task.id" dense>
                                                        <q-item-section>
                                                            <q-item-label class="text-caption">{{ task.name }}</q-item-label>
                                                        </q-item-section>
                                                        <q-item-section side>
                                                            <q-item-label caption>{{ task.estimate }}</q-item-label>
                                                        </q-item-section>
                                                    </q-item>
                                                </q-list>
                                            </q-card-section>
                                        </q-card>
                                    </div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </q-card-section>
                </q-card>
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>

<script setup lang="ts">
import { Sample1, Sample1SprintDetail, Sample1StoryDetail, Sample1TaskDetail, Sample1TeamDetail } from 'src/sdk'
import { onMounted, ref } from 'vue';

const tab = ref('tasks')
const tasks = ref<Sample1TaskDetail[]>([])
const sprints = ref<Sample1SprintDetail[]>([])
const stories = ref<Sample1StoryDetail[]>([])
const teams = ref<Sample1TeamDetail[]>([])

onMounted(async () => {
    tasks.value = (await Sample1.getTasksWithDetail()).data!
    stories.value = (await Sample1.getStoriesWithDetail()).data!
    sprints.value = (await Sample1.getSprintsWithDetail()).data!
    teams.value = (await Sample1.getTeamsWithDetail()).data!
})
</script>

<style scoped></style>