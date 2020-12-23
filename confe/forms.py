from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField, IntegerField,
FloatField, DateField, DecimalField, MultipleFileField, SelectField, validators,
TextAreaField)
from wtforms.validators import DataRequired, InputRequired
from flask_wtf.file import FileField,FileRequired,FileAllowed


navios = [('gnho', 'GNHo'), ('H-44', 'H-44'), ('H-41', 'H-41'), ('H-40', 'H-40'), ('H-39', 'H-39'),
 ('H-38', 'H-38'), ('H-36', 'H-36'), ('H-35', 'H-35'), ('H-34', 'H-34'), ('H-21', 'H-21'), ('H-11', 'H-11')]

class LoginForm(FlaskForm):
    nip = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CadastroForm(FlaskForm):
    nip = StringField('Nip', validators=[DataRequired()])
    usuario = StringField('Nome', validators=[DataRequired()])
    perfil = StringField('Perfil', validators=[DataRequired()])
    om = SelectField('OM', choices = navios, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

class editusuario(FlaskForm):
    nip = StringField('Nip')
    usuario = StringField('Nome')
    perfil = StringField('Perfil')
    om = SelectField('OM', choices = navios)
    password = PasswordField('Password')
    submit = SubmitField('Salvar')

class FornecedorForm(FlaskForm):
    nome_fornecedor = StringField('Nome do Fornecedor')
    cnpj = StringField('CNPJ')
    submit = SubmitField('Cadastrar')

class EditFornecedorForm(FlaskForm):
    nome_fornecedor = StringField('Nome do Fornecedor', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[InputRequired()])
    submit = SubmitField('Cadastrar')

class neForm(FlaskForm):
    id_fornecedor = SelectField('Nome do fornecedor', coerce=int,validators=[DataRequired()])
    n_ne = StringField('NE', validators=[DataRequired()])
    vl_ne = DecimalField('Valor da NE', validators=[DataRequired()])
    data_ne = DateField('Data da NE', validators=[DataRequired()], format= "%d/%m/%Y")
    n_solemp = StringField('SOLEMP', validators=[DataRequired()])
    data_solemp = DateField('Data da SOLEMP', validators=[DataRequired()], format= "%d/%m/%Y")
    nav = SelectField('Navio', coerce=str,validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

class editneForm(FlaskForm):
    id_fornecedor = SelectField('Nome do fornecedor', coerce=int)
    n_ne = StringField('NE')
    vl_ne = DecimalField('Valor da NE')
    data_ne = DateField('Data da NE', format= "%d/%m/%Y")
    n_solemp = StringField('SOLEMP')
    data_solemp = DateField('Data da SOLEMP', validators=[DataRequired()], format= "%d/%m/%Y")
    nav = SelectField('Navio', coerce=str)
    submit = SubmitField('Cadastrar')

class nfForm(FlaskForm):
    n_ne = SelectField('NE', coerce=str, validators=[DataRequired()])
    n_nf = StringField('NF', validators=[DataRequired()])
    vl_nf = DecimalField('Valor da NF', validators=[DataRequired()])
    data_nf = DateField('Data da NF', validators=[DataRequired()], format= "%d/%m/%Y")
    data_pg = DateField('Data do pagamento', format= "%d/%m/%Y")
    submit = SubmitField('Cadastrar')

class editnfForm(FlaskForm):
    n_ne = StringField('NE')
    n_nf = StringField('NF')
    vl_nf = DecimalField('Valor da NF')
    data_nf = DateField('Data da NF', format= "%d/%m/%Y")
    data_pg = DateField('Data do pagamento', format= "%d/%m/%Y")
    submit = SubmitField('Cadastrar')

class UploadForm(FlaskForm):
    files = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png', 'pdf'], 'Imagem ou pdf apenas!')])
    submit = SubmitField('Upload')

class RelatorioForm(FlaskForm):
    rel_pre_def = SelectField('Opções', choices = [('nf_total', 'Notas Fiscais'), ('nf_total_pagas', 'Notas Fiscais Pagas'),
    ('ne', 'Notas de Empenho')])
    nav = SelectField('Navio', choices = [('gnho', 'Todos'), ('H-44', 'H-44'), ('H-41', 'H-41'), ('H-40', 'H-40'), ('H-39', 'H-39'),
 ('H-38', 'H-38'), ('H-36', 'H-36'), ('H-35', 'H-35'), ('H-34', 'H-34'), ('H-21', 'H-21'), ('H-11', 'H-11')])
    data_inicial = DateField('Data inicial', format= "%d/%m/%Y")
    data_final = DateField('Data final', format= "%d/%m/%Y")
    stm = TextAreaField('Statament (SQL)')
    submit = SubmitField('Gerar')

class filtros(FlaskForm):

    om = SelectField('Navio', coerce=str)
    fornecedor = SelectField('Fornecedor', coerce=str)
    nota_fiscal = StringField('Nota Fiscal')
    data_pagamento = DateField('Data de pagamento', format= "%d/%m/%Y")
    solemp = StringField('SOLEMP')
    ne = StringField('NE')
    data = DateField('Data', format= "%d/%m/%Y")
    submit = SubmitField('Filtrar')
