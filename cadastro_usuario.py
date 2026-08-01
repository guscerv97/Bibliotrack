from models import Usuario, Base, conexao
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import json

def cadastro_usuario():
    with open('data/usuarios.json', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
        novos_usuarios = [Usuario(**usuario) for usuario in dados]
        with Session(conexao) as session:
            session.add_all(novos_usuarios)
            session.commit()


if __name__ == "__main__":
    cadastro_usuario()
