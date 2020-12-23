from flask import Flask, flash
from flask import render_template
from flask import request, redirect, send_file
from flask_login import LoginManager, login_required
from flask_paginate import Pagination, get_page_parameter, get_page_args
import sys
import pandas as pd
import glob
import os
import json
from datetime import datetime
from flask_login import current_user, login_user, logout_user
from models import (User, update_dados,
 check_table, check_file, seek_files, filtro)
#from init import app
from forms import (LoginForm, CadastroForm, FornecedorForm, neForm, nfForm, editusuario, 
editneForm, editnfForm, EditFornecedorForm, UploadForm, RelatorioForm, filtros)
from db import fornecedores, nota_fiscal, empenhos, db, usuarios, db_usuarios
from sqlalchemy import types
from werkzeug.utils import secure_filename
from relatorios import rel
from statements import statement


navios = [('GNHo', 'GNHo'), ('H-44', 'H-44'), ('H-41', 'H-41'), ('H-40', 'H-40'), ('H-39', 'H-39'),
 ('H-38', 'H-38'), ('H-36', 'H-36'), ('H-35', 'H-35'), ('H-34', 'H-34'), ('H-21', 'H-21'), ('H-11', 'H-11')]


@app.route('/inicio')
@login_required
def home():    
    nav = current_user.om
    return render_template('main.html', nav = nav)

@app.route('/relatorio', methods=['GET', 'POST'])
@login_required
def relatorio():
    form = RelatorioForm()

    dados = []
    print(form.data_inicial.data, form.data_final.data)
    try:
        print(form.data_inicial.data > form.data_final.data)
    except:
        pass
    if form.data_inicial.data != None and form.data_final.data != None:
        if form.data_inicial.data > form.data_final.data:
            flash('Data inicial posterior a data final')

            return redirect('/relatorio')
    if form.rel_pre_def.data:
        if current_user.om == 'gnho':
            if form.nav.data:
                st = statement(form.rel_pre_def.data, form.nav.data, form.data_inicial.data, form.data_final.data)
            else:
                st = statement(form.rel_pre_def.data, current_user.om, form.data_inicial.data, form.data_final.data)
        else:
            st = statement(form.rel_pre_def.data, current_user.om, form.data_inicial.data, form.data_final.data)
        for rows in db.query(st):
            dados.append(rows)
        if form.rel_pre_def.data == 'nf_total':
            path = rel('Notas Fiscais', dados, current_user.nip, current_user.usuario)
        elif form.rel_pre_def.data == 'nf_total_pagas':
            path = rel('Notas Fiscais Pagas', dados, current_user.nip, current_user.usuario)
        elif form.rel_pre_def.data == 'ne':
            path = rel('Notas de Empenho', dados, current_user.nip, current_user.usuario)
       
        return send_file(path)

    return render_template('relatorio.html', nav = current_user.om, form = form)

#FORNECEDORES

@app.route('/fornecedor', methods=["GET", "POST"])
@login_required
def fornecedor():
    nav = current_user.om
    
    if current_user.om.lower() == 'gnho':
        statement = 'SELECT * FROM fornecedores ORDER BY id'

        query = db.query(statement)

        #devido ao paginate tenho que usar o meu query de uma forma que consigo limitar quanto aparecerá, escolherei aqui uma list de orderdict
        results = []
        for rows in query:
            results.append(rows)
        
        #paginate
        search = False
        q = request.args.get('q')
        if q:
            search = True

        page = request.args.get(get_page_parameter(), type=int, default=1)

        ITEMS_PER_PAGE = 10
        i = (page-1)*ITEMS_PER_PAGE
        #assim, dependendo da page que estamos, consiguimos limitar o que aparecerá
        entries = results[i: i+ITEMS_PER_PAGE]

        #paginate class

        pagination = Pagination(page=page, total= len(results), per_page=ITEMS_PER_PAGE, search=search, record_name='Notas Fiscais', css_framework='bootstrap4')


        return  render_template('fornecedor.html', query=entries, table = fornecedores, nav=nav, pagination= pagination)
    else:
        return redirect('/')

