<script setup>
defineProps({
  modelValue: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue", "search"]);

function clearFilters() {
  emit("update:modelValue", "");
  emit("search");
}
</script>

<template>
  <form class="search-row" @submit.prevent="$emit('search')">
    <label class="search-field">
      <span>Buscar livros</span>
      <input
        :value="modelValue"
        type="search"
        placeholder="Título, autor ou tag"
        aria-label="Buscar livros"
        @input="$emit('update:modelValue', $event.target.value)"
      />
    </label>
    <button type="submit">Buscar</button>
    <button type="button" class="secondary" @click="clearFilters">Limpar filtros</button>
  </form>
</template>

<style scoped>
.search-row {
  display: flex;
  align-items: end;
  gap: 10px;
  margin-top: 10px;
}

.search-field {
  display: grid;
  flex: 1;
  gap: 7px;
}

.search-field > span {
  color: #c5cabb;
  font:
    11px "DM Mono",
    monospace;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.search-field input {
  width: 100%;
  min-height: 48px;
  border: 1px solid #46534d;
  background: #202728;
  color: #f4f0e8;
  padding: 14px 16px;
  outline: none;
}

.search-field input:focus {
  border-color: #d8ef7a;
}

.search-row button {
  min-height: 48px;
  border: 0;
  background: #d8ef7a;
  color: #17201d;
  padding: 0 22px;
  font-weight: 600;
}

.search-row .secondary {
  border: 1px solid #46534d;
  background: transparent;
  color: #a3ada5;
}

@media (max-width: 600px) {
  .search-row {
    flex-direction: column;
  }

  .search-row button {
    width: 100%;
  }
}
</style>
