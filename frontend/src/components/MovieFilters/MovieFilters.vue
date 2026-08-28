<script setup>
import { useMovieFilters } from "./MovieFilters.js";

const query = defineModel("query", { type: String, default: "" });
const genre = defineModel("genre", { type: String, default: "" });

defineProps({
  genres: { type: Array, default: () => [] },
});

const emit = defineEmits(["search"]);

const { changeGenre, clearFilters } = useMovieFilters({ query, genre, emit });
</script>

<template>
  <form class="search-row" @submit.prevent="emit('search')">
    <label class="field search-field">
      <span>Buscar filmes</span>
      <input v-model="query" type="search" placeholder="Título, diretor ou tag" aria-label="Buscar filmes" />
    </label>
    <label class="field genre-field">
      <span>Gênero</span>
      <select :value="genre" @change="changeGenre">
        <option value="">Todos</option>
        <option v-for="option in genres" :key="option" :value="option">{{ option }}</option>
      </select>
    </label>
    <button type="submit" class="btn">Buscar</button>
    <button type="button" class="btn secondary" @click="clearFilters">Limpar</button>
  </form>
</template>

<style scoped src="./MovieFilters.css"></style>
