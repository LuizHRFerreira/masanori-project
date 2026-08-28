const MIN_RATING = 0;
const MAX_RATING = 5;

export function useMovieForm({ props, emit }) {
  function update(key, value) {
    emit("update:modelValue", { ...props.modelValue, [key]: value });
  }

  function updateRating(event) {
    const value = event.target.value;
    update("rating", value === "" ? "" : Math.min(MAX_RATING, Math.max(MIN_RATING, Number(value))));
  }

  return { update, updateRating };
}
