<script setup>
const props = defineProps({
  modelValue: { type: Object, required: true },
  saving: { type: Boolean, default: false },
  editing: { type: Boolean, default: false },
  genres: { type: Array, default: () => [] },
});

const emit = defineEmits(["update:modelValue", "submit", "cancel"]);

function updateRating(event) {
  const value = event.target.value;
  const rating = value === "" ? "" : Math.min(5, Math.max(0, Number(value)));
  emit("update:modelValue", { ...props.modelValue, rating });
}
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('cancel')">
    <form class="book-form modal" @submit.prevent="$emit('submit')">
      <div class="modal-heading">
        <div>
          <p class="eyebrow">Coleção books</p>
          <h2>{{ editing ? "Editar livro" : "Adicionar livro" }}</h2>
        </div>
        <button type="button" class="close-button" aria-label="Fechar" @click="$emit('cancel')">&times;</button>
      </div>
      <label class="field">
        <span>Título <b>*</b></span>
        <input
          :value="modelValue.title"
          type="text"
          placeholder="Digite o título"
          required
          @input="$emit('update:modelValue', { ...modelValue, title: $event.target.value })"
        />
      </label>
      <label class="field">
        <span>Autor</span>
        <input
          :value="modelValue.author"
          type="text"
          placeholder="Digite o autor"
          @input="$emit('update:modelValue', { ...modelValue, author: $event.target.value })"
        />
      </label>
      <label class="field">
        <span>Ano de publicação</span>
        <input
          :value="modelValue.year"
          type="number"
          placeholder="Ex.: 2026"
          min="0"
          @input="$emit('update:modelValue', { ...modelValue, year: $event.target.value })"
        />
      </label>
      <label class="field">
        <span>Gênero</span>
        <select :value="modelValue.genre" @change="$emit('update:modelValue', { ...modelValue, genre: $event.target.value })">
          <option value="" disabled>Selecione um gênero</option>
          <option v-for="genre in genres" :key="genre">{{ genre }}</option>
        </select>
      </label>
      <label class="field">
        <span>Tags</span>
        <input
          :value="modelValue.tags"
          type="text"
          placeholder="Ex.: clássico, leitura"
          @input="$emit('update:modelValue', { ...modelValue, tags: $event.target.value })"
        />
      </label>
      <label class="field">
        <span>Nota</span>
        <input :value="modelValue.rating" type="number" placeholder="0 a 5" min="0" max="5" step="0.1" @input="updateRating" />
      </label>
      <div class="modal-actions">
        <button type="button" class="secondary" @click="$emit('cancel')">Cancelar</button>
        <button type="submit" :disabled="saving">{{ saving ? "Salvando..." : editing ? "Atualizar" : "Adicionar" }}</button>
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

.book-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.book-form.modal {
  width: min(100%, 560px);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 28px;
  border: 1px solid #536359;
  background: #202728;
  box-shadow: 0 24px 80px rgb(0 0 0 / 35%);
}

.modal-heading,
.modal-actions {
  grid-column: 1 / -1;
}

.modal-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
  margin-bottom: 8px;
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

.modal-heading h2 {
  margin: 0;
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

.field {
  display: grid;
  gap: 7px;
  min-width: 0;
}

.field > span {
  color: #c5cabb;
  font:
    11px "DM Mono",
    monospace;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.field b {
  color: #d8ef7a;
  font-weight: 400;
}

.field input,
.field select {
  width: 100%;
  min-height: 48px;
  border: 1px solid #46534d;
  background: #202728;
  color: #f4f0e8;
  padding: 14px 16px;
  outline: none;
}

.field input:focus,
.field select:focus {
  border-color: #d8ef7a;
}

.field select {
  appearance: none;
  background-image: linear-gradient(45deg, transparent 50%, #a3ada5 50%), linear-gradient(135deg, #a3ada5 50%, transparent 50%);
  background-position:
    calc(100% - 18px) 21px,
    calc(100% - 12px) 21px;
  background-size:
    6px 6px,
    6px 6px;
  background-repeat: no-repeat;
  padding-right: 40px;
}

.field select option {
  background: #202728;
  color: #f4f0e8;
}

.modal-actions {
  display: flex;
  justify-content: end;
  gap: 10px;
  margin-top: 8px;
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

@media (max-width: 600px) {
  .book-form.modal {
    grid-template-columns: 1fr;
    padding: 22px;
  }
}
</style>
