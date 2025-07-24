<template>
  <div class="min-h-screen bg-white flex flex-col items-center justify-center font-sans">
    <div class="bg-white p-10 rounded-3xl shadow-2xl max-w-md w-full flex flex-col items-center gap-6 border border-blue-100">
      <div class="flex items-center gap-3 mb-2">
        <span class="text-3xl">🎲</span>
        <h1 class="text-3xl font-extrabold tracking-tight">Participate in Raffle</h1>
      </div>
      <div v-if="loading" class="flex flex-col items-center justify-center h-32">
        <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>
      </div>
      <div v-else class="w-full flex flex-col items-center gap-4">
        <div class="mb-2 w-full text-center">
          <span class="font-semibold text-lg">Raffle ID:</span>
          <span class="ml-2 text-blue-600 font-bold">{{ raffle?.id }}</span>
        </div>
        <div v-if="!success" class="w-full flex flex-col gap-4">
          <input
            v-model="answer"
            class="w-full px-4 py-3 border border-blue-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 text-lg transition"
            placeholder="Enter your answer"
          />
          <button
            @click="submitAnswer"
            :disabled="submitting || !answer"
            class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-full shadow transition uppercase tracking-widest text-lg disabled:opacity-50"
          >
            {{ submitting ? 'Submitting...' : 'Participate' }}
          </button>
        </div>
        <div v-else class="text-green-600 font-semibold mt-4 text-center text-lg flex flex-col items-center gap-2">
          <span class="text-3xl">🎉</span>
          Participation submitted!
        </div>
        <div v-if="error" class="text-red-600 font-semibold mt-2 text-center">{{ error }}</div>
        <button
          @click="router.push('/')"
          class="mt-4 bg-gray-100 hover:bg-blue-50 text-blue-700 font-bold py-2 px-6 rounded-full shadow transition w-full text-base"
        >
          ← Back to Raffles
        </button>
        <div v-if="answers.length" class="w-full mt-6">
          <h3 class="text-lg font-bold mb-2 text-left">Raffle Details</h3>
          <ul class="flex flex-col gap-1 mb-4">
            <li v-for="(item, idx) in raffleDetails" :key="idx" class="flex justify-between items-center">
              <span class="font-semibold capitalize">{{ item.key.replace(/_/g, ' ') }}:</span>
              <span :class="item.key === 'status' ? 'text-blue-700 font-bold' : 'text-gray-700'">{{ item.value || '-' }}</span>
            </li>
          </ul>
          <button
            @click="finalizeRaffle"
            :disabled="finalizeLoading"
            class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-full shadow transition uppercase tracking-widest text-lg mb-4 disabled:opacity-50"
          >
            {{ finalizeLoading ? 'Executing...' : 'EXECUTE RAFFLE' }}
          </button>
          <div v-if="finalizeSuccess" class="text-green-600 font-semibold text-center mb-2">Raffle executed successfully!</div>
          <div v-if="finalizeError" class="text-red-600 font-semibold text-center mb-2">{{ finalizeError }}</div>
          <h3 class="text-lg font-bold mb-2 text-left">Current Answers</h3>
          <ul v-if="answers.length" class="flex flex-col gap-2">
            <li v-for="(item, idx) in answers" :key="idx" class="flex flex-col sm:flex-row sm:justify-between items-start sm:items-center bg-blue-50 rounded-lg px-4 py-2">
              <span class="text-gray-800 break-all font-medium">{{ item.answer }}</span>
              <span class="text-blue-700 font-bold ml-0 sm:ml-4">Score: {{ item.score }}</span>
            </li>
          </ul>
          <div v-else class="text-gray-400 text-center py-4">No answers yet for this raffle.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getRaffle, postResult, getRaffleAnswers, finalizeRaffle as finalizeRaffleService } from '../services/genlayer';
import { client } from '../services/genlayer';

const route = useRoute();
const router = useRouter();
const raffleId = route.params.raffleId;
const raffle = ref(null);
const answer = ref('');
const loading = ref(true);
const submitting = ref(false);
const success = ref(false);
const error = ref(null);

const finalizeLoading = ref(false);
const finalizeSuccess = ref(false);
const finalizeError = ref(null);

function mapToObj(map) {
  if (!(map instanceof Map)) return map;
  const obj = {};
  for (const [k, v] of map.entries()) {
    obj[k] = mapToObj(v);
  }
  return obj;
}

const raffleDetails = ref([]);
const answers = ref([]);

const fetchRaffle = async () => {
  loading.value = true;
  raffle.value = await getRaffle(raffleId);
  let result = await getRaffleAnswers(raffleId);
  result = mapToObj(result);

  // Prepare details for display (excluding answers)
  raffleDetails.value = [];
  for (const [key, value] of Object.entries(result)) {
    if (key !== 'answers') {
      raffleDetails.value.push({ key, value });
    }
  }

  // Prepare answers
  answers.value = [];
  if (result.answers && typeof result.answers === 'object') {
    answers.value = Object.entries(result.answers).map(([address, ans]) => {
      const obj = mapToObj(ans);
      return {
        address: obj.address || address,
        answer: obj.answer,
        score: obj.score
      };
    });
  }
  loading.value = false;
};

const submitAnswer = async () => {
  if (!answer.value) return;
  submitting.value = true;
  error.value = null;
  try {
    await postResult(raffleId, answer.value);
    await fetchRaffle(); // Refresh details and answers
    success.value = true;
  } catch (e) {
    console.error('Error in postResult:', e);
    error.value = 'Error submitting your answer. Please try again.';
  } finally {
    submitting.value = false;
  }
};

const finalizeRaffle = async () => {
  finalizeLoading.value = true;
  finalizeError.value = null;
  try {
    await finalizeRaffleService(raffleId);
    finalizeSuccess.value = true;
    await fetchRaffle();
  } catch (e) {
    finalizeError.value = 'Error executing raffle.';
    console.error(e);
  } finally {
    finalizeLoading.value = false;
  }
};

onMounted(fetchRaffle);
</script> 