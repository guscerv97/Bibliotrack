from models import Usuario, conexao
from sqlalchemy.orm import Session
import json
from pathlib import Path
import shutil
from sqlalchemy.exc import IntegrityError

pasta_usuarios = Path("data/raw/usuarios")
arquivos = list(pasta_usuarios.glob("*.json"))

usuarios_processados = Path("data/processed")


def cadastro_usuario():
    cadastrou = 0
    falhou = 0

    if not arquivos:
        print("A pasta está vazia")
        return

    for file in arquivos:
        with open(file, encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
            
            with Session(conexao) as session:
                for usuario in dados:
                    novo_usuario = Usuario(nome = usuario["nome"], email= usuario["email"])
                    try:
                        session.add(novo_usuario)
                        session.commit()
                        cadastrou +=1
                    except IntegrityError:
                        session.rollback()
                        print("E-mail já cadastrado")
                        falhou +=1

        shutil.move(file, usuarios_processados)

    print(f"Foram cadastrados {cadastrou} novos usuários, {falhou} não foram processados")



if __name__ == "__main__":
    cadastro_usuario()
