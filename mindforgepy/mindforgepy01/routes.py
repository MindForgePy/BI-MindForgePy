from flask import render_template, redirect, url_for, flash, request, abort
from mindforgepy01 import app, database, bcrypt
from mindforgepy01.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from mindforgepy01.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


@app.route('/')
def home():
    # logo_site = url_for('static', filename='logo_site')
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)

@app.route('/teste')
def teste():
    return render_template('teste.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/contato')
def contato():
    # logo_site = url_for('static', filename='logo_site')
    return render_template('contato.html')


@app.route('/perfil')
@login_required
def perfil():
    # logo_site = url_for('static', filename='logo_site')
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo_armazenado = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo_armazenado)
    tamanho_imagem = (400, 400)
    imagem_reduziada = Image.open(imagem)
    imagem_reduziada.thumbnail(tamanho_imagem)
    imagem_reduziada.save(caminho_completo)
    return nome_arquivo_armazenado


def atualizar_cursos(formulario):
    lista_cursos = []
    for campo in formulario:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return ';'.join(lista_cursos)


@app.route('/perfil/editar', methods=['GET', 'POST', 'HEAD'])
@login_required
def editar_perfil():
    # logo_site = url_for('static', filename='logo_site')
    form_editar_perfil_routes = FormEditarPerfil()
    if form_editar_perfil_routes.validate_on_submit():
        current_user.email = form_editar_perfil_routes.email.data
        current_user.fullname = form_editar_perfil_routes.fullname.data
        if form_editar_perfil_routes.foto_perfil.data:
            nome_imagem = salvar_imagem(form_editar_perfil_routes.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form_editar_perfil_routes)
        database.session.commit()
        flash(f"O e-mail foi alterado para '{form_editar_perfil_routes.email.data}' e o nome para '{form_editar_perfil_routes.fullname.data}'!", "alert-success")
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form_editar_perfil_routes.email.data = current_user.email
        form_editar_perfil_routes.fullname.data = current_user.fullname
        form_editar_perfil_routes.foto_perfil.data = current_user.foto_perfil
        form_editar_perfil_routes.curso_excel.data = current_user.curso_excel
        form_editar_perfil_routes.curso_word.data = current_user.curso_word
        form_editar_perfil_routes.curso_power_point.data = current_user.curso_power
        form_editar_perfil_routes.curso_power_bi.data = current_user.curso_power_bi
        form_editar_perfil_routes.curso_sql.data = current_user.curso_sql
        form_editar_perfil_routes.curso_python.data = current_user.curso_python
        form_editar_perfil_routes.curso_javascript.data = current_user.curso_javascript
        form_editar_perfil_routes.curso_html.data = current_user.curso_html
        form_editar_perfil_routes.curso_css.data = current_user.curso_css
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editar_perfil_html.html', foto_perfil=foto_perfil, form_editar_perfil_routes=form_editar_perfil_routes)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form_criar_post_routes = FormCriarPost()
    if form_criar_post_routes.validate_on_submit():
        post = Post(titulo=form_criar_post_routes.titulo.data, corpo=form_criar_post_routes.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash(f"O Post '{form_criar_post_routes.titulo.data}' foi salvo com sucesso!", "alert-success")
        return redirect(url_for('home'))
    return render_template('criarpost.html', form_criar_post_routes=form_criar_post_routes)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form_editar_post_routes = FormCriarPost()
        if request.method == 'GET':
            form_editar_post_routes.titulo.data = post.titulo
            form_editar_post_routes.corpo.data = post.corpo
        elif form_editar_post_routes.validate_on_submit():
            post.titulo = form_editar_post_routes.titulo.data
            post.corpo = form_editar_post_routes.corpo.data
            database.session.commit()
            flash(f"O Post '{form_editar_post_routes.titulo.data}' foi atualizado com sucesso!", "alert-success")
            return redirect(url_for('home'))
    else:
        form_editar_post_routes = None
    return render_template('post.html', post=post, form_editar_post_routes=form_editar_post_routes)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash(f"O Post '{post.titulo}' foi excluído com sucesso!", "alert-danger")
        return redirect(url_for('home'))
    else:
        abort(403)


@app.route('/login', methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    if form_login.validate_on_submit() and "botao_submit_login" in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email_login.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha_login.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f"Login realizado com sucesso para o e-mail '{form_login.email_login.data}'!", "alert-success")
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        elif not usuario:
            flash(f"O e-mail '{form_login.email_login.data}' não possui cadastro! Cadastre-se para continuar.", "alert-danger")
        else:
            flash('Falha no login! E-mail e/ou senha estão incorretos.', "alert-warning")

    form_criar_conta = FormCriarConta()
    if form_criar_conta.validate_on_submit() and "botao_submit_criarconta" in request.form:
        senha_crypt = bcrypt.generate_password_hash(form_criar_conta.senha.data).decode("utf-8")
        usuario = Usuario(fullname=form_criar_conta.fullname.data, email=form_criar_conta.email.data, senha=senha_crypt)
        database.session.add(usuario)
        database.session.commit()
        flash(f"Conta criada para e-mail '{form_criar_conta.email.data}'!", "alert-success")
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criar_conta=form_criar_conta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f"Logout realizado com sucesso!", "alert-success")
    return redirect(url_for('home'))