@app.route('/cadastro_fornecedor', methods=["GET", "POST"])
@login_required
def cadastro_fornecedor():
    nav = current_user.om
    if current_user.om.lower() == 'gnho':
        form = FornecedorForm()
        print(form.errors)
        if form.validate_on_submit():
            
            if fornecedores.find_one(cnpj = form.cnpj.data) == None:
                
                novo_fornecedor = fornecedores.insert(dict(cnpj = form.cnpj.data, nome_fornecedor = form.nome_fornecedor.data))
            
                flash('Fornecedor {} cadatrado com sucesso'.format(fornecedores.find_one(cnpj=form.cnpj.data)['cnpj']))
                return redirect('/fornecedor')
            else:
                flash('Fornecedor já cadastrado para o cnpj {}'.format(form.cnpj.data))
        
    

        return  render_template('cadastro_fornecedor.html', form=form, nav=nav)
    else:
        return redirect('/')

@app.route("/fornecedor-{}".format('<int:id>'), methods=['GET', 'POST'])
@login_required
def editar_fornecedor(id: int):
    nav = current_user.om
    if current_user.om.lower() == 'gnho':
        '''Editar dados salvos, temos que '''
        dict_fornecedor = fornecedores.find_one(id  = id)
        
        form = EditFornecedorForm(nome_fornecedor = dict_fornecedor['nome_fornecedor'], cnpj=dict_fornecedor['cnpj'])

        if form.validate_on_submit():

            dados = dict(id = id, nome_fornecedor =form.nome_fornecedor.data, cnpj=form.cnpj.data)
        
            if check_table(fornecedores, 'cnpj', form.cnpj.data) != False:
                update_dados(fornecedores, 'cnpj', form.cnpj.data, dados)

                flash('Dados atualizados com sucesso')

                return redirect("/fornecedor")
            else:
                flash('Fornecedor {} já cadastrada. Por favor entre com outro nº de CNPJ.'.format(form.cnpj.data))
                return redirect("/fornecedor-{}".format(id))  

        else:

            return render_template('editar_fornecedor.html', form = form, id = id, nav = nav)
    else:
        return redirect('/')

#NOTA FISCAL

@app.route('/nf_inserir', methods=["GET", "POST"])
@login_required
def nf_inserir():
    nav = current_user.om
    form = nfForm()
    if nav == 'gnho':
        st = 'SELECT n_ne FROM nota_empenho'
    else:
        st = "SELECT n_ne FROM nota_empenho WHERE LOWER(nav) = '{}'".format(nav.lower())
    query = db.query(st)

    form.n_ne.choices = [(rows['n_ne'], rows['n_ne']) for rows in query]

    #if form.validate_on_submit():
        
    if nota_fiscal.find_one(n_nf = form.n_nf.data) == None:
        #query as NNFF atrelados ao empenho e verifica se somatório das NF<NE e se 
        #valor da NF que está sendo inserida é menor que NE
        st = ("SELECT SUM(n.vl_nf) AS sum_nf"
             " FROM nota_fiscal AS n" 
             " JOIN nota_empenho AS e" 
             " ON e.n_ne = n.n_ne" 
             " WHERE n.n_ne = '{}'".format(form.n_ne.data))

        q = db.query(st)
        sum_nf = [rows['sum_nf'] for rows in q]
        value_ne = empenhos.find_one(n_ne = form.n_ne.data)['vl_ne']
        
        print(sum_nf)
        if sum_nf == [None]:
            sum_nf = 0
            if value_ne >= sum_nf + form.vl_nf.data:
                nova_nf = nota_fiscal.insert(dict(n_ne = form.n_ne.data, n_nf = form.n_nf.data, vl_nf = form.vl_nf.data, data_nf = form.data_nf.data,
                                                data_entrada_nf = datetime.today().strftime('20%y-%m-%d'), data_pg = form.data_pg.data), 
                                                types = dict(n_ne = types.String,  n_nf = types.Integer, vl_nf = types.Numeric, 
                                                data_nf = types.Date, data_entrada_nf = types.Date, data_pg = types.Date))
                                                
            
                flash('NF {} cadatrado com sucesso'.format(nota_fiscal.find_one(n_nf=form.n_nf.data)['n_nf']))
                return redirect('/nf')
            else:
                flash('Valor da NF acima do valor disponível na NE {}. Disponível: {}'.format(form.n_ne.data, (value_ne - sum_nf)))
        else:
            if value_ne >= sum_nf[0] + form.vl_nf.data:
                nova_nf = nota_fiscal.insert(dict(n_ne = form.n_ne.data, n_nf = form.n_nf.data, vl_nf = form.vl_nf.data, data_nf = form.data_nf.data,
                                                data_entrada_nf = datetime.today().strftime('20%y-%m-%d'), data_pg = form.data_pg.data), 
                                                types = dict(n_ne = types.String,  n_nf = types.Integer, vl_nf = types.Numeric, 
                                                data_nf = types.Date, data_entrada_nf = types.Date, data_pg = types.Date))
                                                
            
                flash('NF {} cadatrado com sucesso'.format(nota_fiscal.find_one(n_nf=form.n_nf.data)['n_nf']))
                return redirect('/nf')
            else:
                flash('Valor da NF acima do valor disponível na NE {}. Disponível: {}'.format(form.n_ne.data, (value_ne - sum_nf[0])))

    elif form.n_nf.data == None:
        return render_template('nf_inserir.html', form = form, nav = nav)
        
    else:
        flash('NF já cadastrado para o número {}'.format(form.n_nf.data))
       
 

    return render_template('nf_inserir.html', form = form, nav = nav)

