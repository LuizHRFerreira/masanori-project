<script setup>
import { useDeleteMovieModal } from "./DeleteMovieModal.js";

defineProps({
  movie: { type: Object, required: true },
  deleting: { type: Boolean, default: false },
});

const emit = defineEmits(["confirm", "cancel"]);

const { confirmButton } = useDeleteMovieModal({ emit });
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('cancel')">
    <div class="modal delete-modal" role="alertdialog" aria-modal="true" aria-labelledby="delete-title" aria-describedby="delete-description">
      <div class="modal-heading">
        <div>
          <p class="eyebrow">Fim de linha</p>
          <h2 id="delete-title">Excluir filme</h2>
        </div>
        <button type="button" class="close-button" aria-label="Fechar" @click="emit('cancel')">&times;</button>
      </div>

      <div class="ticket">
        <span class="pole" aria-hidden="true"></span>
        <div class="ticket-info">
          <strong>{{ movie.title }}</strong>
          <span>
            {{ movie.director || "Direção não informada" }}
            <template v-if="movie.year"> · {{ movie.year }}</template>
          </span>
        </div>
        <span class="status" :class="{ rented: !movie.available }">{{ movie.available ? "Disponível" : "Alugado" }}</span>
      </div>

      <p id="delete-description" class="description">Este título será removido do acervo. A ação não pode ser desfeita.</p>

      <div class="modal-actions">
        <button type="button" class="btn secondary" :disabled="deleting" @click="emit('cancel')">Manter no acervo</button>
        <button ref="confirmButton" type="button" class="btn danger solid" :disabled="deleting" @click="emit('confirm')">
          {{ deleting ? "Excluindo..." : "Excluir" }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped src="./DeleteMovieModal.css"></style>
