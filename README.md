# BiblioTrack

Sistema de gestão de biblioteca desenvolvido para consolidar conceitos de banco de dados relacional, ORM, migrações versionadas e, na v2, uma API REST assíncrona.

## O que é o projeto

O BiblioTrack é um sistema de biblioteca onde usuários cadastrados podem fazer empréstimos dos títulos disponíveis, com prazo de 7 dias para devolução. O sistema impede empréstimos quando não há exemplares disponíveis e controla o estoque automaticamente a cada empréstimo e devolução.

A v2 expõe todas essas operações via API REST (FastAPI), além de manter os scripts originais de linha de comando.

## Tecnologias usadas

- **FastAPI**: API REST assíncrona expondo CRUD completo para usuários, livros e empréstimos, com validação de dados via Pydantic e documentação interativa automática (`/docs`).
- **SQLAlchemy (async)**: definição das tabelas como classes Python (`models.py`), com relacionamentos entre `Livro`, `Usuario` e `Emprestimo` via chave estrangeira. As rotas da API usam `AsyncSession` com driver `aiosqlite`.
- **Alembic**: gerenciamento versionado da estrutura do banco de dados, mantendo o histórico de mudanças em `alembic/versions/`.
- **Pandas**: análise dos livros mais emprestados, via query SQL (`LEFT JOIN` + `GROUP BY`).
- **SQLite**: banco de dados relacional usado no projeto.

## API (v2)

Rotas disponíveis, documentadas em `/docs` ao rodar o servidor:

- `GET/POST/PUT/DELETE /usuarios` — CRUD de usuários
- `GET/POST/DELETE /livros` — CRUD de livros
- `POST /emprestimos` — solicitar empréstimo (bloqueia se não houver exemplar disponível)
- `POST /emprestimos/devolucao/{id}` — registrar devolução
- `DELETE /emprestimos/{id}` — remover empréstimo

Usuários e livros com empréstimo vinculado não podem ser deletados (integridade referencial verificada antes da exclusão).

Uma view SQL (`emprestimos_detalhados`) junta as três tabelas para consulta legível direto no banco.

## Cadastro em lote

`cadastro_usuario.py` e `cadastro_livro.py` leem todos os arquivos `.json` de `data/raw/usuarios` e `data/raw/livros`, processam cada registro individualmente (pulando duplicatas sem interromper o lote) e movem os arquivos processados para `data/processed`. Um resumo final mostra quantos registros foram cadastrados e quantos falharam.

## Empréstimo e devolução (scripts originais)

**Empréstimo** (`emprestar_livro.py`): busca livro e usuário, verifica disponibilidade e cria o registro com prazo de 7 dias, decrementando o estoque na mesma transação.

**Devolução** (`devolver_livro.py`): verifica se o empréstimo existe e ainda não foi devolvido, registra a data de devolução e devolve 1 unidade ao estoque.

**Relatório** (`relatorio.py`): livros mais emprestados via `LEFT JOIN`, incluindo os nunca emprestados (contagem zero).

## Estrutura do projeto

```
projeto_03_Bibliotrack/
├── main.py                 # API FastAPI (CRUD + regras de negócio)
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
└── requirements.txt
```

## Como rodar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Aplique as migrações:
   ```bash
   alembic upgrade head
   ```

3. Popule o banco (coloque arquivos `.json` em `data/raw/usuarios` e `data/raw/livros` antes):
   ```bash
   python cadastro_usuario.py
   python cadastro_livro.py
   ```

4. Suba a API:
   ```bash
   uvicorn main:app --reload
   ```
   Documentação interativa em `http://127.0.0.1:8000/docs`.

## Limitações conhecidas

- **Persistência em produção:** o banco usa SQLite como arquivo local. Em plataformas de deploy com sistema de arquivos efêmero (ex: camada gratuita do Render), os dados podem ser resetados a cada reinicialização. Migrar para um banco hospedado (PostgreSQL) resolveria isso.
- A API ainda não tem autenticação — qualquer cliente que conheça a URL pode chamar qualquer rota.

## Próximos passos

- Autenticação (API key ou OAuth2)
- Migração para PostgreSQL
- Frontend no-code consumindo a API
- Containerização com Docker
