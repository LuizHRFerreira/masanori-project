<script setup>
import { onMounted, ref } from "vue";
import BookFilters from "./components/BookFilters.vue";
import BookForm from "./components/BookForm.vue";
import BookList from "./components/BookList.vue";
import PopulateBooksModal from "./components/PopulateBooksModal.vue";

const books = ref([]);
const totalBooks = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const pageSize = 20;
const genres = ref([]);
const search = ref("");
const editingId = ref(null);
const isFormOpen = ref(false);
const isPopulateOpen = ref(false);
const form = ref({
  title: "",
  author: "",
  year: "",
  genre: "",
  tags: "",
  rating: "",
});
const loading = ref(true);
const saving = ref(false);
const error = ref("");

async function loadBooks(page = currentPage.value) {
  loading.value = true;
  error.value = "";
  try {
    const params = new URLSearchParams({ q: search.value, page, page_size: pageSize });
    const response = await fetch(`/api/books/?${params}`);
    if (!response.ok) throw new Error("Nao foi possivel carregar os livros.");
    const payload = await response.json();
    books.value = payload.results;
    totalBooks.value = payload.total;
    currentPage.value = payload.page;
    totalPages.value = payload.total_pages;
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    loading.value = false;
  }
}

async function loadGenres() {
  try {
    const response = await fetch("/api/genres/");
    if (!response.ok) throw new Error("Nao foi possivel carregar os generos.");
    genres.value = await response.json();
  } catch (requestError) {
    error.value = requestError.message;
  }
}

function searchBooks() {
  currentPage.value = 1;
  loadBooks(1);
}

async function saveBook() {
  const title = form.value.title.trim();
  if (!title || saving.value) return;

  saving.value = true;
  error.value = "";
  try {
    const response = await fetch(editingId.value ? `/api/books/${editingId.value}/` : "/api/books/", {
      method: editingId.value ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form.value,
        year: form.value.year ? Number(form.value.year) : null,
        rating: form.value.rating ? Number(form.value.rating) : null,
        tags: form.value.tags.split(","),
      }),
    });
    if (!response.ok) throw new Error("Nao foi possivel salvar o livro.");
    await loadBooks();
    resetForm();
  } catch (requestError) {
    error.value = requestError.message;
  } finally {
    saving.value = false;
  }
}

function editBook(book) {
  editingId.value = book.id;
  isFormOpen.value = true;
  form.value = {
    ...book,
    tags: book.tags.join(", "),
    year: book.year || "",
    rating: book.rating || "",
  };
}

function openNewBook() {
  resetForm();
  isFormOpen.value = true;
}

function openPopulateBooks() {
  isPopulateOpen.value = true;
}

async function finishPopulation() {
  isPopulateOpen.value = false;
  currentPage.value = 1;
  await loadGenres();
  await loadBooks();
}

async function deleteBook(id) {
  if (!window.confirm("Excluir este livro?")) return;
  await fetch(`/api/books/${id}/`, { method: "DELETE" });
  await loadBooks();
}

function resetForm() {
  editingId.value = null;
  isFormOpen.value = false;
  form.value = {
    title: "",
    author: "",
    year: "",
    genre: "",
    tags: "",
    rating: "",
  };
}

onMounted(() => {
  loadBooks();
  loadGenres();
});
</script>