@app.route("/nf", methods=['GET', 'POST'])
@login_required
def ver_nfiscais():
    nav = current_user.om
    filenames, form = seek_files('nf', nav, db)
    filtro_form = filtros()

    page = request.args.get(get_page_parameter(), type=int, default=1)
   
    if filtro_form.om.data:
        if filtro_form.om.data == 'None':
            fil_om = {"e.nav": None}
        else:
            fil_om = {"e.nav": filtro_form.om.data}
    else:
        fil_om = {"e.nav": None}
    if filtro_form.fornecedor.data:
        if filtro_form.fornecedor.data == 'None':
            fil_for = {"fo.nome_fornecedor":None}
        else:
            fil_for = {"fo.nome_fornecedor":filtro_form.fornecedor.data}
    else:
        fil_for = {"f.nome_fornecedor":None}
    if filtro_form.nota_fiscal.data:
        nota_fiscal = {"f.n_nf": filtro_form.nota_fiscal.data}
    else:
        nota_fiscal = {"f.n_nf": None}
    if filtro_form.ne.data:
        fil_ne = {"f.n_ne": filtro_form.ne.data}
    else:
        fil_ne = {"f.n_ne": None}
    if filtro_form.data.data:
        fil_data = {"f.data_nf": filtro_form.data.data}
    else:
        fil_data = {"f.data_nf": None}
    if filtro_form.data_pagamento.data:
        fil_data_p = {"f.data_pg": filtro_form.data_pagamento.data}
    else:
        fil_data_p = {"f.data_pg": None}
    
    #juntar todos os filtros realizados
    if nav.lower() != 'gnho':
        fil_om = {"e.nav": nav}

    columns = [fil_om, fil_for, nota_fiscal, fil_ne, fil_data, fil_data_p]
    f = {}
    for column in columns:
        f.update(column)
     
    where = filtro(f)

    #variavel de quantos resultado tem no query
    count_query = 0
    st = ("SELECT e.nav, f.id, fo.nome_fornecedor, f.n_ne, f.n_nf, f.vl_nf, f.data_nf, f.data_entrada_nf, f.data_pg" 
    " FROM nota_fiscal as f" 
    " JOIN nota_empenho as e" 
    " ON f.n_ne = e.n_ne" 
    " JOIN fornecedores as fo" 
    " ON fo.id = e.id_fornecedor"
    " {}"
    " ORDER BY f.id").format(where)

    n = navios
    if (None, "Todos") not in n:
        n.append((None, "Todos"))
    filtro_form.om.choices = n
    
    st3 = ("SELECT nome_fornecedor"
    " FROM fornecedores")

    #query que será utilizado
    query = db.query(st)
    query_choice_forn = db.query(st3)


    forn_choi_fil = [(rows['nome_fornecedor'], rows['nome_fornecedor']) for rows in query_choice_forn]
    forn_choi_fil.append((None, "Todos"))
    filtro_form.fornecedor.choices = forn_choi_fil

    #devido ao paginate tenho que usar o meu query de uma forma que consigo limitar quanto aparecerá, escolherei aqui uma list de orderdict
    results = []
    for rows in query:
        results.append(rows)
    
    #paginate
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    if filtro_form.submit.data:
        page = 1

    ITEMS_PER_PAGE = 10
    i = (page-1)*ITEMS_PER_PAGE
    #assim, dependendo da page que estamos, consiguimos limitar o que aparecerá
    entries = results[i: i+ITEMS_PER_PAGE]

    #paginate class

    pagination = Pagination(page=page, total= len(results), per_page=ITEMS_PER_PAGE, search=search, record_name='Notas Fiscais', css_framework='bootstrap4')

    return render_template('nf.html', query = entries, form = form, nav = nav, filenames = filenames, filtro_form=filtro_form, pagination= pagination)

