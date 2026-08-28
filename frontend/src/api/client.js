/**
 * Wrapper mínimo em volta do fetch: serializa JSON, converte erros HTTP
 * em Error com a mensagem vinda da API (`detail`) ou um fallback.
 */
export async function request(path, { method = "GET", body, fallback = "Erro ao falar com a API." } = {}) {
  const response = await fetch(path, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (response.status === 204) return null;

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || fallback);
  return payload;
}
