from sqlalchemy.orm import Session
from models import Livro, conexao
from pathlib import Path
import json
from sqlalchemy.exc import IntegrityError
import shutil


pasta_livros = Path('data/raw/livros')
arquivos = list(pasta_livros.glob('*.json'))

livros_processados = Path('data/processed')

def popular_dados():
    cadastrou = 0
    falhou = 0

    if not arquivos:
        print("A pasta está vazia")
        return
    
    for file in arquivos:
        with open(file, encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

            with Session(conexao) as session:
                for livro in dados:
                    novo_livro = Livro(
                        titulo = livro["titulo"],
                        isbn = livro['isbn'],
                        quantidade_total = livro['quantidade_total'],
                        quantidade_disponivel = livro['quantidade_total']
         )

                    try:
                        session.add(novo_livro)
                        cadastrou += 1
                        session.commit()
                    except IntegrityError:
                        session.rollback()
                        print("Livro já cadastrado")
                        falhou += 1
        shutil.move(file, livros_processados)
    print(f"Foram cadastrados {cadastrou} novos livros, {falhou} não foram processados")



if __name__ == "__main__":
    popular_dados()

