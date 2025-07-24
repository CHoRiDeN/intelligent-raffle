<template>
  <div class="min-h-screen bg-white text-gray-900 flex flex-col items-center font-sans">
    <header class="w-full border-b border-gray-200 py-8 mb-10 bg-white shadow-sm">
      <div class="container mx-auto flex justify-between items-center px-4">
        <div class="flex items-center gap-3">
          <span class="text-4xl">🎉</span>
          <h1 class="text-4xl font-extrabold tracking-tight">GenLayer Raffles</h1>
        </div>
        <div>
          <slot name="account">
            <div v-if="!userAddress">
              <button
                @click="createUserAccount"
                class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-full shadow transition uppercase tracking-widest"
              >
                Create Raffle
              </button>
            </div>
            <div v-else class="flex flex-col items-end">
              <p class="text-base mb-1">Your address: <Address :address="userAddress" /></p>
              <p class="text-base mb-2">Your points: {{ userPoints }}</p>
              <button
                @click="disconnectUserAccount"
                class="bg-blue-100 hover:bg-blue-200 text-blue-700 font-bold py-2 px-4 rounded-full shadow transition text-xs uppercase"
              >
                Disconnect
              </button>
            </div>
          </slot>
        </div>
      </div>
    </header>
    <main class="container mx-auto max-w-2xl px-4 flex flex-col gap-10 w-full">
      <div class="bg-gradient-to-br from-blue-50 to-white rounded-2xl shadow-lg p-10 mb-8 text-center flex flex-col items-center">
        <h2 class="text-2xl font-bold mb-2 tracking-wide">Create a Raffle</h2>
        <div class="text-blue-400 font-semibold text-lg py-8 flex flex-col items-center gap-2">
          <span class="text-4xl">🚧</span>
          <span>Coming soon</span>
        </div>
      </div>
      <div class="bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-lg p-10">
        <h2 class="text-2xl font-bold mb-6 tracking-wide">Active Raffles</h2>
        <ul class="flex flex-col gap-6">
          <li
            v-for="raffle in raffles"
            :key="raffle"
            class="transition hover:shadow-xl hover:bg-blue-50 rounded-xl border border-blue-100 bg-white px-6 py-5"
          >
            <div class="flex items-center gap-4 mb-2">
              <span class="text-2xl">🎲</span>
              <span class="font-semibold text-base tracking-wide">Raffle ID:</span>
              <span class="text-blue-600 text-sm break-all">{{ raffle || 'Unknown' }}</span>
            </div>
            <div v-if="loadingRafflesInfo" class="text-gray-400 text-xs italic">Loading criteria...</div>
            <div v-else class="text-gray-500 text-xs italic ml-8">
              {{ rafflesInfo[raffle]?.evaluation_criteria || 'No criteria' }}
            </div>
            <div class="flex justify-end">
              <button
                @click="selectRaffle(raffle)"
                class="uppercase text-xs font-bold text-blue-600 tracking-widest bg-blue-100 hover:bg-blue-200 px-5 py-2 rounded-full shadow transition focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                Participate
              </button>
            </div>
          </li>
        </ul>
      </div>
    </main>
  </div>
  <div class="flex items-center justify-center h-screen" v-if="loadingInitialData">
    <div class="spinner">Loading...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from 'vue-router';
import { account, createAccount, removeAccount, fetchRaffles, getRaffleAnswers } from "../services/genlayer";
import FootballBets from "../logic/FootballBets";
import Address from "./Address.vue";
// State
const raffleQuestion = ref("");
const creatingRaffle = ref(false);
const raffles = ref([]);
const rafflesInfo = ref({});
const loadingRafflesInfo = ref(false);
const selectedRaffle = ref(null);
const raffleAnswer = ref("");
const participatingRaffle = ref(false);
const loadingInitialData = ref(true);
const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
const studioUrl = import.meta.env.VITE_STUDIO_URL;
const footballBets = new FootballBets(contractAddress, account, studioUrl); // Placeholder logic
const userAccount = ref(account);
const userPoints = ref(0);
const userAddress = computed(() => userAccount.value?.address);
const router = useRouter();

// Methods
const createUserAccount = async () => {
  userAccount.value = createAccount();
  footballBets.updateAccount(userAccount.value);
  userPoints.value = 0;
};

const disconnectUserAccount = async () => {
  userAccount.value = null;
  removeAccount();
  userPoints.value = 0;
};

const loadRaffles = async () => {
  raffles.value = await fetchRaffles();
  loadingRafflesInfo.value = true;
  // Fetch info for each raffle
  const infoEntries = await Promise.all(
    raffles.value.map(async (raffleId) => {
      try {
        const result = await getRaffleAnswers(raffleId);
        // Convert Map to object if needed
        let obj = result;
        if (result instanceof Map) {
          obj = Object.fromEntries(result);
        }
        return [raffleId, obj];
      } catch (e) {
        return [raffleId, {}];
      }
    })
  );
  rafflesInfo.value = Object.fromEntries(infoEntries);
  loadingRafflesInfo.value = false;
};

const createRaffle = async () => {
  if (raffleQuestion.value) {
    creatingRaffle.value = true;
    // Placeholder: use createBet as createRaffle
    await footballBets.createBet("2024-01-01", raffleQuestion.value, "", "1");
    await loadRaffles();
    creatingRaffle.value = false;
    raffleQuestion.value = "";
  }
};

const selectRaffle = (raffleId) => {
  router.push(`/raffle/${raffleId}`);
};

onMounted(async () => {
  await loadRaffles();
  loadingInitialData.value = false;
});
</script>
