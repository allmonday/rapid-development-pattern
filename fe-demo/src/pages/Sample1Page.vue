<template>
  <div class="q-pa-md">
    <q-tabs
      v-model="tab"
      dense
      class="text-grey q-mb-sm"
      active-color="primary"
      indicator-color="primary"
      align="justify"
    >
      <q-tab name="tasks" label="Tasks" />
      <q-tab name="stories" label="Stories" />
      <q-tab name="sprints" label="Sprints" />
      <q-tab name="teams" label="Teams" />
    </q-tabs>

    <q-separator class="q-mb-md" />

    <q-tab-panels v-model="tab" animated>
      <!-- Tasks Panel -->
      <q-tab-panel name="tasks" class="q-pa-none">
        <div class="root-card" v-for="task in tasks" :key="task.id">
          <div class="card-header row items-center no-wrap">
            <div class="text-subtitle2">{{ task.name }}</div>
            <q-space />
            <div class="text-caption text-grey">Story: {{ task.story_id }}</div>
            <q-separator vertical class="q-mx-sm" />
            <div class="text-caption text-grey">Est: {{ task.estimate }}</div>
            <q-separator v-if="task.user" vertical class="q-mx-sm" />
            <div v-if="task.user" class="text-caption text-primary">{{ task.user.name }}</div>
          </div>
        </div>
      </q-tab-panel>

      <!-- Stories Panel -->
      <q-tab-panel name="stories" class="q-pa-none">
        <div class="root-card" v-for="story in stories" :key="story.id">
          <div class="card-header row items-center no-wrap">
            <div class="text-subtitle2">{{ story.name }}</div>
            <q-space />
            <div class="text-caption text-grey">Sprint: {{ story.sprint_id }}</div>
            <q-separator v-if="story.owner" vertical class="q-mx-sm" />
            <div v-if="story.owner" class="text-caption text-primary">{{ story.owner.name }}</div>
          </div>

          <div v-if="story.tasks?.length" class="child-nest">
            <div class="nest-label">Tasks ({{ story.tasks.length }})</div>
            <div class="child-card" v-for="task in story.tasks" :key="task.id">
              <div class="card-header row items-center no-wrap">
                <div class="text-body2">{{ task.name }}</div>
                <q-space />
                <div class="text-caption text-grey">{{ task.estimate }}</div>
                <q-separator v-if="task.user" vertical class="q-mx-sm" />
                <div v-if="task.user" class="text-caption text-primary">{{ task.user.name }}</div>
              </div>
            </div>
          </div>
        </div>
      </q-tab-panel>

      <!-- Sprints Panel -->
      <q-tab-panel name="sprints" class="q-pa-none">
        <div class="root-card" v-for="sprint in sprints" :key="sprint.id">
          <div class="card-header row items-center no-wrap">
            <div class="text-subtitle2">{{ sprint.name }}</div>
            <q-space />
            <div class="text-caption text-grey">Team: {{ sprint.team_id }}</div>
          </div>

          <div v-if="sprint.stories?.length" class="child-nest">
            <div class="nest-label">Stories ({{ sprint.stories.length }})</div>
            <div class="child-card" v-for="story in sprint.stories" :key="story.id">
              <div class="card-header row items-center no-wrap">
                <div class="text-body2">{{ story.name }}</div>
                <q-space />
                <div v-if="story.owner" class="text-caption text-primary">{{ story.owner.name }}</div>
                <q-separator v-if="story.tasks?.length" vertical class="q-mx-sm" />
                <div v-if="story.tasks?.length" class="text-caption text-grey">{{ story.tasks.length }} tasks</div>
              </div>

              <div v-if="story.tasks?.length" class="child-nest">
                <div class="nest-label">Tasks</div>
                <div class="child-card" v-for="task in story.tasks" :key="task.id">
                  <div class="card-header row items-center no-wrap">
                    <div class="text-body2">{{ task.name }}</div>
                    <q-space />
                    <div class="text-caption text-grey">{{ task.estimate }}</div>
                    <q-separator v-if="task.user" vertical class="q-mx-sm" />
                    <div v-if="task.user" class="text-caption text-primary">{{ task.user.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </q-tab-panel>

      <!-- Teams Panel -->
      <q-tab-panel name="teams" class="q-pa-none">
        <div class="root-card" v-for="team in teams" :key="team.id">
          <div class="card-header row items-center no-wrap">
            <div class="text-subtitle2">{{ team.name }}</div>
            <q-space />
            <div v-if="team.members?.length" class="text-caption text-grey">{{ team.members.length }} members</div>
            <q-separator v-if="team.sprints?.length" vertical class="q-mx-sm" />
            <div v-if="team.sprints?.length" class="text-caption text-grey">{{ team.sprints.length }} sprints</div>
          </div>

          <div v-if="team.members?.length" class="card-body">
            <div class="row q-gutter-xs">
              <q-chip v-for="member in team.members" :key="member.id" size="sm" dense>{{ member.name }}</q-chip>
            </div>
          </div>

          <div v-if="team.sprints?.length" class="child-nest">
            <div class="nest-label">Sprints ({{ team.sprints.length }})</div>
            <div class="child-card" v-for="sprint in team.sprints" :key="sprint.id">
              <div class="card-header row items-center no-wrap">
                <div class="text-body2">{{ sprint.name }}</div>
                <q-space />
                <div v-if="sprint.stories" class="text-caption text-grey">{{ sprint.stories.length }} stories</div>
              </div>

              <div v-if="sprint.stories?.length" class="child-nest">
                <div class="nest-label">Stories</div>
                <div class="child-card" v-for="story in sprint.stories" :key="story.id">
                  <div class="card-header row items-center no-wrap">
                    <div class="text-body2">{{ story.name }}</div>
                    <q-space />
                    <div v-if="story.owner" class="text-caption text-primary">{{ story.owner.name }}</div>
                    <q-separator v-if="story.tasks?.length" vertical class="q-mx-sm" />
                    <div v-if="story.tasks?.length" class="text-caption text-grey">{{ story.tasks.length }} tasks</div>
                  </div>

                  <div v-if="story.tasks?.length" class="child-nest">
                    <div class="nest-label">Tasks</div>
                    <div class="child-card" v-for="task in story.tasks" :key="task.id">
                      <div class="card-header row items-center no-wrap">
                        <div class="text-body2">{{ task.name }}</div>
                        <q-space />
                        <div class="text-caption text-grey">{{ task.estimate }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </q-tab-panel>
    </q-tab-panels>
  </div>
</template>

<script setup lang="ts">
import {
  Sample1,
  Sample1SprintDetail,
  Sample1StoryDetail,
  Sample1TaskDetail,
  Sample1TeamDetail,
} from 'src/sdk';
import { onMounted, ref } from 'vue';

const tab = ref('tasks');
const tasks = ref<Sample1TaskDetail[]>([]);
const sprints = ref<Sample1SprintDetail[]>([]);
const stories = ref<Sample1StoryDetail[]>([]);
const teams = ref<Sample1TeamDetail[]>([]);

onMounted(async () => {
  tasks.value = (await Sample1.getTasksWithDetail()).data!;
  stories.value = (await Sample1.getStoriesWithDetail()).data!;
  sprints.value = (await Sample1.getSprintsWithDetail()).data!;
  teams.value = (await Sample1.getTeamsWithDetail()).data!;
});
</script>
