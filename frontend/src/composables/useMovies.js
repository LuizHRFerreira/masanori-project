import { ref } from "vue";
import * as api from "../api/movies";

const PAGE_SIZE = 20;

const emptyForm = () => ({
  title: "",
  director: "",
  year: "",
  genre: "",
  tags: "",
  rating: "",
  available: true,
});

/** Converte o formulário (strings) no payload esperado pela API. */
function toPayload(form) {
  return {
    ...form,
    year: form.year ? Number(form.year) : null,
    rating: form.rating !== "" ? Number(form.rating) : null,
    tags: form.tags.split(","),
    available: Boolean(form.available),
  };
}

/** Converte um filme vindo da API no formato editável do formulário. */
function toForm(movie) {
  return {
    ...movie,
    tags: movie.tags.join(", "),
    year: movie.year ?? "",
    rating: movie.rating ?? "",
    available: movie.available ?? true,
  };
}

export function useMovies() {
  // acervo
  const movies = ref([]);
  const totalMovies = ref(0);
  const currentPage = ref(1);
  const totalPages = ref(1);
  const genres = ref([]);
  const loading = ref(true);
  const error = ref("");

  // filtros
  const search = ref("");
  const genreFilter = ref("");

  // formulário (novo / editar)
  const form = ref(emptyForm());
  const editingId = ref(null);
  const isFormOpen = ref(false);
  const saving = ref(false);

  // modais
  const isPopulateOpen = ref(false);
  const movieToDelete = ref(null);
  const deleting = ref(false);

  async function loadMovies(page = currentPage.value) {
    loading.value = true;
    error.value = "";
    try {
      const payload = await api.listMovies({ q: search.value, genre: genreFilter.value, page, page_size: PAGE_SIZE });
      movies.value = payload.results;
      totalMovies.value = payload.total;
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
      genres.value = await api.listGenres();
    } catch (requestError) {
      error.value = requestError.message;
    }
  }

  function refresh() {
    return Promise.all([loadMovies(), loadGenres()]);
  }

  function searchMovies() {
    currentPage.value = 1;
    loadMovies(1);
  }

  function openNewMovie() {
    resetForm();
    isFormOpen.value = true;
  }

  function editMovie(movie) {
    editingId.value = movie.id;
    form.value = toForm(movie);
    isFormOpen.value = true;
  }

  function resetForm() {
    editingId.value = null;
    isFormOpen.value = false;
    form.value = emptyForm();
  }

  async function saveMovie() {
    if (!form.value.title.trim() || saving.value) return;
    saving.value = true;
    error.value = "";
    try {
      const payload = toPayload(form.value);
      if (editingId.value) await api.updateMovie(editingId.value, payload);
      else await api.createMovie(payload);
      await refresh();
      resetForm();
    } catch (requestError) {
      error.value = requestError.message;
    } finally {
      saving.value = false;
    }
  }

  function requestDelete(movie) {
    movieToDelete.value = movie;
  }

  function cancelDelete() {
    movieToDelete.value = null;
  }

  async function confirmDelete() {
    if (!movieToDelete.value || deleting.value) return;
    deleting.value = true;
    error.value = "";
    try {
      await api.deleteMovie(movieToDelete.value.id);
    } catch (requestError) {
      error.value = requestError.message;
    } finally {
      deleting.value = false;
      movieToDelete.value = null;
      await refresh();
    }
  }

  function openPopulateMovies() {
    isPopulateOpen.value = true;
  }

  function closePopulateMovies() {
    isPopulateOpen.value = false;
  }

  async function finishPopulation() {
    isPopulateOpen.value = false;
    currentPage.value = 1;
    genreFilter.value = "";
    await refresh();
  }

  return {
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
    loadGenres,
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
  };
}