@app.route("/<page>/upload/<id_file>", methods=['GET', 'POST'])
def upload_file(id_file: int, page: str):
    form = UploadForm()

    #salvar a imagem que foi dada para upload
    
    if form.validate_on_submit():
        if check_file(app.instance_path, page, id_file) == None:
            filename = secure_filename(form.files.data.filename)

            #vamos salvar os aqruivos pelo seu id na respectiva pasta
            #por isso temos que retirar a extensão do arquivo, estou fazendo manualmente
            extension = filename[filename.rfind('.'):]
            final_name = str(id_file) + extension
            print(os.path.join(app.instance_path, page, final_name))

            form.files.data.save(os.path.join(
                app.instance_path, page, final_name
            ))

            return redirect('/{}'.format(page))

    return redirect('/{}'.format(page))

@app.route('/download_file/<tipo>/<filename>')
@login_required
def download_file(tipo: str, filename: str):

    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], tipo, filename))
    

@app.route("/nf-{}".format('<int:id>'), methods=['GET', 'POST'])
@login_required
def editar_nf(id: int):
    '''Editar dados salvos, temos que '''
    nav = current_user.om
    dict_nf = nota_fiscal.find_one(id  = id)
    
    form = editnfForm(n_ne = dict_nf['n_ne'], n_nf=dict_nf['n_nf'], 
                        vl_nf=dict_nf['vl_nf'], 
                        data_nf= dict_nf['data_nf'], data_entrada_nf= dict_nf['data_entrada_nf'],
                        data_pg= dict_nf['data_pg'])

    if form.validate_on_submit():

        dados = dict(id = id, n_ne =form.n_ne.data, n_nf=form.n_nf.data,
        vl_nf=form.vl_nf.data , data_nf= form.data_nf.data, data_entrada_nf= form.data_entrada_nf.data,
         data_pg = form.data_pg.data                   
        )
    
        if check_table(nota_fiscal, 'n_nf', form.n_nf.data) != False:
            update_dados(nota_fiscal, 'n_nf', form.n_nf.data, dados)

            flash('Dados atualizados com sucesso')

            return redirect("/nf")
        else:
            flash('Nota de empenho {} já cadastrada. Por favor entre com outro nº de NE.'.format(form.n_ne.data))
            return redirect("/nf-{}".format(id))  

    else:

        return render_template('editar_nf.html', form = form, id = id, nav=nav)

# NOTA DE EMPENHO

