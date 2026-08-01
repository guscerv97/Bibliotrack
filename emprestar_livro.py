from datetime import date, timedelta
from models import Base, Emprestimo, conexao, Usuario, Livro
from sqlalchemy.orm import Session

def emprestar_livro(livro_id, usuario_id):
    with Session(conexao) as session:
        livro = session.get(Livro, livro_id)
        usuario = session.get(Usuario, usuario_id)

        if livro is None or usuario is None:
            print("Usuario ou livro não encontrado")
            return 

        if livro.quantidade_disponivel > 0:
            novo_emprestimo = Emprestimo(livro_id = livro_id, usuario_id = usuario_id, data_emprestimo = date.today(), data_devolucao_prevista = date.today() + timedelta(days=7))
            livro.quantidade_disponivel -= 1
            session.add(novo_emprestimo)
            session.commit()
            print(f"Empréstimo registrado! {usuario.nome} pegou '{livro.titulo}'. Devolver até {novo_emprestimo.data_devolucao_prevista}.")
        else:
            print(f"Desculpe, o livro {livro.titulo} não está disponível no momento")

if __name__ == "__main__":
    emprestar_livro(int(input("Digite o ID do livro desejado: ")), int(input("Digite seu ID: ")))