import { request } from "./client";

export function listMovies(params) {
  return request(`/api/movies/?${new URLSearchParams(params)}`, { fallback: "Não foi possível carregar os filmes." });
}

export function listGenres() {
  return request("/api/genres/", { fallback: "Não foi possível carregar os gêneros." });
}

export function createMovie(movie) {
  return request("/api/movies/", { method: "POST", body: movie, fallback: "Não foi possível salvar o filme." });
}

export function updateMovie(id, movie) {
  return request(`/api/movies/${id}/`, { method: "PUT", body: movie, fallback: "Não foi possível salvar o filme." });
}

export function deleteMovie(id) {
  return request(`/api/movies/${id}/`, { method: "DELETE", fallback: "Não foi possível excluir o filme." });
}

export function populateMovies(amount) {
  return request("/api/movies/populate/", { method: "POST", body: { amount }, fallback: "Não foi possível popular o acervo." });
}