@app.route("/ne", methods=['GET', 'POST'])
@login_required
def ver_empenhos():
    nav = current_user.om
    filenames, form = seek_files('ne', nav, db)
    filtro_form = filtros()

    if filtro_form.om.data:
        if filtro_form.om.data == 'None':
            fil_om = {"e.nav": None}
        else:
            fil_om = {"e.nav": filtro_form.om.data}
    else:
        fil_om = {"e.nav": None}
    if filtro_form.fornecedor.data:
        if filtro_form.fornecedor.data == 'None':
            fil_for = {"f.nome_fornecedor":None}
        else:
            fil_for = {"f.nome_fornecedor":filtro_form.fornecedor.data}
    else:
        fil_for = {"f.nome_fornecedor":None}
    if filtro_form.solemp.data:
        fil_solemp = {"e.n_solemp": filtro_form.solemp.data}
    else:
        fil_solemp = {"e.n_solemp": None}
    if filtro_form.ne.data:
        fil_ne = {"e.n_ne": filtro_form.ne.data}
    else:
        fil_ne = {"e.n_ne": None}
    if filtro_form.data.data:
        fil_data = {"e.data_ne": filtro_form.data.data}
    else:
        fil_data = {"e.data_ne": None}
    
    #juntar todos os filtros realizados
    if nav.lower() != 'gnho':
        fil_om = {"e.nav": nav}

    columns = [fil_om, fil_for, fil_solemp, fil_ne, fil_data]
    f = {}
    for column in columns:
        f.update(column)
     
    where = filtro(f)
   
    st = ("SELECT e.id, e.nav, f.nome_fornecedor, e.n_solemp, e.n_ne, e.vl_ne, e.data_ne, e.data_solemp" 
    " FROM nota_empenho as e" 
    " JOIN fornecedores AS f" 
    " ON e.id_fornecedor = f.id"
    " {}"
    " ORDER BY e.id".format(where ))

    n = navios
    if (None, "Todos") not in n:
        n.append((None, "Todos"))
    filtro_form.om.choices = n
   
    st3 = ("SELECT nome_fornecedor"
    " FROM fornecedores")

    query = db.query(st)
    query3 = db.query(st3)

    forn_choi_fil = [(rows['nome_fornecedor'], rows['nome_fornecedor']) for rows in query3]
    forn_choi_fil.append((None, "Todos"))
    filtro_form.fornecedor.choices = forn_choi_fil

     #devido ao paginate tenho que usar o meu query de uma forma que consigo limitar quanto aparecerá, escolherei aqui uma list de orderdict
    results = []
    for rows in query:
        results.append(rows)

    #paginate
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    #quando estamos em página diferente da primeira e botamos filtro ele não mostra nada
    #isso porque o entries é igual a results[i: i+ITEMS_PER_PAGE], onde o i é uma função da page
    #quando aplicamos o filtro temos que volta o page para 1
    #seria melhor no futuro achar uma solução mais elegante e permanente
    if filtro_form.submit.data:
        page = 1

    ITEMS_PER_PAGE = 10
    i = (page-1)*ITEMS_PER_PAGE
    #assim, dependendo da page que estamos, consiguimos limitar o que aparecerá
    entries = results[i: i+ITEMS_PER_PAGE]


    #paginate class

    pagination = Pagination(page=page, total= len(results), per_page=ITEMS_PER_PAGE, search=search, record_name='Notas de Empenho', css_framework='bootstrap4')
    

    return render_template('ne.html', query = entries, table = nota_empenho, nav = nav, form = form, filenames = filenames, filtro_form = filtro_form, pagination= pagination)

@app.route("/ne-{}".format('<int:id>'), methods=['GET', 'POST'])
@login_required
def editar_ne(id: int):
    nav = current_user.om
    if current_user.om == "gnho":
        dict_ne = empenhos.find_one(id  = id)
        
        form = editneForm(id_fornecedor = dict_ne['id_fornecedor'], n_solemp=dict_ne['n_solemp'], 
                            n_ne=dict_ne['n_ne'] , vl_ne= dict_ne['vl_ne'], data_ne= dict_ne['data_ne'], data_solemp=dict_ne['data_solemp'])
        
        st = 'SELECT id, nome_fornecedor FROM fornecedores'
        query = db.query(st)
        form.id_fornecedor.choices = [(rows['id'], rows['nome_fornecedor']) for rows in query]
        form.nav.choices =  navios

        if form.validate_on_submit():

            dados = dict(id = id, id_fornecedor =form.id_fornecedor.data, n_solemp=form.n_solemp.data,
            n_ne=form.n_ne.data , vl_ne= form.vl_ne.data, data_ne= form.data_ne.data, nav = form.nav.data,
            data_solemp= form.data_solemp.data)
            
            if check_table(empenhos, 'n_ne', form.n_ne.data) != False:
                update_dados(empenhos, 'n_ne', form.n_ne.data, dados)

                flash('Dados atualizados com sucesso')

                return redirect("/ne")
            else:
                flash('Nota de empenho {} já cadastrada. Por favor entre com outro nº de NE.'.format(form.n_ne.data))
                return redirect("/ne-{}".format(id))  

        else:

            return render_template('edit_ne.html', form = form, id = id, nav = nav)
    else:

        return redirect('/')    
    
