from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from models import Usuario, Livro, Emprestimo
import os
from dotenv import load_dotenv


load_dotenv()

url = (
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

sslmode = os.getenv('POSTGRES_SSLMODE')
connect_args = {"ssl": sslmode} if sslmode else {}

conexao = create_async_engine(url, connect_args=connect_args)

API_KEY = os.getenv('API_KEY')

def verificar_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail= 'Chave de API inválida')

class UsuarioCreate(BaseModel):
    nome: str
    email: str

class CadastroLivro(BaseModel):
    titulo : str
    isbn : int
    genero : str
    quantidade_total : int

app = FastAPI()



@app.get("/")
def home():
    return {"mensagem": "API no ar"}

@app.get("/usuarios")
async def listar_usuarios(limite: int = 10):
    async with AsyncSession(conexao) as session:
        resultado = await session.execute(select(Usuario).limit(limite))
        usuarios = resultado.scalars().all()
        return usuarios

@app.get("/livros")
async def listar_livros(limite: int = 10):
    async with AsyncSession(conexao) as session:
        resultado = await session.execute(select(Livro).limit(limite))
        livros = resultado.scalars().all()
        return livros

@app.get("/livros/{livro_id}")
async def procurar_livro(livro_id: int):
    try:
        async with AsyncSession(conexao) as session:
            livro = await session.get(Livro, livro_id)
            return {"Titulo" : livro.titulo, "Quantidade Disponível" : livro.quantidade_disponivel}
    except:
        raise HTTPException(status_code= 404, detail="Livro não encontrado")
            

@app.get("/usuarios/{usuario_id}") 
async def cadastro_usuario(usuario_id : int):
    try:
        async with AsyncSession(conexao) as session:
            usuario = await session.get(Usuario, usuario_id)
        return {"usuario" : usuario.nome, "email" : usuario.email ,"id" : usuario_id}
    except:
        raise HTTPException(status_code=400, detail="Usuario não localizado")

@app.post("/usuarios", dependencies=[Depends(verificar_api_key)])
async def criar_usuario(usuario: UsuarioCreate):
    try:
        async with AsyncSession(conexao) as session:
            novo_usuario = Usuario(nome = usuario.nome, email=usuario.email)
            session.add(novo_usuario)
            novo_usuario_nome = novo_usuario.nome
            novo_usuario_email = novo_usuario.email
            await session.commit()
            return {"mensagem" : "Usuario cadastrado com sucesso", "nome":novo_usuario_nome, "email": novo_usuario_email}
        
    except:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
@app.post("/livros", dependencies=[Depends(verificar_api_key)])
async def cadastro_livro(livro: CadastroLivro):
    try:
        async with AsyncSession(conexao) as session:
            novo_livro = Livro(titulo = livro.titulo, isbn=livro.isbn, genero = livro.genero, quantidade_total = livro.quantidade_total, quantidade_disponivel = livro.quantidade_total)
            session.add(novo_livro)
            await session.commit()
            return {"Mensagem" : "Livro cadastrado com sucesso"}

    except:
        raise HTTPException(status_code= 400, detail= "Livro já cadastrado")


@app.delete("/usuarios/{usuario_id}", dependencies=[Depends(verificar_api_key)])
async def deletar_usuario(usuario_id:int):
        async with AsyncSession(conexao) as session:
            usuario = await session.get(Usuario, usuario_id)
            if usuario is None:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

            resultado = await session.execute(select(Emprestimo).where(Emprestimo.usuario_id == usuario_id))
            emprestimos_vinculados = resultado.scalars().all()

            if emprestimos_vinculados:
                raise HTTPException(status_code=403, detail="Você não pode excluir um usuário já com empréstimo cadastrado")
            
            await session.delete(usuario)
            await session.commit()
            return {"mensagem": "Usuário removido com sucesso"}

@app.put("/usuarios/{usuario_id}", dependencies=[Depends(verificar_api_key)])
async def atualizar_usuario(usuario_id:int, dados: UsuarioCreate):
    async with AsyncSession(conexao) as session:
        usuario = await session.get(Usuario, usuario_id)
        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        usuario.nome = dados.nome
        usuario.email = dados.email
        novo_nome = usuario.nome
        await session.commit()
        return {"mensagem" : f"Dados do usuario {novo_nome} atualizados com sucesso"}

