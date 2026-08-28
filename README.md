# Masanori

Projeto individual para demonstrar um banco NoSQL com MongoDB: um catálogo de livros com documentos flexíveis, busca por texto e operações CRUD.

## Estrutura

- `frontend/`: Vue 3 + Vite, com proxy de `/api` para o Django.
- `backend/`: Django com endpoints JSON em `/api/health/`, `/api/books/`, `/api/books/populate/` e `/api/books/<id>/`.
  - `tasks/views.py`: camada HTTP, responsável por requests, responses e status HTTP.
  - `tasks/services.py`: regras de negócio, validação, serialização e acesso ao MongoDB.
- `docker-compose.yml`: MongoDB local na porta `27017`.

## Como executar

Com Docker e Docker Compose instalados, suba toda a aplicação com um único comando:

```bash
make up
```

Isso inicia MongoDB, Django e Vue. Acesse `http://localhost:5174/`.

Para derrubar todos os serviços:

```bash
make down
```

Para acompanhar os logs:

```bash
make logs
```

A API fica disponível em `http://localhost:8001/api/health/`.

## API

Um documento de livro pode ter campos diferentes sem migração de tabela:

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "year": 2008,
  "genre": "Tecnologia",
  "tags": ["programacao", "qualidade"],
  "rating": 4.8
}
```

Com o backend rodando:

```bash
curl http://localhost:8001/api/health/
curl 'http://localhost:8001/api/books/?q=code&page=1&page_size=20'
curl -X POST http://localhost:8001/api/books/ \
	-H 'Content-Type: application/json' \
	-d '{"title":"Clean Code","author":"Robert C. Martin","year":2008,"genre":"Tecnologia","tags":["programacao"],"rating":4.8}'
curl -X POST http://localhost:8001/api/books/populate/ \
  -H 'Content-Type: application/json' \
  -d '{"amount":20}'
```

A listagem de livros é paginada. O parâmetro `page_size` aceita de 1 a 100 registros e, por padrão, retorna 20 livros por página. A resposta contém `results`, `total`, `page`, `page_size` e `total_pages`.

O endpoint de popularização baixa o dataset público do Kaggle, escolhe um trecho aleatório com a quantidade solicitada (de 1 a 1000), remove os livros atuais e insere os novos documentos.

## Índices e análise de consultas

O backend cria automaticamente o índice `created_at_desc` na inicialização do Django, por meio de `TasksConfig.ready()`. A operação `create_index()` é idempotente: se o índice já existir, ele é reutilizado; se o MongoDB ou o volume forem recriados, ele é criado novamente.

Esse índice atende à ordenação usada pela listagem paginada:

```javascript
db.books.createIndex({ created_at: -1 }, { name: "created_at_desc" });
```

Para verificar o plano de execução da listagem:

```javascript
db.books.explain("executionStats").find({}).sort({ created_at: -1 }).skip(0).limit(20);
```

Antes do índice, a consulta apresentou `COLLSCAN + SORT`, examinando 1000 documentos. Depois do índice, apresentou `IXSCAN`, examinando apenas 20 documentos da página. `COLLSCAN` indica full scan da coleção e `IXSCAN` indica uso de índice. Os campos mais importantes são `totalDocsExamined`, `totalKeysExamined`, `nReturned` e `executionTimeMillis`.

As buscas textuais usam regex case-insensitive em título, autor e tags. Por isso, a contagem feita pela paginação ainda pode apresentar `COLLSCAN`; índices comuns não são eficientes para regex parcial com a opção `i`. Com o volume atual, essa decisão deve ser acompanhada pelo `explain()` antes de criar índices adicionais.

Para observar as operações reais durante a popularização, o profiler pode ser ativado temporariamente:

```javascript
db.setProfilingLevel(2);
// Execute a popularização pelo frontend ou pela API.
db.system.profile.find({ ns: "masanori.books" }).sort({ ts: -1 }).limit(20).pretty();
db.setProfilingLevel(0);
```

Na medição realizada, a remoção de 1000 livros levou 51 ms e a inserção de 20 livros levou 2 ms. A remoção total (`delete_many({})`) não utiliza índice, pois precisa apagar todos os documentos; o índice é relevante principalmente para a listagem e sua ordenação.

## Argumentação do trabalho

**Escolha:** MongoDB, um banco orientado a documentos, foi escolhido por armazenar cada livro como um documento JSON/BSON e permitir evolução do esquema sem migrações rígidas.

**Vantagens:** flexibilidade para adicionar campos; documentos próximos do formato usado pela API; boa experiência para prototipagem; consultas por texto, arrays e filtros.

**Desvantagens:** exige cuidado com validação; relacionamentos complexos podem ser menos naturais que em bancos relacionais; consistência e modelagem precisam ser planejadas; a flexibilidade pode gerar documentos inconsistentes.

**Roteiro do vídeo de 5 minutos:** 1) apresentar o problema e a escolha (1 min); 2) mostrar o documento e a coleção `books` (1 min); 3) demonstrar cadastro, busca, edição e exclusão na tela (2 min); 4) explicar vantagens, desvantagens e o fluxo Vue-Django-MongoDB (1 min).
