# BiblioTrack

Sistema de gestão de biblioteca desenvolvido para consolidar conceitos de banco de dados relacional, ORM e migrações versionadas.

## O que é o projeto

O BiblioTrack é um sistema de biblioteca onde usuários cadastrados podem fazer empréstimos dos títulos disponíveis, com prazo de 7 dias para devolução. O sistema impede empréstimos quando não há exemplares disponíveis e controla o estoque automaticamente a cada empréstimo e devolução.

## Tecnologias usadas

- **SQLAlchemy**: definição das tabelas como classes Python (`models.py`), incluindo relacionamentos entre `Livro`, `Usuario` e `Emprestimo` via chave estrangeira. Também utilizado para a conexão com o banco (`Engine`) e para todas as operações de dado através de `Session` (inserir, buscar, atualizar, deletar).
- **Alembic**: gerenciamento versionado da estrutura do banco de dados. Essa decisão foi tomada visando a segurança da estrutura quando for necessário adicionar novas colunas ou revisar regras de cada coluna, mantendo o histórico de mudanças preservado em `alembic/versions/`.
- **Pandas**: análise dos livros mais emprestados, utilizando uma query SQL (`LEFT JOIN` + `GROUP BY`) para buscar apenas os dados relevantes do banco e apresentá-los como DataFrame.
- **SQLite**: banco de dados relacional usado no projeto.

## O que ele faz

**Cadastro de livros e usuários** (`cadastro_livro.py`, `cadastro_usuario.py`): leem os arquivos `data/livros.json` e `data/usuarios.json`, transformam cada entrada em um objeto (`Livro`/`Usuario`), e inserem no banco via `Session.add_all()`. Atualmente essa leitura é limitada a um arquivo fixo por execução — melhorias para importação incremental estão sendo consideradas para versões futuras.

**Empréstimo** (`emprestar_livro.py`): solicita o ID do livro e o ID do usuário. O programa busca ambos no banco, verifica se o livro está disponível (`quantidade_disponivel > 0`) e, em caso positivo, cria um novo registro em `emprestimos` (com prazo de devolução calculado como hoje + 7 dias) e diminui a quantidade disponível do livro em 1. As duas mudanças acontecem na mesma transação, garantindo que nunca fiquem dessincronizadas.

**Devolução** (`devolver_livro.py`): solicita o ID do empréstimo. O programa verifica se o empréstimo existe e se ainda não foi devolvido (checando se `data_devolucao_real` está vazia). Se for uma devolução válida, preenche a data de devolução com a data atual e devolve 1 unidade ao estoque do livro.

**Relatório** (`relatorio.py`): consulta os livros mais emprestados usando `LEFT JOIN` entre `livros` e `emprestimos`, garantindo que livros nunca emprestados também apareçam no relatório (com contagem zero).

## Estrutura do projeto

```
projeto_03_Bibliotrack/
├── models.py              # Classes SQLAlchemy: Livro, Usuario, Emprestimo (+ engine)
├── cadastro_livro.py       # Popula a tabela livros a partir de data/livros.json
├── cadastro_usuario.py     # Popula a tabela usuarios a partir de data/usuarios.json
├── emprestar_livro.py      # Regra de negócio: registrar um novo empréstimo
├── devolver_livro.py       # Regra de negócio: registrar a devolução de um empréstimo
├── relatorio.py            # Relatório de livros mais emprestados (Pandas)
├── alembic.ini              # Configuração do Alembic (aponta para o banco)
├── alembic/
│   ├── env.py                # Conecta o Alembic às classes de models.py
│   └── versions/              # Histórico de migrações do banco
├── data/
│   ├── livros.json            # Dados de exemplo para popular livros
│   ├── usuarios.json          # Dados de exemplo para popular usuários
│   └── bibliotrack.db          # Banco de dados SQLite (gerado localmente, não versionado)
└── requirements.txt
```

## Como rodar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. A partir da raiz do projeto, aplique as migrações para criar a estrutura do banco:
   ```bash
   alembic upgrade head
   ```
   Isso cria o arquivo `data/bibliotrack.db` com as tabelas `livros`, `usuarios` e `emprestimos`.

3. Popule o banco com os dados de exemplo:
   ```bash
   python cadastro_livro.py
   python cadastro_usuario.py
   ```

4. Use as funções de negócio:
   ```bash
   python emprestar_livro.py
   python devolver_livro.py
   ```

5. Veja o relatório de livros mais emprestados:
   ```bash
   python relatorio.py
   ```

## Melhorias futuras

- Importação incremental de livros/usuários (sem necessidade de sobrescrever o arquivo JSON inteiro)
- Exposição das funções de empréstimo/devolução via API (FastAPI)
- Relatório adicional de empréstimos em atraso
