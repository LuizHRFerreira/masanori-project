<script setup>
import { onMounted } from "vue";
import MovieFilters from "./components/MovieFilters/MovieFilters.vue";
import MovieForm from "./components/MovieForm/MovieForm.vue";
import MovieList from "./components/MovieList/MovieList.vue";
import DeleteMovieModal from "./components/DeleteMovieModal/DeleteMovieModal.vue";
import PopulateMoviesModal from "./components/PopulateMoviesModal/PopulateMoviesModal.vue";
import { useMovies } from "./composables/useMovies";

const {
  movies,
  totalMovies,
  currentPage,
  totalPages,
  genres,
  loading,
  error,
  search,
  genreFilter,
  form,
  editingId,
  isFormOpen,
  saving,
  isPopulateOpen,
  movieToDelete,
  deleting,
  loadMovies,
  refresh,
  searchMovies,
  openNewMovie,
  editMovie,
  resetForm,
  saveMovie,
  requestDelete,
  cancelDelete,
  confirmDelete,
  openPopulateMovies,
  closePopulateMovies,
  finishPopulation,
} = useMovies();

onMounted(refresh);
</script>

<template>
  <main class="shell">

    <section class="intro">
      <h1>Alugue.<br /><em>Assista.</em></h1>
      <p class="subtitle">O acervo de uma locadora de filmes guardado em documentos flexíveis busca, filtros e CRUD no MongoDB.</p>
    </section>

    <section class="catalog" aria-labelledby="movies-title">
      <div class="panel-heading">
        <div>
          <p class="eyebrow">Coleção filmes</p>
          <h2 id="movies-title">Acervo</h2>
        </div>
        <div class="panel-actions">
          <span class="movie-count">{{ totalMovies }} {{ totalMovies === 1 ? "filme" : "filmes" }}</span>
          <button type="button" class="btn secondary" @click="openPopulateMovies">Popular banco</button>
          <button type="button" class="btn" @click="openNewMovie">Novo filme</button>
        </div>
      </div>

      <MovieFilters v-model:query="search" v-model:genre="genreFilter" :genres="genres" @search="searchMovies" />

      <p v-if="error" class="message error">{{ error }}</p>
      <MovieList :movies="movies" :loading="loading" @edit="editMovie" @delete="requestDelete" />

      <nav v-if="totalPages > 1" class="pagination" aria-label="Paginação do acervo">
        <button type="button" class="btn secondary small" :disabled="currentPage === 1 || loading" @click="loadMovies(currentPage - 1)">
          Anterior
        </button>
        <span>Página {{ currentPage }} de {{ totalPages }}</span>
        <button
          type="button"
          class="btn secondary small"
          :disabled="currentPage === totalPages || loading"
          @click="loadMovies(currentPage + 1)"
        >
          Próxima
        </button>
      </nav>
    </section>

    <footer class="credits">
      <span>Locadora</span>
      <span>Vue · Django · MongoDB</span>
    </footer>

    <MovieForm
      v-if="isFormOpen"
      v-model="form"
      :saving="saving"
      :editing="Boolean(editingId)"
      :genres="genres"
      @submit="saveMovie"
      @cancel="resetForm"
    />
    <PopulateMoviesModal v-if="isPopulateOpen" @close="closePopulateMovies" @success="finishPopulation" />
    <DeleteMovieModal v-if="movieToDelete" :movie="movieToDelete" :deleting="deleting" @confirm="confirmDelete" @cancel="cancelDelete" />
  </main>
</template>

<style scoped src="./App.css"></style>
