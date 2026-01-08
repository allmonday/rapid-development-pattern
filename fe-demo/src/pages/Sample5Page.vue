<template>
  <div class="q-ma-sm">
    <q-btn @click="q(1)" class="q-mr-sm">team 1</q-btn>
    <q-btn @click="q(2)">team 2</q-btn>
    <div>
      page info (context)

      <pre>{{ page }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sample5, Sample5Root } from 'src/sdk';
import { onMounted, ref } from 'vue';

const page = ref<Sample5Root>();

onMounted(async () => {
  page.value = (await Sample5.getPageInfo({ path: { team_id: 1 } })).data!;
});

const q = async (id: number) => {
  page.value = (await Sample5.getPageInfo({ path: { team_id: id } })).data!;
};
</script>

<style scoped></style>
