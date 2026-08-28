<script setup>
import { usePopulateMovies } from "./PopulateMoviesModal.js";

const emit = defineEmits(["close", "success"]);

const { MIN_AMOUNT, MAX_AMOUNT, amount, populating, error, populate } = usePopulateMovies({ emit });
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <form class="modal populate-modal" @submit.prevent="populate">
      <div class="modal-heading">
        <div>
          <p class="eyebrow">Importar do Kaggle · IMDB Top 1000</p>
          <h2>Popular acervo</h2>
        </div>
        <button type="button" class="close-button" aria-label="Fechar" @click="emit('close')">&times;</button>
      </div>

      <p class="warning">Os filmes existentes serão removidos antes da importação.</p>

      <label class="field">
        <span>Quantidade de filmes</span>
        <input v-model.number="amount" type="number" :min="MIN_AMOUNT" :max="MAX_AMOUNT" step="1" required />
        <small>Escolha entre {{ MIN_AMOUNT }} e {{ MAX_AMOUNT }} filmes. Um trecho aleatório do dataset será usado e a disponibilidade é sorteada.</small>
      </label>

      <p v-if="error" class="modal-error">{{ error }}</p>

      <div class="modal-actions">
        <button type="button" class="btn secondary" :disabled="populating" @click="emit('close')">Cancelar</button>
        <button type="submit" class="btn" :disabled="populating">{{ populating ? "Importando..." : "Limpar e importar" }}</button>
      </div>
    </form>
  </div>
</template>

<style scoped src="./PopulateMoviesModal.css"></style>
