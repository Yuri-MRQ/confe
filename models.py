# coding: utf-8
from flask_login import UserMixin
import dataset
import psycopg2
from sqlalchemy import create_engine, types
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from dataset import Table
from init import login, app
import os
from forms import UploadForm
from db import usuarios, db_usuarios


#criar classe usuario para adicionar informações ao bd

class User (UserMixin, Table):

    def __init__(self, usuario,  nip, om, senha_hash = 'None', perfil = None):

        #ao criar um novo usuario já acessa o DB do usuarios e insere um novo
        #No mínimo temos que ter tanto o usuario quanto o nip, havendo usuario cadastrado, carregar as informações
        #não havendo insere o que foi opassado

        Table.__init__(self, database = db_usuarios, table_name = 'usuarios')
        #se não há o usuário, insere
        if self.find_one(nip = nip) == None:
            self.usuario = usuario
            self.senha_hash = senha_hash
            self.nip = nip
            self.perfil = perfil
            self.om = om
            self.insert(dict(usuario= usuario, senha_hash= senha_hash, nip= nip, perfil= perfil, om = om))
        #se existe o usuario carrega ele
        else:
            load_usuario = self.find_one(nip=nip)
            self.usuario = load_usuario['usuario']
            self.senha_hash = load_usuario['senha_hash']
            self.nip = load_usuario['nip']
            self.perfil = load_usuario['perfil']
            self.om = load_usuario['om']

    
    def get_id(self):

        return self.nip    

    #função gera a senha hash, com criptografia e da um self.update para atualiza a coluna senha_hash.
    def set_password(self, password):
        self.senha_hash = generate_password_hash(str(password))
        self.update(dict(nip = self.nip, senha_hash = self.senha_hash), ['nip'])

    #função verifica se a senha inserida confere com a do banco de dados
    def check_password(self, password):
        return check_password_hash(self.senha_hash, str(password))

    def check_user(self, nip):
        #verifica se usuário já cadastrado, boolean
        if self.find_one(nip = nip) == None:
            return False
        else:
            return True
    
    def updt(self, id_, usuario, nip, perfil, om):
        
        
        if self.nip == nip:
            self.usuario = usuario
            self.perfil = perfil
            self.om = om
            print("inf do updt:", id_, usuario, nip, perfil)
            self.update(dict(id = id_, nip = self.nip, usuario = self.usuario, perfil = self.perfil, om = self.om, senha_hash = self.senha_hash), ['id'])
    
        else:
            if self.check_user(nip) == False:
                self.usuario = usuario
                self.nip = nip
                self.perfil = perfil
                self.om = om
                self.update(dict(id = id_, nip = self.nip, usuario = self.usuario, perfil = self.perfil, om = self.om, senha_hash = self.senha_hash), ['id'])
            else:
                return('Usuário já cadastrado')

    def __repr__(self):
        return '<User {}>'.format(self.usuario)

@login.user_loader
def load_user(user):
    #recebe classe User já isntanciada
    return User(nip=user, usuario='loading', om = 'loading')


def update_dados(table, key, value, dict_):

    '''Função para atualizar dados do banco de dados.
    arg.
    table = table de um banco de dados
    key 'string'= será o valor unico dos dados, não considerando o ID, mas o valor que tem que ser único
    inserido pelo usuário. Valor da coluna.
    value = valor a ser comprado com a key
    dict = entrada para fazer o update

    '''
    print('update dados', check_table(table, key, value) != False)
    if check_table(table, key, value) != False:
        #não existe nenhuma entrada com esse valor único
        print(dict_)
        table.update(dict_, ['id'])
        return print('Linha atualizada com sucesso')
    else:
        return print('Valor {} já existe na tabela {}'.format(value, table))

def check_table(table, key, value):

    '''Verifica se existe o valor unico na tabela
    table = table de um banco de dados
    key 'string'= será o valor unico dos dados, não considerando o ID, mas o valor que tem que ser único
    inserido pelo usuário. Valor da coluna.
    value = valor a ser comprado com a key
    return True ou False - True se existe o valor na tabela, false se nao existe
    '''
    print('check table', table.find_one(key = value)==None)
    if table.find_one(key = value) != None:

        return table.find_one(key = value) != None

    else:
        return table.find_one(key = value) == None

