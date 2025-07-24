import { createClient, createAccount as createGenLayerAccount, generatePrivateKey } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const accountPrivateKey = localStorage.getItem("accountPrivateKey")
  ? localStorage.getItem("accountPrivateKey")
  : null;
export const account = accountPrivateKey ? createGenLayerAccount(accountPrivateKey) : null;

export const createAccount = () => {
  const newAccountPrivateKey = generatePrivateKey();
  localStorage.setItem("accountPrivateKey", newAccountPrivateKey);
  return createGenLayerAccount(newAccountPrivateKey);
};

export const removeAccount = () => {
  localStorage.removeItem("accountPrivateKey");
};

export const client = createClient({ chain: studionet, account });

// Mocked Raffle Service Functions
export const fetchRaffles = async () => {
  // Returns a list of string IDs
  return ["0xec27311fA59Ee35fbEb1eda3954C3DA63Ac5Ba5e","0x2459361472635a2d1e165b3796a02Cf0De5a991b","0xB508f40b9f93b883974348d305DADC0Ba5A5D1Df","0x095126C1904a5a5bBB8D8f2D860fa5bCe7A22f49","0x28D4E0f91E5B21B76b86443625CB865923900d7c"];
};

export const getRaffle = async (raffleId) => {
  // Returns a mock raffle object
  return {
    id: raffleId,
    name: `Raffle Name for ${raffleId}`
  };
};

export const postResult = async (raffleId, answer) => {
  console.log('Calling postResult with:', { raffleId, answer });
  // TESTING ONLY: Always create a new account for each call (remove for production)
  const account = createAccount();
  const clientWithAccount = createClient({ chain: studionet, account });
  const transactionHash = await clientWithAccount.writeContract({
    address: raffleId,
    functionName: 'add_entry',
    args: [answer],
    value: 0,
  });
  console.log('postResult completed. Transaction hash:', transactionHash);
  return { success: true, transactionHash };
};

export const finalizeRaffle = async (raffleId) => {
  console.log("Finalize Raffle: ", raffleId);
  return await client.writeContract({
    address: raffleId,
    functionName: 'resolver_contract',
  });
};

// Returns a list of answers and ratings for a raffle
export const getRaffleAnswers = async (raffleId) => {
  const result = await client.readContract({
    address: raffleId,
    functionName: 'get_state',
    args: [],
  });
  console.log("RESULT RAFFLES: ", result);
  return result;
};
