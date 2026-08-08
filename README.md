# BiblioTrack

Sistema de gestão de biblioteca desenvolvido para consolidar conceitos de banco de dados relacional, ORM, migrações versionadas e, na v2, uma API REST assíncrona.

## O que é o projeto

O BiblioTrack é um sistema de biblioteca onde usuários cadastrados podem fazer empréstimos dos títulos disponíveis, com prazo de 7 dias para devolução. O sistema impede empréstimos quando não há exemplares disponíveis e controla o estoque automaticamente a cada empréstimo e devolução.

A v2 expõe todas essas operações via API REST (FastAPI), além de manter os scripts originais de linha de comando.

## API publicada

A API está no ar em:

**https://bibliotrack-api-hkqp.onrender.com**

Documentação interativa: **https://bibliotrack-api-hkqp.onrender.com/docs**

Está hospedada na camada gratuita do Render, que hiberna após um período de inatividade. A primeira requisição depois disso pode demorar até um minuto enquanto o serviço reinicia.

### Chave de API para teste

As rotas que criam, alteram ou apagam dados (`POST`, `PUT`, `DELETE` de usuários e livros) exigem uma chave de API, enviada no header `x-api-key`. Para testar, use:

```
x-api-key: chavesupersegura
```

Rotas de leitura (`GET`) e as usadas pelo usuário final para emprestar e devolver livros não exigem chave.

## Tecnologias usadas

- **FastAPI**: API REST assíncrona expondo CRUD completo para usuários, livros e empréstimos, com validação de dados via Pydantic e documentação interativa automática (`/docs`).
- **SQLAlchemy (async)**: definição das tabelas como classes Python (`models.py`), com relacionamentos entre `Livro`, `Usuario` e `Emprestimo` via chave estrangeira. As rotas da API usam `AsyncSession` com driver `aiosqlite`.
- **Alembic**: gerenciamento versionado da estrutura do banco de dados, mantendo o histórico de mudanças em `alembic/versions/`.
- **Pandas**: análise dos livros mais emprestados, via query SQL (`LEFT JOIN` + `GROUP BY`).
- **SQLite**: banco de dados relacional usado no projeto.

## API — rotas disponíveis

- `GET /usuarios` — lista usuários
- `GET /usuarios/{id}` — busca usuário por ID
- `POST /usuarios` 🔒 — cadastra usuário
- `PUT /usuarios/{id}` 🔒 — atualiza usuário
- `DELETE /usuarios/{id}` 🔒 — remove usuário (bloqueado se houver empréstimo vinculado)
- `GET /livros` — lista livros
- `GET /livros/{id}` — busca livro por ID
- `POST /livros` 🔒 — cadastra livro
- `DELETE /livros/{id}` 🔒 — remove livro (bloqueado se houver empréstimo vinculado)
- `POST /emprestimos` — solicita empréstimo (bloqueia se não houver exemplar disponível)
- `POST /emprestimos/devolucao/{id}` — registra devolução
- `DELETE /emprestimos/{id}` 🔒 — remove empréstimo
- `GET /usuarios/emprestimos/{id}` — lista empréstimos de um usuário

🔒 = requer a chave de API no header `x-api-key`

Uma view SQL (`emprestimos_detalhados`) junta as três tabelas para consulta legível direto no banco.

## Cadastro em lote

`cadastro_usuario.py` e `cadastro_livro.py` leem todos os arquivos `.json` de `data/raw/usuarios` e `data/raw/livros`, processam cada registro individualmente (pulando duplicatas sem interromper o lote) e movem os arquivos processados para `data/processed`. Um resumo final mostra quantos registros foram cadastrados e quantos falharam. Esses scripts rodam contra o banco local — não populam o banco publicado no Render.

## Empréstimo e devolução (scripts originais)

**Empréstimo** (`emprestar_livro.py`): busca livro e usuário, verifica disponibilidade e cria o registro com prazo de 7 dias, decrementando o estoque na mesma transação.

**Devolução** (`devolver_livro.py`): verifica se o empréstimo existe e ainda não foi devolvido, registra a data de devolução e devolve 1 unidade ao estoque.

**Relatório** (`relatorio.py`): livros mais emprestados via `LEFT JOIN`, incluindo os nunca emprestados (contagem zero).

## Estrutura do projeto

```
Bibliotrack/
├── main.py                 # API FastAPI (CRUD + regras de negócio + autenticação)
├── models.py                # Classes SQLAlchemy: Livro, Usuario, Emprestimo
├── cadastro_livro.py        # Cadastro em lote a partir de data/raw/livros
├── cadastro_usuario.py      # Cadastro em lote a partir de data/raw/usuarios
├── emprestar_livro.py       # Script original: registrar empréstimo via terminal
├── devolver_livro.py        # Script original: registrar devolução via terminal
├── relatorio.py             # Relatório de livros mais emprestados (Pandas)
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── data/
│   ├── raw/usuarios/         # Arquivos JSON a processar
│   ├── raw/livros/           # Arquivos JSON a processar
│   ├── processed/            # Arquivos já processados
│   └── bibliotrack.db        # Banco SQLite (gerado localmente, não versionado)
├── .env                      # API_KEY (não versionado, ver .gitignore)
└── requirements.txt
```

## Como rodar localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Crie um arquivo `.env` na raiz com sua chave de API:
   ```
   API_KEY=escolha-uma-chave
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

- **Persistência em produção:** o banco usa SQLite como arquivo local. No Render (camada gratuita), o sistema de arquivos é efêmero — a cada novo deploy, o `alembic upgrade head` recria as tabelas do zero e qualquer dado cadastrado anteriormente é perdido. Isso já aconteceu durante o desenvolvimento e é uma limitação conhecida, não um bug. Um banco hospedado (PostgreSQL) resolveria isso.
- Os scripts de cadastro em lote rodam localmente, contra o banco local — não há hoje uma forma de popular o banco publicado em massa, só pela API rota a rota.
- A autenticação é uma chave de API simples, fixa, sem expiração ou usuários individuais. Para uma aplicação real, o ideal seria OAuth2 com login por usuário.

## Próximos passos

Ficam para um próximo projeto, construído do zero:

- Migração para PostgreSQL, resolvendo a persistência em produção
- Containerização com Docker
- Frontend consumindo a API