<template>
  <main class="shell">
    <header class="topbar">
      <span class="brand-mark">M</span>
      <span class="brand-name">Masanori</span>
      <span class="api-status">API + MongoDB</span>
    </header>

    <section class="intro">
      <p class="eyebrow">Banco NoSQL em prática</p>
      <h1>Livros que contam <em>histórias.</em></h1>
      <p class="subtitle">Um catálogo flexível para demonstrar documentos, filtros e CRUD no MongoDB.</p>
    </section>

    <section class="task-panel" aria-labelledby="books-title">
      <div class="panel-heading">
        <div>
          <p class="eyebrow">Coleção books</p>
          <h2 id="books-title">Catálogo</h2>
        </div>
        <div class="panel-actions">
          <span class="task-count">{{ totalBooks }} livros</span>
          <button type="button" class="populate-button" @click="openPopulateBooks">Popular banco</button>
          <button type="button" class="new-book-button" @click="openNewBook">Novo livro</button>
        </div>
      </div>

      <BookForm
        v-if="isFormOpen"
        v-model="form"
        :saving="saving"
        :editing="Boolean(editingId)"
        :genres="genres"
        @submit="saveBook"
        @cancel="resetForm"
      />

      <BookFilters v-model="search" @search="searchBooks" />

      <p v-if="error" class="message error">{{ error }}</p>
      <BookList :books="books" :loading="loading" @edit="editBook" @delete="deleteBook" />

      <nav v-if="totalPages > 1" class="pagination" aria-label="Paginação do catálogo">
        <button type="button" :disabled="currentPage === 1 || loading" @click="loadBooks(currentPage - 1)">Anterior</button>
        <span>Página {{ currentPage }} de {{ totalPages }}</span>
        <button type="button" :disabled="currentPage === totalPages || loading" @click="loadBooks(currentPage + 1)">Próxima</button>
      </nav>
    </section>

    <PopulateBooksModal v-if="isPopulateOpen" @close="isPopulateOpen = false" @success="finishPopulation" />
  </main>
</template>

<style scoped>
.shell {
  width: min(100% - 40px, 1080px);
  margin: auto;
  padding: 28px 0 80px;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #c5cabb;
  font-size: 14px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  background: #d8ef7a;
  color: #17201d;
  font-weight: 700;
}

.brand-name {
  font-weight: 600;
  letter-spacing: 0.3px;
}

.api-status {
  margin-left: auto;
  border: 1px solid #46534d;
  padding: 7px 12px;
  color: #a3b3a5;
  font:
    11px "DM Mono",
    monospace;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.intro {
  padding: 125px 0 78px;
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

h1 {
  font-size: clamp(44px, 7vw, 82px);
  line-height: 0.98;
  letter-spacing: -3px;
  margin: 0;
  font-weight: 600;
}

h1 em {
  color: #d8ef7a;
  font-style: normal;
}

.subtitle {
  color: #a3ada5;
  font-size: 18px;
  margin-top: 22px;
}

.task-panel {
  border-top: 1px solid #46534d;
  padding-top: 24px;
}

.panel-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin-bottom: 24px;
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

h2 {
  font-size: 27px;
  margin: 0;
  font-weight: 500;
}

.task-count {
  color: #8e9c92;
  font:
    12px "DM Mono",
    monospace;
}

.new-book-button {
  min-height: 42px;
  border: 0;
  background: #d8ef7a;
  color: #17201d;
  padding: 0 22px;
  font-weight: 600;
}

.populate-button {
  min-height: 42px;
  border: 1px solid #d8ef7a;
  background: transparent;
  color: #d8ef7a;
  padding: 0 16px;
  font-weight: 600;
}

.message {
  color: #8e9c92;
  padding: 26px 0;
}

.error {
  color: #f19a8e;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  color: #8e9c92;
  font:
    12px "DM Mono",
    monospace;
}

.pagination button {
  min-height: 38px;
  border: 1px solid #46534d;
  background: transparent;
  color: #d8ef7a;
  padding: 0 14px;
}

.pagination button:disabled {
  cursor: not-allowed;
  color: #536359;
}

@media (max-width: 600px) {
  .shell {
    width: min(100% - 28px, 1080px);
    padding-top: 20px;
  }

  .intro {
    padding: 100px 0 62px;
  }

  h1 {
    letter-spacing: -2px;
  }

  .panel-actions {
    align-items: end;
    flex-direction: column-reverse;
    gap: 10px;
  }

  .populate-button,
  .new-book-button {
    width: 100%;
  }

  .pagination {
    gap: 8px;
  }

  .pagination button {
    padding: 0 9px;
  }
}
</style>
