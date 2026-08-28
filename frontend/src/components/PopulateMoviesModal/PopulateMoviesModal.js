import { ref } from "vue";
import { populateMovies } from "../../api/movies";

const MIN_AMOUNT = 1;
const MAX_AMOUNT = 1000;

export function usePopulateMovies({ emit }) {
  const amount = ref(20);
  const populating = ref(false);
  const error = ref("");

  async function populate() {
    const quantity = Number(amount.value);
    if (!Number.isInteger(quantity) || quantity < MIN_AMOUNT || quantity > MAX_AMOUNT || populating.value) return;

    populating.value = true;
    error.value = "";
    try {
      const payload = await populateMovies(quantity);
      emit("success", payload.inserted);
    } catch (requestError) {
      error.value = requestError.message;
    } finally {
      populating.value = false;
    }
  }

  return { MIN_AMOUNT, MAX_AMOUNT, amount, populating, error, populate };
}