@app.route('/inserir_ne', methods=["GET", "POST"])
@login_required
def nota_empenho():
    #conseguindo o navio do usuario
    nav = current_user.om
    
    form = neForm()
    st = 'SELECT id, nome_fornecedor FROM fornecedores'
    query = db.query(st)
    form.id_fornecedor.choices = [(rows['id'], rows['nome_fornecedor']) for rows in query]
    form.nav.choices =  navios
 
    if nav == 'gnho':
        if form.validate_on_submit():
            
            if empenhos.find_one(n_ne = form.n_ne.data) == None:
                
                nova_ne = empenhos.insert(dict(id_fornecedor = form.id_fornecedor.data, n_solemp = form.n_solemp.data,
                                                n_ne = form.n_ne.data, vl_ne = form.vl_ne.data, data_ne = form.data_ne.data, nav = form.nav.data, 
                                                data_solemp=form.data_solemp.data), 
                                                types = dict(id_fornecedor = types.Integer , n_solemp = types.Integer,
                                                n_ne = types.String, vl_ne = types.Numeric, data_ne = types.Date, nav = types.String, data_solemp= types.Date))
            
                flash('NE {} cadatrado com sucesso'.format(empenhos.find_one(n_ne=form.n_ne.data)['n_ne']))
                return redirect('/ne')
            else:
                flash('NE já cadastrado para o número {}'.format(form.n_ne.data))
 

        return  render_template('inserir_ne.html', form=form, nav = nav)
    else:
        return redirect('/')

#USUARIOS

@app.route("/cadastro", methods=["GET", "POST"])
@login_required
def cadastro_usuario():
    form = CadastroForm()
    nav = current_user.om
    if form.validate_on_submit():
        
        if usuarios.find_one(nip = form.nip.data) == None:
            
            novo_usuario =User(nip = form.nip.data, usuario = form.usuario.data, perfil = form.perfil.data, om = form.om.data)
            novo_usuario.set_password(form.password.data)
            flash('Usuario(a) {} cadatrado com sucesso'.format(novo_usuario.usuario))
            return redirect('/usuarios')
        else:
            flash('Usuario já cadastrado para o nip {}'.format(form.nip.data))
         
 

    return  render_template('cadastro_usuario.html', title="Inserir novo usuário", form=form, nav = nav)
    
@app.route("/usuarios")
@login_required
def users():

    nav = current_user.om
    st = 'SELECT * FROM usuarios ORDER BY id'
    query = db_usuarios.query(st)

    #devido ao paginate tenho que usar o meu query de uma forma que consigo limitar quanto aparecerá, escolherei aqui uma list de orderdict
    results = []
    for rows in query:
        results.append(rows)
    
    #paginate
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get(get_page_parameter(), type=int, default=1)

    ITEMS_PER_PAGE = 10
    i = (page-1)*ITEMS_PER_PAGE
    #assim, dependendo da page que estamos, consiguimos limitar o que aparecerá
    entries = results[i: i+ITEMS_PER_PAGE]

    #paginate class

    pagination = Pagination(page=page, total= len(results), per_page=ITEMS_PER_PAGE, search=search, record_name='Notas Fiscais', css_framework='bootstrap4')

    return render_template('usuarios.html', query = entries, table=usuarios, nav = nav, pagination=pagination)

