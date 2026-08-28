<script setup>
defineProps({
  books: { type: Array, required: true },
  loading: { type: Boolean, default: false },
});

defineEmits(["edit", "delete"]);
</script>

<template>
  <p v-if="loading" class="message">Carregando catálogo...</p>
  <p v-else-if="!books.length" class="message">Nenhum livro encontrado. Cadastre o primeiro.</p>
  <ul v-else class="book-list">
    <li v-for="book in books" :key="book.id">
      <span class="book-dot"></span>
      <div class="book-info">
        <strong>{{ book.title }}</strong>
        <span>
          {{ book.author || "Autor não informado" }} · {{ book.genre }}
          <template v-if="book.year"> · {{ book.year }}</template>
        </span>
        <small>{{ book.tags.join(" · ") || "Sem tags" }}</small>
      </div>
      <span v-if="book.rating !== null && book.rating !== undefined" class="rating" :aria-label="`Nota ${book.rating} de 5`">
        <span class="stars" aria-hidden="true">
          <span v-for="star in 5" :key="star" :class="{ filled: star <= book.rating }">★</span>
        </span>
        <small>{{ Number(book.rating).toFixed(1) }}/5</small>
      </span>
      <button class="icon-button" type="button" @click="$emit('edit', book)">Editar</button>
      <button class="icon-button danger" type="button" @click="$emit('delete', book.id)">Excluir</button>
    </li>
  </ul>
</template>

<style scoped>
.message {
  color: #8e9c92;
  padding: 26px 0;
}

.book-list {
  list-style: none;
  padding: 0;
  margin: 22px 0 0;
  border-top: 1px solid #303a37;
}

.book-list li {
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid #303a37;
  padding: 17px 4px;
  color: #d9ded5;
}

.book-dot {
  width: 8px;
  height: 8px;
  background: #d8ef7a;
  flex: 0 0 auto;
}

.book-info {
  display: grid;
  gap: 4px;
  flex: 1;
}

.book-info span,
.book-info small {
  color: #8e9c92;
  font-size: 12px;
}

.rating {
  display: grid;
  gap: 3px;
  color: #8e9c92;
  font:
    12px "DM Mono",
    monospace;
  text-align: right;
}

.stars {
  color: #536359;
  font-family: sans-serif;
  font-size: 15px;
  letter-spacing: 1px;
  white-space: nowrap;
}

.stars .filled {
  color: #d8ef7a;
}

.rating small {
  color: #d8ef7a;
  font-size: 11px;
}

.icon-button {
  padding: 7px 10px;
  border: 1px solid #46534d;
  background: transparent;
  color: #d8ef7a;
  font-size: 12px;
}

.icon-button.danger {
  color: #f19a8e;
}

@media (max-width: 600px) {
  .book-list li {
    align-items: start;
    flex-wrap: wrap;
  }

  .book-info {
    min-width: calc(100% - 22px);
  }

  .rating {
    margin-left: 22px;
    text-align: left;
  }
}
</style>
