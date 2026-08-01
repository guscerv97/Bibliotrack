import pandas as pd
from models import conexao

query = """
SELECT livros.titulo, COUNT(emprestimos.id) as total_emprestimos
FROM livros
LEFT JOIN emprestimos ON livros.id = emprestimos.livro_id
GROUP BY livros.titulo
ORDER BY total_emprestimos DESC
"""

df = pd.read_sql_query(query, conexao)
print(df)