@app.route("/usuario-{}".format('<int:id>'), methods=['GET', 'POST'])
@login_required
def editar_usuario(id: int):
    '''Temos que acessar o usuario atraves da classe User.
    depois verificar se os campos foram preenchidos e quais foram preenchidos
    para poder fazer o user.update()'''
    nav = current_user.om
    nip = usuarios.find_one(id = id)['nip']
    nome = usuarios.find_one(id = id)['usuario']
    perfil = usuarios.find_one(id = id)['perfil']
    om =  usuarios.find_one(id = id)['om']

    form = editusuario(nip = nip, usuario = nome, perfil = perfil, om = om)
    form.nip.default = nip
    
    #carregando o usuário
    edit_user = User(nip = nip, usuario = nome, om = om)
    
    if form.validate_on_submit():
        #atualizando as modificações
        if int(form.nip.data) != int(form.nip.default):
            if edit_user.check_user(nip = form.nip.data) == False:
                print("info do form", form.nip.data, form.usuario.data, form.perfil.data)
                edit_user.updt(id_ = id, nip = form.nip.data, usuario = form.usuario.data, perfil = form.perfil.data, om = form.om.data)
                #verificando se foi feita modificação na senha
                if form.password.data != None and form.password.data != '':
                    edit_user.set_password(form.password.data)
                    flash('Alterações salvas')

                    return redirect('/usuarios')
                else:
                    flash('Alterações salvas')

                    return redirect('/usuarios')

            else:
                flash('Usuário já cadastrado para o nip: {}. Por favor entre com outro nip.'.format(form.nip.data))
                return redirect("/usuario-{}".format(id))
        else:
            edit_user.updt(id_ = id, nip = form.nip.default, usuario = form.usuario.data, perfil = form.perfil.data, om = form.om.data)
                #verificando se foi feita modificação na senha
            if form.password.data != None and form.password.data != '':
                edit_user.set_password(form.password.data)
                flash('Alterações salvas')

                return redirect('/usuarios')
            else:
                flash('Alterações salvas')
                return redirect('/usuarios')

    return render_template('edit_usuario.html', form = form, id = id, nav = nav)


@app.route("/delete_row/<table>/<int:id>")
@login_required
def delete_row(table, id: int):
    
    if table == 'usuarios':
        r_url = 'usuarios'
        table = usuarios
    elif table == 'fornecedor':
        id_fornecedor = fornecedores.find_one(id = id)['id']
        if empenhos.find_one(id_fornecedor = id_fornecedor) == None:
            r_url = 'fornecedor'
            table = fornecedores
        else:
            r_url = 'fornecedor'
            flash('Existem NNEE atreladas ao {}, por favor exluas primeiro.'.format(fornecedores.find_one(id = id)['nome_fornecedor']))

            return redirect('/{}'.format(r_url))

    elif table == 'nf':
        r_url = 'nf'
        table = nota_fiscal
    else:
        #verificar se tem alguma nota fiscal atrelada a essa NE
        n_ne = empenhos.find_one(id = id)['n_ne']
        if nota_fiscal.find_one(n_ne = n_ne) == None:
            r_url = 'ne'
            table = empenhos
        else:
            r_url = 'ne'
            flash('Existem NNFF atreladas a {}, por favor exluas primeiro.'.format(n_ne))

            return redirect('/{}'.format(r_url))
    
    table.delete(id = id)

    return redirect('/{}'.format(r_url))

@app.route('/set_date/<int:id>')
@login_required
def set_date(id:int):

    current_date = datetime.today().strftime('20%y-%m-%d')
    if nota_fiscal.find_one(id = id)['data_pg'] is None:
        nota_fiscal.update(dict(id = id, data_pg = current_date), ['id'])
    else:
        flash('Nota Fiscal já está paga')

    return redirect('/nf')

@app.route("/usuarios/<int:usuario_id>")
@login_required
def login_senha(usuario_id):
    nav = current_user.om
    usuario_i = usuarios.find_one(id = usuario_id) #query na tabela

    return render_template('resultado.html', usuario_i = usuario_i, nav = nav)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        nav = current_user.om
        pass
    except AttributeError:
        nav = 'anonimo'
        pass
        

    if current_user.is_authenticated:
        return redirect('/inicio')
    form = LoginForm()
    if form.validate_on_submit():
        user = User(nip=form.nip.data, usuario = 'load_user', om = 'load_user')
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect('/login')
        login_user(User(nip=form.nip.data, usuario = 'load_user', om = 'load_user'), remember=form.remember_me.data)
        return redirect('/inicio')
    return render_template('login.html', title='Sign In', form=form, nav = nav)

@app.route('/logout')
def logout():

    if current_user.is_authenticated:
        logout_user()

    return redirect('/login')
    