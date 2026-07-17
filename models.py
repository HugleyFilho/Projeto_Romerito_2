from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class Usuario(UserMixin, db.Model):

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    projetos = db.relationship(
        "Projeto", backref="autor", lazy=True, cascade="all, delete-orphan"
    )
    avaliacoes = db.relationship(
        "Avaliacao", backref="autor", lazy=True, cascade="all, delete-orphan"
    )

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<Usuario {self.email}>"


class Projeto(db.Model):

    __tablename__ = "projetos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    avaliacoes = db.relationship(
        "Avaliacao", backref="projeto", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def media_avaliacoes(self):
        if not self.avaliacoes:
            return 0
        return round(sum(a.nota for a in self.avaliacoes) / len(self.avaliacoes), 1)

    def __repr__(self):
        return f"<Projeto {self.nome}>"


class Avaliacao(db.Model):

    __tablename__ = "avaliacoes"

    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(300), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


    projeto_id = db.Column(db.Integer, db.ForeignKey("projetos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    def __repr__(self):
        return f"<Avaliacao projeto={self.projeto_id} nota={self.nota}>"
