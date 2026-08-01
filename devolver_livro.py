from datetime import date
from models import Base, Emprestimo, conexao, Usuario, Livro
from sqlalchemy.orm import Session

def devolver_livro(emprestimo_id):

    with Session(conexao) as session:
        emprestimo = session.get(Emprestimo, emprestimo_id)

        if emprestimo is None:
            print("Desculpe, seu empréstimo não foi localizado")
            return

        if emprestimo.data_devolucao_real is not None:
            print("Esse empréstimo já foi devolvido anteriormente")
            return

        emprestimo.data_devolucao_real = date.today()
        usuario = session.get(Usuario, emprestimo.usuario_id)
        livro = emprestimo.livro_id
        livro_devolvido = session.get(Livro, livro)
        livro_devolvido.quantidade_disponivel += 1
        session.commit()
        print(f"Olá {usuario.nome}, você devolveu o livro {livro_devolvido.titulo} com sucesso!")


if __name__ == "__main__":
    devolver_livro(int(input("Digite o ID do seu empréstimo para seguir com a devolução: ")))
