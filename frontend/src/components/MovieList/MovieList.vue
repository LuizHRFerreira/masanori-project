<script setup>
import { hasRating } from "./MovieList.js";

defineProps({
  movies: { type: Array, required: true },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["edit", "delete"]);
</script>

<template>
  <p v-if="loading" class="message">Carregando acervo...</p>
  <p v-else-if="!movies.length" class="message">Nenhum filme encontrado. Cadastre o primeiro título.</p>
  <ol v-else class="movie-list">
    <li v-for="movie in movies" :key="movie.id">
      <span class="pole" aria-hidden="true"></span>
      <div class="movie-info">
        <strong>{{ movie.title }}</strong>
        <span>
          {{ movie.director || "Direção não informada" }} · {{ movie.genre }}
          <template v-if="movie.year"> · {{ movie.year }}</template>
        </span>
        <small>{{ movie.tags.join(" · ") || "Sem tags" }}</small>
      </div>
      <span class="status" :class="{ rented: !movie.available }">{{ movie.available ? "Disponível" : "Alugado" }}</span>
      <span v-if="hasRating(movie)" class="rating" :aria-label="`Nota ${movie.rating} de 5`">
        <span class="stars" aria-hidden="true">
          <span v-for="star in 5" :key="star" :class="{ filled: star <= Math.round(movie.rating) }">★</span>
        </span>
        <small>{{ Number(movie.rating).toFixed(1) }}/5</small>
      </span>
      <span v-else class="rating placeholder">Sem nota</span>
      <div class="row-actions">
        <button class="btn secondary small" type="button" @click="emit('edit', movie)">Editar</button>
        <button class="btn danger small" type="button" @click="emit('delete', movie)">Excluir</button>
      </div>
    </li>
  </ol>
</template>

<style scoped src="./MovieList.css"></style>
