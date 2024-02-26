from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from mindforgepy01.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    fullname = StringField('Nome Completo:', validators=[DataRequired(), Length(3, 50)])
    email = StringField('Melhor E-mail:', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha:', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha:', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError(f'O e-mail informado ({email.data}) foi cadastrado anteriormente. '
                                  'Por gentileza, utilizar outro e-mail ou realizar o login para continuar!')


class FormLogin(FlaskForm):
    email_login = StringField('E-mail:', validators=[DataRequired(), Email()])
    senha_login = PasswordField('Senha:', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar dados de login?')
    botao_submit_login = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    fullname = StringField('Insira o Novo Nome Completo:', validators=[Length(3, 50)])
    email = StringField('Insira o Novo E-mail:', validators=[Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil:',
                            validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    curso_excel = BooleanField('Excel')
    curso_word = BooleanField('Word')
    curso_power_point = BooleanField('Power Point')
    curso_power_bi = BooleanField('Power BI')
    curso_sql = BooleanField('SQL')
    curso_python = BooleanField('Python')
    curso_javascript = BooleanField('Javascript')
    curso_html = BooleanField('HTML')
    curso_css = BooleanField('CSS')
    botao_submit_editarperfil = SubmitField('Confirmar Alterações')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError(f'O e-mail informado ({email.data})é utilizado por um usuário. '
                                      'Por favor altere para outro e-mail, caso necessário!')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post:', validators=[DataRequired(), Length(2, 150)])
    corpo = TextAreaField('Escreva Seu Post:', validators=[DataRequired()])
    botao_submit_criar_post = SubmitField('Gravar Post')
