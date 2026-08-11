from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from sqlalchemy import BigInteger, func, ForeignKey, create_engine
from typing import Optional
from dotenv import load_dotenv
import os


load_dotenv()


class Base(DeclarativeBase):
    pass

class Livro(Base):
    __tablename__ = "livros"
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str]
    isbn: Mapped[int] = mapped_column(BigInteger, unique=True)
    quantidade_total: Mapped[int]
    quantidade_disponivel: Mapped[int]
    genero: Mapped[str]

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    data_cadastro: Mapped[date] = mapped_column(server_default=func.current_date())
    
class Emprestimo(Base):
    __tablename__ = "emprestimos"
    id: Mapped[int] = mapped_column(primary_key=True)
    livro_id: Mapped[int] = mapped_column(ForeignKey("livros.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    data_emprestimo: Mapped[date] = mapped_column(server_default=func.current_date())
    data_devolucao_prevista: Mapped[date]
    data_devolucao_real: Mapped[Optional[date]]

url = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

sslmode = os.getenv('POSTGRES_SSLMODE')
if sslmode:
    url += f"?sslmode={sslmode}"

conexao = create_engine(url)