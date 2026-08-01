import json
from sqlalchemy.orm import Session
from models import Livro
from sqlalchemy import create_engine

def popular_dados():
    with open('data/livros.json', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    livros_novos = [Livro(**item) for item in dados]

    conexao = create_engine('sqlite:///data/bibliotrack.db')
    with Session(conexao) as session:
        session.add_all(livros_novos)
        session.commit()


if __name__ == "__main__":
    popular_dados()

