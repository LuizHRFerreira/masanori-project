import { onMounted, onUnmounted, ref } from "vue";

export function useDeleteMovieModal({ emit }) {
  const confirmButton = ref(null);

  function onKeydown(event) {
    if (event.key === "Escape") emit("cancel");
  }

  onMounted(() => {
    window.addEventListener("keydown", onKeydown);
    confirmButton.value?.focus();
  });

  onUnmounted(() => window.removeEventListener("keydown", onKeydown));

  return { confirmButton };
}
