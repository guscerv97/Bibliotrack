# BiblioTrack

Sistema de gestão de biblioteca desenvolvido para consolidar conceitos de banco de dados relacional, ORM, migrações versionadas e, na v2, uma API REST assíncrona.

## O que é o projeto

O BiblioTrack é um sistema de biblioteca onde usuários cadastrados podem fazer empréstimos dos títulos disponíveis, com prazo de 7 dias para devolução. O sistema impede empréstimos quando não há exemplares disponíveis e controla o estoque automaticamente a cada empréstimo e devolução.

A v2 expõe todas essas operações via API REST (FastAPI), além de manter os scripts originais de linha de comando.

## API publicada

A API está no ar em:

**https://bibliotrack-api-hkqp.onrender.com**

Documentação interativa: **https://bibliotrack-api-hkqp.onrender.com/docs**

Está hospedada na camada gratuita do Render, que hiberna após um período de inatividade — a primeira requisição depois disso pode demorar até um minuto enquanto o serviço reinicia. O banco de dados é PostgreSQL hospedado na Neon, então os dados persistem normalmente entre deploys e reinicializações do serviço.

## Frontend

Um frontend em Next.js (gerado com [v0.dev](https://v0.dev), da Vercel) consome essa API e está publicado em:

**https://bibliotrack-gamma.vercel.app**

Ele se conecta à API através da variável de ambiente `NEXT_PUBLIC_API_URL` (sem URL hardcoded no código do frontend). O CORS da API (configurado em `main.py`) libera especificamente esse domínio, os métodos `GET`, `POST`, `PUT` e `DELETE`, e o header `x-api-key` usado nas rotas administrativas.

### Chave de API para teste

As rotas que criam, alteram ou apagam dados (`POST`, `PUT`, `DELETE` de usuários e livros) exigem uma chave de API, enviada no header `x-api-key`. Para testar, use:

```
x-api-key: chavesupersegura
```

Rotas de leitura (`GET`) e as usadas pelo usuário final para emprestar e devolver livros não exigem chave.

## Tecnologias usadas

- **FastAPI**: API REST assíncrona expondo CRUD completo para usuários, livros e empréstimos, com validação de dados via Pydantic, CORS configurado para o frontend, e documentação interativa automática (`/docs`).
- **SQLAlchemy**: definição das tabelas como classes Python (`models.py`), com relacionamentos entre `Livro`, `Usuario` e `Emprestimo` via chave estrangeira. A API (`main.py`) usa `AsyncSession` com driver `asyncpg`; os scripts de linha de comando usam a engine síncrona de `models.py`, com driver `psycopg2`.
- **PostgreSQL (Neon)**: banco de dados relacional hospedado na Neon, usado tanto pela API publicada no Render quanto pelos scripts locais — substituiu o SQLite das versões anteriores do projeto.
- **Alembic**: gerenciamento versionado da estrutura do banco de dados, mantendo o histórico de mudanças em `alembic/versions/` (inclui, por exemplo, a migração que adicionou a coluna `genero` a `livros`).
- **Pandas**: análise dos livros mais emprestados, via query SQL (`LEFT JOIN` + `GROUP BY`).

## API — rotas disponíveis

- `GET /usuarios` — lista usuários
- `GET /usuarios/{id}` — busca usuário por ID
- `POST /usuarios` 🔒 — cadastra usuário
- `PUT /usuarios/{id}` 🔒 — atualiza usuário
- `DELETE /usuarios/{id}` 🔒 — remove usuário (bloqueado se houver empréstimo vinculado)
- `GET /livros` — lista livros
- `GET /livros/{id}` — busca livro por ID
- `POST /livros` 🔒 — cadastra livro (inclui `genero`)
- `DELETE /livros/{id}` 🔒 — remove livro (bloqueado se houver empréstimo vinculado)
- `POST /emprestimos` — solicita empréstimo; bloqueia se não houver exemplar disponível ou se o usuário já tiver um empréstimo ativo (não devolvido) do mesmo livro
- `POST /emprestimos/devolucao/{id}` — registra devolução; exige o `usuario_id` do solicitante e confirma que o empréstimo pertence a esse usuário
- `DELETE /emprestimos/{id}` 🔒 — remove empréstimo
- `GET /usuarios/emprestimos/{id}` — lista empréstimos de um usuário

🔒 = requer a chave de API no header `x-api-key`

### Verificação de identidade (sem senha)

As rotas de empréstimo (`POST /emprestimos`) e devolução (`POST /emprestimos/devolucao/{id}`) confirmam a identidade do usuário apenas pelo `usuario_id` informado na requisição — não existe senha, login ou sessão para o usuário final. Essa é uma decisão consciente de escopo: o projeto é de demonstração/portfólio, e essa verificação já é suficiente para expressar a regra de negócio (um usuário não pode devolver, em nome de outro, um empréstimo que não é seu). Para um sistema real com dados sensíveis, isso precisaria de autenticação de verdade (ex: login com senha, OAuth2, tokens de sessão).

## Cadastro em lote

`cadastro_usuario.py` e `cadastro_livro.py` leem todos os arquivos `.json` de `data/raw/usuarios` e `data/raw/livros`, processam cada registro individualmente (pulando duplicatas sem interromper o lote) e movem os arquivos processados para `data/processed`. Um resumo final mostra quantos registros foram cadastrados e quantos falharam.

Como esses scripts e a API publicada no Render agora apontam para o mesmo banco Postgres (Neon), rodar esses scripts localmente popula diretamente os dados que a API em produção também enxerga. Ainda assim, não existe endpoint na API para importação em massa — o cadastro em lote continua sendo um processo manual, executado localmente.

## Empréstimo e devolução (scripts originais)

**Empréstimo** (`emprestar_livro.py`): busca livro e usuário, verifica disponibilidade e cria o registro com prazo de 7 dias, decrementando o estoque na mesma transação.

**Devolução** (`devolver_livro.py`): verifica se o empréstimo existe e ainda não foi devolvido, registra a data de devolução e devolve 1 unidade ao estoque.

**Relatório** (`relatorio.py`): livros mais emprestados via `LEFT JOIN`, incluindo os nunca emprestados (contagem zero).

## Estrutura do projeto

```
Bibliotrack/
├── main.py                   # API FastAPI (CRUD + regras de negócio + autenticação + CORS)
├── models.py                  # Classes SQLAlchemy: Livro, Usuario, Emprestimo + engine síncrona (psycopg2)
├── cadastro_livro.py          # Cadastro em lote a partir de data/raw/livros
├── cadastro_usuario.py        # Cadastro em lote a partir de data/raw/usuarios
├── emprestar_livro.py         # Script original: registrar empréstimo via terminal
├── devolver_livro.py          # Script original: registrar devolução via terminal
├── relatorio.py                # Relatório de livros mais emprestados (Pandas)
├── alembic.ini
├── alembic/
│   ├── env.py                 # monta a URL do Postgres (Neon) a partir do .env
│   └── versions/
├── data/
│   ├── raw/usuarios/          # Arquivos JSON a processar
│   ├── raw/livros/            # Arquivos JSON a processar
│   └── processed/             # Arquivos já processados
├── .env                        # API_KEY, POSTGRES_* (não versionado, ver .gitignore)
└── requirements.txt
```

## Como rodar localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Crie um arquivo `.env` na raiz com suas credenciais:
   ```
   API_KEY=escolha-uma-chave
   POSTGRES_USER=seu-usuario
   POSTGRES_PASSWORD=sua-senha
   POSTGRES_HOST=seu-host-neon
   POSTGRES_PORT=5432
   POSTGRES_DB=seu-banco
   POSTGRES_SSLMODE=require
   ```

3. Aplique as migrações:
   ```bash
   alembic upgrade head
   ```

4. Popule o banco (coloque arquivos `.json` em `data/raw/usuarios` e `data/raw/livros` antes):
   ```bash
   python cadastro_usuario.py
   python cadastro_livro.py
   ```

5. Suba a API:
   ```bash
   uvicorn main:app --reload
   ```
   Documentação interativa em `http://127.0.0.1:8000/docs`.

## Limitações conhecidas

- Os scripts de cadastro em lote (`cadastro_usuario.py`, `cadastro_livro.py`) continuam sendo executados manualmente, localmente — não existe endpoint na API para importação em massa.
- A autenticação das rotas administrativas é uma chave de API simples, fixa, sem expiração ou usuários individuais. Para uma aplicação real, o ideal seria OAuth2 com login por usuário.
- A identificação do usuário nas rotas de empréstimo e devolução é feita apenas pelo `usuario_id`, sem senha ou sessão (ver "Verificação de identidade" acima). É suficiente para demonstrar a regra de negócio, mas não é autenticação real — não deve ser usada como está para dados sensíveis em produção.

## Próximos passos

- Containerização com Docker