def rt():
    '''filtros será uma list contendo os input'''
    st = ("SELECT  ne.nav, f.nome_fornecedor,nf.n_nf, nf.vl_nf, nf.data_pg FROM nota_fiscal AS nf JOIN nota_empenho as ne ON ne.n_ne = nf.n_ne JOIN fornecedores AS f ON ne.id_fornecedor = f.id WHERE LOWER(ne.nav) = 'gnho' AND nf.data_pg IS NOT NULL")

def check_file(app_path ,tipo, id):
    '''essa função verificará se há arquivo para o id da NF ou da NE
    havendo arquivo ela retornará o caminho para o arquivio
    tipo = nota fiscal ou nota de empenho, nf ou ne
    id = id da entrada no banco de dados
    
    return path filename'''
    extensions = ('.jpg', '.png', '.pdf')
    path_final = ''
    filename = ''
    for e in extensions:
        test_name = str(id) + e
        path = os.path.join(app_path, tipo, test_name)
        if os.path.exists(path) == True:
            path_final = path
            filename = test_name
    if path_final == '':
        filename = None

    
    return filename

def seek_files(tipo, nav, db):
    form = UploadForm()
   
    if nav.lower() == 'gnho':
        
        if tipo == 'nf':
            st = "SELECT f.id, fo.nome_fornecedor, f.n_ne, f.n_nf, f.vl_nf, f.data_nf, f.data_entrada_nf, f.data_pg FROM nota_fiscal as f JOIN nota_empenho as e ON f.n_ne = e.n_ne JOIN fornecedores as fo ON fo.id = e.id_fornecedor"
        elif tipo == 'ne':
            st = "SELECT e.id, f.nome_fornecedor, e.n_solemp, e.n_ne, e.vl_ne, e.data_ne FROM nota_empenho as e JOIN fornecedores AS f ON e.id_fornecedor = f.id"
    else:
        if tipo == 'nf':
            st = "SELECT f.id, fo.nome_fornecedor, f.n_ne, f.n_nf, f.vl_nf, f.data_nf, f.data_entrada_nf, f.data_pg FROM nota_fiscal as f JOIN nota_empenho as e ON f.n_ne = e.n_ne JOIN fornecedores as fo ON fo.id = e.id_fornecedor WHERE LOWER(e.nav) = '{}'".format(str(nav).lower())
        elif tipo == 'ne':
            st = "SELECT e.id, f.nome_fornecedor, e.n_solemp, e.n_ne, e.vl_ne, e.data_ne FROM nota_empenho as e JOIN fornecedores AS f ON e.id_fornecedor = f.id WHERE LOWER(e.nav) = '{}'".format(str(nav).lower())
        
    query = db.query(st)

    filenames = dict()
    for row in query:
        
        if check_file(app.instance_path, str(tipo), row['id']) != None:
            
            filenames[row['id']] = check_file(app.instance_path,str(tipo), row['id'])
    print(filenames)
    return filenames, form
    

def filtro(fil_dic):
    '''fil_dic será um dict com todos os filtros desejados
    a key será a coluna do SQL statemente eo value será o fitlro desejado
    
    ex: fil_dic = {e.nav: gnho}'''
    
    where_st = "WHERE "
    filtros = 0
    count_not_none = 0

    for value in fil_dic.values():
        if value != None:
            count_not_none += 1
    print(count_not_none)
    for key in fil_dic.keys():
        if fil_dic[key] == "":
            pass
        elif fil_dic[key] != None:
            new_filter = " {} = '{}'".format(key, fil_dic[key])
            where_st += new_filter
            filtros += 1
            count_not_none -= 1
            if count_not_none >= 1:
                print('count_not_none', count_not_none )
                #necessário para não botar um último AND sem ter argumento que segue
                where_st += " AND "
        

    if filtros == 0:
        where_st = ""

    print("where:", where_st)
    return where_st

    

        
