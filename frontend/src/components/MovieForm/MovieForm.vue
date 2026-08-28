<script setup>
import { useMovieForm } from "./MovieForm.js";

const props = defineProps({
  modelValue: { type: Object, required: true },
  saving: { type: Boolean, default: false },
  editing: { type: Boolean, default: false },
  genres: { type: Array, default: () => [] },
});

const emit = defineEmits(["update:modelValue", "submit", "cancel"]);

const { update, updateRating } = useMovieForm({ props, emit });
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('cancel')">
    <form class="modal movie-form" @submit.prevent="emit('submit')">
      <div class="modal-heading">
        <div>
          <p class="eyebrow">Coleção movies</p>
          <h2>{{ editing ? "Editar filme" : "Novo filme" }}</h2>
        </div>
        <button type="button" class="close-button" aria-label="Fechar" @click="emit('cancel')">&times;</button>
      </div>
      <label class="field full">
        <span>Título <b>*</b></span>
        <input :value="modelValue.title" type="text" placeholder="Digite o título" required @input="update('title', $event.target.value)" />
      </label>
      <label class="field">
        <span>Direção</span>
        <input :value="modelValue.director" type="text" placeholder="Quem dirigiu" @input="update('director', $event.target.value)" />
      </label>
      <label class="field">
        <span>Ano de lançamento</span>
        <input :value="modelValue.year" type="number" placeholder="Ex.: 1994" min="1888" max="2100" @input="update('year', $event.target.value)" />
      </label>
      <label class="field">
        <span>Gênero</span>
        <input :value="modelValue.genre" type="text" list="genre-options" placeholder="Ex.: Drama" @input="update('genre', $event.target.value)" />
        <datalist id="genre-options">
          <option v-for="genre in genres" :key="genre" :value="genre" />
        </datalist>
      </label>
      <label class="field">
        <span>Nota</span>
        <input :value="modelValue.rating" type="number" placeholder="0 a 5" min="0" max="5" step="0.1" @input="updateRating" />
      </label>
      <label class="field full">
        <span>Tags</span>
        <input :value="modelValue.tags" type="text" placeholder="Ex.: clássico, road movie" @input="update('tags', $event.target.value)" />
      </label>
      <label class="availability full">
        <input :checked="modelValue.available" type="checkbox" @change="update('available', $event.target.checked)" />
        <span class="availability-label">
          <strong>{{ modelValue.available ? "Disponível na prateleira" : "Alugado no momento" }}</strong>
          <small>Desmarque quando o filme sair com um cliente.</small>
        </span>
      </label>
      <div class="modal-actions full">
        <button type="button" class="btn secondary" @click="emit('cancel')">Cancelar</button>
        <button type="submit" class="btn" :disabled="saving">{{ saving ? "Salvando..." : editing ? "Atualizar" : "Adicionar" }}</button>
      </div>
    </form>
  </div>
</template>

<style scoped src="./MovieForm.css"></style>
