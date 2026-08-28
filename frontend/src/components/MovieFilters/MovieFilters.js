export function useMovieFilters({ query, genre, emit }) {
  function changeGenre(event) {
    genre.value = event.target.value;
    emit("search");
  }

  function clearFilters() {
    query.value = "";
    genre.value = "";
    emit("search");
  }

  return { changeGenre, clearFilters };
}
