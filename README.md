# Locadora

Projeto individual para demonstrar um banco NoSQL com MongoDB: o acervo de uma locadora de filmes com documentos flexíveis, busca por texto, filtro por gênero e operações CRUD.

A identidade visual é inspirada no álbum *The Car* (Arctic Monkeys, 2022): paleta verde-oliva, creme, areia e vermelho queimado, tipografia grotesca pesada em caixa alta e grão de filme 35mm.

## Estrutura

```
backend/
└── tasks/
    ├── db.py          # conexão com o MongoDB, coleções e índices
    ├── kaggle.py      # download e normalização do dataset IMDB Top 1000
    ├── services.py    # regras de negócio: validação, CRUD, busca e serialização
    ├── views.py       # camada HTTP: requests, responses e status
    └── urls.py        # rotas da API
frontend/
└── src/
    ├── main.js
    ├── App.vue / App.css          # template da página e seu estilo
    ├── api/                       # chamadas HTTP (client.js + movies.js)
    ├── composables/useMovies.js   # estado e ações do acervo (lista, form, exclusão…)
    ├── components/<Nome>/         # cada componente em sua pasta: .vue (template + props/emits),
    │                              # .js (lógica) e .css (estilo)
    └── styles/                    # tokens da paleta, base, tipografia, botões, forms e modais
```

- `frontend/`: Vue 3 + Vite, com proxy de `/api` para o Django.
- `backend/`: Django com endpoints JSON em `/api/health/`, `/api/movies/`, `/api/genres/`, `/api/movies/populate/` e `/api/movies/<id>/`.
- `docker-compose.yml`: MongoDB, Django e Vue em containers.

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

Um documento de filme pode ter campos diferentes sem migração de tabela:

```json
{
  "title": "Drive",
  "director": "Nicolas Winding Refn",
  "year": 2011,
  "genre": "Crime",
  "tags": ["neo-noir", "road movie"],
  "rating": 4.5,
  "available": true
}
```

O campo `available` indica se o filme está na prateleira (`true`) ou alugado (`false`). A nota vai de 0 a 5.

Com o backend rodando:

```bash
curl http://localhost:8001/api/health/
curl 'http://localhost:8001/api/movies/?q=drive&genre=Crime&page=1&page_size=20'
curl http://localhost:8001/api/genres/
curl -X POST http://localhost:8001/api/movies/ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Drive","director":"Nicolas Winding Refn","year":2011,"genre":"Crime","tags":["neo-noir"],"rating":4.5,"available":true}'
curl -X PUT http://localhost:8001/api/movies/<id>/ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Drive","available":false}'
curl -X DELETE http://localhost:8001/api/movies/<id>/
curl -X POST http://localhost:8001/api/movies/populate/ \
  -H 'Content-Type: application/json' \
  -d '{"amount":20}'
```

A listagem de filmes é paginada. O parâmetro `q` busca por título, diretor ou tag (regex case-insensitive) e `genre` filtra pelo gênero exato. O parâmetro `page_size` aceita de 1 a 100 registros e, por padrão, retorna 20 filmes por página. A resposta contém `results`, `total`, `page`, `page_size` e `total_pages`.

O endpoint de popularização baixa o dataset público [IMDB Top 1000](https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows) do Kaggle, escolhe um trecho aleatório com a quantidade solicitada (de 1 a 1000), remove os filmes atuais e insere os novos documentos. Na importação, o primeiro gênero vira `genre`, todos os gêneros e a classificação indicativa viram `tags`, a nota IMDB (0–10) é convertida para a escala de 0 a 5 e a disponibilidade é sorteada (cerca de 75% disponíveis). As demais colunas do CSV (sinopse, elenco, duração, bilheteria...) são mantidas no documento, ilustrando o esquema flexível.

## Índices e análise de consultas

O backend cria automaticamente o índice `created_at_desc` na inicialização do Django, por meio de `TasksConfig.ready()`. A operação `create_index()` é idempotente: se o índice já existir, ele é reutilizado; se o MongoDB ou o volume forem recriados, ele é criado novamente.

Esse índice atende à ordenação usada pela listagem paginada:

```javascript
db.movies.createIndex({ created_at: -1 }, { name: "created_at_desc" });
```

Para verificar o plano de execução da listagem:

```javascript
db.movies.explain("executionStats").find({}).sort({ created_at: -1 }).skip(0).limit(20);
```

Sem o índice, a consulta apresenta `COLLSCAN + SORT`, examinando todos os documentos da coleção. Com o índice, apresenta `IXSCAN`, examinando apenas os documentos da página. `COLLSCAN` indica full scan da coleção e `IXSCAN` indica uso de índice. Os campos mais importantes são `totalDocsExamined`, `totalKeysExamined`, `nReturned` e `executionTimeMillis`.

As buscas textuais usam regex case-insensitive em título, diretor e tags. Por isso, a contagem feita pela paginação ainda pode apresentar `COLLSCAN`; índices comuns não são eficientes para regex parcial com a opção `i`. O filtro por gênero é uma igualdade simples e seria um bom candidato a índice caso o volume cresça — a decisão deve ser acompanhada pelo `explain()`.

Para observar as operações reais durante a popularização, o profiler pode ser ativado temporariamente:

```javascript
db.setProfilingLevel(2);
// Execute a popularização pelo frontend ou pela API.
db.system.profile.find({ ns: "masanori.movies" }).sort({ ts: -1 }).limit(20).pretty();
db.setProfilingLevel(0);
```

A remoção total (`delete_many({})`) não utiliza índice, pois precisa apagar todos os documentos; o índice é relevante principalmente para a listagem e sua ordenação.

## Argumentação do trabalho

**Escolha:** MongoDB, um banco orientado a documentos, foi escolhido por armazenar cada filme como um documento JSON/BSON e permitir evolução do esquema sem migrações rígidas — um filme importado do Kaggle carrega sinopse e elenco, enquanto um cadastrado à mão tem só os campos básicos, e ambos convivem na mesma coleção.

**Vantagens:** flexibilidade para adicionar campos; documentos próximos do formato usado pela API; boa experiência para prototipagem; consultas por texto, arrays (tags) e filtros.

**Desvantagens:** exige cuidado com validação; relacionamentos complexos (clientes, locações, devoluções) podem ser menos naturais que em bancos relacionais; consistência e modelagem precisam ser planejadas; a flexibilidade pode gerar documentos inconsistentes.

**Roteiro do vídeo de 5 minutos:** 1) apresentar o problema e a escolha (1 min); 2) mostrar o documento e a coleção `movies` (1 min); 3) demonstrar cadastro, busca, filtro por gênero, edição, marcação de alugado/disponível e exclusão na tela (2 min); 4) explicar vantagens, desvantagens e o fluxo Vue-Django-MongoDB (1 min).