@app.post("/emprestimos")
async def solicitar_emprestimo(livro_id: int, usuario_id: int):
    async with AsyncSession(conexao) as session:
        usuario = await session.get(Usuario, usuario_id)
        livro = await session.get(Livro, livro_id)

        if livro is None or usuario is None:
            raise HTTPException(status_code=404, detail="Usuário ou Livro não encontrado")
        if livro.quantidade_disponivel == 0:
            raise HTTPException(status_code=400, detail=f"Livro {livro.titulo} não disponível")
        
        novo_emprestimo = Emprestimo(usuario_id = usuario_id, livro_id = livro_id, data_emprestimo = date.today(), data_devolucao_prevista = date.today() + timedelta(days=7))
        session.add(novo_emprestimo)
        livro.quantidade_disponivel -= 1
        nome_usuario = usuario.nome
        titulo_livro = livro.titulo
        prazo_devolucao = novo_emprestimo.data_devolucao_prevista
        await session.commit()
        return {"Mensagem" : f"Olá {nome_usuario}, empréstimo do livro {titulo_livro} realizado com sucesso! Devolva até {prazo_devolucao}"}

@app.post("/emprestimos/devolucao/{emprestimo_id}")
async def devolucao_livro(emprestimo_id:int):
    async with AsyncSession(conexao) as session:

        emprestimo = await session.get(Emprestimo, emprestimo_id)
        if emprestimo is None:
            raise HTTPException(status_code=404, detail="Empréstimo não localizado")
        
        livro = await session.get(Livro, emprestimo.livro_id)
        if emprestimo.data_devolucao_real is not None:
            raise HTTPException(status_code=400, detail= "Empréstimo já devolvido")
        
        emprestimo.data_devolucao_real = date.today()
        livro.quantidade_disponivel += 1
        livro_devolvido = livro.titulo
        await session.commit()
        return {"Mensagem" : f"O livro {livro_devolvido} foi devolvido com sucesso!"}

@app.delete("/livros/{livro_id}", dependencies=[Depends(verificar_api_key)])
async def deletar_livro(livro_id: int):
    async with AsyncSession(conexao) as session:
        livro = await session.get(Livro, livro_id)
        if livro is None:
            raise HTTPException(status_code= 404, detail="Livro não localizado")
        resultado = await session.execute(select(Emprestimo).where(Emprestimo.livro_id == livro_id))
        emprestimos_vinculados = resultado.scalars().all()

        if emprestimos_vinculados:
            raise HTTPException(status_code=403, detail="Você não pode deletar um livro já emprestado.")

        nome_livro = livro.titulo
        await session.delete(livro)
        await session.commit()
        return{"Mensagem" : f"Livro {nome_livro} deletado com sucesso!"}

@app.delete("/emprestimos/{emprestimo_id}", dependencies=[Depends(verificar_api_key)])
async def deletar_emprestimo(emprestimo_id : int):
    async with AsyncSession(conexao) as session:
        emprestimo = await session.get(Emprestimo, emprestimo_id)
        if emprestimo is None:
            raise HTTPException(status_code=404, detail="Emprestimo não localizado")
        livro = await session.get(Livro, emprestimo.livro_id)
        nome_livro = livro.titulo
        usuario = await session.get(Usuario, emprestimo.usuario_id)
        nome_usuario = usuario.nome
        await session.delete(emprestimo)
        await session.commit()
        return {"Mensagem" : f"O empréstimo do livro {nome_livro} do usuário {nome_usuario} foi deletado com sucesso!"}

@app.get('/usuarios/emprestimos/{usuario_id}')
async def emprestimos_de_usuario(usuario_id:int):
    async with AsyncSession(conexao) as session:
        resultado = await session.execute(select(Emprestimo).where(Emprestimo.usuario_id == usuario_id))
        emprestimos = resultado.scalars().all()
        livros_emprestados = []
        for emprestimo in emprestimos:
            livro_emprestado = await session.get(Livro, emprestimo.livro_id)

            livros_emprestados.append({
                "emprestimo_id" : emprestimo.id,
                "titulo" : livro_emprestado.titulo,
                "data_emprestimo" : emprestimo.data_emprestimo,
                "data_devolucao" : emprestimo.data_devolucao_prevista,
                "data_devolucao_real": emprestimo.data_devolucao_real})

    return livros_emprestados
        