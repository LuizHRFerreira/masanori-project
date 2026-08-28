<script setup>
import { ref } from "vue";

const emit = defineEmits(["close", "success"]);
const amount = ref(20);
const populating = ref(false);
const error = ref("");

async function populateBooks() {
  const quantity = Number(amount.value);
  if (!Number.isInteger(quantity) || quantity < 1 || quantity > 1000 || populating.value) return;

  populating.value = true;
  error.value = "";
  try {
    const response = await fetch("/api/books/populate/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount: quantity }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Nao foi possível popular o catálogo.");
    emit("success", payload.inserted);
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    populating.value = false;
  }
}
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <form class="populate-modal" @submit.prevent="populateBooks">
      <div class="modal-heading">
        <div>
          <p class="eyebrow">Importar do Kaggle</p>
          <h2>Popular catálogo</h2>
        </div>
        <button type="button" class="close-button" aria-label="Fechar" @click="$emit('close')">&times;</button>
      </div>

      <p class="warning">Os livros existentes serão removidos antes da importação.</p>

      <label class="field">
        <span>Quantidade de livros</span>
        <input v-model.number="amount" type="number" min="1" max="1000" step="1" required />
        <small>Escolha entre 1 e 1000 livros. Um trecho aleatório do dataset será usado.</small>
      </label>

      <p v-if="error" class="modal-error">{{ error }}</p>

      <div class="modal-actions">
        <button type="button" class="secondary" :disabled="populating" @click="$emit('close')">Cancelar</button>
        <button type="submit" :disabled="populating">{{ populating ? "Importando..." : "Limpar e importar" }}</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 10;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgb(10 14 14 / 78%);
}

.populate-modal {
  width: min(100%, 520px);
  display: grid;
  gap: 18px;
  padding: 28px;
  border: 1px solid #536359;
  background: #202728;
  box-shadow: 0 24px 80px rgb(0 0 0 / 35%);
}

.modal-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
}

.eyebrow {
  color: #d8ef7a;
  font:
    11px "DM Mono",
    monospace;
  text-transform: uppercase;
  letter-spacing: 1.8px;
  margin: 0 0 14px;
}

h2 {
  margin: 0;
  font-size: 27px;
  font-weight: 500;
}

.close-button {
  width: 34px;
  height: 34px;
  padding: 0;
  border: 0;
  background: transparent;
  color: #a3ada5;
  font-size: 25px;
  line-height: 1;
}

.warning {
  margin: 0;
  padding: 12px 14px;
  border-left: 2px solid #f19a8e;
  background: rgb(241 154 142 / 9%);
  color: #f1c4bd;
  font-size: 14px;
  line-height: 1.45;
}

.field {
  display: grid;
  gap: 7px;
}

.field > span {
  color: #c5cabb;
  font:
    11px "DM Mono",
    monospace;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.field input {
  width: 100%;
  min-height: 48px;
  border: 1px solid #46534d;
  background: #202728;
  color: #f4f0e8;
  padding: 14px 16px;
  outline: none;
}

.field input:focus {
  border-color: #d8ef7a;
}

.field small {
  color: #8e9c92;
  font-size: 12px;
}

.modal-error {
  margin: 0;
  color: #f19a8e;
  font-size: 13px;
}

.modal-actions {
  display: flex;
  justify-content: end;
  gap: 10px;
}

.modal-actions button {
  min-height: 48px;
  border: 0;
  background: #d8ef7a;
  color: #17201d;
  padding: 0 22px;
  font-weight: 600;
}

.modal-actions .secondary {
  border: 1px solid #46534d;
  background: transparent;
  color: #d9ded5;
}

.modal-actions button:disabled {
  cursor: wait;
  opacity: 0.65;
}

@media (max-width: 600px) {
  .populate-modal {
    padding: 22px;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>
