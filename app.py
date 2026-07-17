import os

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user

from config import Config
from extensions import db, login_manager
from models import Usuario, Projeto, Avaliacao

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def carregar_usuario(usuario_id):
    return db.session.get(Usuario, int(usuario_id))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        erro = None
        if not nome or not email or not senha:
            erro = "Preencha todos os campos."
        elif len(senha) < 6:
            erro = "A senha precisa ter pelo menos 6 caracteres."
        elif senha != confirmar_senha:
            erro = "As senhas não coincidem."
        elif Usuario.query.filter_by(email=email).first():
            erro = "Já existe uma conta com esse e-mail."

        if erro:
            flash(erro, "erro")
            return render_template("registro.html", nome=nome, email=email)

        usuario = Usuario(nome=nome, email=email)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login.", "sucesso")
        return redirect(url_for("login"))

    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.checar_senha(senha):
            login_user(usuario)
            proxima_pagina = request.args.get("next")
            return redirect(proxima_pagina or url_for("index"))

        flash("E-mail ou senha inválidos.", "erro")
        return render_template("login.html", email=email)

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    busca = request.args.get("q", "").strip()

    consulta = Projeto.query
    if busca:
        consulta = consulta.filter(Projeto.nome.ilike(f"%{busca}%"))

    projetos = consulta.order_by(Projeto.criado_em.desc()).all()

    meus_projetos = (
        Projeto.query.filter_by(usuario_id=current_user.id)
        .order_by(Projeto.criado_em.desc())
        .all()
    )

    minhas_avaliacoes = (
        Avaliacao.query.filter_by(usuario_id=current_user.id)
        .order_by(Avaliacao.criado_em.desc())
        .all()
    )

    return render_template(
        "index.html",
        projetos=projetos,
        meus_projetos=meus_projetos,
        avaliacoes=minhas_avaliacoes,
        busca=busca,
    )

@app.route("/projetos/novo", methods=["POST"])
@login_required
def criar_projeto():
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome:
        flash("Dê um nome ao projeto.", "erro")
        return redirect(url_for("index"))

    projeto = Projeto(nome=nome, descricao=descricao, usuario_id=current_user.id)
    db.session.add(projeto)
    db.session.commit()

    flash("Projeto adicionado.", "sucesso")
    return redirect(url_for("index"))

@app.route("/projetos/<int:projeto_id>/editar", methods=["POST"])
@login_required
def editar_projeto(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)

    if projeto.usuario_id != current_user.id:
        abort(403)

    nome = request.form.get("nome", "").strip()
    if not nome:
        flash("O nome do projeto não pode ficar vazio.", "erro")
        return redirect(url_for("index"))

    projeto.nome = nome
    projeto.descricao = request.form.get("descricao", "").strip()
    db.session.commit()

    flash("Projeto atualizado.", "sucesso")
    return redirect(url_for("index"))

@app.route("/projetos/<int:projeto_id>/deletar", methods=["POST"])
@login_required
def deletar_projeto(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)

    if projeto.usuario_id != current_user.id:
        abort(403)

    db.session.delete(projeto)
    db.session.commit()

    flash("Projeto removido.", "sucesso")
    return redirect(url_for("index"))

@app.route("/projetos/<int:projeto_id>/avaliar", methods=["POST"])
@login_required
def criar_avaliacao(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)

    comentario = request.form.get("comentario", "").strip()
    nota = request.form.get("nota", "5")

    if not comentario:
        flash("Escreva um comentário para avaliar.", "erro")
        return redirect(url_for("index"))

    try:
        nota = max(1, min(5, int(nota)))
    except ValueError:
        nota = 5

    avaliacao = Avaliacao(
        comentario=comentario,
        nota=nota,
        projeto_id=projeto.id,
        usuario_id=current_user.id,
    )
    db.session.add(avaliacao)
    db.session.commit()

    flash("Avaliação registrada.", "sucesso")
    return redirect(url_for("index"))

@app.route("/avaliacoes/<int:avaliacao_id>/editar", methods=["POST"])
@login_required
def editar_avaliacao(avaliacao_id):
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    if avaliacao.usuario_id != current_user.id:
        abort(403)

    comentario = request.form.get("comentario", "").strip()
    if not comentario:
        flash("O comentário não pode ficar vazio.", "erro")
        return redirect(url_for("index"))

    avaliacao.comentario = comentario
    try:
        avaliacao.nota = max(1, min(5, int(request.form.get("nota", avaliacao.nota))))
    except ValueError:
        pass

    db.session.commit()
    flash("Avaliação atualizada.", "sucesso")
    return redirect(url_for("index"))

@app.route("/avaliacoes/<int:avaliacao_id>/deletar", methods=["POST"])
@login_required
def deletar_avaliacao(avaliacao_id):
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)

    if avaliacao.usuario_id != current_user.id:
        abort(403)

    db.session.delete(avaliacao)
    db.session.commit()

    flash("Avaliação removida.", "sucesso")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)