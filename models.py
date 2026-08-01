from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from sqlalchemy import func, ForeignKey, create_engine
from typing import Optional

class Base(DeclarativeBase):
    pass

class Livro(Base):
    __tablename__ = "livros"
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str]
    isbn: Mapped[int] = mapped_column(unique=True)
    quantidade_total: Mapped[int]
    quantidade_disponivel: Mapped[int]

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

conexao = create_engine('sqlite:///data/bibliotrack.db')