import { createRouter, createWebHistory } from 'vue-router';
import RaffleScreen from './components/RaffleScreen.vue';
import Raffle from './components/Raffle.vue';

const routes = [
  { path: '/', component: RaffleScreen },
  { path: '/raffle/:raffleId', component: Raffle, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router; 